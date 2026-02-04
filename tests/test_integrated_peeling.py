from src.logic_miner.engine import LogicMiner
import random

def test_integrated_peeling():
    print("### ENGINE FIT() PEELING TEST ###")
    miner = LogicMiner()
    
    # Generate 2-Layer Logic (Linear/Linear)
    # y = 3x + 1 (Mod 17) - 80%
    # y = 8x + 5 (Mod 17) - 20%
    
    p = 17
    data_X = []
    data_Y = []
    
    for _ in range(80):
        x = random.randint(0, 100)
        y = (3*x + 1) % p
        data_X.append([x]) # Vector format for Multivariate trigger
        data_Y.append(y)
        
    for _ in range(20):
        x = random.randint(0, 100)
        y = (8*x + 5) % p
        data_X.append([x])
        data_Y.append(y)
        
    # Run Fit
    res = miner.fit(data_X, data_Y)
    
    print("\nResult:", res)
    
    if res.get('mode') == 'MULTIMODAL':
        branches = res.get('branches', [])
        print(f"Found {len(branches)} branches.")
        
        if len(branches) >= 2:
            b1 = branches[0]['params']
            b2 = branches[1]['params']
            print(f"Branch 1: {b1} (Expected 3x+1)")
            print(f"Branch 2: {b2} (Expected 8x+5)")
            
            # Check Bias/Slope. Multivariate pads [Bias, Slope]
            # 3x+1 -> [1, 3]
            # 8x+5 -> [5, 8]
            
            success = True
            if not (b1 == [1, 3] or b1 == (1,3)): success = False
            if not (b2 == [5, 8] or b2 == (5,8)): success = False
            
            if success:
                print("[SUCCESS] Engine correctly identified multimodal logic.")
            else:
                print("[PARTIAL] Branches found but params mismatch.")
        else:
            print("[FAIL] Less than 2 branches.")
    else:
        print(f"[FAIL] Mode is {res.get('mode')}, expected MULTIMODAL.")

if __name__ == "__main__":
    test_integrated_peeling()
