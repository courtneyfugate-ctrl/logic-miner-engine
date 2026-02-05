
import random
import re
import math
import hashlib
from collections import Counter, defaultdict
from pypdf import PdfReader
import sys
import os
import json

# Add src to path just in case
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
# Attempt import or mock
try:
    from logic_miner.core.text_featurizer import TextFeaturizer
except ImportError:
    # Fallback if running relative
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
    from logic_miner.core.text_featurizer import TextFeaturizer

class AdelicMapper:
    """
    Phase 1: Pre-Ingestion Topology (Adelic Product Space).
    Maps terms to a Vector of Integers for primes p=3, 5, 7.
    """
    def __init__(self, dimensions=12):
        self.dimensions = dimensions
        self.primes = [3, 5, 7]
        # Independent seeds for independent filtrations
        self.seeds = {
            3: "PROTOCOL_V13_PHYSICS",
            5: "PROTOCOL_V13_CHEMISTRY",
            7: "PROTOCOL_V13_STRUCTURE"
        }

    def _get_projection_sign(self, term, dim_index, prime):
        # Deterministic random sign unique to the Prime Axis
        seed = self.seeds[prime]
        h = hashlib.md5(f"{seed}_{term}_{dim_index}".encode()).hexdigest()
        val = int(h, 16)
        return 1 if val % 2 == 0 else -1

    def compute_mappings(self, association_matrix, entities):
        """
        Returns a Dict: { term: {3: c3, 5: c5, 7: c7} }
        """
        n = len(entities)
        print(f"     > Adelic Map: Projecting {n} entities to Product Space (p=3,5,7)...")
        
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
    """
    Phase 2: Manifold Solver for the Adelic Sheaf.
    Solves each prime fiber independently (Sheaf Logic).
    """
    def __init__(self, primes=[3, 5, 7]):
        self.primes = primes
        
    def solve(self, matrix, entities, fixed_anchors, initial_adelic_map):
        refined_map = defaultdict(dict)
        
        # Solve each prime independenty
        for p in self.primes:
            p_anchors = {}
            for term, vec in fixed_anchors.items():
                if p in vec: p_anchors[term] = vec[p]
                
            p_initial = {}
            for term, vec in initial_adelic_map.items():
                if p in vec: p_initial[term] = vec[p]
                
            p_solved = self._solve_fiber(matrix, entities, p_anchors, p_initial, p)
            
            for term, coord in p_solved.items():
                refined_map[term][p] = coord
                
        return refined_map
        
    def _solve_fiber(self, matrix, entities, anchors, hints, p):
        current = {}
        variables = []
        
        for e in entities:
            if e in anchors:
                current[e] = anchors[e]
            else:
                if e in hints:
                    current[e] = hints[e] * p 
                else:
                    current[e] = random.randint(1, 1000)
                variables.append(e)
                
        ent_to_idx = {e: i for i,e in enumerate(entities)}
        
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

