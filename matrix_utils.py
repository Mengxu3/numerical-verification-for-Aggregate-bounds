# 文件名: matrix_utils.py
import numpy as np
import itertools
from scipy.special import comb
from scipy.linalg import null_space, eigvalsh, qr, eigh

def generate_hermitian(n):
    """生成随机厄米矩阵"""
    A = np.random.randn(n, n) + 1j * np.random.randn(n, n)
    return A + A.conj().T

def get_sub_eigs(mat, size):
    """获取所有子矩阵特征值"""
    idx = list(range(mat.shape[0]))
    vals = []
    for subset in itertools.combinations(idx, size):
        sub_A = mat[np.ix_(subset, subset)]
        vals.extend(np.linalg.eigvalsh(sub_A))
    return np.sort(np.array(vals))[::-1]

# ==========================================
# Theorem 1.4: Aggregate Bounds
# ==========================================
def check_bounds_theorem(n, l, r):
    A = generate_hermitian(n)
    lambdas = np.linalg.eigvalsh(A)[::-1]
    
    sub_eigs_sum = 0.0
    idx_list = list(range(n))
    for k in range(n):
        keep = [i for i in idx_list if i != k]
        w = np.linalg.eigvalsh(A[np.ix_(keep, keep)])[::-1]
        sub_eigs_sum += np.sum(w[l-1:r])
    
    term_lam = np.sum(lambdas[l-1:r])
    term_lam_next = np.sum(lambdas[l:r+1])
    
    lb = (r - l + 1) * lambdas[l-1] + (n - 1) * term_lam_next
    ub = (n - 1) * term_lam + (r - l + 1) * lambdas[r]
    
    passed = (lb - 1e-7 <= sub_eigs_sum <= ub + 1e-7)
    return passed, sub_eigs_sum, lb, ub

# ==========================================
# Theorem 4.1: Spectral Hierarchy
# ==========================================
def check_hierarchy_theorem(n, m, k):
    A = generate_hermitian(n)
    X_m = get_sub_eigs(A, m)
    X_k = get_sub_eigs(A, k)
    
    c_m = int(comb(m-1, k-1))
    c_k = int(comb(n-k, m-k))
    
    v_left = np.repeat(X_m, c_m)
    v_right = np.repeat(X_k, c_k)
    
    diff = np.cumsum(v_left) - np.cumsum(v_right)
    min_diff = np.min(diff)
    
    passed = (min_diff >= -1e-7) and (abs(diff[-1]) < 1e-7)
    
    violation = 0.0
    if not passed:
        violation = abs(min_diff)
        
    return passed, v_left, v_right, violation

# ==========================================
# Theorem 2.2: Weighted Projection (Main Result)
# ==========================================
def check_weighted_theorem(n, l, r, stress_mode=False):
    if stress_mode:
        # 地狱模式：完全复刻脚本逻辑
        # 1. 强制重根
        raw_vals = np.random.uniform(-10, 10, n)
        if np.random.rand() < 0.5:
            dup_idx = np.random.randint(0, n-2)
            raw_vals[dup_idx+1] = raw_vals[dup_idx]
            if n > 3: raw_vals[dup_idx+2] = raw_vals[dup_idx]
        lambdas = np.sort(raw_vals)[::-1]

        # 2. 强制零权重/微小权重 (复刻 logic)
        u = np.random.randn(n)
        rand_val = np.random.rand()
        if rand_val < 0.3:
            # 30% 概率：绝对零
            u[np.random.randint(0, n)] = 0.0
        elif rand_val < 0.6:
            # 30% 概率：微小值 (1e-8)
            u[np.random.randint(0, n)] = 1e-8
            
        u /= np.linalg.norm(u)
        weights = u**2
        
        try:
            V = null_space(u.reshape(1, -1))
            mus = np.sort(eigvalsh(V.T @ np.diag(lambdas) @ V))[::-1]
        except:
            Q, _ = qr(u.reshape(-1, 1), mode='full')
            V = Q[:, 1:]
            mus = np.sort(eigvalsh(V.T @ np.diag(lambdas) @ V))[::-1]
    else:
        # 普通模式
        A = generate_hermitian(n)
        lambdas, V_eigen = np.linalg.eigh(A)
        idx = np.argsort(lambdas)[::-1]
        lambdas = lambdas[idx]
        V_eigen = V_eigen[:, idx]
        
        u = np.random.randn(n) + 1j * np.random.randn(n)
        u /= np.linalg.norm(u)
        u_rotated = V_eigen.conj().T @ u
        weights = np.abs(u_rotated)**2 
        
        Q, _ = qr(u.reshape(-1, 1), mode='full')
        V_perp = Q[:, 1:] 
        sub_mat = V_perp.conj().T @ A @ V_perp
        mus = np.linalg.eigvalsh(sub_mat)[::-1]

    if r >= n-1: r = n-2
    
    sum_mu = np.sum(mus[l : r + 1])
    U_l = np.sum(weights[l:])
    L_r_plus_1 = np.sum(weights[:r + 2])
    
    if U_l < 1e-12 or L_r_plus_1 < 1e-12:
        return True, 0, 0, 0, 0 

    term1_rhs = np.sum(lambdas[l : r + 1])
    diff_rhs = lambdas[l : r + 1] - lambdas[r + 1]
    term2_rhs = np.sum((weights[l : r + 1] / U_l) * diff_rhs)
    rhs = term1_rhs - term2_rhs
    
    term1_lhs = np.sum(lambdas[l + 1 : r + 2])
    diff_lhs = lambdas[l] - lambdas[l + 1 : r + 2]
    term2_lhs = np.sum((weights[l + 1 : r + 2] / L_r_plus_1) * diff_lhs)
    lhs = term1_lhs + term2_lhs
    
    violation = 0.0
    if sum_mu < lhs - 1e-9: violation = lhs - sum_mu
    if sum_mu > rhs + 1e-9: violation = sum_mu - rhs
    
    passed = (violation == 0.0)
    return passed, sum_mu, lhs, rhs, violation

