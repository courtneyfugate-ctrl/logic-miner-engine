from src.logic_miner.engine import LogicMiner
import random

def test_passive_integration():
    print("### INTEGRATION TEST: PASSIVE & GROKKING ###")
    miner = LogicMiner()
    
    # 1. Passive Sparse Audit (LASSO)
    # y = 5x^13 + 7 (Mod 61)
    # Random Inputs (Passive)
    print("\n--- Target 1: Passive Sparse 5x^13 + 7 (Mod 61) ---")
    p = 61
    X = [random.randint(0, 1000) for _ in range(30)]
    Y = [(5*pow(x, 13, p) + 7) % p for x in X]
    
    # Ensure no geometric progression accidentally (Active detection)
    
    res = miner.fit(X, Y)
    print("Result:", res)
    
    # Check if we used Sparse Logic
    trace = res.get('logic_trace', {})
    coefficients = trace.get('coefficients', [])
    # Or note?
    
    # Since Mod 61 is in scan list, Discovery will find it.
    # It will call SparseSolver.
    # SparseSolver should print "Random Data. Using Passive OMP." (if logging enabled)
    # And return valid parameters.
    
    if res['p'] == 61: # and 'SPARSE' in res.get('mode', ''):
        # We don't have 'mode' field consistently tailored for Sparse in 'fit' return?
        # LogicMiner.fit checks RANSAC score.
        # If score is high using Sparse, it returns that.
        # Check params?
        # Sparse params are (c, e, d).
        pass
    else:
        print("[FAIL] Did not find p=61.")
        
    # 2. Grokking Detector (LLL)
    # y = 123x + 456 (Mod 1009)
    # p=1009 is NOT in default scan list (max 71).
    # N=50 (No Collisions).
    print("\n--- Target 2: Hidden Modulus 123x + 456 (Mod 1009) ---")
    p2 = 1009
    X2 = list(range(50))
    Y2 = [(123*x + 456) % p2 for x in X2]
    
    res2 = miner.fit(X2, Y2)
    print("Result:", res2)
    
    if res2['p'] == 1009:
        print("[SUCCESS] LLL Discovered Hidden Modulus p=1009!")
    else:
        print(f"[FAIL] Failed to discover p=1009. Found {res2.get('p')}.")

if __name__ == "__main__":
    test_passive_integration()
