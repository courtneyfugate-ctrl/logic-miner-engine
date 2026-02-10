from .serial_synthesis_v50 import SerialSynthesizerV50
from .discovery import PrimeSelector
from .lifter import HenselLifter
from collections import defaultdict, Counter
import math

class SerialSynthesizerV53(SerialSynthesizerV50):
    """
    Protocol V.53: The Compliance.
    Strictly follows the 'abandoned' architecture:
    1. Hilbert Mapping (Term -> Integer).
    2. RANSAC Discovery (PrimeSelector).
    3. Hensel Lifting (HenselLifter).
    4. Adelic Reconstruction.
    """
    def __init__(self, chunk_size=50, momentum=0.3):
        super().__init__(chunk_size=chunk_size, momentum=momentum)
        self.prime_selector = PrimeSelector()
        self.lifter = None # Compliant Interface
        # adelic_coords structure: term -> {p: [val1, val2...]}
        self.adelic_coords = defaultdict(lambda: defaultdict(list))
        self.global_freqs = defaultdict(int)
        
    def _process_block(self, text_block, block_idx):
        # 1. Featurize
        # Limit to 500 candidates per block to keep RANSAC fast
        candidates = self.featurizer.extract_entities(text_block, limit=500)
        if not candidates: return
        
        matrix_raw, counts, _ = self.featurizer.build_association_matrix(text_block, candidates)
        
        # 2. Hilbert Mapping (Term -> Integer)
        # This gives us the raw "Signal" y
        hilbert_map = self.hilbert_mapper.compute_mappings(matrix_raw, candidates)
        
        # Sort candidates by frequency for stable ranking (Input X)
        # Higher Freq -> Lower Index (0) -> Core Concept
        sorted_candidates = sorted(candidates, key=lambda c: counts.get(c.replace(" ", "_"), 0), reverse=True)
        
        # Prepare Data for RANSAC
        # x = Rank (0..N), y = HilbertCoordinate
        inputs = list(range(len(sorted_candidates))) 
        outputs = [hilbert_map.get(c, 0) for c in sorted_candidates] 
        
        # 3. Discovery (RANSAC)
        # Find best p that models y = F(x)
        print(f"   > [Block {block_idx}] RANSAC Discovery on {len(inputs)} terms...")
        
        try:
            best_p, score, _ = self.prime_selector.select_detailed(inputs, outputs)
        except Exception as e:
            print(f"     ! PrimeSelector Error: {e}")
            return

        if score > 0.4: # Threshold for "Structure Found"
            print(f"     ! Found Logic Structure at p={best_p} (Score={score:.2f})")
            
            # 4. Refinement (Hensel Lifting)
            try:
                lifter = HenselLifter(best_p)
                lift_res = lifter.lift(inputs, outputs, max_depth=3, min_consensus=0.5)
                
                if lift_res['status'] == 'CONVERGED':
                    # We have a valid lifted polynomial logic!
                    coeffs = lift_res['coefficients'][-1]['params'] # Parameters at max depth
                    degree = lift_res['coefficients'][-1]['degree']
                    
                    # 5. Adelic Accumulation
                    # We store the *Predicted* (Ideal) coordinate for each term.
                    # This effectively "Denoises" the Hilbert Coordinate towards the algebraic ideal.
                    
                    # Note: lift_res['inliers'] tells us which points fit the model.
                    # We could strictly keep only inliers.
                    # Or we could Project everyone onto the curve.
                    # The User wants "Peeling". So maybe only inliers.
                    # But if we peer too aggressively, we lose yield.
                    # Compromise: Keep Inliers + High Confidence Projections.
                    
                    # Let's map inliers first for O(1) lookup
                    inlier_indices = set()
                    # Inliers format depends on lifter logic. Usually pairs (x,y).
                    # lift_res['coefficients'] doesn't return inliers explicitly for the final layer easily?
                    # Wait, lift() returns dict with 'final_consensus'.
                    # It does NOT return the final inlier set in the top level dict.
                    # We must re-evaluate or trust the model.
                    
                    # Let's project everyone. If the error is small, keep it.
                    # p-adic distance check.
                    
                    mapped_count = 0
                    for i, term in enumerate(sorted_candidates):
                        x_val = i
                        y_true = outputs[i]
                        
                        # Evaluate Polynomial
                        y_pred = 0
                        # Params usually (c, b, a) for a*x^2 + b*x + c?
                        # Solver.solve_polynomial returns (a,b,c) for ax^2+bx+c.
                        # HenselLifter stores them as is.
                        # Degree 0: (c,)
                        # Degree 1: (m, c) -> m*x + c
                        # Degree 2: (a, b, c) -> a*x^2 + b*x + c
                        
                        if degree == 0:
                            y_pred = coeffs[0]
                        elif degree == 1:
                            y_pred = coeffs[0] * x_val + coeffs[1]
                        elif degree == 2:
                            y_pred = coeffs[0] * (x_val**2) + coeffs[1] * x_val + coeffs[2]
                        elif degree == 3:
                            y_pred = coeffs[0] * (x_val**3) + coeffs[1] * (x_val**2) + coeffs[2] * x_val + coeffs[3]
                            
                        # Check "Fit"
                        # Only keep if y_true is close to y_pred (mod p)?
                        # RANSAC already filtered for the model.
                        # If we just take y_pred, we are enforcing the logic.
                        # Let's check if (y_true - y_pred) % best_p == 0 (Basic Modular Fit)
                        
                        if (y_true - y_pred) % best_p == 0:
                            # It fits the base logic!
                            self.adelic_coords[term][best_p].append(y_pred)
                            self.global_freqs[term] += counts.get(term.replace(" ", "_"), 0)
                            mapped_count += 1
                            
                    print(f"     + Mapped {mapped_count} terms to Adelic Lattice (p={best_p}).")

            except Exception as e:
                print(f"     ! Lifting Error: {e}")
        else:
             print(f"     . Noise (Score={score:.2f}). Skipping block.")

    def _consolidate_global_lattice(self):
        """
        Build Tree from RANSAC-Verified Adelic Coordinates.
        """
        print(f"     > Phase V.53: Compliance Consolidation...")
        
        # 1. Filter: Only terms that survived RANSAC (exist in adelic_coords)
        valid_terms = [t for t in self.adelic_coords if t not in self.STOPWORDS_SEMANTIC]
        
        # 2. Vectorize
        self.final_vectors = {}
        for term in valid_terms:
            vec = {}
            for p, coords in self.adelic_coords[term].items():
                if coords:
                    vec[p] = int(sum(coords) // len(coords)) # Average integer coordinate
            
            if vec:
                self.final_vectors[term] = vec
                
        print(f"       - Consolidated {len(self.final_vectors)} RANSAC-Verified Terms.")
        
        # 3. Build Tree (Restored V.33 Logic)
        print(f"       - Constructing Logic Tree...")
        self.tree_structure = self._build_divisibility_tree(list(self.final_vectors.keys())) # Keys are terms

    def _build_divisibility_tree(self, entities):
        # Sort by Freq
        sorted_ents = sorted(entities, key=lambda e: self.global_freqs[e], reverse=True)
        tree = defaultdict(list)
        roots = []
        
        for i, child in enumerate(sorted_ents):
            best_parent = None
            max_strength = -1
            
            child_vec = self.final_vectors[child]
            
            potential_parents = sorted_ents[:i]
            if len(potential_parents) > 200: potential_parents = sorted_ents[:200]
            
            for parent in potential_parents:
                parent_vec = self.final_vectors[parent]
                
                # Check Intersection of Primes
                common = set(child_vec.keys()) & set(parent_vec.keys())
                if not common: continue
                
                strength = self._calculate_adelic_strength(child_vec, parent_vec)
                
                if strength > max_strength:
                    max_strength = strength
                    best_parent = parent
            
            # Threshold: Strength >= 1 (Divisible in at least one common prime)
            if best_parent and max_strength >= 1:
                tree[best_parent].append(child)
            else:
                roots.append(child)
                
        return {'tree': tree, 'roots': roots}

    def _calculate_adelic_strength(self, vec_a, vec_b):
        max_v = -1
        common_primes = set(vec_a.keys()) & set(vec_b.keys())
        
        for p in common_primes:
            diff = abs(vec_a[p] - vec_b[p])
            if diff == 0:
                v = 10
            else:
                v = 0
                temp = diff
                while temp % p == 0:
                    v += 1
                    temp //= p
            if v > max_v: max_v = v
            
        return max_v
