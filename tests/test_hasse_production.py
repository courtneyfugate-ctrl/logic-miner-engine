from src.logic_miner.engine import LogicMiner

def test_hasse_production():
    print("### PRODUCTION TEST: Hasse Synthesis (Mod 12) ###")
    
    # Logic: y = 5x + 3 (mod 12)
    # This requires synthesizing Mod 4 (p=2) and Mod 3 (p=3).
    # Previous engine discovered p=2 and failed to find full logic.
    # New engine should return 'ADELIC_COMPOSITE_LINEAR' with p=12.
    
    X = list(range(100))
    Y = [(5*x + 3) % 12 for x in X]
    
    miner = LogicMiner()
    
    # We set min_consensus high to force rejection of partial Mod 2 solutions (which have 50% consensus?)
    # 5x+3 mod 12 -> x is odd/even logic?
    # Mod 2: 1x + 1. It fits 100% of data locally!
    # Wait, if p=2 fits 100% locally, score will be 1.0!
    # The engine will stop at p=2.
    # Ah.
    
    # ISSUE: Mod 12 logic *IS* Mod 2 logic (locally).
    # y = 5x+3 = x+1 (mod 2).
    # This is a valid Projection.
    # The engine finding p=2 is NOT wrong. It's just incomplete.
    # BUT we want the Global Logic.
    
    # How do we force it to look deeper?
    # It stops if consensus > min_consensus.
    # If p=2 has 1.0 consensus, it stops.
    
    # UNLESS we check "Unexplained Variance"?
    # The Mod 2 model explains y%2. It says nothing about y%3.
    # But RANSAC for p=2 maps y->y%2.
    
    # The user wants "Global Logic". 
    # Global Logic implies recovering the logic over Z (or Z/12Z).
    # If we return p=2, we claim the logic is Modulo 2.
    
    # Hasse Synthesis works if NO single prime explains the data well?
    # Or if we want to synthesize explicitly.
    # In Mod 12 case, p=2 explains y%2 perfectly. p=3 explains y%3 perfectly.
    # But neither explains y (real integer).
    
    # Current engine goal: "Find Logic".
    # If it finds "This data is Odd/Even", it succeeds.
    # But for "Mod 12 Clock", that's partial.
    
    # Let's see what happens.
    # In 'limit_probe_arena', Mod 12 failed. Why?
    # Because (5x+3)%12 is NOT 5x+3 (mod 2).
    # (5x+3)%12 values are 3, 8, 1, 6...
    # mod 2: 1, 0, 1, 0...
    # mod 4: 3, 0, 1, 2...
    # So y % 2 IS 1, 0, 1, 0...
    # Wait. (5*0+3)%12 = 3. 3%2 = 1.
    # (5*1+3)%12 = 8. 8%2 = 0.
    # (5*2+3)%12 = 13=1. 1%2 = 1.
    # Yes, it is perfectly 1, 0, 1, 0.
    # So p=2 solver sees 100% fit for linear logic.
    
    # So if p=2 is perfect, why did Limit Probe fail?
    # Because Limit Probe checks "Prediction Fidelity".
    # It reconstructs y using the p=2 model.
    # The p=2 model predicts y_pred = x+1 (mod 2).
    # It predicts 0 or 1.
    # But actual Y is 3, 8, 1...
    # So Fidelity is 0%.
    
    # AH! The Engine finds the *projection*, but Prediction fails.
    # We need to realize that p=2 is good LOCAL fit but bad GLOBAL fit.
    # But `discovery` only checks Local RANSAC.
    
    # To trigger Hasse, we need `select` to return score < min_consensus?
    # But here p=2 score is 1.0.
    # So Discovery says "I found p=2!".
    # But Validation (implied) fails.
    
    # We need a Global Check in Discovery?
    # "Does this model explain the Integer Data?"
    # If not, it's a projection.
    # Ideally, we want to find the Modulus M such that y = f(x) (mod M) explains y.
    
    # For this test, I will define a Mod 12 logic where NO single prime fits 100%?
    # Hard. CRT implies projections are valid.
    
    # Alternatively, I can force the LogicMiner to perform "Exhaustive Synthesis" if user requests?
    # Or heuristic: If p=2 and p=3 BOTH have score 1.0, we MUST combine them.
    # Current logic: `p, score = select(...)`. select returns Best.
    # If p=2 and p=3 are ties, it returns one.
    # I modified `select` to return candidates.
    # I should modify `engine.py` to check:
    # If top candidates are Multiple and High Score, Try Synthesis!
    # Even if score > min_consensus.
    
    # I'll update the test to run and see. 
    # If it returns p=2, I will need to update `engine.py` to be more greedy for synthesis.
    
    result = miner.fit(X, Y)
    print(f"Result: {result}")
    
    if 'ADELIC' in result.get('mode', ''):
        print(f"[PASS] Discovered Adelic Logic Mod {result.get('p')}")
    else:
        print(f"[FAIL] Found {result.get('mode')} p={result.get('p')}")
        # If it found p=2, that's partial success but not Hasse.

if __name__ == "__main__":
    test_hasse_production()
