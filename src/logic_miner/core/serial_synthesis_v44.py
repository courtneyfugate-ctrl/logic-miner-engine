from .serial_synthesis_v42 import SerialSynthesizerV42
from collections import defaultdict
import math
import numpy as np

class SerialSynthesizerV44(SerialSynthesizerV42):
    """
    Protocol V.44: The Diffusion Model.
    Restores Discrete Momentum (V.34) and adds Vladimirov Diffusion (V.41)
    to distinguish Hubs from Artifacts via Spectral Analysis.
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
        for u in G_directed:
            if u not in purified: continue
            for v, raw_w in G_directed[u].items():
                if v not in purified: continue
                
                # Retrieve Memory
                pair_key = (u, v)
                mem_w = self.adjacency_memory.get(pair_key, 0.0)
                
                # Blend
                final_w = (1.0 - self.momentum) * raw_w + self.momentum * mem_w
                
                # Update Memory
                if final_w > 0.001:
                    self.adjacency_memory[pair_key] = final_w
                
                # 4. Accumulate to Global
                self.global_directed_adj[u][v] += final_w
                
                # ALSO Update Symmetric Global Adj (Required for V.32 Lattice Logic)
                pair = tuple(sorted((u, v)))
                self.global_adj[pair] = self.global_adj.get(pair, 0) + final_w
                
        # Update Freqs
        for c in purified:
            self.global_freqs[c] += counts.get(c.replace(" ", "_"), 0)

    def _compute_vladimirov_spectrum(self):
        """
        Protocol V.41: Vladimirov Diffusion Analysis.
        Computes the Spectrum of the Combinatorial Laplacian L = D - A.
        Returns eigenvalues and eigenvectors to identify Hubs.
        """
        # Convert Directed Graph to Undirected for Laplacian
        nodes = sorted(list(self.global_directed_adj.keys()))
        n = len(nodes)
        if n < 2: return
        
        idx_map = {node: i for i, node in enumerate(nodes)}
        
        # Build Adjacency Matrix A (Symmetrized)
        A = np.zeros((n, n))
        for u in self.global_directed_adj:
            for v, w in self.global_directed_adj[u].items():
                if v in idx_map:
                    i, j = idx_map[u], idx_map[v]
                    A[i][j] += w
                    A[j][i] += w # Symmetrize
                    
        # Build Degree Matrix D
        D = np.diag(np.sum(A, axis=1))
        
        # Laplacian L = D - A
        L = D - A
        
        # Compute Eigenvalues
        try:
            # eigh for symmetric matrices
            vals, vecs = np.linalg.eigh(L)
            
            # Analyze Spectrum
            # lambda_0 is always 0. lambda_1 is Fiedler value (Algebraic Connectivity).
            # High lambda_max corresponds to "bipartite oscillations" or noise.
            # Low lambda (near 0) corresponds to smooth structural modes (Hubs/Clusters).
            
            print(f"     > Vladimirov Spectrum (V.41):")
            print(f"       Lambda_1 (Fiedler): {vals[1] if n>1 else 0:.4f}")
            print(f"       Lambda_Max: {vals[-1]:.4f}")
            
            # Identify Terms in the "Slow Mode" (Fiedler Vector)
            # Fiedler Vector partitions the graph.
            # Terms with extreme values in Fiedler Vector are "Poles".
            # Terms near 0 are "Bridges".
            
            fiedler_vec = vecs[:, 1] if n > 1 else np.zeros(n)
            
            # We can use this to filter, but V.42 Bandpass is already good.
            # We just log it for now as a "Spectral Quality Check".
            
            # Heuristic: Hubs tend to have centrality.
            # In spectral terms, they might be maximizing the Principal Eigenvector (of A, not L).
            # Let's check Principal Eigenvector of A (PageRank-ish).
            
            vals_A, vecs_A = np.linalg.eigh(A)
            principal_vec = vecs_A[:, -1] # Largest eigenvalue
            
            # Print Top 5 Hubs by Principal Eigenvector
            top_indices = np.argsort(np.abs(principal_vec))[-5:][::-1]
            print(f"       Top 5 Spectral Hubs (Principal Eigenvector):")
            for idx in top_indices:
                print(f"       - {nodes[idx]} ({principal_vec[idx]:.4f})")
                
        except Exception as e:
            print(f"     ! Spectral Analysis Failed: {e}")

    def _consolidate_global_lattice(self):
        # 1. Run Spectral Analysis (Diagnostic)
        self._compute_vladimirov_spectrum()
        
        # 2. Proceed with V.32 Forest Logic
        super()._consolidate_global_lattice()
