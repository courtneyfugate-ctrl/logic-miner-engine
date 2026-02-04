from src.logic_miner.engine import LogicMiner

def generate_parity_data(n=200):
    """
    Logic: Parity
    f(x) = 1 if x is even, 0 if x is odd.
    (Or x % 2)
    In Standard Polynomials (RANSAC Basis), this is noise/oscillation.
    In Mahler Basis (p=2), this is finite:
    f(0)=1, f(1)=0, f(2)=1, f(3)=0...
    Diffs:
    d^0: 1, 0, 1, 0...
    d^1: -1, 1, -1...
    d^2: 2, -2...
    d^3: -4...
    Coeffs: 1, -1, 2, -4...
    |a_n|_2: 1, 1, 0.5, 0.25... -> Decays to 0!
    """
    inputs = list(range(n))
    outputs = [(1 if x % 2 == 0 else 0) for x in inputs]
    return inputs, outputs

def test_mahler():
    print("### MAHLER PARITY TEST ###")
    print("Logic: Parity (Even=1, Odd=0).")
    print("Expectation: Polynomial Miner should FAIL. Mahler Miner should SUCCEED (p=2).")
    
    X, Y = generate_parity_data()
    
    miner = LogicMiner()
    try:
        # Step 1: Fitting
        # The Poly solver will see consensus 50% for y=0 or y=1.
        # Default min_consensus is 0.30?
        # Parity hits 50%. So Poly solver might say "Found y=0, 50% consensus".
        # But this is "Low Confidence" compared to 90%?
        # Or maybe it accepts 50% as valid?
        # If it returns y=0 (Deg 0), it ignores half the data.
        # We need to verify if it switches to Mahler.
        # To force Mahler check, we might need to set standard strictness higher, or check if Mahler score is BETTER.
        # Currently code: if score_poly < min_consensus.
        # If parity is 50%, and min is 30%, it accepts Poly.
        # We should set min_consensus higher for this test to force failure of "weak" models.
        
        result = miner.fit(X, Y, min_consensus=0.60) # High bar to force Poly fail
        
        print("\n### RESULTS ###")
        print(f"Mode: {result.get('mode', 'POLYNOMIAL')}")
        print(f"Discovered p: {result['p']}")
        
        if result.get('mode') == 'MAHLER':
            print(f"Confidence: {result['discovery_confidence']:.2f}")
            coeffs = result['coefficients']
            print(f"Mahler Coeffs (First 5): {coeffs[:5]}")
            
            # Check p=2
            if result['p'] == 2:
                print("[PASS] Correctly identified p=2 for Parity.")
            else:
                 print(f"[FAIL] Expected p=2, got {result['p']}")
                 
            # Check Decay
            # 1, -1, 2, -4...
            # Valuations: 0, 0, 1, 2...
            # Should be high decay score.
            if result['discovery_confidence'] > 0.5:
                print("[PASS] Decay Metric confirms continuity.")
        else:
            print("[FAIL] Engine stuck in Polynomial Mode (or failed completely).")
            
    except Exception as e:
        print(f"[ERROR or SUCCESS?] Engine raised exception: {e}")
        # If it raises "No logic rule found", that means Mahler also failed?
        # Or Poly failed and Mahler scan failed.

if __name__ == "__main__":
    test_mahler()
