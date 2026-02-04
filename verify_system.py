from src.logic_miner.core.lifter import HenselLifter

def test_system():
    print("Initializing Logic Miner System...")
    p = 5
    lifter = HenselLifter(p_base=p)
    
    # --- Synthetic Data Generation ---
    # Logic: F(x) = 3x + 2 (Base logic) + 1*p (Nuance)
    # i.e., y = (3 + 1*5)x + (2 + 0*5) = 8x + 2
    print(f"Generating synthetic data for Logic: y = 8x + 2 (mod {p}^2)...")
    
    inputs = [0, 1, 2, 3, 4] * 4  # 20 points
    outputs = []
    for x in inputs:
        # True logic
        y = 8 * x + 2
        outputs.append(y)
        
    # Add Noise (Phase Shift simulation)
    outputs[-1] = 0 # Corrupt last point
    outputs[-2] = 0 # Corrupt second to last
    
    # --- Execution ---
    print("Running Hensel Lifter...")
    result = lifter.lift(inputs, outputs, max_depth=2)
    
    # --- Report ---
    print("\n--- RESULTS ---")
    print(f"Status: {result['status']}")
    
    coeffs = result['coefficients']
    if len(coeffs) >= 1:
        print(f"Level 0 (Base Logic): y = {coeffs[0][0]}x + {coeffs[0][1]} (mod 5)")
        # Expected: 8 = 3 mod 5, 2 = 2 mod 5 -> m=3, c=2
    if len(coeffs) >= 2:
        print(f"Level 1 (Nuance):     y = {coeffs[1][0]}x + {coeffs[1][1]} (mod 5)")
        # Expected: 8 = 3 + 1*5 -> m_1=1. c_1=0.
        
    if result['status'] == 'CONVERGED':
        print("\nSUCCESS: Logic successfully mined and lifted.")
    else:
        print("\nALERT: Phase Shift detected.")

if __name__ == "__main__":
    test_system()
