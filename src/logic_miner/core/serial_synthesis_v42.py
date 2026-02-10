from .serial_synthesis import SerialManifoldSynthesizer
from .adelic import AdelicIntegrator
from .algebraic_text import AlgebraicTextSolver
from collections import defaultdict, Counter
import math

class SerialSynthesizerV42(SerialManifoldSynthesizer):
    """
    Protocol V.42: The Integrated Adelic Tree.
    Combines V.32 (Discrete Modular Hierarchy) with V.41 (Global Adelic Filter).
    """
    def __init__(self, p=13, chunk_size=50):
        super().__init__(p=p, chunk_size=chunk_size)
        self.adelic_integrator = AdelicIntegrator()
        self.filter_primes = [5, 7, 11] # Adelic Basis for Filtering
        
    def _process_block(self, text_block, block_idx):
        # 1. Spectral Purification (V.32 Base)
        print(f"     > Spectral Purification (V.32)...")
        print(f"       [Debug] Text Block Size: {len(text_block)} chars")
        candidates = self.featurizer.extract_entities(text_block, limit=400)
        print(f"       [Debug] Raw Candidates: {len(candidates)}")
        
        matrix, counts, G_directed = self.featurizer.build_association_matrix(text_block, candidates)
        
        # metrics = self.featurizer.calculate_spectral_metrics(candidates, G_directed, counts)
        # classifications = self.featurizer.classify_terms(metrics)
        # purified = [c for c in candidates if classifications.get(c) == "CONCEPT"]
        # print(f"       [Debug] V.32 Purified: {len(purified)} (Spectral)")
        
        # BYPASS V.32 SPECTRAL FILTER - TRUST ADELIC FILTER
        purified = candidates
        print(f"       [Debug] Bypassed V.32 Filter. Passing {len(purified)} terms to Adelic Filter.")
        
        if not purified: return

        # --- V.42 INJECTION: ADELIC FILTER ---
        print(f"     > Adelic Global Filter (V.41)...")
        real_concepts = self._apply_adelic_filter(purified, text_block)
        print(f"       ! Filtered {len(purified)} -> {len(real_concepts)} terms via Hasse Principle.")
        
        if not real_concepts: return
        purified = real_concepts
        # -------------------------------------

        # Update Global Freqs & Edges (V.32 Base Logic)
        for i, c1 in enumerate(purified):
            self.global_freqs[c1] += counts.get(c1.replace(" ", "_"), 0)
            
            # Simple local centrality
            idx1 = candidates.index(c1)
            local_deg = sum(matrix[idx1])
            self.global_variances[c1].append(local_deg)

            for j, c2 in enumerate(purified):
                if i == j: continue
                # Update Symmetric Matrix (Legacy Support)
                idx2 = candidates.index(c2)
                w = matrix[idx1][idx2]
                if w > 0:
                    pair = tuple(sorted((c1, c2)))
                    # Accumulate Global Weight
                    self.global_adj[pair] = self.global_adj.get(pair, 0) + w
        
        # Accumulate Directed Operator Edges (V.32 Base Logic)
        for u in G_directed:
            if u not in purified: continue
            for v, w in G_directed[u].items():
                if v not in purified: continue
                self.global_directed_adj[u][v] += w

        # 2. Local Trace (for Spline Monitoring)
        # We reuse the V.32 method but use our P
        solver = AlgebraicTextSolver(p=self.p)
        p_matrix, p_counts, _ = self.featurizer.build_association_matrix(text_block, purified)
        local_result = solver.solve(p_matrix, purified, p_counts)
        
        # 3. Energy Analysis
        current_energy = 1.0 - local_result['analytic_score']
        self.energy_history.append(current_energy)
        self.spline_trace.append({
            'block': block_idx, 'p': self.p, 'energy': current_energy, 'polynomial': local_result['polynomial']
        })
        print(f"     > Global Energy: {current_energy:.4f} (p={self.p})")
        
    def _apply_adelic_filter(self, candidates, text_block):
        """
        Applies K(x) = |CRT(x)| / M filter.
        Returns list of terms that pass the Hasse Principle.
        """
        term_vectors = defaultdict(dict)
        
        # 1. Compute Coordinates in 3 Primes
        for p in self.filter_primes:
            # We construct a temporary solver just to get coordinates
            # This is expensive but necessary for purity
            solver = AlgebraicTextSolver(p=p)
            try:
                # Re-build matrix for this prime attempt
                # We can optimize by reusing the raw matrix if possible, 
                # but build_association_matrix is fast enough for 400 terms usually.
                p_matrix, p_counts, _ = self.featurizer.build_association_matrix(text_block, candidates)
                res = solver.solve(p_matrix, candidates, p_counts)
                coords = res.get('coordinates', {})
                for t, c in coords.items():
                    term_vectors[t][p] = c
            except Exception:
                pass
                
        # 2. Check Global Integrity
        real_concepts = []
        for t in candidates:
            if len(term_vectors[t]) < 3: continue # Must span all fields
            
            vec = [term_vectors[t][p] for p in self.filter_primes]
            
            # Construct Models for CRT Integration
            models = []
            for i, p in enumerate(self.filter_primes):
                # Degree 0 (Constant) assumption for coordinate mapping
                models.append({'p': p, 'params': (vec[i],), 'degree': 0})
            
            # Solve CRT
            res = self.adelic_integrator.solve_crt(models)
            
            if res:
                modulus = res['modulus'] # 5*7*11 = 385
                global_val = res['params'][0]
                
                # Complexity Metric: Ratio of Global Value to Modulus
                # Analysis (Debug V.42):
                # - Arthifacts (Introduction, Access) -> Low K (< 0.15) (Universal Roots)
                # - Concepts (Atoms, Water) -> High K (> 0.2) (Specific Leaves)
                # - Noise -> Max K (~1.0)
                
                ratio = global_val / float(modulus)
                
                # Bandpass Filter:
                # 1. Reject Universal Artifacts (Low Entropy): < 0.15
                # 2. Reject Random Noise (Max Entropy): > 0.95 (Optional)
                if ratio > 0.15:
                    real_concepts.append(t)
                
        return real_concepts
