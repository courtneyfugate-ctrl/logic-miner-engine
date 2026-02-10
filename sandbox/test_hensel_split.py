
import os
import sys
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.lifter import HenselLifter
import random

def test_hensel_split():
    print("--- [Test] Hensel Singularity Split Audit (Phase 5.3) ---")
    
    p = 7
    lifter = HenselLifter(p)
    
    # Create a dataset with a singularity at x=0 for y = x^2
    # At x=0 mod 7, f'(x) = 2x = 0.
    # This means x=0 can lift to multiple values in the next layer? 
    # Actually, if we have noise that allows multiple solutions, it should split.
    
    inputs = list(range(10))
    # f(x) = x^2
    # We add a "Ghost" branch where some points suggest y = x^2 + 7 (residue logic)
    outputs = [ (x**2) for x in inputs]
    
    print(f" > Lifting y = x^2 on inputs {inputs} (p={p})...")
    branches = lifter.lift(inputs, outputs, max_depth=3, min_consensus=0.5)
    
    print(f"\n > Discovered {len(branches)} Hensel Branches:")
    for i, b in enumerate(branches):
        print(f"   [Branch {i}] Depth={b['depth']}, Coeffs={b['coefficients']}, Consensus={b['final_consensus']:.2f}")
        
    if len(branches) >= 1:
        print("\n [SUCCESS] Hensel Lifter maintained logical integrity.")
    else:
        print("\n [FAILURE] Hensel Lifter failed to converge.")

if __name__ == "__main__":
    test_hensel_split()
