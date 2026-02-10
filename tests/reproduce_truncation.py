
import sys
import os
from collections import defaultdict, Counter

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis import SerialManifoldSynthesizer

def reproduce_truncation():
    print("--- Reproduction Test: Component Truncation ---")
    
    # Initialize with small p
    miner = SerialManifoldSynthesizer(p=5)
    print(f"Initial p: {miner.p}")
    
    # Create 10 disjoint components (A->a, B->b, ..., J->j)
    # Each is a Root->Leaf pair.
    # Total entities: 20
    roots = "ABCDEFGHIJ"
    
    # Mock global_directed_adj AND global_adj (legacy check requires it)
    # Structure: u -> {v: weight}
    for i, r in enumerate(roots):
        child = r.lower()
        miner.global_directed_adj[r][child] = 10.0 
        pair = tuple(sorted((r, child)))
        miner.global_adj[pair] = 10.0
    
    print(f"Created {len(roots)} disjoint components (20 nodes total).")
    print(f"Expected behavior (Bug): Only {miner.p - 1} components effectively retained (approx 8 nodes).")
    
    # Run consolidation
    miner._consolidate_global_lattice()
    
    # Check results
    coords = miner.global_coordinates
    print(f"\nFinal Coordinates Count: {len(coords)}")
    print(f"Final p: {miner.p}")
    
    # Verify
    # We expect p=5 (unchanged)
    # We expect len(coords) <= (5-1)*2 = 8 (4 components)
    
    if len(coords) < 20:
        print("\n[SUCCESS] Reproduction successful: Truncation occurred.")
        print(f"Missing nodes: {20 - len(coords)}")
    else:
        print("\n[FAILURE] Reproduction failed: No truncation.")

if __name__ == "__main__":
    reproduce_truncation()
