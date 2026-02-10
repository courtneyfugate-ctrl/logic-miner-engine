
import math
from collections import defaultdict

class SheafScanner:
    """
    Protocol V.13: Sheaf Manifold Scanner.
    Enforces Rigid Locking between overlapping logic windows.
    If Logic(Window A) != Logic(Window B) on Intersection -> REJECT Link.
    """
    def __init__(self, p=31):
        self.p = p
        self.locked_sections = [] # Stores successfully glued manifolds

    def get_valuation(self, coordinate):
        """Calculates p-adic valuation v_p(x)."""
        if coordinate == 0: return float('inf')
        val = 0
        temp = abs(coordinate)
        while temp > 0 and temp % self.p == 0:
            val += 1
            temp //= self.p
        return val

    def verify_overlap(self, manifold_a, manifold_b, overlap_terms):
        """
        Checks if two manifolds agree on the overlapping terms.
        Returns: (bool is_compatible, list disagreements)
        """
        disagreements = []
        
        # Filter terms that actually exist in both manifolds (in case overlap_terms is loose)
        common_terms = [t for t in overlap_terms if t in manifold_a['coordinates'] and t in manifold_b['coordinates']]
        
        if not common_terms:
            # No overlap in logic terms -> No glue possible (Disjoint)
            # Or should we allow if they don't contradict? 
            # Protocol: "Rigorous Lock". If no intersection, they are separate components.
            return True, [] 

        for term in common_terms:
            coord_a = manifold_a['coordinates'][term]
            coord_b = manifold_b['coordinates'][term]
            
            # Strict Coordinate Check? Or just Valuation?
            # User specified: "Logic derived... must match exactly".
            # "Valuation_{M1}(t) == Valuation_{M2}(t)"
            
            v_a = self.get_valuation(coord_a)
            v_b = self.get_valuation(coord_b)
            
            if v_a != v_b:
                disagreements.append({
                    'term': term, 
                    'v_a': v_a, 
                    'v_b': v_b,
                    'c_a': coord_a,
                    'c_b': coord_b
                })
        
        is_compatible = (len(disagreements) == 0)
        return is_compatible, disagreements

    def glue_manifolds(self, manifold_a, manifold_b):
        """
        Merges two verified manifolds. 
        Since they agree on overlap, we can union them.
        For non-overlapping terms, we preserve their coordinates.
        """
        # Start with A
        new_coords = manifold_a['coordinates'].copy()
        new_depths = manifold_a['depths'].copy()
        
        # Add B (overlapping keys will be overwritten, but they are identical/compatible)
        new_coords.update(manifold_b['coordinates'])
        new_depths.update(manifold_b['depths'])
        
        # Calculate new energy/metrics?
        # For now return the structure
        return {
            'coordinates': new_coords,
            'depths': new_depths,
            'p': self.p
        }
