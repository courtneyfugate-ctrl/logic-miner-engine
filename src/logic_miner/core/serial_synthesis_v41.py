
from .serial_synthesis_v40 import SerialSynthesizerV40
from .adelic import AdelicIntegrator
from collections import defaultdict
import math

class SerialSynthesizerV41(SerialSynthesizerV40):
    """
    Protocol V.41: Adelic Restoration (The Global Concept Protocol).
    
    Extends V.40 (Strict Ultrametric) with:
    1.  Adelic Integration (CRT/Hasse Principle).
    2.  Global Integrity Filtering (Complexity check).
    
    Hypothesis:
    -   Concepts exist as identifying 'Small Global Integers'.
    -   Artifacts exist as 'Maximum Entropy Integers'.
    """
    def __init__(self, chunk_size=50, momentum=0.3, resolution=0.5):
        super().__init__(chunk_size, momentum, resolution)
        self.integrator = AdelicIntegrator()
        
    def compute_global_integrity(self, term, vectors):
        """
        Attempts to stitch local p-adic coordinates into a Global Integer.
        Returns: (GlobalValue, Modulus, ComplexityScore)
        """
        models = []
        for p in self.primes:
            # Get coordinate (default to 0 if missing, but missing usually means 0)
            coord = vectors.get(term, {}).get(p, 0)
            
            # Construct model dict for AdelicIntegrator
            # We treat coordinate as a constant 'param' for Degree 0 model
            models.append({
                'p': p,
                'degree': 0,
                'params': (coord,) 
            })
            
        # Run CRT
        # This will fail if moduli are not coprime (they are: 5,7,11)
        res = self.integrator.solve_crt(models)
        
        if not res:
            return (0, 1, 1.0) # Failure (High Complexity)
            
        global_val = res['params'][0]
        modulus = res['modulus']
        
        # Complexity Metric: K(x)
        # Ratio of GlobalValue to Maximum Capacity (Modulus).
        # Small Integer Hypothesis: Concepts have value << Modulus.
        # Artifacts (Random) have value ~ Modulus/2 (Uniform distribution).
        # We use relative magnitude: |val| / M
        
        # Handle negative reconstruction? CRT returns [0, M-1].
        # If val > M/2, it might be a small negative number in Z.
        # e.g. M=385 (5*7*11). val=384 -> -1.
        # We should take min(val, M-val) to represent "distance from 0".
        
        dist_from_zero = min(global_val, modulus - global_val)
        
        # Normalize by Modulus
        complexity = dist_from_zero / float(modulus)
        
        return (global_val, modulus, complexity)

    def solve_adelic_manifold(self):
        """
        1. Generate p-adic vectors (V.40 logic).
        2. Filter by Global Integrity (V.41 logic).
        3. Run TDA on the Surviving Global Constants? 
           Or just output the Integrity Map for Audit.
        """
        # A. Vector Generation (Reuse V.40)
        # We need to expose the internal vector generation from V.40 solve_manifold
        # but V.40 bundles it all.
        # Let's copy-paste or refactor V.40? 
        # Refactoring V.40 is cleaner but I can't edit it easily without changing V.40 file.
        # I will inline the generation part here for safety (Redundancy is fine for Audit).
        
        # 1. Memory & Terms
        degrees = defaultdict(float)
        for (u,v), w in self.global_adjacency_memory.items():
            degrees[u] += w
            degrees[v] += w
            
        top_terms = sorted(degrees.keys(), key=degrees.get, reverse=True)[:2000]
        if not top_terms: return {}

        # 2. Matrix
        matrix = self._build_matrix_from_memory(top_terms)
        raw_counts = {t.replace(" ", "_"): degrees[t] for t in top_terms}
        
        term_vectors = defaultdict(dict)
        
        # 3. Solvers
        print(f"   > [Adelic] Generating p-adic fibers for {len(top_terms)} terms...")
        for p in self.primes:
            try:
                res = self.solvers[p].solve(matrix, top_terms, raw_counts.copy())
                coords = res.get('coordinates', {})
                for t, c in coords.items():
                    term_vectors[t][p] = c
            except Exception as e:
                print(f"       ! Solver (p={p}) Failed: {e}")

        # 4. Adelic Integration (The Hasse Step)
        print("   > [Adelic] Stitching Global Integers (Hasse Principle)...")
        adelic_results = {}
        
        for t in top_terms:
            g_val, mod, complexity = self.compute_global_integrity(t, term_vectors)
            
            # Also compute V.40 Depth for comparison
            # (Requires re-fetching depths from solver or approximating from vectors)
            # Approximation: val(x) ~ log_p(x) roughly? No.
            # We'll skip V.40 Depth here and focus on V.41 Integrity.
            
            adelic_results[t] = {
                'global_val': g_val,
                'modulus': mod,
                'complexity': complexity,
                'fiber': term_vectors[t] # (v5, v7, v11)
            }
            
        return adelic_results
