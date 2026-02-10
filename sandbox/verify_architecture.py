
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner

def verify():
    print("--- Verifying Architecture Enforcement ---")
    miner = LogicMiner()
    
    # Tiny input to trigger fit_text
    # Should STILL trigger V.53 because we hard-coded it.
    text = "Hydrogen is an element. Helium is a gas."
    
    try:
        result = miner.fit(text)
        print(f"\n[Success] Result Mode: {result.get('mode')}")
        print(f"[Success] Note: {result.get('note')}")
        
    except Exception as e:
        print(f"\n[Error] {e}")

if __name__ == "__main__":
    verify()
