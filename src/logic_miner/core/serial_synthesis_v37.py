
from .serial_synthesis_v36 import SerialSynthesizerV36
import math
import statistics

class SerialSynthesizerV37(SerialSynthesizerV36):
    """
    Protocol V.37: Topological Filter Cycle.
    Extends V.36 (Flow Conservation) with Structural Sediment Filtering.
    
    Hypothesis: 
    - Concepts (Hubs) have High Clustering Coefficient (Cliques).
    - Scaffolding (Bridges) have Low Clustering Coefficient (Star/Line).
    """
    def __init__(self, chunk_size=50, momentum=0.3, resolution=0.5):
        super().__init__(chunk_size=chunk_size, momentum=momentum, resolution=resolution)

    def _calculate_clustering_coefficients(self, matrix, candidates):
        """
        Calculates Local Clustering Coefficient (Ci) for each node.
        Ci = 2 * E_neighbors / (k * (k-1))
        """
        n = len(matrix)
        clustering_coeffs = {}
        
        for i in range(n):
            # 1. Identify Neighbors
            neighbors = [j for j, w in enumerate(matrix[i]) if w > 0 and i != j]
            k = len(neighbors)
            
            if k < 2:
                clustering_coeffs[candidates[i]] = 0.0
                continue
                
            # 2. Count Edges between Neighbors
            edges_between_neighbors = 0
            for x_idx in range(len(neighbors)):
                u = neighbors[x_idx]
                for y_idx in range(x_idx + 1, len(neighbors)):
                    v = neighbors[y_idx]
                    
                    if matrix[u][v] > 0:
                        edges_between_neighbors += 1
                        
            # 3. Calculate Ci
            possible_edges = k * (k - 1) / 2
            if possible_edges > 0:
                Ci = edges_between_neighbors / possible_edges
            else:
                Ci = 0.0
                
            clustering_coeffs[candidates[i]] = Ci
            
        return clustering_coeffs

    def _apply_topological_filter(self, matrix, candidates):
        """
        Filters 'Sediment' by suppressing nodes with Low Clustering Coefficient.
        """
        # 1. Calculate Ci
        c_coeffs = self._calculate_clustering_coefficients(matrix, candidates)
        values = list(c_coeffs.values())
        
        if not values: return matrix
        
        # 2. Compute Statistics
        mean_c = statistics.mean(values)
        stdev_c = statistics.stdev(values) if len(values) > 1 else 0.0
        
        # 3. Define Threshold (Sediment Boundary)
        # Hypothesis: Bridges are < Mean - 1*StdDev
        threshold = mean_c - (1.0 * stdev_c)
        # Ensure threshold is reasonable (e.g., not negative if distribution is tight)
        threshold = max(threshold, 0.0)
        
        # 4. Apply Mask (Viscosity)
        # We modify the matrix in-place or create a copy? 
        # Safest to create a copy, but let's modify the row/col weights.
        # Actually, V34/36 logic creates 'blended_matrix' in _process_block.
        # We need to intercept that.
        
        # Since I cannot easily intercept `_process_block` local variable `blended_matrix` 
        # without rewriting the whole method, I will accept that I must Copy-Paste `_process_block` implementation.
        # This is the trade-off for inheritance modification of local logic.
        pass # Only a helper, logic is in process_block
        
        return c_coeffs, threshold

    def _process_block(self, text):
        # We Must Rewrite _process_block to inject the Filter between Matrix Build and Solve.
        
        # 1. Featurize
        candidates = self.featurizer.extract_entities(text, limit=400)
        if not candidates: return
        
        # Update Global Freqs
        _, counts_raw, _ = self.featurizer.build_association_matrix(text, candidates)
        for c in candidates:
            self.global_freqs[c] += counts_raw.get(c.replace(" ", "_"), 0)
            
        # 2. Grammar Suppression (Pre-Matrix)
        # (Recalculate dynamic curvature for suppression)
        suppression_map = {}
        for c in candidates:
            k = self._calculate_dynamic_curvature(c)
            if k > 5.0:
                suppression_map[c] = 0.1
            else:
                suppression_map[c] = 1.0

        # 3. Build & Blend Matrix (Momentum)
        local_cands = sorted(candidates, key=lambda x: counts_raw.get(x.replace(" ", "_"), 0), reverse=True)[:100]
        
        # Re-build matrix for local cands
        raw_matrix, local_counts, _ = self.featurizer.build_association_matrix(text, local_cands)
        
        blended_matrix = []
        for i, row_term in enumerate(local_cands):
            new_row = []
            suppress_i = suppression_map.get(row_term, 1.0)
            
            for j, col_term in enumerate(local_cands):
                raw_val = raw_matrix[i][j]
                pair_key = tuple(sorted((row_term, col_term)))
                mem_val = self.global_adjacency_memory.get(pair_key, 0.0)
                
                final_val = (1.0 - self.momentum) * raw_val + self.momentum * mem_val
                suppress_j = suppression_map.get(col_term, 1.0)
                final_val *= (suppress_i * suppress_j)
                
                if final_val > 0.001:
                    self.global_adjacency_memory[pair_key] = final_val
                
                new_row.append(final_val)
            blended_matrix.append(new_row)
            
        # --- V.37 INJECTION: TOPOLOGICAL FILTER ---
        # 4. Calculate Ci & Apply Viscosity Mask
        c_coeffs = self._calculate_clustering_coefficients(blended_matrix, local_cands)
        if c_coeffs:
            values = list(c_coeffs.values())
            mean_c = statistics.mean(values)
            stdev_c = statistics.stdev(values) if len(values) > 1 else 0.0
            threshold = max(mean_c - (1.0 * stdev_c), 0.0) # V.37 Tuning: 1 Sigma
            
            # Apply Mask to Matrix
            for i, row_term in enumerate(local_cands):
                Ci = c_coeffs.get(row_term, 0.0)
                
                # If Sediment (Bridge), suppress connections
                if Ci < threshold:
                    # print(f"   [Sediment] {row_term} (Ci={Ci:.2f} < {threshold:.2f})")
                    for j in range(len(local_cands)):
                         # Weaken outgoing/incoming edges -> Viscosity
                         blended_matrix[i][j] *= 0.1 # Viscosity Factor
                         # Symmetry handle? The loop will hit matrix[j][i] later.
                         
        # 5. Solve (V.36 Flow Balanced)
        for p in self.primes:
            res = self.solvers[p].solve(blended_matrix, local_cands, local_counts)
            coords = res['coordinates']
            
            # Record Trajectory (Same as V34/35/36)
            for e, c in coords.items():
                self.history[p][e].append(c)
