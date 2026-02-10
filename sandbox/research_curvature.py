
import sys
import os
from collections import defaultdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis import SerialManifoldSynthesizer
from logic_miner.engine import LogicMiner # For dependency check

def calculate_curvature(trajectory):
    # Discrete curvature for 1D sequence x0, x1, x2...
    # sum |x(t+1) - 2x(t) + x(t-1)|
    if len(trajectory) < 3: return 0.0
    
    k = 0.0
    for i in range(1, len(trajectory)-1):
        d2 = trajectory[i+1] - 2*trajectory[i] + trajectory[i-1]
        k += abs(d2)
    return k

def run_experiment():
    print("--- Curvature-Weighted Promotion Research ---")
    
    # Synthetic Stream: 3 Blocks
    # "Matter" is stable anchor. "Given" is random noise.
    
    blocks = []
    
    # Block 1: Matter is near Atoms. Given is near Atoms.
    b1 = ("Matter Atoms " * 50) + "\n" + ("Atoms Given " * 50)
    blocks.append(b1)
    
    # Block 2: Matter is near Energy. Given is near Energy.
    b2 = ("Matter Energy " * 50) + "\n" + ("Energy Given " * 50)
    blocks.append(b2)
    
    # Block 3: Matter is near Reaction. Given is near Reaction.
    b3 = ("Matter Reaction " * 50) + "\n" + ("Reaction Given " * 50)
    blocks.append(b3)
    
    # Observe: "Matter" is always the primary subject (Left side).
    # "Given" is always the object of the object (Right side).
    # In V.31/32 adjacency, Matter is Central. Given is Peripheral?
    # Or Given is connecting to everything, pulling it towards center?
    
    # Manual Block Processing
    from logic_miner.core.algebraic_text import AlgebraicTextSolver
    from logic_miner.core.text_featurizer import TextFeaturizer
    
    history = defaultdict(list)
    targets = ["Matter", "Given"]
    p = 5
    
    print("   > Processing Stream (Manual Local Solving)...")
    featurizer = TextFeaturizer()
    solver = AlgebraicTextSolver(p=p)
    
    for i, block in enumerate(blocks):
        print(f"     > Block {i+1}...")
        
        # 1. Featurize
        # We need to ensure "Matter" and "Given" are in candidates
        candidates = ["Matter", "Atoms", "Given", "Energy", "Reaction"]
        matrix, counts, _ = featurizer.build_association_matrix(block, candidates)
        
        # 2. Solve Local
        # Bypass purification, just solve
        res = solver.solve(matrix, candidates, counts)
        coords = res['coordinates']
        
        # Capture coords
        for t in targets:
            c = coords.get(t, 0)
            history[t].append(c)
            v_p = 0
            # Heuristic depth check
            if c % p == 1 or c % p == 2: # Root-ish?
               pass
            print(f"       {t}: {c}")
            
    print("\n--- RESULTS: Trajectory Curvature ---")
    print(f"{'TERM'.ljust(15)} | {'TRAJECTORY'.ljust(30)} | {'CURVATURE'}")
    print("-" * 60)
    
    for t in targets:
        traj = history[t]
        k = calculate_curvature(traj)
        print(f"{t.ljust(15)} | {str(traj).ljust(30)} | {k:.2f}")

    # Interpretation
    k_matter = calculate_curvature(history["Matter"])
    k_given = calculate_curvature(history["Given"])
    
    if k_given > k_matter:
        print("\n[SUCCESS] Hypothesis Confirmed: 'Given' has higher curvature (instability) than 'Matter'.")
    else:
        print("\n[FAILURE] Hypothesis Refuted: Curvature indistinguishable.")

if __name__ == "__main__":
    run_experiment()
