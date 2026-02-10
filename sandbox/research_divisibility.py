
import sys
import os
import math
from collections import defaultdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.text_featurizer import TextFeaturizer
from logic_miner.core.algebraic_text import AlgebraicTextSolver
from pypdf import PdfReader

def get_vp(n, p):
    if n == 0: return 0 # Distance 0 means infinite valuation, but for divisibility check?
    # v_p(diff)
    val = 0
    temp = abs(n)
    while temp > 0 and temp % p == 0:
        val += 1
        temp //= p
    return val

def build_divisibility_tree(coordinates, p, counts):
    print(f"   > Rebuilding Tree via p-adic Divisibility (p={p})...")
    
    # Sort entities by Frequency (High freq = likely Parent)
    entities = sorted(coordinates.keys(), key=lambda e: counts.get(e.replace(" ", "_"), 0), reverse=True)
    
    tree = defaultdict(list)
    roots = []
    
    # For every entity, find the "Best Parent"
    # Criteria:
    # 1. Parent must be "more fundamental" (Higher Frequency? Or just present?)
    #    Let's use Frequency as strict hierarchy enforcement for now.
    # 2. Maximize v_p(child_coord - parent_coord)
    
    for i, child in enumerate(entities):
        child_coord = coordinates[child]
        best_parent = None
        max_vp = -1
        
        # Search potential parents (must be higher freq, so earlier in sorted list)
        # Scan all `j < i`? 
        # Yes, purely generative.
        
        candidates = entities[:i]
        
        if not candidates:
            roots.append(child)
            continue
            
        for parent in candidates:
            parent_coord = coordinates[parent]
            dist = child_coord - parent_coord
            if dist == 0: continue # Same coord?
            
            vp = get_vp(dist, p)
            
            if vp > max_vp:
                max_vp = vp
                best_parent = parent
            elif vp == max_vp:
                # Tie-breaker: Prefer closer coordinate value (geometric backup)
                # or prefer higher frequency (first in list) logic
                pass
        
        # Threshold: If max_vp is 0, is it really a child?
        # If v_p(diff) = 0, they are in different mod-p classes (distance 1).
        # We might accept it as a weak link, or declare a new Root.
        
        if best_parent and max_vp >= 1: 
             # Strong link (share p-factor)
             tree[best_parent].append(child)
        else:
             # Weak link or Root
             roots.append(child)
             
    return tree, roots

def run_experiment():
    print("Using Synthetic Text for Reliability...")
    # Generate synthetic text with known frequencies and co-occurrences
    # Structure:
    # Matter -> Atoms -> Hydrogen
    # Matter -> Atoms -> Carbon
    # Matter -> Energy
    # Reaction -> Energy
    
    text = ""
    # "Matter" is root (High freq)
    text += ("Matter " * 100) + "\n"
    # "Atoms" (Med freq) nearby Matter
    text += ("Matter Atoms " * 50) + "\n"
    # "Energy" (Med freq) nearby Matter and Reaction
    text += ("Matter Energy " * 40) + "\n"
    text += ("Reaction Energy " * 40) + "\n"
    # "Hydrogen" and "Carbon" (Low freq) nearby Atoms
    text += ("Atoms Hydrogen " * 20) + "\n"
    text += ("Atoms Carbon " * 20) + "\n"
    # "Reaction" -> "Bond"
    text += ("Reaction Bond " * 30) + "\n"
    
    candidates = [ "Matter", "Atoms", "Energy", "Reaction", "Hydrogen", "Carbon", "Bond" ]
    print(f"   > Synthetic Text Length: {len(text)} chars")
    print("   > building matrix...")
    featurizer = TextFeaturizer()
    matrix, counts, _ = featurizer.build_association_matrix(text, candidates)
    
    # Classify/Purify (mimic V.32) - BYPASS FOR SYNTHETIC
    # metrics = featurizer.calculate_spectral_metrics(candidates, _, counts)
    # classifications = featurizer.classify_terms(metrics)
    # purified = [c for c in candidates if classifications.get(c) == "CONCEPT"]
    purified = candidates
    
    # Solve
    solver = AlgebraicTextSolver(p=5)
    # Re-build matrix for purified
    p_matrix, p_counts, _ = featurizer.build_association_matrix(text, purified)
    res = solver.solve(p_matrix, purified, p_counts)
    
    coords = res['coordinates']
    p = res['p']
    
    print(f"   > Baseline p={p}. Extracted {len(coords)} coordinates.")
    
    # Rebuild Tree
    new_tree, new_roots = build_divisibility_tree(coords, p, counts)
    
    print("\n--- RESULTS: Divisibility-Based Tree ---")
    print(f"Roots Discovered: {len(new_roots)}")
    print(f"Roots: {new_roots[:10]}")
    
    # Check specific deeply nested items
    # e.g. "Hydrogen" should be near "Elements"?
    
    def print_tree(node, depth=0):
        print("  " * depth + f"- {node} (v_p={get_vp(coords[node], p)})")
        for child in new_tree.get(node, []):
             print_tree(child, depth+1)
             
    # Print top 3 trees
    for r in new_roots[:3]:
        print(f"\n[Tree Root: {r}]")
        print_tree(r)

if __name__ == "__main__":
    run_experiment()
