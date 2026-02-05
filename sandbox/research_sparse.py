from src.logic_miner.core.solver import ModularSolver
# No numpy needed

def solve_sparse_prony(points, p):
    """
    Attempt to use Prony's method to find sparse polynomial.
    y(x) = c1 * x^e1 + c2 * x^e2...
    We evaluate at x = 2^0, 2^1, ... 2^(2T-1).
    Actually, standard Ben-Or/Tiwari evaluates at prime powers.
    For univariate: Evaluate at x = 2^k.
    y_k = f(2^k) = sum c_i (2^{e_i})^k.
    Let u_i = 2^{e_i}.
    y_k = sum c_i (u_i)^k.
    This is exactly the form for Prony's method (sum of exponentials).
    
    We need 2T evaluations to find T terms.
    """
    # 1. Collect y_k for k=0..N
    ys = []
    # Points is list of (x, y)
    # Map x -> y
    lookup = {pt[0]: pt[1] for pt in points}
    
    # We need sequential powers of alpha (let alpha=2).
    # x_k = 2^k.
    alpha = 2
    sequence = []
    k = 0
    while True:
        x_val = pow(alpha, k) # No mod p here? The input x grows.
        # Wait, f(x) mod p.
        # x can be larger than p?
        # x is integer.
        if x_val in lookup:
            sequence.append(lookup[x_val])
        else:
            break
        k += 1
        
    print(f"Collected {len(sequence)} points at powers of {alpha}: {sequence}")
    
    if len(sequence) < 4:
        print("Not enough points for sparse interpolation.")
        return
        
    # 2. Hankel Matrix + Berlekamp-Massey to find Recurrence
    # Simplified: Find linear recurrence in sequence.
    # For 1 term (c x^e): y_k = c (2^e)^k. Geometric series. Ratio y_{k+1}/y_k = 2^e.
    # For 2 terms: A bit complex.
    
    # Let's try brute force for 1 Term: y = c * x^e + d?
    # SparseUsually means monomials.
    
    # Test for Single Monomial: y = c * x^e
    # check ratio r_k = y_{k+1} / y_k (mod p)
    # All r_k should be equal to u = 2^e.
    
    # We need modular inverse for division.
    def inv(n): return pow(n, p-2, p)
    
    ratios = []
    valid = True
    for i in range(len(sequence)-1):
        if sequence[i] == 0: 
            valid=False; break
        r = (sequence[i+1] * inv(sequence[i])) % p
        ratios.append(r)
        
    if valid and len(set(ratios)) == 1:
        u = ratios[0]
        # u = 2^e mod p.
        # Solve Discrete Log?
        # Or brute force e.
        e = -1
        for candidate_e in range(100): # max degree 100
             if pow(alpha, candidate_e, p) == u:
                 e = candidate_e
                 break
        
        if e != -1:
            # Find c
            # y_0 = c * (2^e)^0 = c * 1 = c.
            c = sequence[0]
            print(f"[Success] Found Sparse Term: {c} * x^{e}")
            return
            
    print("Could not find single sparse monomial.")

def run_sparse_research():
    print("### Proposal 1: Sparse Interpolation Feasibility ###")
    
    # Logic: y = 5 * x^13 (mod 101)
    p = 101
    c = 5
    e = 13
    
    print(f"Target: y = {c} * x^{e} (mod {p})")
    
    X = list(range(100)) # Dense 0..99
    Y = [(c * pow(x, e, p)) % p for x in X]
    points = list(zip(X, Y))
    
    solve_sparse_prony(points, p)

if __name__ == "__main__":
    run_sparse_research()
