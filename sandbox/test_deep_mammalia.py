import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from logic_miner.engine import LogicMiner

def test_deep_mammalia():
    print("--- [Verification] Deep Mammalia Logic Mining ---")
    
    # 1. Load Text
    with open('sandbox/mammalia_full.txt', 'r', encoding='utf-8') as f:
        text = f.read()
        
    print(f"   > Loaded Text ({len(text)} chars).")
    
    # 2. Initialize Engine
    miner = LogicMiner()
    
    # 3. fit_text (This runs Featurizer -> Solver -> RANSAC)
    print("   > Running Universal Blackbox...")
    result = miner.fit_text(text)
    
    # 4. Analyze Results
    print("\n--- [Audit Results] ---")
    print(f"   > Mahler Score (Convergence): {result.get('analytic_score', 'N/A')}")
    print(f"   > Polynomial Degree: {len(result.get('polynomial', []))-1}")
    
    coords = result.get('coordinates', {})
    
    # 5. Check specific entities to verify Logic Discovery
    key_entities = ['Mammalia', 'Eutheria', 'Platypus', 'Elephant', 'Bat', 'Whale']
    
    print("\n   > Discovered p-adic Coordinates:")
    for k in key_entities:
        if k in coords:
            print(f"     {k}: {coords[k]}")
        else:
             # Try checking if it was mapped with underscores or slightly diff name
             found = False
             for c in coords:
                 if k in c:
                    print(f"     {c}: {coords[c]}")
                    found = True
                    break
             if not found:
                print(f"     {k}: [Not Found/Filtered]")

    # 6. Verify Optimization
    # The output log will show if "Attempting 15 RANSAC permutations" occurred.
    
    print("\n   > Verification Complete.")
    
    # 7. Write Dump File
    dump_path = 'sandbox/deep_mammalia_dump.txt'
    with open(dump_path, 'w', encoding='utf-8') as f:
        f.write("--- Algebraic Model Dump (Universal Blackbox V.5) ---\n")
        f.write(f"Source: sandbox/mammalia_full.txt\n")
        f.write(f"Mahler Score: {result.get('analytic_score', 'N/A')}\n")
        f.write(f"Lipschitz Violation: {result.get('lipschitz_violation', 'N/A')}\n\n")
        
        f.write("--- Defining Polynomial P(x) ---\n")
        poly = result.get('polynomial', [])
        f.write(f"Degree: {len(poly)-1}\n")
        f.write(f"Coefficients: {poly}\n\n")
        
        f.write("--- Godel Mapping & P-adic Coordinates ---\n")
        for ent, coord in coords.items():
            f.write(f"{ent}: {coord}\n")
            
    print(f"   > Artifacts Dumped to: {dump_path}")

if __name__ == "__main__":
    test_deep_mammalia()
