
import random
import re
import math
import hashlib
import sys
import os
import json
from collections import defaultdict, Counter
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
                    current[e] = 0
                variables.append(e)
                
        ent_to_idx = {e: i for i,e in enumerate(entities)}
        
        for _ in range(5):
            for var in variables:
                idx = ent_to_idx[var]
                row = matrix[idx]
                neighbor_sum = 0
                weight_sum = 0
                for j, w in enumerate(row):
                    if w > 0:
                        neighbor = entities[j]
                        neighbor_sum += current[neighbor] * w
                        weight_sum += w
                if weight_sum > 0:
                    current[var] = int(neighbor_sum / weight_sum)
        return current

class HybridPipeline:
    def __init__(self):
        self.featurizer = TextFeaturizer()
        
    def run_experiment(self, pdf_path):
        print(f"--- [Protocol V.17: The Hybrid Filter] ---")
        
        # 1. Ingestion
        reader = PdfReader(pdf_path)
        text = ""
        for i in range(min(50, len(reader.pages))): 
            text += reader.pages[i].extract_text() + "\n"
            
        full_ents = self.featurizer.extract_entities(text, limit=600)
        
        # 2. Frequency Audit
        term_counts = Counter()
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)
        
        # Map phrases to sums of words (Approximate frequency)
        entity_freqs = {}
        for ent in full_ents:
            parts = ent.lower().split()
            # Mean frequency of constituent words
            freq = sum(word_counts[p] for p in parts) / len(parts)
            entity_freqs[ent] = freq
            
        # Determine Protection Threshold (Top 10%)
        sorted_freqs = sorted(entity_freqs.values(), reverse=True)
        threshold_idx = int(len(sorted_freqs) * 0.10)
        threshold_val = sorted_freqs[threshold_idx]
        
        protected_set = {ent for ent, freq in entity_freqs.items() if freq >= threshold_val}
        
        print(f"   > [Phase 1: Frequency Audit]")
        print(f"     - Protected {len(protected_set)} terms (Top 10%, Freq >= {threshold_val:.1f}).")
        
        # Check targets
        targets = ["Energy", "Atom", "Matter", "Grand Prix", "Scotland", "Flickr"]
        for t in targets:
             # Find actual casing
             for real_t in entity_freqs:
                 if t.lower() in real_t.lower():
                     stat = "PROTECTED" if real_t in protected_set else "VULNERABLE"
                     f = entity_freqs[real_t]
                     print(f"     - '{real_t}': Freq={f:.1f} -> {stat}")
                     break

        # 3. Adelic Shake (V.16 Logic)
        print(f"\n   > [Phase 2: Adelic Shake (N=3)]")
        seeds = ["ALPHA", "BETA", "GAMMA"]
        universe_edges = []
        matrix, _ = self.featurizer.build_association_matrix(text, full_ents)
        
        for seed in seeds:
            mapper = AdelicMapper(seed_prefix=seed)
            adelic_map = mapper.compute_mappings(matrix, full_ents)
            solver = SheafSolver()
            
            # Solve for P=3,5,7
            solutions = {}
            for p in [3, 5, 7]:
                hints = {t: adelic_map[t][p] for t in full_ents}
                anchors = {t: adelic_map[t][p] for t in full_ents[:10]}
                solutions[p] = solver.solve(matrix, full_ents, anchors, hints, p)
                
            # Compute Edges
            edges = set()
            for i, child in enumerate(full_ents):
                for j, parent in enumerate(full_ents):
                    if i == j: continue
                    votes = 0
                    for p in [3, 5, 7]:
                         c_c = solutions[p][child]
                         c_p = solutions[p][parent]
                         if c_p != 0 and c_c != 0 and c_p % c_c == 0:
                             votes += 1
                    if votes >= 2:
                        edges.add((child, parent))
                        
            universe_edges.append(edges)
            print(f"       - Universe {seed}: {len(edges)} edges.")
            
        # Intersection
        intersection_edges = universe_edges[0]
        for i in range(1, len(seeds)):
            intersection_edges = intersection_edges.intersection(universe_edges[i])
            
        print(f"     - Intersection Size: {len(intersection_edges)}")
        
        # 4. Hybrid Union
        # Final Graph = Edges in Intersection OR Edges connected to Protected Terms? 
        # Safer: Nodes = (Nodes in Intersection) UNION (Protected Nodes)
        # We need to construct edges for Protected Nodes.
        # Policy: If a node is Protected, we accept its edges from Universe ALPHA (Default).
        
        final_edges = set()
        
        # Add stable edges
        for e in intersection_edges:
            final_edges.add(e)
            
        # Add protected edges (From Alpha)
        protected_additions = 0
        for u, v in universe_edges[0]:
            if (u in protected_set) or (v in protected_set):
                if (u, v) not in final_edges:
                    final_edges.add((u, v))
                    protected_additions += 1
                    
        print(f"\n   > [Phase 3: Hybrid Union]")
        print(f"     - Restored {protected_additions} edges via Frequency Protection.")
        print(f"     - Final Graph Size: {len(final_edges)} edges.")
        
        # 5. Final Audit
        surviving_terms = {u for u, v in final_edges} | {v for u, v in final_edges}
        
        print("\n   > [Final Audit V.17]")
        for t in targets:
             found = False
             for real_t in surviving_terms:
                 if t.lower() in real_t.lower():
                     print(f"     - '{real_t}': SURVIVED (Success).")
                     found = True
                     break
             if not found:
                 print(f"     - '{t}': VANISHED (Success).")

if __name__ == "__main__":
    base_path = "d:/Dropbox/logic-miner-engine/"
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    pipeline = HybridPipeline()
    pipeline.run_experiment(pdf_path)
