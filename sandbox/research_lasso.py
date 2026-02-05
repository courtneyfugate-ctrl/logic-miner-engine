from src.logic_miner.core.solver import ModularSolver
import random

def inverse(n, p):
    return pow(n, p-2, p)

def dot(v1, v2, p):
    return sum((a*b) % p for a,b in zip(v1, v2)) % p

def solve_linear_system_mod_p(X, y, p):
    """
    Gaussian elimination mod p to solve X * beta = y.
    X: matrix (list of lists)
    y: vector (list)
    Returns beta (list) or None
    """
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
            
        if curr == rows: continue # No pivot in this column
        
        # Swap
        M[pivot_row], M[curr] = M[curr], M[pivot_row]
        
        # Normalize pivot row
        inv = inverse(M[pivot_row][j], p)
        M[pivot_row] = [(x * inv) % p for x in M[pivot_row]]
        
        # Eliminate others
        for i in range(rows):
            if i != pivot_row:
                factor = M[i][j]
                M[i] = [(M[i][k] - factor * M[pivot_row][k]) % p for k in range(cols + 1)]
                
        col_pivots.append(j)
        pivot_row += 1
        
    # Back substitution? Matrix is already RREF-ish.
    # Extract solution
    beta = [0] * cols
    for i in range(len(col_pivots)):
        # Pivot at (i, col_pivots[i]) is 1.
        # Solution component is last col.
        # This assumes independent cols? 
        # For OMP we build independent set.
        beta[col_pivots[i]] = M[i][-1]
        
    return beta

def solve_omp_mod_p(X_input, y_target, p, max_degree=50, max_terms=3):
    """
    Orthogonal Matching Pursuit Modulo P.
    Finds sparse beta such that y = sum beta_i * x^i (mod p).
    
    X_input: list of x values.
    y_target: list of y values.
    max_degree: columns to consider (frequencies 0..max_degree).
    max_terms: sparsity constraint (L0 norm).
    """
    n = len(X_input)
    
    # Feature Dictionary: Columns are x^d
    # C_d = [x_0^d, x_1^d, ...]^T
    dictionary = []
    for d in range(max_degree + 1):
        col = [pow(x, d, p) for x in X_input]
        dictionary.append({'degree': d, 'vec': col})
        
    residual = y_target[:]
    support = [0] # Always include Constant term to handle offsets
    
    # Check baseline score (Constant model)
    # Solve for y = d
    # Most frequent element? Or LS?
    # LS for deg 0 is just finding d?
    # Our LS solver might find d.
    
    for step in range(max_terms):
        best_d = -1
        best_score = -1
        
        for cand in dictionary:
            d = cand['degree']
            if d in support: continue
            
            # Try solving LS with [Current Support + d]
            current_degrees = support + [d]
            
            # Build Sub-Matrix
            A = []
            for i in range(n):
                row = [pow(X_input[i], deg, p) for deg in current_degrees]
                A.append(row)
                
            if n < len(current_degrees):
                continue
                
            if len(A) >= len(current_degrees):
                beta = solve_linear_system_mod_p(A[:len(current_degrees)], y_target[:len(current_degrees)], p)
                if beta:
                    matches = 0
                    for i in range(n):
                        pred = sum(beta[k] * pow(X_input[i], deg, p) for k, deg in enumerate(current_degrees)) % p
                        if pred == y_target[i]: matches += 1
                        
                    if matches > best_score:
                        best_score = matches
                        best_d = d
        
        if best_d != -1:
            support.append(best_d)
            print(f"  [OMP] Step {step+1}: Added x^{best_d} (Score: {best_score}/{n})")
            if best_score == n:
                print("  [OMP] Perfect Fit found!")
                break
        else:
            print("  [OMP] No improvement found.")
            break
            
    return support

def research_lasso():
    print("### Proposal A: LASSO / OMP Modulo P ###")
    
    # Target: 5x^13 + 7 (Mod 101)
    p = 101
    c = 5
    e = 13
    d = 7
    print(f"Logic: {c}x^{e} + {d} (Mod {p})")
    
    # Data: Random (Passive)
    # 20 points. Degree 13. Max Degree search 50.
    # N=20 < D_max=50. Underdetermined if dense.
    # But Sparse (K=2 terms).
    
    X = [random.randint(0, p-1) for _ in range(20)]
    X = list(set(X)) # Unique
    Y = [(c*pow(x, e, p) + d) % p for x in X]
    
    print(f"Data: {len(X)} points (Random).")
    
    # Run OMP
    support = solve_omp_mod_p(X, Y, p, max_degree=50, max_terms=3)
    
    print(f"Recovered Support: {support}")
    if 13 in support and 0 in support:
        print("[SUCCESS] Recovered x^13 and x^0 (Constant).")
    else:
        print("[FAIL] Failed to recover sparse support.")

if __name__ == "__main__":
    research_lasso()
