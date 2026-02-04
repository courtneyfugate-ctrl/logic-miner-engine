from src.logic_miner.engine import LogicMiner

def generate_step_data(n=100):
    """
    Archimedean Logic: y = floor(x/10)
    Discontinuous in p-adic metric.
    Continuous in Real metric.
    Expected: Engine switches to REAL_STEP_FUNCTION mode.
    """
    X = list(range(n))
    Y = [x // 10 for x in X]
    return X, Y

def generate_parity_data(n=100):
    """
    Non-Archimedean Logic: y = x % 2
    Discontinuous in Real metric.
    Continuous in 2-adic metric.
    Expected: Engine switches to MAHLER (p=2) mode.
    """
    X = list(range(n))
    Y = [x % 2 for x in X]
    return X, Y

def test_adelic():
    miner = LogicMiner()
    
    print("\n### ADELIC TEST 1: Step Function (The Infinite Prime) ###")
    X1, Y1 = generate_step_data()
    # Force low poly consensus to trigger scan (Step function is not a single poly mod p)
    res1 = miner.fit(X1, Y1, min_consensus=0.85)
    
    print(f"Mode: {res1.get('mode')}")
    print(f"Confidence: {res1.get('discovery_confidence'):.2f}")
    if 'REAL_STEP_FUNCTION' in res1.get('mode', ''):
        print("[PASS] Engine correctly identified Archimedean Step Logic.")
    else:
        print(f"[FAIL] Engine missed Real logic. Got {res1.get('mode')}")

    print("\n### ADELIC TEST 2: Parity (The Finite Prime p=2) ###")
    X2, Y2 = generate_parity_data()
    res2 = miner.fit(X2, Y2, min_consensus=0.85)
    
    print(f"Mode: {res2.get('mode')}")
    print(f"p: {res2.get('p')}")
    if res2.get('mode') == 'MAHLER' and res2.get('p') == 2:
        print("[PASS] Engine correctly identified 2-adic Parity Logic.")
    else:
        print(f"[FAIL] Engine missed p-adic logic. Got {res2.get('mode')}")

if __name__ == "__main__":
    test_adelic()
