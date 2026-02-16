import random
import math
import re
from collections import Counter, deque, defaultdict

class AlgebraicTextSolver:
    """
    The Algebraic Logic Miner V.5 (Protocol V.56-Field).
    Goal: Mirror Hierarchical Ontology through p-adic Hensel Lifting.
    Transitions from "Grammatical Graphs" to "Implication Fields".
    """
    def __init__(self, p=31, lift_threshold=0.4):
        self.p = p 
        self.lift_threshold = lift_threshold
        self.coordinates = {} 

    def _get_vp(self, n, p):
        if n == 0: return 10.0
        val = 0
        temp = abs(n)
        while temp > 0 and temp % p == 0:
            val += 1
            temp //= p
        return float(val)

    def hensel_lift(self, valuations, implication_matrix):
        """
        [Protocol V.56] The Hensel Lifter.
        Constructs a tree by lifting concepts based on Altitude (v) and Implication (P).
        """
        tree = defaultdict(list)
        
        # 1. Find Roots (The Integers: v=0)
        roots = [e for e, v in valuations.items() if v == 0]
        if not roots:
            min_v = min(valuations.values()) if valuations else 0
            roots = [e for e, v in valuations.items() if v == min_v]
            
        # 2. Recursive Lift (The Lift Test)
        queue = deque(roots)
        visited = set(roots)
        
        while queue:
            parent = queue.popleft()
            p_v = valuations.get(parent, 0)
            
            # Scan all atoms B where v(B) >= v(A) 
            potential_children = [e for e, v in valuations.items() if v >= p_v and e not in visited and e != parent]
            
            for child in potential_children:
                # Lift Test: Is P(Parent | Child) > Threshold?
                p_imply = implication_matrix.get(child, {}).get(parent, 0.0)
                
                # Rigid Lift: v(B) > v(A)
                # Soft Lift: v(B) == v(A) but very high implication (Lateral Branching)
                c_v = valuations.get(child, 0)
                if c_v > p_v:
                    if p_imply >= self.lift_threshold:
                        tree[parent].append(child)
                        visited.add(child)
                        queue.append(child)
                elif c_v == p_v:
                    if p_imply >= self.lift_threshold + 0.2: # Higher bar for lateral
                        tree[parent].append(child)
                        visited.add(child)
                        queue.append(child)
                    
        return tree

    def _assign_bfe_coordinates(self, tree, entities, roots_dict):
        """
        Protocol V.30: Adelic Forest Representation.
        """
        coords = {}
        depths = {}
        visited = set()
        queue = deque()
        
        # Initialize Multi-Root Forest
        for root_name, cong_class in roots_dict.items():
            coords[root_name] = cong_class
            depths[root_name] = 0
            visited.add(root_name)
            queue.append(root_name)
            
        # Breadth-First Coordinate Assignment
        while queue:
            parent = queue.popleft()
            p_coord = coords[parent]
            p_depth = depths[parent]
            
            children = tree.get(parent, [])
            for i, child in enumerate(children):
                if child in visited: continue
                c_val = i + 1
                coords[child] = p_coord + c_val * (self.p ** (p_depth + 1))
                depths[child] = p_depth + 1
                visited.add(child)
                queue.append(child)
        
        return coords, depths

    def solve(self, adelic_features, entities, raw_counts_bond, fixed_root=None, fixed_addr=None):
        """
        V.31+ Production Pipeline: Ramified Adelic Solver.
        """
        print(f"   > Protocol V.31+ (Ramified): Flow-Based Hierarchy (p={self.p})")
        
        purified_entities = list(entities)
        
        # 1. Unpack Adelic Features
        if 'primes' in adelic_features and self.p in adelic_features['primes']:
            prime_feats = adelic_features['primes'][self.p]
            inclusion_matrix = prime_feats['inclusion_matrix']
            valuations = prime_feats['valuations']
        else:
            print(f"     ! WARNING: Prime {self.p} not in Adelic Features.")
            inclusion_matrix = [[0.0]*len(entities) for _ in range(len(entities))]
            valuations = {}
            
        commutator_matrix = adelic_features.get('commutator_matrix', [[0.0]*len(entities) for _ in range(len(entities))])

        # 2. Compute Ramification Balance (R = Out - In)
        # R is the row-sum of the commutator matrix (Asymmetry Flow)
        ramification_balance = {}
        for i, ent in enumerate(entities):
            r_sum = sum(commutator_matrix[i]) # Summing row K[i,:] = Sum(N[i,j] - N[j,i])
            ramification_balance[ent] = r_sum

        # 3. Sort Entities by (Valuation, -Ramification)
        # High Valuation (v >= 1) terms are logic atoms.
        # High Ramification (Source) should be the Root.
        if valuations:
            # Sort Key: (Valuation, -Ramification)
            # This ensures units (v=0) are at the front, but we will soon shift them
            sorted_entities = sorted(purified_entities, key=lambda e: (valuations.get(e, 99.0), -ramification_balance.get(e, 0.0)))
            
            # Root Correction: Strictly enforce v_p(Root) >= 1.0 (The Logic Anchor)
            if valuations.get(sorted_entities[0], 0) < 1.0:
                for i, ent in enumerate(sorted_entities):
                    if valuations.get(ent, 0) >= 1.0:
                        # Re-anchor: The first logic atom in the ramified priority queue becomes the root
                        root_ent = sorted_entities.pop(i)
                        sorted_entities.insert(0, root_ent)
                        print(f"     ! Root Re-anchored (Ramified Source): '{root_ent}' (v_{self.p}={valuations.get(root_ent, 0)}, R={ramification_balance.get(root_ent,0)})")
                        break
        else:
            sorted_entities = sorted(purified_entities, key=lambda e: (raw_counts_bond.get(e.replace(" ", "_"), 0), -ramification_balance.get(e, 0.0)), reverse=True)
            
        print(f"     > Adelic Sorting: Root='{sorted_entities[0]}' (v_{self.p}={valuations.get(sorted_entities[0], 0)}, R={ramification_balance.get(sorted_entities[0],0)})")
        
        # 4. Connected Component Pruning (Protocol V.16)
        # After selecting the Root, perform a Reachability Scan.
        # Discard all entities NOT reachable from the Root.
        root_entity = sorted_entities[0]
        reachable = {root_entity}
        stack = [root_entity]
        
        # Build adjacency for traversal (K_ij > 0 implies i -> j)
        adj = defaultdict(list)
        for i, u in enumerate(entities):
            for j, v in enumerate(entities):
                if commutator_matrix[i][j] > 0:
                    adj[u].append(v)
                    
        while stack:
            curr = stack.pop()
            for neighbor in adj.get(curr, []):
                if neighbor not in reachable:
                    reachable.add(neighbor)
                    stack.append(neighbor)
                    
        original_count = len(sorted_entities)
        sorted_entities = [e for e in sorted_entities if e in reachable]
        print(f"     > Pruning: {len(sorted_entities)} nodes reachable, {original_count - len(sorted_entities)} orphans vaporized.")

        # 5. Align Matrices to Sorted Entities (Only Reachable Set)
        orig_idx_map = {e: i for i, e in enumerate(entities)}
        sorted_indices = [orig_idx_map[e] for e in sorted_entities]
        n = len(sorted_entities)
        
        aligned_inclusion = [[0.0]*n for _ in range(n)]
    def solve(self, valuations, implication_matrix, atom_counts):
        """
        V.56+ Integrated Solver: Field -> Lift -> Tree -> Coordinates.
        """
        print(f"   > Protocol V.56 (Hensel Field): Altitude-Based Lifting (p={self.p})")
        
        # 1. Hensel Lift
        tree = self.hensel_lift(valuations, implication_matrix)
        
        # 2. Multi-Root BFE Walk (Coordinate Assignment)
        all_children = set()
        for children in tree.values():
            all_children.update(children)
        roots = [n for n in valuations if n not in all_children]
        
        if not roots and valuations:
            min_v = min(valuations.values())
            roots = [e for e, v in valuations.items() if v == min_v]
            
        roots_dict = {r: (i % (self.p - 1)) + 1 for i, r in enumerate(roots)}
        
        self.coordinates, depths = self._assign_bfe_coordinates(tree, list(valuations.keys()), roots_dict)
        
        # 3. Mahler Regression
        layers = defaultdict(list)
        for ent, d in depths.items():
            layers[d].append(math.log(atom_counts.get(ent, 1) + 1))
            
        depth_keys = sorted(layers.keys())
        xs = depth_keys
        ys = [sum(layers[d]) / len(layers[d]) for d in depth_keys]
        
        from .mahler import MahlerSolver
        ms = MahlerSolver(self.p)
        coeffs = ms.compute_coefficients(xs, ys)
        score = ms.validation_metric(coeffs)
        
        return {
            'mode': f"HENSEL_FIELD_{self.p}ADIC",
            'p': self.p,
            'polynomial': [float(c) for c in coeffs],
            'energy': 1.0 - score,
            'coordinates': self.coordinates,
            'depths': depths,
            'tree': dict(tree),
            'analytic_score': score,
            'valuations': valuations,
            'implication_tensor': implication_matrix
        }

    def _compute_polynomial_from_coords(self, coords):
        poly = [1]
        for c in coords:
            new_poly = [0] * (len(poly) + 1)
            for i, coeff in enumerate(poly):
                new_poly[i+1] += coeff
                new_poly[i] -= c * coeff
            poly = new_poly
        return poly

    def _optimize_mapping(self, tree, entities, roots_dict):
        """
        [RESTORED] Uses RANSAC to find the coordinate mapping that minimizes Mahler Energy.
        Attempts 50 random permutations of the tree structure.
        """
        from .mahler import MahlerSolver
        msolver = MahlerSolver(self.p)
        
        best_coords = self.coordinates
        best_score = msolver.validation_metric(self._compute_polynomial_from_coords(list(best_coords.values())))
        
        for _ in range(self.iterations):
            # Attempt a permutation: Re-shuffle children in the tree
            shuffled_tree = {k: random.sample(v, len(v)) for k, v in tree.items()}
            
            # Re-assign coordinates with new sibling order
            test_coords, _ = self._assign_bfe_coordinates(shuffled_tree, entities, roots_dict)
            
            # Evaluate
            test_poly = self._compute_polynomial_from_coords(list(test_coords.values()))
            test_score = msolver.validation_metric(test_poly)
            
            if test_score > best_score:
                best_score = test_score
                best_coords = test_coords
                print(f"     + Found Better Topology: Score {best_score:.4f}")
                
        return best_coords
