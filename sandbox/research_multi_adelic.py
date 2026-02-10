
import sys
import os
import random
import time
from collections import defaultdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.algebraic_text import AlgebraicTextSolver
from logic_miner.core.text_featurizer import TextFeaturizer
from pypdf import PdfReader

class MultiAdelicSolver:
    def __init__(self, primes=[5, 7, 11]):
        self.primes = primes
        self.solvers = {p: AlgebraicTextSolver(p=p) for p in primes}
        
    def solve(self, text, limit=200):
        print(f"--- Multi-Adelic Decomposition (Primes: {self.primes}) ---")
        
        # Shared Featurization (Siloed)
        print("   > Featurizing Text...")
        featurizer = TextFeaturizer()
        candidates = featurizer.extract_entities(text, limit=limit)
        matrix, counts, G_directed = featurizer.build_association_matrix(text, candidates)
        
        # Purify (Simple top 50 for research speed)
        candidates = candidates[:50]
        trimmed_matrix = [[matrix[i][j] for j in range(50)] for i in range(50)]
        
        results = {}
        
        # Independent Projections
        for p in self.primes:
            print(f"   > Solving Projection Q_{p}...")
            # Shuffle/Randomize is implicit in RANSAC if not fixed seed, 
            # but AlgebraicTextSolver might be deterministic? 
            # Let's assume standard solver run.
            
            # Note: The solver builds a tree. We need the VALUATION (depth).
            # v_p(x) = depth in the p-adic tree.
            
            res = self.solvers[p].solve(trimmed_matrix, candidates, counts)
            coords = res['coordinates']
            
            # Extract valuation v_p(addr)
            # Actually, standard coord is: trunk + digit*p^(depth+1)
            # We want the DEPTH as the valuation surrogate (or actual v_p of relative distance).
            # Simple Proxy: Depth in tree.
            
            # Trace depth from coordinates?
            # Coords: trunk + ... 
            # The solver doesn't explicitly return depth map easily, but we can compute v_p(addr).
            # Wait, roots have v_p(addr) = 0. Children have v_p(addr) >= 1 (if address is divisible by p? No.)
            # V.32 scheme: children = parent + digit * p^(depth+1).
            # Difference (child - parent) is divisible by p^(depth+1).
            # This is complex to decode blindly.
            
            # Let's rely on the reported 'coordinates' having structure.
            results[p] = coords

        # Synthesize Vectors
        print("   > Synthesizing Valuation Vectors v(x)...")
        vectors = {}
        alignment_score = 0
        
        for c in candidates:
            vec = []
            for p in self.primes:
                addr = results[p].get(c, 0)
                # Compute effective valuation/depth
                # Heuristic: If addr < p -> Depth 0
                # If addr > p -> Depth > 0
                # Just store raw address modulo p pair?
                # Research Note says: v(x) = (v_p1, v_p2...)
                # Let's store the raw tuple of assignments relative to root.
                
                vec.append(addr)
            vectors[c] = tuple(vec)
            
        return vectors, candidates

def run_experiment():
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    print(f"Reading {pdf_path}...")
    reader = PdfReader(pdf_path)
    
    # Extract first 50 pages text
    text = ""
    for i in range(50):
        text += reader.pages[i].extract_text() + "\n"
        
    solver = MultiAdelicSolver()
    vectors, entities = solver.solve(text)
    
    print("\n--- RESULTS: Concept Separation ---")
    print(f"{'CONCEPT'.ljust(30)} | {'Q_5'.ljust(10)} | {'Q_7'.ljust(10)} | {'Q_11'.ljust(10)}")
    print("-" * 70)
    
    # Pick a few key terms to check separation
    targets = ["Energy", "Matter", "Atoms", "Reaction", "Mass", "Unknown", "Solution"]
    
    for e in entities:
        if e in targets or random.random() < 0.1: # Sample
            v = vectors[e]
            print(f"{e.ljust(30)} | {str(v[0]).ljust(10)} | {str(v[1]).ljust(10)} | {str(v[2]).ljust(10)}")

if __name__ == "__main__":
    run_experiment()