class SheafManifold:
    """
    Protocol V.14 Manager (The Consensus Iteration)
    """
    def __init__(self, chunk_size=10, overlap=0.5):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.global_anchors = {} 
        self.splines = [] 
        self.term_history = defaultdict(lambda: {3:[], 5:[], 7:[]}) 
        self.term_curvature = {}
        self.term_classification = {} # New in V.14
        
    def run_pipeline(self, pdf_path, max_pages=None):
        print(f"--- [Protocol V.14: Sheaf Consensus Engine] ---")
        
        print("   > Phase 0: Constituting Adelic Global Anchors...")
        featurizer = TextFeaturizer()
        
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        if max_pages: total_pages = min(total_pages, max_pages)
            
        full_text_sample = ""
        for i in range(0, total_pages, 5):
             full_text_sample += reader.pages[i].extract_text() + "\n"
             
        global_ents = featurizer.extract_entities(full_text_sample)
        anchor_terms = global_ents[:50] 
        
        matrix, _ = featurizer.build_association_matrix(full_text_sample, global_ents)
        mapper = AdelicMapper(dimensions=12)
        global_adelic = mapper.compute_mappings(matrix, global_ents)
        
        for term in anchor_terms:
            self.global_anchors[term] = global_adelic.get(term, {})
            
        print(f"     > Fixed {len(anchor_terms)} Anchors in Product Space.")

        # Spline Processing
        stride = int(self.chunk_size * (1.0 - self.overlap))
        current_idx = 0
        patch_id = 0
        
        while current_idx < total_pages:
            end_idx = min(current_idx + self.chunk_size, total_pages)
            print(f"\n   > Processing Sheaf Patch {patch_id} (Pages {current_idx}-{end_idx})...")
            
            text_block = ""
            for i in range(current_idx, end_idx):
                text_block += reader.pages[i].extract_text() + "\n"
            
            entity_limit = self.chunk_size * 3
            local_ents = featurizer.extract_entities(text_block, limit=entity_limit)
            local_mat, _ = featurizer.build_association_matrix(text_block, local_ents)
            
            local_adelic = mapper.compute_mappings(local_mat, local_ents)
            
            solver = SheafSolver(primes=[3, 5, 7])
            patch_map = solver.solve(local_mat, local_ents, self.global_anchors, local_adelic)
            
            for term, vec in patch_map.items():
                for p, coord in vec.items():
                    self.term_history[term][p].append(coord)
            
            self.splines.append({
                'id': patch_id,
                'range': (current_idx, end_idx),
                'map': patch_map, 
                'terms': len(patch_map)
            })
            
            current_idx += stride
            patch_id += 1
            
        self.analyze_stability()
        self.export_sheaf_json()
        return self.report()
        
    def analyze_stability(self):
        """
        V.14 Goldilocks Filter:
        Combines Energy (Curvature) and Frequency to classify terms.
        """
        print("\n   > Phase 3: Analyzing Stability (Goldilocks Filter)...")
        
        all_energies = []
        all_freqs = []
        
        # 1. Calculate Raw Metrics
        temp_metrics = {}
        for term, prime_histories in self.term_history.items():
            # Frequency: Max patches appeared in
            freq = max(len(coords) for coords in prime_histories.values())
            
            # Energy: Spline Curvature
            total_energy = 0.0
            primes_counted = 0
            for p, coords in prime_histories.items():
                if len(coords) < 3: continue
                primes_counted += 1
                energy = 0.0
                for i in range(len(coords)-2):
                    v1 = coords[i+1] - coords[i]
                    v2 = coords[i+2] - coords[i+1]
                    energy += abs(v2 - v1)
                total_energy += energy / (len(coords)-2)
            
            avg_energy = total_energy / max(1, primes_counted)
            
            temp_metrics[term] = (avg_energy, freq)
            if primes_counted > 0: # Only count terms with energy history for stats
                all_energies.append(avg_energy)
                all_freqs.append(freq)
                
        # 2. Derive Thresholds
        if not all_freqs: # Safety
            avg_freq = 0
        else:
            avg_freq = sum(all_freqs) / len(all_freqs)
            
        print(f"     > Average Frequency: {avg_freq:.2f} patches")
        
        # 3. Classify
        # SCAFFOLDING: Low Energy (Stable) BUT High Frequency (Ubiquitous) -> "Rice University"
        # NOISE: High Energy (Unstable)
        # CONCEPT: Goldilocks (Stable enough, Contextual enough)
        
        for term, (energy, freq) in temp_metrics.items():
            self.term_curvature[term] = energy # Keep raw metric
            
            classification = "CONCEPT"
            
            # Heuristics
            if energy > 100.0:
                classification = "NOISE"
            elif energy < 5.0 and freq > (avg_freq * 1.5):
                # Extremely stable and very common -> Scaffolding (Boilerplate)
                classification = "SCAFFOLDING"
            elif energy < 5.0 and freq < (avg_freq * 0.5):
                 # Extremely stable but very rare -> Maybe 'Fixed Constant' or 'Snippet'? 
                 # Let's keep as Concept for now, or "Weak".
                 pass
                 
            self.term_classification[term] = classification

    def report(self):
        print("\n--- [Phase 4: Skeptical Audit V.14] ---")
        
        print("   > Goldilocks Classification Report:")
        counts = Counter(self.term_classification.values())
        for k, v in counts.items():
            print(f"     - {k}: {v} terms")
            
        print("\n   > Scaffolding Detection (Expect 'Rice University' here):")
        scaffold_terms = [t for t, c in self.term_classification.items() if c == "SCAFFOLDING"]
        for t in scaffold_terms[:10]:
            print(f"     - {t} (E={self.term_curvature[t]:.2f})")
            
        if "Rice University" in self.term_classification:
            print(f"\n   > 'Rice University' Status: {self.term_classification['Rice University']}")
        else:
            print(f"\n   > 'Rice University' Not Found in Classification.")

        return self.splines

    def export_sheaf_json(self, filename="sandbox/sheaf_data.json"):
        print(f"\n   > Exporting Sheaf Data: {filename}...")
        
        data = {
            "splines": [],
            "curvature": self.term_curvature,
            "classification": self.term_classification
        }
        
        for s in self.splines:
            data["splines"].append({
                "id": s['id'],
                "range": s['range'],
                "map": s['map']
            })
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    base_path = "d:/Dropbox/logic-miner-engine/"
    # Target specific PDF
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    
    if not os.path.exists(pdf_path):
        # Fallback for generic test env
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    manifold = SheafManifold(chunk_size=10, overlap=0.5)
    try:
        manifold.run_pipeline(pdf_path, max_pages=100) # Run 100 pages for rapid Consensus test
    except Exception as e:
        print(f"Execution Error: {e}")
