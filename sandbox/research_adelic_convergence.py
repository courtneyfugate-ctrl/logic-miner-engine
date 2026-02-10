
import sys
import os
from collections import defaultdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.algebraic_text import AlgebraicTextSolver
from logic_miner.core.text_featurizer import TextFeaturizer
from pypdf import PdfReader

def run_experiment():
    print("--- Adelic Convergence Research (Hypothesis 2) ---")
    print("Hypothesis: Force p=2 collision to find 'Element' parent.")
    
    # Use synthetic text to guarantee high density of "Hydrogen" and "Carbon" and "Element"
    # We want to see if dist(H, C) is SMALLER than dist(H, Reaction) under p=2.
    
    text = ""
    # "Element" is the parent context
    text += ("Element " * 100) + "\n"
    # "Hydrogen" and "Carbon" appear with Element
    text += ("Element Hydrogen " * 50) + "\n"
    text += ("Element Carbon " * 50) + "\n"
    # "Reaction" is distinct
    text += ("Reaction Energy " * 50) + "\n"
    
    candidates = ["Element", "Hydrogen", "Carbon", "Reaction"]
    
    # Solve with p=2
    print("   > Running Solver with p=2...")
    featurizer = TextFeaturizer()
    matrix, counts, _ = featurizer.build_association_matrix(text, candidates)
    
    solver = AlgebraicTextSolver(p=2)
    res = solver.solve(matrix, candidates, counts)
    coords = res['coordinates']
    
    # Analyze Distances
    # v_p(diff)
    
    h_c = coords["Hydrogen"]
    c_c = coords["Carbon"]
    r_c = coords["Reaction"]
    e_c = coords["Element"]
    
    print(f"   > Coordinates (p=2):")
    for c in candidates:
        print(f"     {c}: {coords[c]}")
        
    def get_vp(n):
        if n == 0: return 999
        v = 0
        while n % 2 == 0:
            v += 1
            n //= 2
        return v
        
    dist_HC = get_vp(abs(h_c - c_c))
    dist_HR = get_vp(abs(h_c - r_c))
    dist_HE = get_vp(abs(h_c - e_c))
    
    print("\n   > p-adic Valuations of Differences (Shared Prefix Depth):")
    print(f"     v_2(Hydrogen - Carbon): {dist_HC}")
    print(f"     v_2(Hydrogen - Reaction): {dist_HR}")
    print(f"     v_2(Hydrogen - Element): {dist_HE}")
    
    if dist_HC > dist_HR:
        print("\n[SUCCESS] Hydrogen and Carbon share a deeper trunk than Hydrogen and Reaction.")
    else:
        print("\n[FAILURE] Hydrogen and Carbon are equally distant or Reaction is closer.")

if __name__ == "__main__":
    run_experiment()
