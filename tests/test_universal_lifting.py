from src.logic_miner.engine import LogicMiner
import random

def test_universal_lifting():
    print("### UNIVERSAL LIFTING TEST (TROLLEY XL) ###")
    miner = LogicMiner()
    
    # Target: y = 1000*M + 500*C (Real Integers)
    # We want the engine to find this starting from Mod 7.
    
    print("\n--- Target: y = 1000*M + 500*C ---")
    
    # Generate data
    X = []
    Y = []
    for _ in range(50):
        m = random.randint(0, 100)
        c = random.randint(0, 100)
        X.append([m, c])
        # Exact integer logic (Real)
        Y.append(1000*m + 500*c)
        
    # We hope Discovery finds a prime (e.g. 7 divides something? No, it's linear)
    # The Engine will try Mod 2, Mod 3... Mod 7.
    # Mod 7: 1000 = 6, 500 = 3.
    # So y = 6m + 3c (Mod 7).
    # Then LIFTER should upgrade 6 -> 1000.
    
    res = miner.fit(X, Y)
    
    print("Result:", res)
    
    trace = res.get('logic_trace', {})
    coeffs = trace.get('coefficients', [])
    p = res.get('p', 2)
    trace = res.get('logic_trace', {})
    coeffs_history = trace.get('coefficients', [])
    
    if coeffs_history:
        # Reconstruct Total Model
        # coeffs_history[k] is Delta_k (Mod p)
        # Total = Sum(Delta_k * p^k)
        
        # Determine vector size
        dim = len(coeffs_history[0]['params'])
        total_beta = [0] * dim
        
        current_p_pow = 1
        for step in coeffs_history:
            delta = step['params']
            for i in range(dim):
                total_beta[i] += delta[i] * current_p_pow
            current_p_pow *= p
            
        print(f"Reconstructed Beta: {total_beta}")
        
        bias = total_beta[0]
        men_w = total_beta[1]
        child_w = total_beta[2]
        
        print(f"Bias={bias}, Men={men_w}, Children={child_w}")
        
        if men_w == 1000 and child_w == 500:
             print("[SUCCESS] Fully Lifted to Global Integers!")
        elif men_w > 0:
             print("[PARTIAL] Found Non-Zero Logic.")
    else:
        print("[FAIL] No coefficients found.")

if __name__ == "__main__":
    test_universal_lifting()
