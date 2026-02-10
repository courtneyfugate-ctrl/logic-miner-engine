from .serial_synthesis import SerialManifoldSynthesizer
from .algebraic_text import AlgebraicTextSolver
from collections import defaultdict, Counter
import math
import numpy as np

class SerialSynthesizerV45(SerialManifoldSynthesizer):
    """
    Protocol V.45: The Curvature Model.
    Replaces continuous smoothing with Discrete Curvature Thresholding.
    Logic:
    - Grammar/Noise = Flat Trajectory (K ~ 0).
    - Concepts = Spiky Trajectory (K >> 0).
    """
    def __init__(self, p=13, chunk_size=50):
        super().__init__(p=p, chunk_size=chunk_size)
        
        # Trajectory History for Curvature Calculation
        # Key: Term -> List of Coordinates [c1, c2, c3...]
        self.trajectory_history = defaultdict(list)
        
    def _calculate_discrete_curvature(self, coords):
        """
        Computes the Total Discrete Curvature (L1 Norm of 2nd Difference).
        K = Sum |x_{t+1} - 2x_t + x_{t-1}|
        """
        if len(coords) < 3: return 0.0
        
        k_total = 0.0
        for i in range(1, len(coords)-1):
            val = abs(coords[i+1] - 2*coords[i] + coords[i-1])
            k_total += val
            
        # Normalize by length to get "Average Jaggedness"
        if len(coords) - 2 == 0: return 0.0
        return k_total / (len(coords) - 2)

    def _process_block(self, text_block, block_idx):
        # 1. Featurize
        candidates = self.featurizer.extract_entities(text_block, limit=400)
        # 2. Build Matrix
        matrix, counts, G_directed = self.featurizer.build_association_matrix(text_block, candidates)
        if not candidates: return

        # 3. Compute Local Coordinates for Trajectory
        # We solve broadly here purely to measure curvature
        solver = AlgebraicTextSolver(p=self.p)
        try:
            # We bypass spectral purification for the trajectory check
            # We solve on ALL candidates to see who is Grammar and who is Concept
            res = solver.solve(matrix, candidates, counts)
            block_coords = res['coordinates']
        except Exception as e:
            # print(f"Warning: Block Solve Failed: {e}")
            block_coords = {}
            
        # 4. Update Trajectories
        # If a term is missing in this block, we append None or 0? 
        # Better to only track *active* appearances.
        for term, coord in block_coords.items():
            self.trajectory_history[term].append(coord)
            
        # 5. Filter by Curvature (V.45 Logic)
        purified = []
        
        for term in candidates:
            # Only consider terms we have coordinates for
            traj = self.trajectory_history.get(term, [])
            
            # Grace Period: First 3 observations are free
            if len(traj) < 3:
                # Basic Stopword filter just in case
                if term not in ["Introduction", "Chapter", "Section"]: 
                    purified.append(term)
                continue
                
            k = self._calculate_discrete_curvature(traj)
            
            # Threshold: K > 0.5 (Any deviation from linear drift)
            # Grammar tends to have K=0 (Linear progression or Constant)
            if k > 0.5: 
                purified.append(term)
                # print(f" [Keep] {term} (K={k:.2f})")
            # else:
                # print(f" [Drop] {term} (K={k:.2f})")

        if not purified: return

        # 6. Accumulate Global Stats (V.32 Core) for Purified Terms
        for i, c1 in enumerate(purified):
            self.global_freqs[c1] += counts.get(c1.replace(" ", "_"), 0)
            
            # Update Directed Graph (for V.41/V.44 compat)
            if c1 in G_directed:
                for c2, w in G_directed[c1].items():
                    if c2 in purified:
                        self.global_directed_adj[c1][c2] += w
                        
            # Update Symmetric Global Adj
            try:
                # Re-map indices from original candidates list
                if c1 in candidates:
                    idx1 = candidates.index(c1)
                    for c2 in purified:
                        if c1 == c2: continue
                        if c2 in candidates:
                            idx2 = candidates.index(c2)
                            w = matrix[idx1][idx2]
                            if w > 0:
                                pair = tuple(sorted((c1, c2)))
                                self.global_adj[pair] = self.global_adj.get(pair, 0) + w
            except ValueError:
                pass

    def _consolidate_global_lattice(self):
        # 1. Proceed with V.32 Forest Logic
        # We rely on the populated global_adj
        super()._consolidate_global_lattice()
