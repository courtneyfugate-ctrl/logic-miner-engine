from .solver import ModularSolver
import random

def inverse(n, p):
    return pow(n, p-2, p)

def solve_linear_system_mod_p(X, y, p):
    """
    Gaussian elimination mod p to solve X * beta = y.
    X: matrix (list of lists)
    y: vector (list)
    Returns beta (list) or None
    """
    if not X or not y: return None
    rows = len(X)
    cols = len(X[0])
    
    # Augment
    M = [row[:] + [val] for row, val in zip(X, y)]
    
    pivot_row = 0
    col_pivots = []
    
    for j in range(cols):
        if pivot_row >= rows: break
        
        # Find pivot
        curr = pivot_row
        while curr < rows and M[curr][j] == 0:
            curr += 1
            
        if curr == rows: continue
        
        # Swap
        M[pivot_row], M[curr] = M[curr], M[pivot_row]
        
        # Normalize
        inv = inverse(M[pivot_row][j], p)
        M[pivot_row] = [(x * inv) % p for x in M[pivot_row]]
        
        # Eliminate
        for i in range(rows):
            if i != pivot_row:
                factor = M[i][j]
                M[i] = [(M[i][k] - factor * M[pivot_row][k]) % p for k in range(cols + 1)]
                
        col_pivots.append(j)
        pivot_row += 1
        
    beta = [0] * cols
    for i in range(len(col_pivots)):
        # Pivot is at (i, col_pivots[i])
        beta[col_pivots[i]] = M[i][-1]
        
    return beta

