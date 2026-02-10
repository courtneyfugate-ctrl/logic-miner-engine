
from .serial_synthesis_v33 import SerialSynthesizerV33
from collections import defaultdict, Counter
import math

class SerialSynthesizerV34(SerialSynthesizerV33):
    """
    Protocol V.34: The Refined Ontology Extractor.
    Extends V.33 with:
    1. Matrix Momentum (Spline Continuity)
    2. Grammar Suppression (Curvature-Weighted Adjacency)
    """
    def __init__(self, chunk_size=50, momentum=0.3):
        super().__init__(chunk_size=chunk_size)
        self.momentum = momentum
        self.prev_matrix_state = {} # Key -> row dict or similar? 
        # Since matrix is dense list-of-lists for a specific candidate set, 
        # and candidate sets CHANGE every block, strict element-wise momentum is hard.
        #
        # Implementation Strategy for Sparse/Dynamic Momentum:
        # Maintain a 'Global Adjacency Memory' (Start with empty).
        # When building Block N matrix:
        #   1. Build raw matrix for current candidates.
        #   2. Add (momentum * memory_value) to (current_value).
        #   3. Update memory with new blended value.
        
        self.global_adjacency_memory = defaultdict(float) # (termA, termB) -> weight
        
        # Curvature History for Suppression
        # Defined in V33 as self.history[p][e] -> [coords]
        
    def _calculate_dynamic_curvature(self, entity):
        # Calculate curvature based on current history across all primes
        total_k = 0
        count = 0
        for p in self.primes:
            traj = self.history[p].get(entity, [])
            if len(traj) < 3: continue
            
            # Just look at last 5 steps for local volatility?
            # Or global? Let's use last 5 steps to be responsive.
            snippet = traj[-5:]
            if len(snippet) < 3: continue
            
            k = 0
            for i in range(1, len(snippet)-1):
                 k += abs(snippet[i+1] - 2*snippet[i] + snippet[i-1])
            total_k += k
            count += 1
            
        if count == 0: return 0.0
        return total_k / count # Average curvature per field

    def _process_block(self, text):
        # 1. Featurize
        candidates = self.featurizer.extract_entities(text, limit=400)
        if not candidates: return
        
        # Update Freqs (V33 logic)
        _, counts_raw, _ = self.featurizer.build_association_matrix(text, candidates)
        for c in candidates:
            self.global_freqs[c] += counts_raw.get(c.replace(" ", "_"), 0)
            
        # 2. Grammar Suppression (Pre-Matrix Weighting)
        # Identify Parasites based on History
        suppression_map = {}
        for c in candidates:
            k = self._calculate_dynamic_curvature(c)
            # If K is high, suppress.
            # E.g. K > 5.0 -> weight *= 0.1
            if k > 5.0:
                suppression_map[c] = 0.1
                # print(f"   [Suppress] {c} (K={k:.1f})")
            else:
                suppression_map[c] = 1.0
                
        # 3. Build & Blend Matrix (Momentum)
        # We need to construct the matrix manually to inject momentum?
        # TextFeaturizer builds it from scratch.
        # Let's get the raw matrix first.
        
        # We use the purified candidates logic from V33 for efficiency
        # Sort by local counts
        local_cands = sorted(candidates, key=lambda x: counts_raw.get(x.replace(" ", "_"), 0), reverse=True)[:100]
        c_map = {c: i for i, c in enumerate(local_cands)}
        
        raw_matrix, local_counts, _ = self.featurizer.build_association_matrix(text, local_cands)
        
        # Apply Momentum & Suppression
        # New Matrix size is len(local_cands) x len(local_cands)
        
        blended_matrix = []
        for i, row_term in enumerate(local_cands):
            new_row = []
            suppress_i = suppression_map.get(row_term, 1.0)
            
            for j, col_term in enumerate(local_cands):
                raw_val = raw_matrix[i][j]
                
                # Retrieve Memory
                pair_key = tuple(sorted((row_term, col_term)))
                mem_val = self.global_adjacency_memory.get(pair_key, 0.0)
                
                # Blend
                # val = (1 - alpha) * raw + alpha * memory
                # But memory only exists if seen before.
                # If mem_val is 0, it's just raw.
                
                final_val = (1.0 - self.momentum) * raw_val + self.momentum * mem_val
                
                # Apply Suppression (Grammar Filter)
                # If either term is a parasite, weaken the link.
                suppress_j = suppression_map.get(col_term, 1.0)
                final_val *= (suppress_i * suppress_j)
                
                # Update Memory (Store the BLENDED value? or the RAW value? 
                # Usually momentum carries the blended state.)
                if final_val > 0.001:
                    self.global_adjacency_memory[pair_key] = final_val
                
                new_row.append(final_val)
            blended_matrix.append(new_row)
            
        # 4. Multi-Adelic Solving (V33 logic with new matrix)
        for p in self.primes:
            res = self.solvers[p].solve(blended_matrix, local_cands, local_counts)
            coords = res['coordinates']
            
            # Record Trajectory
            for e, c in coords.items():
                self.history[p][e].append(c)
