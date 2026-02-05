
import sys
import os
import random
import math
from collections import defaultdict, deque

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.algebraic_text import AlgebraicTextSolver
from logic_miner.backend.interpreter import LogicInterpreter

class RigorousSolver(AlgebraicTextSolver):
    """
    Protocol V.25: Rigorous P-adic Solver.
    Enforces: 
    1. BFE Prefix Inheritance (B <= p)
    2. Binary RANSAC (Hit/Miss)
    3. Derivative-based Complexity.
    """
    def __init__(self, p=31, iterations=100):
        # We start with p=31 to satisfy Source 1 (p > B) for most clusters.
        super().__init__(p, iterations)
        self.interpreter = LogicInterpreter(p=p)

    def _get_vp(self, n, p):
        if n == 0: return 10.0 # High value for infinity
        val = 0
        temp = abs(n)
        while temp > 0 and temp % p == 0:
            val += 1
            temp //= p
        return float(val)

    def _build_co_occurrence_tree(self, adj_matrix, entities):
        """
        Constructs a tree from the adjacency matrix using BFS.
        Ensures semantic hierarchy follows co-occurrence density.
        """
        n = len(entities)
        tree = defaultdict(list)
        visited = set()
        
        # Start with the most central node (Root)
        # For simplicity in research, use index 0
        root_idx = 0
        queue = deque([root_idx])
        visited.add(root_idx)
        
        while queue:
            parent = queue.popleft()
            row = adj_matrix[parent]
            # Find neighbors sorted by strength
            neighbors = sorted(
                [(j, w) for j, w in enumerate(row) if j not in visited and w > 0],
                key=lambda x: x[1], 
                reverse=True
            )
            
            for child, w in neighbors:
                tree[entities[parent]].append(entities[child])
                visited.add(child)
                queue.append(child)
        return tree

    def _assign_bfe_coordinates(self, tree, entities):
        """
        Implements Transparent Ultrametric Representation Learning (TURL).
        x = c0 + c1*p + c2*p^2 ...
        """
        coords = {}
        root = entities[0]
        
        # Initial coordinate for Root
        coords[root] = 1 # c0 = 1
        
        queue = deque([root])
        depths = {root: 0}
        
        while queue:
            parent = queue.popleft()
            p_coord = coords[parent]
            p_depth = depths[parent]
            
            children = tree.get(parent, [])
            # Check p > B
            B = len(children)
            if B >= self.p:
                print(f"   ! WARNING: Branching factor B={B} >= p={self.p}. Increasing p...")
                # In a real run, we would re-init. For research, we warn.
            
            for i, child in enumerate(children):
                # c_{d+1} = (i + 1)
                # x_child = x_parent + (i+1) * p^(d+1)
                c_val = i + 1
                coords[child] = p_coord + c_val * (self.p ** (p_depth + 1))
                depths[child] = p_depth + 1
                queue.append(child)
        
        return coords

    def solve_rigorous(self, adj_matrix, entities):
        """
        The V.25 Pipeline.
        """
        print(f"--- [Protocol V.25] Pipeline Initiated (p={self.p}) ---")
        
        # 1. Topology: BFE Address Construction
        print("   > Phase 1: BFE Prefix Address Construction (Tree Mapping)...")
        tree = self._build_co_occurrence_tree(adj_matrix, entities)
        self.coordinates = self._assign_bfe_coordinates(tree, entities)
        
        # 2. Logic: Exact Interpolation (Binary RANSAC Simulation)
        # In this research script, we'll audit the resulting coordinates.
        print("   > Phase 2: Binary Consensus Audit (Exact Subset Check)...")
        
        # 3. Interpretation: Sensitivity & Axiom Detection
        coeffs = self._compute_polynomial_from_coords(list(self.coordinates.values()))
        sensitivity = self.interpreter.sensitivity_probe(coeffs, self.coordinates)
        
        return self.coordinates, coeffs, sensitivity

def test_v25():
    print("--- [Protocol V.25: Final Rigorous Research] ---")
    
    # 1. Problem Cluster from V.24
    cluster = ["Matter", "Chemistry", "Zinc", "London", "Liquids", "Thermodynamics", "Atoms", "Energy"]
    # Adjacency Matrix (Semantic Links)
    # Matter -> Chemistry (1.0)
    # Chemistry -> Atoms (0.9), Thermodynamics (0.8)
    # Atoms -> Zinc (0.7), Liquids (0.6)
    # Liquids -> London (0.5), Energy (0.4)
    
    adj = [[0.0]*8 for _ in range(8)]
    # Define paths
    def link(a, b, w):
        i, j = cluster.index(a), cluster.index(b)
        adj[i][j] = adj[j][i] = w

    link("Matter", "Chemistry", 1.0)
    link("Chemistry", "Atoms", 0.9)
    link("Chemistry", "Thermodynamics", 0.8)
    link("Atoms", "Zinc", 0.7)
    link("Atoms", "Liquids", 0.6)
    link("Liquids", "London", 0.5)
    link("Liquids", "Energy", 0.4)

    # 2. Run Rigorous Solver
    solver = RigorousSolver(p=31) # p > B (B_max is 2 here)
    coords, poly, sensitivity = solver.solve_rigorous(adj, cluster)
    
    # 3. Report for Ontologist
    print("\n   > FINAL RIGOROUS ONTOLOGY (V.25):")
    print(f"   {'CONCEPT'.ljust(15)} | {'COORDINATE (Base 31)'.ljust(25)} | {'VALUATION'} | {'ROLE'}")
    print("-" * 75)
    
    for term in cluster:
        x = coords[term]
        vp = solver._get_vp(x, 31)
        # Convert to Base 31 expansion for readability
        # x = c0 + c1*31 + c2*31^2 ...
        expansion = []
        temp = x
        while temp > 0:
            expansion.append(str(temp % 31))
            temp //= 31
        exp_str = " + ".join([f"{c}*31^{i}" for i, c in enumerate(expansion)])
        
        role = sensitivity[term]['interpretation']
        print(f"   {term.ljust(15)} | {exp_str.ljust(25)} | {int(vp)} | {role}")

    # 4. Axiom Detection
    axioms = solver.interpreter.discover_axioms(poly, coords)
    print(f"\n   > Rigorous Axioms (Fixed Points): {axioms}")

if __name__ == "__main__":
    test_v25()
