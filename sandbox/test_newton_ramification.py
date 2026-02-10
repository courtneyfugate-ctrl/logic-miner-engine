
import os
import sys
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.solver import ModularSolver
import random

def test_newton_ramification():
    print("--- [Test] Newton Ramification Audit (Phase 5.2) ---")
    
    p = 7
    solver = ModularSolver(p)
    
    # Create two synthetic branches with different p-adic structures (simulated via residuals)
    # Branch 1: y = 2x + 1 (Straight logic)
    # Branch 2: y = 3x^2 + x + 2 (High energy, different slope)
    
    data = []
    # Branch 1 (50 points)
    for _ in range(50):
        x = random.randint(0, 1000)
        y = (2*x + 1) % p
        data.append((x, y))
        
    # Branch 2 (30 points) - We use "Abs" values that would project to different residue classes
    for _ in range(30):
        x = random.randint(0, 1000)
        # We simulate a "valuation shift" by picking x that are multiples of p
        # or by shifting the y output
        y = (3*x**2 + x + 2) % p
        data.append((x, y))
        
    # Add noise
    for _ in range(20):
        data.append((random.randint(0, 1000), random.randint(0, p-1)))
        
    print(f" > Running Iterative Peeling on {len(data)} points (p={p})...")
    layers = solver.ransac_iterative(data, min_size=10, min_ratio=0.2)
    
    print(f"\n > Discovered {len(layers)} Layers:")
    for i, layer in enumerate(layers):
        m = layer['model']
        slope = layer['valuation_slope']
        profile = layer['newton_profile']
        ratio = layer['ratio']
        print(f"   [Layer {i}] Model={m}, Slope={slope:.2f}, Profile={profile}, Ratio={ratio:.2f}")
        
    if len(layers) >= 2:
        slopes = [l['valuation_slope'] for l in layers]
        # Verify if we have ramification (different slopes or non-zero slopes)
        if any(abs(s) > 0.0 for s in slopes):
            print("\n [SUCCESS] Newton Polygon detected ramification.")
        else:
            print("\n [WARNING] Detected multiple layers but they are 'Flat' (Slopes=0). Check valuation logic.")
    else:
        print("\n [FAILURE] Could not detect multiple logical branches.")

if __name__ == "__main__":
    test_newton_ramification()
