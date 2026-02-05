
import sys
import os
import random
import math
from collections import Counter

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.algebraic_text import AlgebraicTextSolver
from logic_miner.core.mahler import MahlerSolver
from logic_miner.engine import LogicMiner

class ResearchSolver(AlgebraicTextSolver):
    """
    Protocol V.24 Experimental Solver.
    Implements High-Resolution Manifolds and Collision Jitter.
    """
    def __init__(self, p=5, ransac_iterations=150):
        super().__init__(p, ransac_iterations)
        self.max_pool_depth = 6 # Force search up to p^6
        
    def _get_vp(self, n, p):
        if n == 0: return 6.0 # Max depth
        val = 0
        temp = abs(n)
        while temp > 0 and temp % p == 0:
            val += 1
            temp //= p
        return float(val)

    def _optimize_mapping(self, adj_matrix, entities, raw_counts):
        """
        Overridden with Jitter Phase and Deeper Search.
        """
        # 1. Base Logic from V.22
        top_entities = list(entities)
        n = len(top_entities)
        original_to_bonded = {e: e.replace(" ", "_") for e in top_entities}
        centralities = {e: raw_counts.get(original_to_bonded[e], 1) for e in top_entities}
        max_c = max(centralities.values()) if centralities else 1
        norm_centralities = {e: c/max_c for e, c in centralities.items()}

        # V.24: Deep Pool Expansion
        pool_size = n * (self.p ** 3) # Much larger pool
        
        def calculate_topology_energy(mapping):
            E = 0.0
            for ent, coord in mapping.items():
                c = norm_centralities[ent]
                vp = self._get_vp(coord, self.p)
                target_vp = 1.0 + (1.0 - c) * 4.0 # Target deeper branches
                dist = abs(vp - target_vp)
                # Penalty for v=0 remains
                if vp == 0: dist += 5.0
                E += dist
            
            # V.24 COLLISION PENALTY
            # Count unique coordinates vs total concepts
            unique_count = len(set(mapping.values()))
            collision_penalty = (len(mapping) - unique_count) * 100.0 # Heavy penalty for collapse
            return E + collision_penalty

        # 2. Seeding (Greedy)
        sorted_ents = sorted(top_entities, key=lambda e: centralities[e], reverse=True)
        current_mapping = {}
        used_slots = set()
        
        for i, ent in enumerate(sorted_ents):
            # Target vp
            c = norm_centralities[ent]
            target_v = int(1.0 + (1.0 - c) * 4.0)
            
            # Find a slot with EXACTLY target_v or better
            found = False
            for attempt in range(100):
                # Try to find a multiple of p^target_v
                r = random.randint(1, pool_size // (self.p ** target_v))
                cand = r * (self.p ** target_v)
                if cand not in used_slots:
                    current_mapping[ent] = cand
                    used_slots.add(cand)
                    found = True
                    break
            
            if not found:
                # Fallback to absolute random
                while True:
                    r = random.randint(1, pool_size)
                    if r not in used_slots:
                        current_mapping[ent] = r
                        used_slots.add(r)
                        break
        
        best_mapping = current_mapping.copy()
        best_score = calculate_topology_energy(best_mapping)
        
        print(f"   > V.24 Research: Start Energy {best_score:.4f} (Collisions: {len(best_mapping) - len(set(best_mapping.values()))})")

        # 3. RANSAC + Jitter
        for k in range(self.iterations):
            cand_mapping = best_mapping.copy()
            
            # Detect Collisions
            rev_map = {}
            collisions = []
            for e, val in cand_mapping.items():
                if val in rev_map:
                    collisions.append(e)
                rev_map[val] = e
            
            # Move Strategy
            if collisions and random.random() < 0.8:
                # JITTER: Move a collided node
                node = random.choice(collisions)
                # Find a new slot
                for _ in range(10):
                    new_c = random.randint(0, pool_size)
                    if new_c not in cand_mapping.values():
                        cand_mapping[node] = new_c
                        break
            else:
                # Normal Swap/Migrate
                node = random.choice(top_entities)
                cand_mapping[node] = random.randint(0, pool_size)

            new_score = calculate_topology_energy(cand_mapping)
            if new_score <= best_score:
                best_score = new_score
                best_mapping = cand_mapping

        self.coordinates = best_mapping
        print(f"   > V.24 Research: Final Energy {best_score:.4f} (Collisions: {len(best_mapping) - len(set(best_mapping.values()))})")
        return self.coordinates

def test_v24():
    print("--- [Protocol V.24: Resolution Research Simulation] ---")
    
    # 1. Load a collision cluster (Mock based on V.22 dump)
    # Concepts that were collapsed into Coord 25
    cluster = ["Zinc", "London", "Liquids", "Thermodynamics", "Solute", "Properties", "Rates", "Acidic"]
    
    # Mock raw counts (Centralities)
    # If they all have similar centrality, the old solver collapsed them.
    # We give them a slightly tiered centrality to see if we can resolve them.
    counts = {
        "Zinc": 15, "London": 14, "Liquids": 18, 
        "Thermodynamics": 22, "Solute": 12, "Properties": 11, 
        "Rates": 16, "Acidic": 13
    }
    
    # 2. Run the Research Solver
    solver = ResearchSolver(p=5, ransac_iterations=500)
    # Mock empty adjacency matrix (just testing the mapping optimizer)
    adj = [[0.0]*len(cluster) for _ in range(len(cluster))]
    
    print(f"   > Attempting to resolve Cluster: {cluster}")
    coords = solver._optimize_mapping(adj, cluster, counts)
    
    # 3. Report Results
    print("\n   > Resolved Lattice:")
    for term in cluster:
        c = coords[term]
        vp = solver._get_vp(c, 5)
        print(f"     * {term.ljust(15)} | Coord: {str(c).ljust(10)} | Val(5): {vp}")
    
    unique_count = len(set(coords.values()))
    if unique_count == len(cluster):
        print("\n   [RESULT]: PROTOCOL V.24 SUCCESS. Collision Cluster Resolved.")
    else:
        print(f"\n   [RESULT]: PARTIAL SUCCESS. {unique_count}/{len(cluster)} unique.")

if __name__ == "__main__":
    test_v24()
