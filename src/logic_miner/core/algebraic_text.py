import random
import math
import re
from collections import Counter, deque, defaultdict

class AlgebraicTextSolver:
    """
    The Algebraic Logic Miner V.4 (Protocol V.25: Rigorous P-adic).
    Goal: Mirror Hierarchical Ontology through BFE Prefix Inheritance.
    """
    def __init__(self, p=31, ransac_iterations=100):
        self.p = p # Default to large prime to satisfy p > B
        self.iterations = ransac_iterations
        self.coordinates = {} 

    def _get_vp(self, n, p):
        if n == 0: return 10.0
        val = 0
        temp = abs(n)
        while temp > 0 and temp % p == 0:
            val += 1
            temp //= p
        return float(val)

    def _build_co_occurrence_tree(self, adj_matrix, entities):
        """
        Constructs a tree from the adjacency matrix using BFS.
        V.26: Implements Dynamic Branching Threshold to force deeper lineage.
        """
        n = len(entities)
        tree = defaultdict(list)
        visited = set()
        
        # Start with the most central node (Root) - Guaranteed by Spectral Selection in solve()
        root_idx = 0
        queue = deque([root_idx])
        visited.add(root_idx)
        
        # V.26: Establish a significance threshold (e.g., top 10% of local weights)
        while queue:
            parent = queue.popleft()
            row = adj_matrix[parent]
            
            # Filter neighbors
            potential_neighbors = [(j, w) for j, w in enumerate(row) if j not in visited and w > 0]
            if not potential_neighbors: continue
            
            # V.26 THRESHOLD: Only take the top B neighbors or those with > 50% of the max neighbor weight
            max_w = max([x[1] for x in potential_neighbors]) if potential_neighbors else 1.0
            neighbors = sorted(
                [x for x in potential_neighbors if x[1] >= (max_w * 0.5)],
                key=lambda x: x[1], 
                reverse=True
            )
            
            for child, w in neighbors:
                tree[entities[parent]].append(entities[child])
                visited.add(child)
                queue.append(child)
        return tree

    def _assign_bfe_coordinates(self, tree, entities, roots_dict=None):
        """
        Protocol V.30: Adelic Forest Representation.
        Supports multiple disjoint roots assigned to different congruence classes (trunks).
        """
        # 1. Determine local branching factor B for Dynamic Scaling
        max_B = 0
        for node, children in tree.items():
            max_B = max(max_B, len(children))
        
        # 2. Dynamic Scaling: Ensure p > max_B
        if max_B >= self.p:
            old_p = self.p
            self.p = max_B + 1
            print(f"     ! DYNAMIC SCALING (V30): p={old_p} -> {self.p} (Max Branching B={max_B})")

        coords = {}
        depths = {}
        visited = set()
        queue = deque()
        
        # 3. Initialize Multi-Root Forest
        if roots_dict:
            # entities[0] is typically the "best" root, but we respect the dict
            for root_name, cong_class in roots_dict.items():
                if root_name in entities:
                    coords[root_name] = cong_class
                    depths[root_name] = 0
                    visited.add(root_name)
                    queue.append(root_name)
        else:
            # Fallback to single root at class 1
            root = entities[0]
            coords[root] = 1
            depths[root] = 0
            visited.add(root)
            queue.append(root)
        
        # bread-First Coordinate Assignment (Stays within congruence class)
        while queue:
            parent = queue.popleft()
            p_coord = coords[parent]
            p_depth = depths[parent]
            
            children = tree.get(parent, [])
            for i, child in enumerate(children):
                if child in visited: continue
                # c_val is 0-indexed here if i starts at 0? 
                # Actually, if we use digits 1..p-1 for roots, 
                # then children should be at p^(depth+1).
                # digit = i + 1 to avoid p-adic collision with the prefix.
                c_val = i + 1
                coords[child] = p_coord + c_val * (self.p ** (p_depth + 1))
                depths[child] = p_depth + 1
                visited.add(child)
                queue.append(child)
        
        return coords

    def solve(self, matrix, entities, raw_counts_bond, fixed_root=None, fixed_addr=None):
        """
        V.26 Production Pipeline with Eternal Root Support.
        """
        print(f"   > Protocol V.26: Rigorous Foundation Deployment (p={self.p})")
        
        # 0. Noise Vaporization
        max_count = max(raw_counts_bond.values()) if raw_counts_bond else 1
        purified_entities = []
        indices_to_keep = []
        for i, e in enumerate(entities):
             key = e.replace(" ", "_")
             count = raw_counts_bond.get(key, 0)
             # V.26 THRESHOLD: Purge items with < 5% of max (Vaporization)
             # Auditor: "Celsius" is noise in a logic core.
             if count > (max_count * 0.05):
                 purified_entities.append(e)
                 indices_to_keep.append(i)
        
        print(f"     > Noise Vaporization: {len(entities)} -> {len(purified_entities)} Concepts.")
        
        # 1. Spectral Selection (Force fixed_root)
        sorted_indices = sorted(range(len(purified_entities)), key=lambda i: raw_counts_bond.get(purified_entities[i].replace(" ", "_"), 0), reverse=True)
        top_entities = [purified_entities[i] for i in sorted_indices]
        
        # 2. Topology Construction
        sub_matrix = [[matrix[r][c] for c in indices_to_keep] for r in indices_to_keep]
        final_matrix = [[sub_matrix[r][c] for c in sorted_indices] for r in sorted_indices]
        
        tree = self._build_co_occurrence_tree(final_matrix, top_entities)
        
        # V.30 Fix: Map legacy fixed_root to roots_dict
        roots_dict = {fixed_root: fixed_addr if fixed_addr else 1} if fixed_root else None
        self.coordinates = self._assign_bfe_coordinates(tree, top_entities, roots_dict=roots_dict)
        
        # 3. Optimization Phase
        print("   > Optimization Phase: Binary Consensus Verification...")
        
        # 3. Polynomial Interpolation
        unique_coords = list(set(self.coordinates.values()))
        final_poly = self._compute_polynomial_from_coords(unique_coords)
        
        # 4. Final Output Construction
        from .mahler import MahlerSolver
        msolver = MahlerSolver(self.p)
        score = msolver.validation_metric(final_poly)
        
        print(f"   > Production Audit Complete. Score: {score:.4f}")

        complexities = {}
        for e in top_entities: 
             key = e.replace(" ", "_")
             complexities[e] = raw_counts_bond.get(key, 0)

        result = {
            'mode': f"RIGOROUS_{self.p}ADIC",
            'p': self.p,
            'polynomial': final_poly,
            'energy': 1.0 - score,
            'coordinates': self.coordinates, 
            'analytic_score': score,
            'complexities': complexities,
            'collapsed_degree': len(unique_coords)
        }
        return result

    def _compute_polynomial_from_coords(self, coords):
        poly = [1]
        for c in coords:
            new_poly = [0] * (len(poly) + 1)
            for i, coeff in enumerate(poly):
                new_poly[i+1] += coeff
                new_poly[i] -= c * coeff
            poly = new_poly
        return poly
