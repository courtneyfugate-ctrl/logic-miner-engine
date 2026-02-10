from .serial_synthesis_v46 import SerialSynthesizerV46
from .adelic import AdelicIntegrator
from .algebraic_text import AlgebraicTextSolver
from collections import defaultdict, Counter
import math
import numpy as np

class SerialSynthesizerV47(SerialSynthesizerV46):
    """
    Protocol V.47: The High-Res Lattice.
    Scales to 500+ terms using:
    - Base Processing: p=13 (for local compatibility)
    - Global Basis: Adelic Primorial M = 30,030 via CRT
    - Spectral Projection: Lambda < 0.5
    """
    def __init__(self, chunk_size=50):
        # We use p=13 for local processing (V.32/V.45/V.46 compatibility)
        super().__init__(p=13, chunk_size=chunk_size)
        self.adelic_integrator = AdelicIntegrator()
        # Full Basis for M=30030
        self.basis_primes = [2, 3, 5, 7, 11, 13]
        # Store Adelic Coordinates for CRT
        # Term -> Prime -> List of Local Coords
        self.adelic_coords = defaultdict(lambda: defaultdict(list))
        
    def _spectral_projection_filter(self, candidates):
        # ... (Same as before) ...
        nodes = sorted(candidates)
        n = len(nodes)
        if n < 2: return candidates
        
        idx_map = {node: i for i, node in enumerate(nodes)}
        A = np.zeros((n, n))
        for u in self.global_directed_adj:
            if u not in idx_map: continue
            for v, w in self.global_directed_adj[u].items():
                if v in idx_map:
                    i, j = idx_map[u], idx_map[v]
                    A[i][j] += w
                    A[j][i] += w
        
        D = np.diag(np.sum(A, axis=1))
        L = D - A
        
        try:
            # Eigen Decomposition
            vals, vecs = np.linalg.eigh(L)
            low_freq_indices = [i for i, val in enumerate(vals) if val < 0.5]
            if not low_freq_indices: return candidates
            
            node_energies = {}
            for i in range(n):
                energy = sum(vecs[i, k]**2 for k in low_freq_indices)
                node_energies[nodes[i]] = energy
                
            avg_energy = sum(node_energies.values()) / n
            threshold = avg_energy * 0.1 
            structure_terms = [node for node, e in node_energies.items() if e > threshold]
            
            print(f"       ! V.47 Spectral Projection: {len(low_freq_indices)} Modes (<0.5). Kept {len(structure_terms)}/{n} terms.")
            return structure_terms
        except:
            return candidates

    def _process_block(self, text_block, block_idx):
        # 1. Run V.46 Unified Pipeline (Featurize -> Curvature -> Complexity -> Global Graph)
        # This filters noise and populates global_adj/freqs/graph
        super()._process_block(text_block, block_idx)
        
        # 2. Collect Adelic Coordinates for Surviving Terms
        # We need coords in ALL basis primes to map to M=30030
        # V.46 might have filtered terms, so we only process those in Global Graph
        # Optimization: Only calculate for new terms or periodic refresh?
        # Let's calculate for ALL candidates in the block that survived V.46
        
        # Identify current survivors in this block (implicitly those in global_adj update)
        # But super() doesn't return them.
        # We can just re-check the candidates against global_freqs
        candidates = self.featurizer.extract_entities(text_block, limit=400)
        survivors = [c for c in candidates if c in self.global_freqs]
        
        if not survivors: return
        
        # Batch Solve for Basis Primes
        for p in self.basis_primes:
            # Skip p=13 if already done? (V.45 tracks trajectory in p=13)
            # Just redo for uniformity
            solver = AlgebraicTextSolver(p=p)
            try:
                # Build Matrix for this prime
                p_matrix, p_counts, _ = self.featurizer.build_association_matrix(text_block, survivors)
                res = solver.solve(p_matrix, survivors, p_counts)
                coords = res.get('coordinates', {})
                for t, c in coords.items():
                    self.adelic_coords[t][p].append(c)
            except:
                pass

    def _consolidate_global_lattice(self):
        print(f"     > V.47 Spectral Projection Filter (Lambda < 0.5)...")
        survivors = self._spectral_projection_filter(list(self.global_freqs.keys()))
        
        # Prune
        final_survivors = set(survivors)
        self.global_freqs = Counter({t: self.global_freqs[t] for t in survivors})
        
        new_adj = defaultdict(lambda: Counter())
        for u in self.global_directed_adj:
            if u in final_survivors:
                for v, w in self.global_directed_adj[u].items():
                    if v in final_survivors:
                        new_adj[u][v] = w
        self.global_directed_adj = new_adj
        
        # 2. CRT Mapping to M=30030
        print(f"     > Phase XIX: Primorial Mapping (M=30030) via CRT...")
        self.global_coordinates = {} 
        
        # Compute Averaged Coordinates per Prime -> Solve CRT
        map_count = 0
        for term in survivors:
            if term not in self.adelic_coords: continue
            
            # Prepare CRT Models
            models = []
            valid = True
            for p in self.basis_primes:
                coords = self.adelic_coords[term][p]
                if not coords:
                    valid = False
                    break
                # Use Mode or Mean? Discrete -> Mode is safer for integers
                avg_coord = Counter(coords).most_common(1)[0][0]
                models.append({'p': p, 'params': (avg_coord,), 'degree': 0})
            
            if not valid: continue
            
            # CRT
            res = self.adelic_integrator.solve_crt(models)
            if res:
                # Global Coordinate X in Z_30030
                X = res['params'][0]
                self.global_coordinates[term] = X
                map_count += 1
                
        print(f"       ! Mapped {map_count} terms to Primorial Lattice Z_30030.")
        
        # Update P for the final report to reflect the Adelic modulus
        self.p = 30030
