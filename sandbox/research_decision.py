from src.logic_miner.engine import LogicMiner
import random

def research_decision_logic():
    print("### PROPOSAL: DECISION LOGIC MINING ###")
    miner = LogicMiner()
    
    # Feature: Frustration Score (0-100)
    X = list(range(100))
    
    # 1. Modular Decision: Chat if Frustration is Odd (Parity Logic)
    # This represents a specialized rule like "Chat on alternate turns".
    print("\n--- Case 1: Modular Decision (Odd/Even) ---")
    # Map Yes -> 1, No -> 0
    Y1 = [1 if x % 2 != 0 else 0 for x in X]
    
    res1 = miner.fit(X, Y1)
    print(f"Result: Mode={res1.get('mode')}, p={res1.get('p')}")
    if res1.get('p') == 2:
        print("[SUCCESS] Discovered Parity Decision Logic.")
    
    # 2. Threshold Decision: Chat if Frustration > 50 (Step Function)
    # This is a standard "Business Rule".
    print("\n--- Case 2: Threshold Decision (x > 50) ---")
    Y2 = [1 if x > 50 else 0 for x in X]
    
    try:
        res2 = miner.fit(X, Y2)
        print(f"Result: Mode={res2.get('mode')}, p={res2.get('p')}")
        
        # We expect Adelic/Real or Mahler detection here.
        # A threshold is NOT modular (mod p logic repeats).
        # So p should be inf or Mahler.
        if res2.get('p') == float('inf') or res2.get('mode') == 'MAHLER':
            print("[SUCCESS] Discovered Non-Modular Threshold Logic.")
        else:
            print("[PARTIAL] Found a modular approximation?")
            
    except Exception as e:
        print(f"[FAIL] Engine crashed on Step Function: {e}")
        
    # 3. Complex Modulo Decision: Chat if x = 3 mod 7
    # "Chat every 7th message, offset by 3"
    print("\n--- Case 3: Sparse modulo (x % 7 == 3) ---")
    Y3 = [1 if x % 7 == 3 else 0 for x in X]
    
    res3 = miner.fit(X, Y3)
    print(f"Result: Mode={res3.get('mode')}, p={res3.get('p')}")
    # Logic should be:
    # 1 if x=3, 0 otherwise?
    # No, this is a delta function in Z_7.
    # In Z_7, can we represent "1 if x=3 else 0" as a polynomial?
    # Yes, Lagrange interpolation.
    # Degree will be high (p-1 = 6)?
    # Let's see if it finds p=7.
    if res3.get('p') == 7:
        print("[SUCCESS] Discovered Mod 7 Decision Pattern.")

if __name__ == "__main__":
    research_decision_logic()
