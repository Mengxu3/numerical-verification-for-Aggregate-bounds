# 文件名: theorem_texts.py

# ==========================================
# Theorem 1.4: Aggregate Bounds (Benchmark)
# ==========================================

THM1_4_DESC = (
    "OBJECTIVE:\n"
    "This theorem (from our paper) establishes global bounds for the sum of eigenvalues "
    "of all principal submatrices. It serves as the foundational aggregate result.\n\n"
    
    "LEGEND (SYMBOL DEFINITIONS):\n"
    "• A : An n × n Hermitian matrix.\n"
    "• λ : Eigenvalues of A, sorted descending (λ₁ ≥ λ₂ ≥ ... ≥ λₙ).\n"
    "• μₖ,ⱼ : The j-th eigenvalue of the principal submatrix obtained by deleting the k-th row/col.\n"
    "• Middle Term : The double summation sums these μ values over all submatrices (k=1..n) "
    "and within the window (j=l..r).\n\n"
    
    "SIGNIFICANCE:\n"
    "It proves that the total 'partial energy' of all subsystems is strictly confined by "
    "the eigenvalues of the original system."
)

THM1_4_LATEX = (
    r"$(r-l+1)\lambda_{l} + (n-1)\sum_{j=l}^{r}\lambda_{j+1} \leq "
    r"\sum_{k=1}^{n}\sum_{j=l}^{r}\mu_{k,j} \leq "
    r"(n-1)\sum_{j=l}^{r}\lambda_{j} + (r-l+1)\lambda_{r+1}$"
)


# ==========================================
# Theorem 2.2: Weighted Projection (Main Result)
# ==========================================

THM2_2_DESC = (
    "OBJECTIVE:\n"
    "Our Main Result. It generalizes the bounds to any compressed matrix projected onto "
    "a subspace orthogonal to a vector u, incorporating weights for tighter precision.\n\n"
    
    "LEGEND:\n"
    "• u : A unit vector (projection direction). Weights w_i = |u_i|^2.\n"
    "• μ : Eigenvalues of the matrix compressed by u (on the orthogonal complement u^⊥).\n"
    "• U_l, L_r+1 : Partial sums of the weights (normalization factors).\n"
    "• INSIGHT : The weights 'w' allow this theorem to adapt to the geometry of "
    "the projection, yielding much sharper bounds."
)

THM2_2_LATEX = (
    r"$\sum_{j=\ell}^{r}\lambda_{j+1} + \sum_{j=\ell}^{r}\frac{w_{j+1}}{L_{r+1}}(\lambda_{\ell}-\lambda_{j+1}) "
    r"\leq \sum_{j=\ell}^{r}\mu_j \leq "
    r"\sum_{j=\ell}^{r}\lambda_{j} - \sum_{j=\ell}^{r}\frac{w_j}{U_{\ell}}(\lambda_{j}-\lambda_{r+1})$"
)


# ==========================================
# Theorem 4.1: Spectral Hierarchy
# ==========================================

THM4_1_DESC = (
    "OBJECTIVE:\n"
    "This result reveals the 'Spectral Hierarchy' structure: Information from larger submatrices "
    "(size m) strictly majorizes information from smaller submatrices (size k).\n\n"
    
    "LEGEND:\n"
    "• Xₘ(A) : The collection (multiset) of eigenvalues of ALL principal submatrices of size m.\n"
    "• Copies : To compare sets of different sizes, we replicate them to find a common multiple.\n"
    "• ≻ : Majorization relationship. The cumulative sum vector of the Left Side (Blue) "
    "must always be ≥ the Right Side (Orange).\n"
)

THM4_1_LATEX = (
    r"$\binom{m-1}{k-1} \text{ copies of } X_m(A) \succ "
    r"\binom{n-k}{m-k} \text{ copies of } X_k(A)$"
)


# ==========================================
# Lemma 3.1: Polynomial Roots Representation
# ==========================================

LEMMA3_1_DESC = (
    "OBJECTIVE:\n"
    "Verify that the eigenvalues (μ) of the projected matrix B are precisely the roots of "
    "a specific polynomial derived from the original eigenvalues (λ) and projection weights (w).\n\n"
    
    "SIGNIFICANCE:\n"
    "Unlike the classical secular equation (which uses fractions and fails when weights are zero), "
    "this polynomial form is robust and holds for ALL cases, including repeated eigenvalues "
    "and zero weights (as tested in the 'Hell Mode' audit)."
)

LEMMA3_1_LATEX = (
    r"$\sum_{i=1}^{n} | \langle u, v_i \rangle |^2 \prod_{j \neq i} (x - \lambda_j) = 0$"
)