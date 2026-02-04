import random
from src.logic_miner.engine import LogicMiner, StochasticChaosError

def generate_nightmare_data(n=200):
    """
    Hidden Logic: p=7
    Level 0: y = 2x^2 + 3 (Quad)
    Level 1: y = 5x + 1   (Linear)
    Formula: y_total = (2x^2 + 3) + 7*(5x + 1)
             y_total = 2x^2 + 3 + 35x + 7
             y_total = 2x^2 + 35x + 10
             
    Noise: 40% random garbage.
    Decoy: Ensure x=0..10 are purely linear y=x to fool simpler systems? (Optional, skipping for now to focus on Poly check).
    """
    inputs = list(range(n))
    outputs = []
    
    # Logic
    def true_logic(x):
        return 2*(x**2) + 35*x + 10
        
    for x in inputs:
        if random.random() < 0.40:
            # 40% Noise
            outputs.append(random.randint(0, 10000))
        else:
            outputs.append(true_logic(x))
            
    return inputs, outputs

def run_torture_test():
    print("### TORTURE TEST: 'THE NIGHTMARE DATASET' ###")
    print("Goal: Auto-discover p=7, Quad(L0), Linear(L1) with 40% Noise.")
    
    random.seed(666) # Doom seed
    X, Y = generate_nightmare_data()
    
    miner = LogicMiner()
    
    try:
        result = miner.fit(X, Y)
        
        print("\n### RESULTS ###")
        print(f"Discovered p: {result['p']} (Expected: 7)")
        
        trace = result['logic_trace']
        print(f"Status: {trace['status']}")
        
        coeffs = trace['coefficients']
        for i, level in enumerate(coeffs):
            deg = level['degree']
            params = level['params']
            print(f"Level {i}: Degree {deg}, Params {params}")
            
        # Verify with Polynomial Reconstruction
        # Since integer logic is valid in any prime base, checking for specific p is fragile.
        # We reconstruct the total logic: F(x) = L0(x) + p*L1(x) + p^2*L2(x)...
        # And check if it matches the ground truth: 2x^2 + 35x + 10.
        
        print("\n[VERIFICATION] Reconstructing Total Logic...")
        
        p = result['p']
        # We need to sum up the polynomials.
        # We assume max degree 2 for simplicity of check.
        total_a, total_b, total_c = 0, 0, 0
        
        current_p_pow = 1
        for level in coeffs:
            deg = level['degree']
            params = level['params']
            
            # Normalize to ax^2 + bx + c
            a, b, c = 0, 0, 0
            if deg == 2:
                a, b, c = params
            elif deg == 1:
                b, c = params
            elif deg == 0:
                c = params[0]
                
            total_a += a * current_p_pow
            total_b += b * current_p_pow
            total_c += c * current_p_pow
            
            current_p_pow *= p
            
        print(f"Reconstructed: y = {total_a}x^2 + {total_b}x + {total_c}")
        print(f"Ground Truth:  y = 2x^2 + 35x + 10")
        
        if total_a == 2 and total_b == 35 and total_c == 10:
             print("[PASS] Logic Successfully Mined! (Exact Match)")
        else:
             print(f"[FAIL] Logic Mismatch.")
            
    except StochasticChaosError as e:
        print(f"[FAIL] Engine gave up: {e}")

if __name__ == "__main__":
    run_torture_test()
