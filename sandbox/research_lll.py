import math
import random

def gcd_list(numbers):
    if not numbers: return 0
    result = numbers[0]
    for n in numbers[1:]:
        result = math.gcd(result, n)
    return result

def research_lll_determinant():
    print("### Proposal B: Lattice Reduction / Determinant GCD ###")
    
    # Target: 123x + 456 (Mod 1009)
    # p=1009. Data=50 points.
    # No collisions (Bijectivity Barrier holds).
    
    p = 1009
    a = 123
    b = 456
    
    X = list(range(50))
    # y = ax + b + kp
    Y = [(a*x + b) % p for x in X]
    
    print(f"Logic: {a}x + {b} (Mod {p})")
    print(f"Data: {len(X)} points.")
    
    # Algorithm: Cross-Product Determinants
    # dy_i = a dx_i + K_i p
    # dy_j = a dx_j + K_j p
    # Det = dy_i dx_j - dy_j dx_i = a dx_i dx_j + K_i p dx_j - (a dx_j dx_i + K_j p dx_i)
    #     = p (K_i dx_j - K_j dx_i)
    # So Det is multiple of p.
    
    determinants = []
    
    # Use dx from x_0 for simplicity
    dx_0 = [X[i] - X[0] for i in range(1, len(X))]
    dy_0 = [Y[i] - Y[0] for i in range(1, len(Y))]
    
    # Compute determinants for pairs (i, i+1)
    # To avoid O(N^2), just sample sequential pairs?
    # Or just a few random pairs.
    
    for i in range(len(dx_0) - 1):
        # Pair (i, i+1)
        dxi = dx_0[i]
        dyi = dy_0[i]
        dxj = dx_0[i+1]
        dyj = dy_0[i+1]
        
        det = dyi * dxj - dyj * dxi
        if det != 0:
            determinants.append(abs(det))
            
    print(f"Computed {len(determinants)} determinants.")
    
    print(f"First 5 determinants: {determinants[:5]}")
    
    g = gcd_list(determinants)
    print(f"Global GCD of Determinants: {g}")
    
    if g == p:
        print(f"[SUCCESS] Recovered p={p} from small dataset (N < p).")
    elif g % p == 0:
        print(f"[PARTIAL] Recovered multiple of p: {g} (p={p}).")
    else:
        print("[FAIL] Failed to recover p.")

if __name__ == "__main__":
    research_lll_determinant()
