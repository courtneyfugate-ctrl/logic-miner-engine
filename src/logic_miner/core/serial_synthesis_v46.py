from .serial_synthesis_v45 import SerialSynthesizerV45
from .adelic import AdelicIntegrator
from .algebraic_text import AlgebraicTextSolver
from collections import defaultdict
import math

class SerialSynthesizerV46(SerialSynthesizerV45):
    """
    Protocol V.46: The Unified Field.
    Combines V.45 (Geometric Curvature) and V.42 (Adelic Information)
    to create a high-precision, high-yield lattice.
    """
    def __init__(self, p=13, chunk_size=50):
        super().__init__(p=p, chunk_size=chunk_size)
        self.adelic_integrator = AdelicIntegrator()
        self.filter_primes = [5, 7, 11] # Basis for V.42 Check
        
    def _compute_adelic_complexity(self, term, text_block):
        """
        V.42 Metric: Information Content via CRT.
        Returns K_info.
        """
        # We need coordinates in 3 primes. 
        # This is expensive, so we only do it for terms that pass Geometric Filter First?
        # Yes, optimization: Filter V.45 first, then V.42.
        
        term_vectors = {}
        valid_primes = 0
        
        for p in self.filter_primes:
            solver = AlgebraicTextSolver(p=p)
            try:
                # We can reuse matrix construction or cache it if we want speed
                # For now, just rebuild for Purity
                # This is a bit slow doing it per term per prime, but safe.
                # Actually, better to solve for ALL candidate terms in one go per prime
                # ... but we only want to check ONE term here.
                # Let's assume we do batch solve in _process_block.
                pass
            except:
                pass
        return 0.0

    def _process_block(self, text_block, block_idx):
        # 1. Featurize
        candidates = self.featurizer.extract_entities(text_block, limit=400)
        matrix, counts, G_directed = self.featurizer.build_association_matrix(text_block, candidates)
        if not candidates: return

        # 2. Compute Trajectories (V.45 Logic)
        solver = AlgebraicTextSolver(p=self.p)
        try:
            res = solver.solve(matrix, candidates, counts)
            block_coords = res['coordinates']
        except:
            block_coords = {}
            
        for term, coord in block_coords.items():
            self.trajectory_history[term].append(coord)
            
        # 3. Geometric Filter (V.45) - The "Spiky" Check
        spiky_candidates = []
        for term in candidates:
            traj = self.trajectory_history.get(term, [])
            if len(traj) < 3:
                if term not in ["Introduction", "Chapter"]:
                    spiky_candidates.append(term)
                continue
                
            k_geom = self._calculate_discrete_curvature(traj)
            if k_geom > 0.5:
                spiky_candidates.append(term)
                
        if not spiky_candidates: return
        
        # 4. Adelic Information Filter (V.42) - The "Complexity" Check
        # Now we run the expensive Adelic Check ONLY on the Spiky Candidates
        complex_candidates = self._apply_adelic_filter(spiky_candidates, text_block)
        
        if not complex_candidates: return
        
        purified = complex_candidates

        # 5. Accumulate Global Stats (V.32 Core)
        for i, c1 in enumerate(purified):
            self.global_freqs[c1] += counts.get(c1.replace(" ", "_"), 0)
            
            if c1 in G_directed:
                for c2, w in G_directed[c1].items():
                    if c2 in purified:
                        self.global_directed_adj[c1][c2] += w
            
            # Symmetric Adj Logic
            try:
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
            except:
                pass

    def _apply_adelic_filter(self, candidates, text_block):
        """
        V.42 Logic: Calculates K_info via CRT.
        """
        term_vectors = defaultdict(dict)
        
        # Batch solve for all filter primes
        for p in self.filter_primes:
            solver = AlgebraicTextSolver(p=p)
            try:
                p_matrix, p_counts, _ = self.featurizer.build_association_matrix(text_block, candidates)
                res = solver.solve(p_matrix, candidates, p_counts)
                coords = res.get('coordinates', {})
                for t, c in coords.items():
                    term_vectors[t][p] = c
            except:
                pass
                
        real_concepts = []
        for t in candidates:
            if len(term_vectors[t]) < 3: continue 
            
            vec = [term_vectors[t][p] for p in self.filter_primes]
            models = [{'p': p, 'params': (vec[i],), 'degree': 0} for i, p in enumerate(self.filter_primes)]
            
            res = self.adelic_integrator.solve_crt(models)
            if res:
                modulus = res['modulus']
                global_val = res['params'][0]
                ratio = global_val / float(modulus)
                
                # V.42 Threshold
                if ratio > 0.15:
                    real_concepts.append(t)
                    
        return real_concepts
