
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
        # print(f"     > Adelic Map: Projecting {n} entities to Product Space (p=3,5,7)...")
        
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
                    # FIX: Initialize to 0 or Neutral, avoids random noise injecting false variance
                    current[e] = 0
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
    Protocol V.15 Manager (Skeptical Experiment)
    Features:
    - Polysemy Detection (Sheaf Blow-Up)
    - Distinguishing Noise vs Multi-Concept
    """
    def __init__(self, chunk_size=10, overlap=0.5):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.global_anchors = {} 
        self.splines = [] 
        self.term_history = defaultdict(lambda: {3:[], 5:[], 7:[]}) 
        self.term_curvature = {}
        self.term_classification = {} 
        self.polysemy_map = {} # {term: [cluster_centers...]}
        
    def run_pipeline(self, pdf_path, max_pages=None):
        print(f"--- [Protocol V.15: Skeptical Experiment] ---")
        
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
            sys.stdout.write(f"\r   > Processing Patch {patch_id} (Pages {current_idx}-{end_idx})...")
            sys.stdout.flush()
            
            text_block = ""
            for i in range(current_idx, end_idx):
                text_block += reader.pages[i].extract_text() + "\n"
            
            entity_limit = self.chunk_size * 3
            local_ents = featurizer.extract_entities(text_block, limit=entity_limit)
            local_mat, _ = featurizer.build_association_matrix(text_block, local_ents)
            
            local_adelic = mapper.compute_mappings(local_mat, local_ents)
            
            solver = SheafSolver(primes=[3, 5, 7])
            patch_map = solver.solve(local_mat, local_ents, self.global_anchors, local_adelic)
            
            # Record Interactions for Polysemy Check? 
            # Ideally we check *neighbors*, but sticking to algebra: check Coordinates.
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
            
        print("\n   > Patch Processing Complete.")
        self.analyze_polysemy()
        return self.report()
        
    def analyze_polysemy(self):
        """
        V.15 Theorizer Hypothesis:
        - Noise = High Variance, No Clusters (Uniform Distribution)
        - Polysemy = High Variance, Distinct Clusters (Bi-Modal Distribution)
        
        We iterate history for p=3 (Physics) and p=5 (Chemistry).
        If history shows gaps > Threshold, we separate.
        """
        print("\n   > Phase 3: Sheafification (Polysemy Blow-Up)...")
        
        # Threshold: How far apart must coords be to be "Different Concepts"?
        # Coordinate Space is roughly 0-4096 (12 bits) or similar.
        # Let's say 10% of space.
        GAP_THRESHOLD = 500 
        
        for term, prime_histories in self.term_history.items():
            # Check p=5 (Chemistry) especially
            for p in [3, 5]:
               history = sorted(prime_histories[p])
               if len(history) < 4: continue
               
               # Simple 1D Clustering (Gap Detection)
               clusters = []
               current_cluster = [history[0]]
               
               for i in range(1, len(history)):
                   diff = history[i] - history[i-1]
                   if diff > GAP_THRESHOLD:
                       # Split
                       clusters.append(current_cluster)
                       current_cluster = [history[i]]
                   else:
                       current_cluster.append(history[i])
               clusters.append(current_cluster)
               
               # Analyze Clusters
               if len(clusters) > 1:
                   # Check stability of clusters (Size > 1)
                   stable_clusters = [c for c in clusters if len(c) >= 2]
                   
                   if len(stable_clusters) >= 2:
                       # POLYSEMY DETECTED
                       # Distinct stable meanings in fiber p
                       centers = [int(sum(c)/len(c)) for c in stable_clusters]
                       self.polysemy_map[term] = self.polysemy_map.get(term, {})
                       self.polysemy_map[term][p] = centers
                       self.term_classification[term] = f"POLYSEMY (p={p})"

    def report(self):
        print("\n--- [Phase 4: Skeptical Report V.15] ---")
        
        print("   > Polysemy Detection Results:")
        if not self.polysemy_map:
            print("     (No Polysemy Detected - Terms are Mono-semantic or Noise)")
        else:
            for term, p_map in self.polysemy_map.items():
                print(f"     > Term '{term}':")
                for p, centers in p_map.items():
                    print(f"       - Fiber p={p}: Split into {len(centers)} Concepts at {centers}")
                    
        # Check 'Energy' explicitly
        if "Energy" in self.polysemy_map:
            print(f"\n   > SUCCESS: 'Energy' was successfully blown up.")
        else:
            print(f"\n   > FAILURE: 'Energy' remained singular.")
            # Debug info for Energy
            if "Energy" in self.term_history:
                hist = self.term_history["Energy"][3]
                print(f"     DEBUG: Energy p=3 History: {hist}")
                hist5 = self.term_history["Energy"][5]
                print(f"     DEBUG: Energy p=5 History: {hist5}")

        return self.polysemy_map

if __name__ == "__main__":
    base_path = "d:/Dropbox/logic-miner-engine/"
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    
    if not os.path.exists(pdf_path):
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    manifold = SheafManifold(chunk_size=15, overlap=0.2)
    try:
        manifold.run_pipeline(pdf_path, max_pages=150) # Run slightly more to capture drift
    except Exception as e:
        print(f"Execution Error: {e}")
