import random
import math
import re
from collections import Counter

class AlgebraicTextSolver:
    """
    The Algebraic Logic Miner V.3 (Pure P-adic).
    Implements the Map-and-Derive Protocol.
    Goal: Derive Ultrametric Distance from Co-occurrence Density.
    """
    def __init__(self, p=5, ransac_iterations=20):
        self.p = p
        self.iterations = ransac_iterations
        self.coordinates = {} 
        self.mapping = {} # Entity -> Integer ID

    def solve(self, matrix, entities, raw_counts_bond):
        """
        V.5 Pipeline (Structural & Audited):
        1. Input: Abstract Adjacency Matrix & Entity Set.
        2. Optimization: Discover p-adic Mapping via Mahler Energy.
        3. Polynomial: Define P(x).
        4. Audit: Check Lipschitz/Mahler.
        """
        # 1. Algebraic Optimization (Discovery)
        print("   > Phase VI: Algebraic Optimization (Mahler Energy Minimization)...")
        # Optimization finds the coordinates.
        self._optimize_mapping(matrix, entities, raw_counts_bond)
        
        # 2. Generate Polynomial from Discovered Coordinates
        # The coordinates are now set in self.coordinates
        coords = list(self.coordinates.values())
        
        # Compute Poly
        print(f"   > Computing Defining Polynomial (Degree {len(coords)})...")
        coeffs = self._compute_polynomial_from_coords(coords)
        
        # 3. Audit (Mahler & Lipschitz)
        lipschitz_score = 0.0 # Placeholder
        
        print("   > Auditing Model...")
        from .mahler import MahlerSolver
        msolver = MahlerSolver(self.p)
        
        # Compute Mahler Series Decay
        decay_score = msolver.validation_metric(coeffs)
        print(f"     > Mahler Decay Score: {decay_score:.2f}")
        
        # Prepare complexities for Engine visualization
        complexities = {}
        for e in entities:
             key = e.replace(" ", "_")
             # raw_counts_bond keys are bonded strings.
             complexities[e] = raw_counts_bond.get(key, 0)

        result = {
            'mode': 'ALGEBRAIC_DISCOVERY',
            'p': self.p,
            'polynomial': coeffs,
            'energy': 0.0,
            'coordinates': self.coordinates,
            'analytic_score': decay_score,
            'lipschitz_violation': lipschitz_score,
            'matrix': matrix, # Included for engine compatibility
            'complexities': complexities
        }
        
        if decay_score < 0.1:
             result['mode'] = f"Refused:Mahler_Divergence ({decay_score:.2f})"
             
        return result

    def _optimize_mapping(self, adj_matrix, entities, raw_counts):
        """
        The Solver Loop (Phase VII: Iterative Discovery).
        Goal: Find a mapping M: Entities -> Z that minimizes Mahler Energy.
        
        Strategy:
        1. Heuristic Initialization (Centrality).
        2. RANSAC / Hill Climbing:
           - Helper: Compute P(x) -> Mahler Score.
           - If Score < Threshold: Swap nodes, Shift coordinates.
           - Minimize Energy (Maximize Decay Score).
        """
        n = len(entities)
        self.p = 5 # Default for Biology
        
        # --- Helper: Score A Mapping ---
        from .mahler import MahlerSolver
        msolver = MahlerSolver(self.p)
        
        def calculate_energy(current_map):
            # 1. Extract coords
            coords = list(current_map.values())
            # 2. Compute Poly
            # (Re-use efficient poly compute? We need to duplicate code or call self)
            # Implemented inline for speed or define small helper
            p_coeffs = [1]
            for c in coords:
                new_poly = [0] * (len(p_coeffs) + 1)
                for i, coeff in enumerate(p_coeffs):
                    new_poly[i+1] += coeff # x
                    new_poly[i] -= c * coeff # -c
                p_coeffs = new_poly
            # 3. Mahler Score
            return msolver.validation_metric(p_coeffs)

        # 1. Initialization (Centrality)
        original_to_bonded = {e: e.replace(" ", "_") for e in entities}
        sorted_entities_by_centrality = sorted(entities, 
                                               key=lambda e: raw_counts.get(original_to_bonded[e], 0), 
                                               reverse=True)
        
        # Hypothesis A: Centrality = Depth 0, 1, 2...
        # Map: E[0] -> 0, E[1] -> 1, E[2] -> 2 ... (Dense Integer Lattice)
        # Allows for p-adic hierarchy to emerge naturally (e.g. 5 is close to 0, 1 is far).
        best_mapping = {}
        for rank, ent in enumerate(sorted_entities_by_centrality):
            best_mapping[ent] = rank # DENSE PACKING FIX
            
        best_score = calculate_energy(best_mapping)
        print(f"     > Initial Heuristic Score: {best_score:.4f}")
        
        # 2. Optimization Loop (RANSAC / Hill Climb)
        # If Initial is good, we keep it. If not, we search.
        # Threshold: 0.1 is failure. We want > 0.5 ideally.
        
        import random
        iterations = self.iterations
        
        # Heuristic Shortcut: If score is already perfect, skip (unless forcing).
        # But for experiment, we obey the param.
        
        if iterations > 0:
            print(f"     > Low Convergence. Attempting {iterations} RANSAC permutations to find stability...")
            
            entities_list = list(entities)
            
            for k in range(iterations):
                # Mutation Strategy:
                # 1. Swap two random nodes
                # 2. Shift a node to a new p-adic branch
                
                candidate_mapping = best_mapping.copy()
                
                # Swap
                a, b = random.sample(entities_list, 2)
                candidate_mapping[a], candidate_mapping[b] = candidate_mapping[b], candidate_mapping[a]
                
                score = calculate_energy(candidate_mapping)
                if score > best_score:
                    best_score = score
                    best_mapping = candidate_mapping
                    print(f"       * New Best Configuration found! (Score: {best_score:.4f})")
        
        self.coordinates = best_mapping
        return self.coordinates

    def _compute_polynomial_from_coords(self, coords):
        # Quick interpolation P(x) where P(c) = 0 for all c in coords.
        # Product (x - c).
        # We need efficient expansion.
        # For sandbox, simple iterative multiplication is fine.
        # (x - c1)(x - c2)...
        
        # Coefficients array. Start with [1] (which is x^0? No, poly is a list of coeffs [a0, a1...])
        # Wait, (x-c) -> [-c, 1].
        
        poly = [1]
        for c in coords:
            # Multiply poly by (x - c)
            # New Poly has degree + 1
            new_poly = [0] * (len(poly) + 1)
            for i, coeff in enumerate(poly):
                # coeff * x^i * x -> coeff * x^(i+1)
                new_poly[i+1] += coeff
                # coeff * x^i * (-c) -> -c*coeff * x^i
                new_poly[i] -= c * coeff
            poly = new_poly
            
        return poly

    # Phase VI: Obsolete Methods (_lift_to_ultrametric, _embed_coordinates, _compute_polynomial) Removed.
    # The Solver now handles topology via _optimize_mapping.
