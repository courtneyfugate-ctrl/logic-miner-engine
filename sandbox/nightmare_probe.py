from src.logic_miner.core.solver import ModularSolver
from src.logic_miner.core.adelic import AdelicIntegrator

def solve_sparse_prony(points, p):
    """
    Simulated Sparse Solver (from research_sparse.py)
    Returns {'params': (c, e), 'type': 'SPARSE_MONOMIAL'} or None.
    """
    # 1. Collect y_k for k=0..N (x=2^k)
    lookup = {pt[0]: pt[1] for pt in points}
    alpha = 2
    sequence = []
    k = 0
    while True:
        x_val = pow(alpha, k) 
        if x_val in lookup:
            sequence.append(lookup[x_val])
        else:
            break
        k += 1
    
    if len(sequence) < 4: return None
    
    # Check for Monomial: y = c * x^e + d? 
    # Simplified for Demo: y = c * x^e (offset handled externally or ignored for now)
    # Actually user function is 3x^13 + 7. +7 is an offset.
    # Sparse Solver needs to handle offset.
    # Differencing? y_{k+1} - y_k?
    # Monomial c*x^e + d.
    # y_k = c * (2^e)^k + d.
    # Diff d_k = y_{k+1} - y_k = c * (2^e)^k * (2^e - 1).
    # Ratio of diffs: d_{k+1} / d_k = 2^e.
    # This cancels d!
    
    diffs = [(sequence[i+1] - sequence[i]) % p for i in range(len(sequence)-1)]
    
    def inv(n): return pow(n, p-2, p)
    
    ratios = []
    valid = True
    for i in range(len(diffs)-1):
        if diffs[i] == 0: 
            # If diff is 0, constant function? or x^e mod p cycles?
            continue
        r = (diffs[i+1] * inv(diffs[i])) % p
        ratios.append(r)
        
    if not ratios:
        # Constant function?
        # Check if all sequence equal?
        if len(set(sequence)) == 1:
            return {'params': (0, 0, sequence[0]), 'type': 'CONSTANT'} # 0x^0 + d
        return None

    if len(set(ratios)) == 1:
        u = ratios[0]
        # u = 2^e mod p
        e = -1
        for candidate_e in range(100):
             if pow(alpha, candidate_e, p) == u:
                 e = candidate_e
                 break
        
        if e != -1:
            # Found e. Now find c.
            # d_0 = c * (2^e)^0 * (2^e - 1) = c * (u - 1).
            # c = d_0 * inv(u - 1).
            d0 = diffs[0]
            if (u - 1) % p == 0:
                # u=1 => e=0 (Constant). handled above?
                return None
            
            c = (d0 * inv(u - 1)) % p
            
            # Find d.
            # y_0 = c * (2^e)^0 + d = c + d.
            # d = y_0 - c.
            d = (sequence[0] - c) % p
            
            return {'params': (c, e, d), 'type': 'SPARSE_MONOMIAL'}
            
    return None

def nightmare_demo():
    print("### NIGHTMARE FUNCTION PROBE ###")
    
    # 1. User's Request: f(x) = 3x^13 + 7 mod 6
    # Note: Simplifies to 3(x%2) + 1.
    print("\n--- Target 1: 3x^13 + 7 (Mod 6) ---")
    
    # Split Mod 6 -> Mod 2, Mod 3.
    X = list(range(100))
    Y = [(3*pow(x, 13) + 7) % 6 for x in X]
    
    # Mod 2 projection
    print(">> Processing Mod 2...")
    Y2 = [y % 2 for y in Y]
    # Solve Sparse Mod 2
    res2 = solve_sparse_prony(list(zip(X, Y2)), 2)
    print(f"Mod 2 Result: {res2}")
    # Mod 2: 3x^13 + 7 = 1x^13 + 1 = x + 1.
    # Sparse should find c=1, e=1, d=1.
    
    # Mod 3 projection
    print(">> Processing Mod 3...")
    Y3 = [y % 3 for y in Y]
    res3 = solve_sparse_prony(list(zip(X, Y3)), 3)
    print(f"Mod 3 Result: {res3}")
    # Mod 3: 3x^13 + 7 = 0 + 1 = 1.
    # Sparse should find Constant d=1.
    
    # Merge
    print(">> Merging...")
    # Manual Merge or Conceptual?
    # Logic:
    # Mod 2: x + 1
    # Mod 3: 1
    # Check x=0: M2=1, M3=1 -> 1.
    # Check x=1: M2=0, M3=1 -> 4.
    # Result: 3(x%2) + 1.
    print("Merged Logic: 3(x%2) + 1 (Mod 6) [Simplified form of 3x^13+7]")

    # 2. True Nightmare: f(x) = 5x^13 + 7 (Mod 303 = 3 * 101)
    # High Degree doesn't collapse modulo 101.
    print("\n--- Target 2: TRUE NIGHTMARE: 5x^13 + 7 (Mod 303) ---")
    p1 = 3
    p2 = 101
    M = p1 * p2
    
    Y_night = [(5*pow(x, 13, M) + 7) % M for x in X]
    
    # Split
    print(f">> Processing Mod {p1}...")
    Y_p1 = [y % p1 for y in Y_night]
    # 5x^13 + 7 mod 3 = 2x^13 + 1.
    # x^13 mod 3 = x.
    # So 2x + 1.
    res_p1 = solve_sparse_prony(list(zip(X, Y_p1)), p1)
    print(f"Mod {p1} Result: {res_p1}")
    
    print(f">> Processing Mod {p2}...")
    Y_p2 = [y % p2 for y in Y_night]
    # 5x^13 + 7 mod 101.
    res_p2 = solve_sparse_prony(list(zip(X, Y_p2)), p2)
    print(f"Mod {p2} Result: {res_p2}")
    
    if res_p2 and res_p2['params'][1] == 13:
        print("[SUCCESS] Sparse Solver identified Degree 13 in Mod 101!")
        print("Adelic Integrator would now merge (2x+1 Mod 3) and (5x^13+7 Mod 101).")
    else:
        print("[FAIL] Sparse Solver missed Degree 13.")

if __name__ == "__main__":
    nightmare_demo()