# ==========================================
# Lemma 3.1: Polynomial Roots
# ==========================================
def check_lemma_polynomial(n, stress_mode=False):
    if stress_mode:
        # 地狱模式：复刻 test lemma 3.1 new.py 的核心逻辑
        
        # 1. 制造重根 (随机整数范围 -10 到 10)
        lambdas = np.sort(np.random.randint(-10, 10, n).astype(float))[::-1]
        
        # 2. 制造零权重/微小权重 (恐怖谷)
        u = np.random.randn(n)
        rand_val = np.random.rand()
        
        if rand_val < 0.3:
            # 30% 概率：绝对零
            u[np.random.randint(0, n)] = 0.0
        elif rand_val < 0.6:
            # 30% 概率：微小值 (1e-8) - 专门测试数值稳定性
            u[np.random.randint(0, n)] = 1e-8
            
        u /= np.linalg.norm(u)
        weights = u**2
        
        try:
            Q = null_space(u.reshape(1, -1))
            mus_geometric = eigvalsh(Q.T @ np.diag(lambdas) @ Q)
        except:
            Q, _ = qr(u.reshape(-1, 1), mode='full')
            mus_geometric = eigvalsh(Q[:, 1:].T @ np.diag(lambdas) @ Q[:, 1:])
    else:
        # 普通模式 (用于可视化)
        A = generate_hermitian(n)
        lambdas, V = np.linalg.eigh(A)
        idx = np.argsort(lambdas)[::-1]
        lambdas = lambdas[idx]
        V = V[:, idx]
        
        u = np.random.randn(n) + 1j * np.random.randn(n)
        u /= np.linalg.norm(u)
        weights = np.abs(V.conj().T @ u)**2 
        
        Q, _ = qr(u.reshape(-1, 1), mode='full')
        V_perp = Q[:, 1:]
        mus_geometric = eigvalsh(V_perp.conj().T @ A @ V_perp)

    mus_geometric = np.sort(mus_geometric)[::-1]

    # 定义多项式函数 P(x)
    def poly_func(x_vec):
        y_vec = np.zeros_like(x_vec, dtype=float)
        for k, x in enumerate(x_vec):
            val = 0.0
            for i in range(n):
                # prod(lambda_j - x) for j != i
                term = weights[i]
                for j in range(n):
                    if i == j: continue
                    term *= (lambdas[j] - x)
                val += term
            y_vec[k] = val
        return y_vec

    residuals = poly_func(mus_geometric)
    
    # 归一化处理
    scale = np.mean(np.abs(lambdas))**(n-2) if n > 2 else 1.0
    if scale < 1e-6: scale = 1.0
    max_res = np.max(np.abs(residuals)) / scale
    
    # 稍微放宽一点阈值，因为微小权重可能导致高阶多项式数值抖动
    passed = (max_res < 1e-4)

    padding = (lambdas[0] - lambdas[-1]) * 0.1
    if padding == 0: padding = 1.0
    x_range = (lambdas[-1] - padding, lambdas[0] + padding)

    return passed, lambdas, mus_geometric, poly_func, x_range, max_res