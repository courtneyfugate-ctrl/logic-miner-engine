import random
from src.logic_miner.engine import LogicMiner

def generate_ghost_data(n=200):
    """
    Logic: y = 7x^2 + x
    p = 7
    Modulo 7: y = x (Linear)
    Modulo 49: y = 7x^2 + x (Quadratic term appears)
    
    The engine MUST detect the Global Quadratic nature.
    Legacy engine (Strict Degree) will lock degree 1 at L0 and fail to see x^2 at L1.
    """
    inputs = list(range(n))
    outputs = []
    
    for x in inputs:
        # y = 7*x^2 + x
        y = 7*(x**2) + x
        outputs.append(y)
        
    return inputs, outputs

def test_ghost():
    print("### GHOST TERM TEST ###")
    print("Logic: y = 7x^2 + x  (p=7)")
    print("Expectation: Engine must upgrade L0 model to Quadratic.")
    
    X, Y = generate_ghost_data()
    
    print("\n--- FORCING p=7 (Direct Core Test) ---")
    
    from src.logic_miner.core.lifter import HenselLifter
    # We must mock 'GhostDetector' being importable by lifter. It is traversing relative imports.
    # PYTHONPATH is set, so it should work.
    
    lifter = HenselLifter(7)
    
    try:
        # Run lift
        result = lifter.lift(X, Y, min_consensus=0.5)
        
        print(f"Status: {result['status']}")
        coeffs = result['coefficients']
        for i, c in enumerate(coeffs):
            print(f"Level {i}: Deg {c['degree']} Params {c['params']}")
            
        l0 = coeffs[0]
        if l0['degree'] == 2:
            print("[PASS] Ghost Term Detected! Level 0 is Quadratic.")
            a, b, c = l0['params']
            if a == 0 and b == 1 and c == 0:
                 print("       And correctly identified (0x^2 + 1x + 0) mod 7.")
        else:
            print("[FAIL] Level 0 remained Linear. Ghost Term missed.")
            
        if len(coeffs) > 1:
            l1 = coeffs[1]
            if l1['degree'] == 2 and l1['params'] == (1, 0, 0):
                print("[PASS] Level 1 identified x^2.")
            else:
                print(f"[FAIL] Level 1 mismatch: {l1['params']}")
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_ghost()