class SparseSolver:
    """
    Solves for Sparse Monomials y = c * x^e + d (mod p).
    Supports two modes:
    1. Active (Prony): Requires inputs at x = 2^k. High Accuracy.
    2. Passive (LASSO/OMP): Works on random data. Lower capacity but passive.
    """
    def __init__(self, p):
        self.p = p

    def solve(self, data):
        """
        Expects list of (x, y).
        Auto-detects strategy.
        """
        if not data: return None
        
        # Detect Geometric Progression for Prony
        x_vals = set(d[0] for d in data)
        alpha = 2
        k = 0
        geometric_count = 0
        while True:
             val = pow(alpha, k)
             # Note: val grows. Stop reasonable bound.
             # Or check if data contains small powers of 2.
             if val in x_vals:
                 geometric_count += 1
             else:
                 # If we miss 2^k, can we continue? Prony needs contiguous?
                 # Yes, usually needs contiguous y_k, y_{k+1}.
                 # So if we miss one, sequence breaks.
                 break
             k += 1
             if geometric_count > 4: break
             
        if geometric_count >= 4:
            # Active path
            # print(f"[SparseSolver] Detected Geometric Data (Count {geometric_count}). Using Prony.")
            return self._solve_prony(data)
        else:
            # Passive path
            if len(data) >= 5: # Min samples for OMP
                 # print(f"[SparseSolver] Random Data. Using Passive OMP.")
                 return self._solve_omp(data)
            return None

    def _solve_prony(self, data):
        # ... (Existing Logic) ...
        # Copied from previous sparse.py impl
        lookup = {pt[0]: pt[1] for pt in data}
        alpha = 2
        sequence = []
        k = 0
        max_k = 100 
        
        while k < max_k:
            x_val = pow(alpha, k) 
            if x_val in lookup:
                sequence.append(lookup[x_val])
            else:
                break
            k += 1
            
        if len(sequence) < 4: return None
            
        diffs = [(sequence[i+1] - sequence[i]) % self.p for i in range(len(sequence)-1)]
        
        ratios = []
        for i in range(len(diffs)-1):
            if diffs[i] == 0: continue
            r = (diffs[i+1] * inverse(diffs[i], self.p)) % self.p
            ratios.append(r)
            
        if not ratios:
             if len(set(sequence)) == 1:
                  return {'params': (0, 0, sequence[0]), 'type': 'CONSTANT', 'ratio': 1.0}
             return None

        from collections import Counter
        ratio_counts = Counter(ratios)
        if not ratio_counts: return None
        
        u, count = ratio_counts.most_common(1)[0]
        if count < len(ratios) * 0.8: return None
            
        e = -1
        found_e = False
        for candidate_e in range(200):
             if pow(alpha, candidate_e, self.p) == u:
                 e = candidate_e
                 found_e = True
                 break
        
        if not found_e: return None
        if (u - 1) % self.p == 0: return None
            
        d0 = diffs[0]
        c = (d0 * inverse(u - 1, self.p)) % self.p
        d = (sequence[0] - c) % self.p
        
        hits = 0
        for x, y in data:
            pred = (c * pow(x, e, self.p) + d) % self.p
            if pred == y: hits += 1
            
        ratio = hits / len(data)
        if ratio > 0.7:
             return {
                 'params': (c, e, d),
                 'type': 'SPARSE_MONOMIAL',
                 'degree': e,
                 'ratio': ratio,
                 'note': f"Sparse Monomial {c}x^{e} + {d} (Active)"
             }
        return None

    def _solve_omp(self, data):
        """
        Affine Matching Pursuit (LASSO-like) for Passive Data.
        """
        n = len(data)
        X_input = [d[0] for d in data]
        y_target = [d[1] for d in data]
        
        # Max Degree Search
        # If N=20, we can check degree up to say 50 or 100.
        max_degree = 100
        max_terms = 2 # We want Mono+Constant (2 terms).
        
        # Dictionary computation on fly or cached? 
        # On fly is fine.
        
        residual = y_target[:]
        support = [0] # Always include Constant
        
        # Iteratively add 1 term
        # Since we want Monomial + Constant, we only need 1 step (add x^e)
        # Check all degrees 1..max_degree
        
        best_d = -1
        best_score = -1
        best_beta = None
        
        # Pre-filter degrees? No, brute force LS is fine for N=20.
        
        for d in range(1, max_degree + 1):
            current_degrees = [0, d]
            
            # Build A
            A = []
            for i in range(n):
                # row = [x^0, x^d]
                row = [1, pow(X_input[i], d, self.p)]
                A.append(row)
                
            # Need N >= 2
            if n < 2: continue
            
            # Solve using first 2 points? No, use all (overdetermined) or subset.
            # Use first 2 points to get candidate beta, then score on rest (RANSAC style)
            # Or use Gaussian Elim on first 2 rows.
            
            beta = solve_linear_system_mod_p(A[:2], y_target[:2], self.p)
            
            if beta:
                # Score
                matches = 0
                for i in range(n):
                    const_term = beta[0]
                    var_term = beta[1]
                    pred = (const_term + var_term * pow(X_input[i], d, self.p)) % self.p
                    if pred == y_target[i]: matches += 1
                    
                if matches > best_score:
                    best_score = matches
                    best_d = d
                    best_beta = beta
                    
        if best_d != -1:
            support.append(best_d)
            print(f"  [OMP] Passive Scan: Added x^{best_d} (Score: {best_score}/{n})")
            if best_score == n:
                print("  [OMP] Perfect Fit found!")
                # break # This break was commented out in the original, so I'm keeping it commented.
        ratio = best_score / n
        if ratio > 0.7:
             # beta = [d, c] (since degrees are [0, d])
             # params expected (c, e, d)
             # beta[0] is constant (d), beta[1] is coeff (c).
             d_const = best_beta[0]
             c_coeff = best_beta[1]
             e_exp = best_d
             
             return {
                 'params': (c_coeff, e_exp, d_const),
                 'type': 'SPARSE_MONOMIAL',
                 'degree': e_exp,
                 'ratio': ratio,
                 'note': f"Sparse Monomial {c_coeff}x^{e_exp} + {d_const} (Passive)"
             }
             
        return None
