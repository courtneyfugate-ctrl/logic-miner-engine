
import random
import re
import math
import hashlib
import sys
import os
import json
from collections import defaultdict
from pypdf import PdfReader

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
try:
    from logic_miner.core.text_featurizer import TextFeaturizer
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
    from logic_miner.core.text_featurizer import TextFeaturizer

class AdelicMapper:
    def __init__(self, dimensions=12, seed_prefix="DEFAULT"):
        self.dimensions = dimensions
        self.primes = [3, 5, 7]
        # Rotational Invariance: Use the seed_prefix to change the projection basis
        self.seeds = {
            3: f"{seed_prefix}_P3",
            5: f"{seed_prefix}_P5",
            7: f"{seed_prefix}_P7"
        }

    def _get_projection_sign(self, term, dim_index, prime):
        seed = self.seeds[prime]
        h = hashlib.md5(f"{seed}_{term}_{dim_index}".encode()).hexdigest()
        val = int(h, 16)
        return 1 if val % 2 == 0 else -1

    def compute_mappings(self, association_matrix, entities):
        mappings = defaultdict(dict)
        for p in self.primes:
            for i, term_a in enumerate(entities):
                bits = 0
                row = association_matrix[i]
                for d in range(self.dimensions):
                    dot_val = 0.0
                    for j, weight in enumerate(row):
                        if weight > 0:
                            term_b = entities[j]
                            sign = self._get_projection_sign(term_b, d, p)
                            dot_val += weight * sign
                    if dot_val >= 0:
                        bits |= (1 << d)
                mappings[term_a][p] = bits
        return mappings

class SheafSolver:
    def __init__(self, primes=[3, 5, 7]):
        self.primes = primes
        
    def solve(self, matrix, entities, anchors, hints, p):
        current = {}
        variables = []
        for e in entities:
            if e in anchors:
                current[e] = anchors[e]
            else:
                if e in hints:
                    current[e] = hints[e] * p 
                else:
                    current[e] = 0 # Neutral Start
                variables.append(e)
                
        ent_to_idx = {e: i for i,e in enumerate(entities)}
        
        # Relaxation
        for _ in range(5):
            for var in variables:
                idx = ent_to_idx[var]
                row = matrix[idx]
                sum_c = 0.0
                sum_w = 0.0
                for j, w in enumerate(row):
                    if w > 0:
                        neighbor = entities[j]
                        sum_c += current[neighbor] * w
                        sum_w += w
                if sum_w > 0:
                    current[var] = int(sum_c / sum_w)
        return current

class PurityPipeline:
    def __init__(self):
        self.featurizer = TextFeaturizer()
        
    def run_single_universe(self, text, seed_name):
        """
        Runs one full extraction with a specific rotation seed.
        Returns: Set of 'Consensus Edges' (A->B) found in this universe.
        """
        print(f"     > Running Universe '{seed_name}'...")
        
        # 1. Global extraction (Simulated for speed using chunk)
        full_ents = self.featurizer.extract_entities(text, limit=400)
        matrix, _ = self.featurizer.build_association_matrix(text, full_ents)
        
        # 2. Map
        mapper = AdelicMapper(seed_prefix=seed_name)
        adelic_map = mapper.compute_mappings(matrix, full_ents)
        
        # 3. Solve (Simulated single patch for speed)
        solver = SheafSolver()
        
        # We need per-prime solutions
        solutions = {} # {p: {term: coord}}
        for p in [3, 5, 7]:
            # Anchors? Just use self-consistency.
            hints = {t: adelic_map[t][p] for t in full_ents}
            # Mock anchors (top 10 fixed)
            anchors = {t: adelic_map[t][p] for t in full_ents[:10]}
            
            sol = solver.solve(matrix, full_ents, anchors, hints, p)
            solutions[p] = sol
            
        # 4. Identify Consensus Edges for this Universe
        # Edge exists if Child divides Parent in >= 2 fibers.
        universe_edges = set()
        
        for i, child in enumerate(full_ents):
            for j, parent in enumerate(full_ents):
                if i == j: continue
                
                votes = 0
                for p in [3, 5, 7]:
                    c_child = solutions[p][child]
                    c_parent = solutions[p][parent]
                    if c_parent != 0 and c_child != 0:
                        if c_parent % c_child == 0:
                            votes += 1
                
                if votes >= 2:
                    universe_edges.add((child, parent))
                    
        return universe_edges

    def run_experiment(self, pdf_path):
        print(f"--- [Protocol V.16: The Purity Iteration] ---")
        
        # Ingestion
        reader = PdfReader(pdf_path)
        text = ""
        for i in range(min(50, len(reader.pages))): # 50 page sample
            text += reader.pages[i].extract_text() + "\n"
            
        # Multi-Verse Execution
        seeds = ["ALPHA", "BETA", "GAMMA"]
        universe_results = []
        
        for seed in seeds:
            edges = self.run_single_universe(text, seed)
            print(f"       - Found {len(edges)} Consensus Edges.")
            universe_results.append(edges)
            
        # Intersection (The Adelic Shake)
        final_edges = universe_results[0]
        for i in range(1, len(seeds)):
            final_edges = final_edges.intersection(universe_results[i])
            
        print(f"\n   > [Purity Filter Results]")
        print(f"     - Initial Edges (Alpha Universe): {len(universe_results[0])}")
        print(f"     - Final Edges (Intersection of 3): {len(final_edges)}")
        
        # Check Targets
        # Need to know what terms survived.
        surviving_terms = set()
        for c, p in final_edges:
            surviving_terms.add(c)
            surviving_terms.add(p)
            
        targets = ["Grand Prix", "Scotland", "Flickr", "Energy", "Atom", "Matter"]
        print("\n   > Target Audit:")
        for t in targets:
            # Case insensitive check
            found = False
            for s in surviving_terms:
                if t.lower() in s.lower():
                    found = True
                    print(f"     - '{t}': SURVIVED (Verified Real). Found in '{s}'")
                    break
            if not found:
                 print(f"     - '{t}': VANISHED (Confirmed Ghost).")

        return final_edges

if __name__ == "__main__":
    base_path = "d:/Dropbox/logic-miner-engine/"
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    pipeline = PurityPipeline()
    pipeline.run_experiment(pdf_path)
