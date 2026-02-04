from src.logic_miner.engine import LogicMiner
import random

def test_universal_interface():
    print("### UNIVERSAL INTERFACE INTEGRATION TEST ###")
    miner = LogicMiner()
    
    # 1. Scalar Logic (Standard)
    print("\n--- Test 1: Scalar Logic (y = 3x + 1 Mod 17) ---")
    p = 17
    X = list(range(20))
    Y = [(3*x + 1) % p for x in X]
    res1 = miner.fit(X, Y)
    print("Result:", res1)
    if res1.get('p') == 17:
        print("[SUCCESS] Scalar Pipeline works.")
    else:
        print("[FAIL] Scalar Pipeline break.")

    # 2. Multivariate Logic (Trolley)
    print("\n--- Test 2: Multivariate Logic (y = 2a + 3b Mod 7) ---")
    p2 = 7
    X2 = []
    Y2 = []
    for _ in range(50):
        a = random.randint(0, 10)
        b = random.randint(0, 10)
        X2.append([a, b])
        Y2.append( (2*a + 3*b) % p2 )
        
    res2 = miner.fit(X2, Y2)
    print("Result:", res2)
    if res2.get('mode') == 'MULTIVARIATE' and res2.get('p') == 7:
        print("[SUCCESS] Multivariate Pipeline works.")
    else:
        print("[FAIL] Multivariate Pipeline break.")

    # 3. Ultrametric Tree (Species)
    print("\n--- Test 3: Ultrametric Tree (Structure) ---")
    labels = ["A", "B", "C"]
    # Distance Matrix
    # A-B close (0.1), C far (0.9)
    dist = [
        [0.0, 0.1, 0.9],
        [0.1, 0.0, 0.9],
        [0.9, 0.9, 0.0]
    ]
    # Inputs = Matrix, Outputs = Labels
    res3 = miner.fit(dist, labels)
    print("Result:", res3)
    if res3.get('mode') == 'ULTRAMETRIC' and "((A,B),C)" in res3.get('tree'):
        print("[SUCCESS] Ultrametric Pipeline works.")
    else:
        print("[FAIL] Ultrametric Pipeline break.")
        
if __name__ == "__main__":
    test_universal_interface()
