from src.logic_miner.engine import LogicMiner
import math

def test_nightmare_integration():
    print("### INTEGRATION TEST: NIGHTMARE FUNCTION ###")
    miner = LogicMiner()
    
    # 1. User Logic: 3x^13 + 7 (Mod 6)
    # Becomes 3(x%2) + 1.
    print("\n--- Target 1: 3x^13 + 7 (Mod 6) ---")
    X = list(range(100))
    Y = [(3*pow(x,13) + 7) % 6 for x in X]
    
    res = miner.fit(X, Y)
    print("Result:", res)
    
    # Verify Fidelity
    if res['p'] == 6 and 'ADELIC' in res['mode']:
        print("[SUCCESS] Discovered Mod 6 logic via Adelic Synthesis.")
    else:
        print("[FAIL] Did not synthesize Mod 6.")

if __name__ == "__main__":
    test_nightmare_integration()
