
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
            # print(f"       > Projecting Prime p={p}...")
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
        """
        fixed_anchors: {term: {p: coord}}
        initial_adelic_map: {term: {p: coord}} (From Adelic Map)
        Returns: {term: {p: refined_coord}}
        """
        refined_map = defaultdict(dict)
        
        # Solve each prime independenty
        for p in self.primes:
            # Extract Single-Prime Problem
            p_anchors = {}
            for term, vec in fixed_anchors.items():
                if p in vec: p_anchors[term] = vec[p]
                
            p_initial = {}
            for term, vec in initial_adelic_map.items():
                if p in vec: p_initial[term] = vec[p]
                
            # Run 1D Solver logic (Simulated Hill Climbing)
            p_solved = self._solve_fiber(matrix, entities, p_anchors, p_initial, p)
            
            # Merge back
            for term, coord in p_solved.items():
                refined_map[term][p] = coord
                
        return refined_map
        
    def _solve_fiber(self, matrix, entities, anchors, hints, p):
        # Similar to V.11 Solver but for one prime axis
        current = {}
        variables = []
        
        # Init
        for e in entities:
            if e in anchors:
                current[e] = anchors[e]
            else:
                if e in hints:
                    current[e] = hints[e] * p # Spread by prime factor?
                else:
                    current[e] = random.randint(1, 1000)
                variables.append(e)
                
        ent_to_idx = {e: i for i,e in enumerate(entities)}
        
        # Optimize (Simple Relaxation)
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
    Protocol V.13 Manager
    """
    def __init__(self, chunk_size=10, overlap=0.5):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.global_anchors = {} # {term: {3:x, 5:y, 7:z}}
        self.splines = [] 
        self.term_history = defaultdict(lambda: {3:[], 5:[], 7:[]}) # Track trajectory for Curvature
        
    def run_pipeline(self, pdf_path, max_pages=None):
        print(f"--- [Protocol V.13: Sheaf Manifold Synthesis] ---")
        
        print("   > Phase 0: Constituting Adelic Global Anchors...")
        featurizer = TextFeaturizer()
        
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        if max_pages: total_pages = min(total_pages, max_pages)
            
        full_text_sample = ""
        for i in range(0, total_pages, 5):
             full_text_sample += reader.pages[i].extract_text() + "\n"
             
        global_ents = featurizer.extract_entities(full_text_sample)
        anchor_terms = global_ents[:50] # Top 50
        
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
            
            # Dynamic Limit
            entity_limit = self.chunk_size * 3
            local_ents = featurizer.extract_entities(text_block, limit=entity_limit)
            local_mat, _ = featurizer.build_association_matrix(text_block, local_ents)
            
            # Adelic Map
            local_adelic = mapper.compute_mappings(local_mat, local_ents)
            
            # Solve Sheaf
            solver = SheafSolver(primes=[3, 5, 7])
            patch_map = solver.solve(local_mat, local_ents, self.global_anchors, local_adelic)
            
            # Record History for Curvature
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
            
        self.calculate_curvature()
        self.export_sheaf_json()
        return self.report()
        
    def calculate_curvature(self):
        print("\n   > Phase 3: Calculating Spline Curvature (Energy)...")
        self.term_curvature = {} # {term: energy (avg across primes)}
        
        for term, prime_histories in self.term_history.items():
            total_energy = 0.0
            
            for p, coords in prime_histories.items():
                if len(coords) < 3: 
                    # Not enough points for curvature (need 3 for 2nd derivative)
                    continue
                    
                energy = 0.0
                for i in range(len(coords)-2):
                    v1 = coords[i+1] - coords[i]
                    v2 = coords[i+2] - coords[i+1]
                    accel = abs(v2 - v1)
                    energy += accel
                
                # Normalize by length
                total_energy += energy / (len(coords)-2)
            
            # Average across primes
            self.term_curvature[term] = total_energy / 3.0
            
    def report(self):
        print("\n--- [Phase 4: Skeptical Audit] ---")
        
        # 1. Curvature Analysis
        print("   > Curvature Filter Report:")
        sorted_curv = sorted(self.term_curvature.items(), key=lambda x: x[1])
        
        print("     > Top 5 Stable Terms (Invariant Laws):")
        for t, e in sorted_curv[:5]:
             print(f"       - {t}: Energy={e:.2f}")
             
        print("     > Top 5 Unstable Terms (Contextual Noise):")
        for t, e in sorted_curv[-5:]:
             print(f"       - {t}: Energy={e:.2f}")
             
        # 2. Rice University Check
        print("\n   > Isolation Audit ('Rice University'):")
        rice_found = False
        rice_p5_roots = 0
        
        # Check specific patch maps for Rice in p=5 roots
        for s in self.splines:
            if "Rice University" in s['map']:
                vec = s['map']["Rice University"]
                # Is it a root in p=5? (Not divisible by 5)
                # Actually, root means coord % p != 0 (Valuation 0)
                # If Rice is in Chemistry Tree (p=5), it should be DEEP (Valuation > 0) to be a child?
                # Or if it floats, it has low valuation?
                # The User said: "Rice University will likely vanish or appear only in the 7-tree"
                # "Dead end node that divides nothing"
                pass
                
        # Just check Adelic Classification
        # Inspect p=3, p=5, p=7 coords for "Rice University" vs "Atom"
        
        targets = ["Rice University", "Atom", "Matter"]
        for t in targets:
            if t in self.term_history:
                 # Get last known coord
                 last_vec = {p: self.term_history[t][p][-1] for p in [3,5,7] if self.term_history[t][p]}
                 print(f"     > {t}: {last_vec}")
                 
        return self.splines

    def export_sheaf_json(self, filename="sandbox/sheaf_data.json"):
        print(f"\n   > Exporting Sheaf Data: {filename}...")
        
        data = {
            "splines": [],
            "curvature": self.term_curvature
        }
        
        for s in self.splines:
            # Flatten map for JSON? or keep nested?
            # Let's keep nested: map: {Term: {3:123, 5:456}}
            data["splines"].append({
                "id": s['id'],
                "range": s['range'],
                "map": s['map']
            })
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    # Test Run
    base_path = "d:/Dropbox/logic-miner-engine/"
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    
    # If sample doesn't exist (it might not in test env?), try to find one
    # Assuming standard test file exists
    
    if not os.path.exists(pdf_path):
        # Fallback to creating a dummy or checking location
        # The user has chemistry audio dump, imply pdf exists?
        # Actually in previous steps I used PyPDF on a path?
        # Re-check where I got text before?
        # Ah, I see `test_v11_chemistry.py` used `d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf` or similar?
        # I'll check file list.
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    manifold = SheafManifold(chunk_size=10, overlap=0.5)
    # If PDF not found, this will crash. I should be careful. 
    # But for now, let's write the code. I can fix path later.
    try:
        manifold.run_pipeline(pdf_path, max_pages=100)
    except Exception as e:
        print(f"Execution Error: {e}")
