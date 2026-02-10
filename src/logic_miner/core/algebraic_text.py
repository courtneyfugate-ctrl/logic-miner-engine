import random
import math
import re
from collections import Counter, deque, defaultdict

class AlgebraicTextSolver:
    """
    The Algebraic Logic Miner V.4 (Protocol V.25: Rigorous P-adic).
    Goal: Mirror Hierarchical Ontology through BFE Prefix Inheritance.
    """
    def __init__(self, p=31, ransac_iterations=100, branching_threshold=0.5):
        self.p = p # Default to large prime to satisfy p > B
        self.iterations = ransac_iterations
        self.coordinates = {} 
        self.branching_threshold = branching_threshold

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
            
            # V.26 THRESHOLD: Only take the top B neighbors or those with > THRESHOLD of the max neighbor weight
            max_w = max([x[1] for x in potential_neighbors]) if potential_neighbors else 1.0
            neighbors = sorted(
                [x for x in potential_neighbors if x[1] >= (max_w * self.branching_threshold)],
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
        
        return coords, depths

    def _build_ramified_system(self, inclusion_matrix, commutator_matrix, entities):
        """
        Protocol V.31+: Constructs the Valuation Poset and Ramification Graph.
        """
        n = len(entities)
        poset = defaultdict(list)
        ramification_graph = defaultdict(dict)
        
        # We need to map sorted entities back to their original indices in the matrices
        # But wait, the matrices passed in `solve` are already re-indexed or need to be?
        # In `solve`, we re-indexed `inclusion_matrix` to `final_matrix`.
        # We need to do the same for `commutator_matrix`.
        
        # Actually, let's assume the matrices passed HERE are already aligned to `entities`.
        # The caller (solve) will handle the re-indexing.
        
        links_count = 0
        ramified_count = 0
        
        for i in range(n):
            for j in range(n):
                if i == j: continue
                
                # 1. Divisibility (Poset)
                # A | B iff I_AB >= 1.
                # In our matrix, row=A, col=B.
                if inclusion_matrix[i][j] >= 1.0:
                    poset[entities[i]].append(entities[j])
                    links_count += 1
                    
                # 2. Ramification (Flow)
                # K_AB = N(A->B) - N(B->A)
                # We need the raw commutator value. 
                # The commutator matrix might be raw integers or normalized?
                # In TextFeaturizer, it's raw counts difference.
                k_val = commutator_matrix[i][j]
                
                # Direction: If K_AB > 0, A -> B dominates.
                # We only process if K_AB > 0 to avoid double counting (since K_BA = -K_AB).
                if k_val > 0:
                    # Calculate Ramification Index R = v_p(|K_AB|)
                    r_val = self._get_vp(int(k_val), self.p)
                    if r_val >= 1.0:
                        ramification_graph[entities[i]][entities[j]] = r_val
                        ramified_count += 1
                        
        print(f"     > Ramified System: {links_count} Divisibility edges, {ramified_count} Ramified edges (R>=1).")
        return poset, ramification_graph

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
        aligned_commutator = [[0.0]*n for _ in range(n)]
        
        for r_new, r_old in enumerate(sorted_indices):
            for c_new, c_old in enumerate(sorted_indices):
                # Bounds check
                if r_old < len(inclusion_matrix) and c_old < len(inclusion_matrix):
                    aligned_inclusion[r_new][c_new] = inclusion_matrix[r_old][c_old]
                if r_old < len(commutator_matrix) and c_old < len(commutator_matrix):
                    aligned_commutator[r_new][c_new] = commutator_matrix[r_old][c_old]

        # 4. Build Ramified System
        poset, ram_graph = self._build_ramified_system(aligned_inclusion, aligned_commutator, sorted_entities)
        
        # 5. RANSAC + Hensel Lifting (Simulated for V.31)
        # For now, we will map the Poset to a Tree for coordinate assignment,
        # privileging Ramified edges as "Trunks".
        # TODO: Full Polynomial Fitting. 
        # Interim: Use Poset depth for BFE.
        
        self.coordinates = {}
        # 6. Layer Aggregation (Protocol V.17: The Law of the Layers)
        # We map x = Logical Depth and y = Average Layer Complexity
        self.coordinates = {}
        depths = {root_entity: 0}
        queue = deque([root_entity])
        visited = {root_entity}
        
        # Build adjacency for BFS (K_ij > 0 implies parent -> child)
        adj = defaultdict(list)
        for i, u in enumerate(entities):
            for j, v in enumerate(entities):
                if commutator_matrix[i][j] > 0:
                    adj[u].append(v)
                    
        layers = defaultdict(list)
        layers[0].append(raw_counts_bond.get(root_entity.replace(" ", "_"), 0))
        self.coordinates[root_entity] = 0 # Root is x=0
        
        while queue:
            parent = queue.popleft()
            p_depth = depths[parent]
            for child in adj.get(parent, []):
                if child not in visited:
                    visited.add(child)
                    depths[child] = p_depth + 1
                    self.coordinates[child] = p_depth + 1
                    complexity = raw_counts_bond.get(child.replace(" ", "_"), 0)
                    layers[p_depth + 1].append(complexity)
                    queue.append(child)
                    
        # x = Depths, y = Average Complexities
        depth_keys = sorted(layers.keys())
        xs = depth_keys
        ys = [sum(layers[d]) / len(layers[d]) for d in depth_keys]
        
        # 7. Mahler Regression & Amice Decay
        from .mahler import MahlerSolver
        ms = MahlerSolver(self.p)
        coeffs = ms.compute_coefficients(xs, ys)
        
        # Analytic Score: Amice Condition (|a_n|_p -> 0)
        # score = percentage of coefficients satisfying v_p(a_n) >= floor(log_p n)
        score = ms.validation_metric(coeffs)
        
        # Penalty for insufficient hierarchy (we need vertical depth for a law)
        if len(xs) < 2:
            score = min(score, 0.1)

        result = {
            'mode': f"RAMIFIED_{self.p}ADIC",
            'p': self.p,
            'polynomial': [float(c) for c in coeffs], 
            'energy': 1.0 - score,
            'coordinates': self.coordinates, 
            'depths': self.coordinates, # Preserved for sheaf logic (depth is coordinate)
            'entities': sorted_entities,
            'analytic_score': score,
            'net_ramification': ramification_balance,
            'ramified_edges': ram_graph, # Topology Data
            'layer_centroids': dict(zip(xs, ys))
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
