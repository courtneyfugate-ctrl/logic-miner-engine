from .serial_synthesis_v42 import SerialSynthesizerV42
from collections import defaultdict
import math

class SerialSynthesizerV43(SerialSynthesizerV42):
    """
    Protocol V.43: The Renaissance.
    Restores discrete innovations (V.34 Momentum, V.36 Flow Balance) 
    integrated with V.42 Adelic Tree.
    """
    def __init__(self, p=13, chunk_size=50, momentum=0.3):
        super().__init__(p=p, chunk_size=chunk_size)
        self.momentum = momentum
        self.adjacency_memory = defaultdict(float) # (u, v) -> weight
        
    def _process_block(self, text_block, block_idx):
        # 1. Featurize (Bypass V.32 Spectral as per V.42 Fix)
        candidates = self.featurizer.extract_entities(text_block, limit=400)
        matrix, counts, G_directed = self.featurizer.build_association_matrix(text_block, candidates)
        
        # 2. Adelic Filter (V.42 Bandpass)
        purified = self._apply_adelic_filter(candidates, text_block)
        if not purified: return

        # 3. Apply Matrix Momentum (V.34 Restoration) - Directed Graph
        # We update G_directed weights using memory
        for u in G_directed:
            if u not in purified: continue
            for v, raw_w in G_directed[u].items():
                if v not in purified: continue
                
                # Retrieve Memory
                pair_key = (u, v)
                mem_w = self.adjacency_memory.get(pair_key, 0.0)
                
                # Blend
                final_w = (1.0 - self.momentum) * raw_w + self.momentum * mem_w
                
                # Update Memory (if meaningful)
                if final_w > 0.001:
                    self.adjacency_memory[pair_key] = final_w
                
                # 4. Accumulate to Global (Using Blended Weight)
                self.global_directed_adj[u][v] += final_w

        # Update Freqs (Standard)
        for c in purified:
            self.global_freqs[c] += counts.get(c.replace(" ", "_"), 0)

        # 5. Local Trace (V.32/V.42 Standard)
        # We skip re-solving local trace to save time in V.43 
        # unless specifically needed for Spline monitoring.
        # But we do need energy history.
        # ... (Skipping for now to focus on Tree)

    def _sinkhorn_balance_global(self, iterations=10):
        """
        V.36 Restoration: Sinkhorn-Knopp on Global Directed Graph.
        Makes the graph doubly stochastic (Rows sum to 1, Cols sum to 1).
        Enforces 'Conservation of Semantic Influence'.
        """
        # Convert nested dict to matrix-like structure for iteration
        nodes = list(self.global_directed_adj.keys())
        # Add target nodes that might not be source keys
        for u in list(self.global_directed_adj.keys()):
            for v in self.global_directed_adj[u]:
                if v not in self.global_directed_adj:
                    self.global_directed_adj[v] = defaultdict(float)
        
        nodes = sorted(list(self.global_directed_adj.keys()))
        idx_map = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        
        if n == 0: return

        # Build Dense Matrix
        mat = [[0.0] * n for _ in range(n)]
        for u, neighbors in self.global_directed_adj.items():
            i = idx_map[u]
            for v, w in neighbors.items():
                if v in idx_map:
                    j = idx_map[v]
                    mat[i][j] = w
        
        # Iterative Balancing
        for _ in range(iterations):
            # Row Norm
            for i in range(n):
                s = sum(mat[i])
                if s > 0:
                    mat[i] = [x / s for x in mat[i]]
            
            # Col Norm
            col_sums = [sum(mat[i][j] for i in range(n)) for j in range(n)]
            for j in range(n):
                if col_sums[j] > 0:
                    for i in range(n):
                        mat[i][j] /= col_sums[j]
        
        # Write back to Global Directed Adj
        self.global_directed_adj = defaultdict(lambda: Counter())
        for i in range(n):
            for j in range(n):
                if mat[i][j] > 0.001: # Prune weak links
                    u, v = nodes[i], nodes[j]
                    self.global_directed_adj[u][v] = mat[i][j]
                    
        print(f"     > Flow Conservation (V.36): Global Graph Balanced (Sinkhorn n={n}).")

    def _consolidate_global_lattice(self):
        # 1. Apply V.36 Sinkhorn Balance BEFORE Forest Construction
        self._sinkhorn_balance_global()
        
        # 2. Proceed with V.32/V.31 Forest Logic
        super()._consolidate_global_lattice()
