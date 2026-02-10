
from .serial_synthesis_v37 import SerialSynthesizerV37
from collections import defaultdict
import math
import statistics
import random
import itertools

class SerialSynthesizerV40(SerialSynthesizerV37):
    """
    Protocol V.40: The Manifold Protocol (Strict Ultrametric).
    """
    def __init__(self, chunk_size=50, momentum=0.3, resolution=0.5):
        super().__init__(chunk_size=chunk_size, momentum=momentum, resolution=resolution)
        self.vectors = defaultdict(dict) # {term: {prime: coordinate}}
        self.primes = [5, 7, 11] # The Semantic Primes

    def _get_valuation(self, n, p):
        """Returns the p-adic valuation of integer n."""
        if n == 0: return 20.0 # Infinite valuation (max for our scale)
        val = 0
        temp = abs(int(n))
        while temp > 0 and temp % p == 0:
            val += 1
            temp //= p
        return float(val)

    def p_adic_distance(self, u, v, vectors):
        """
        Calculates strict ultrametric distance between terms u and v.
        d(u, v) = max(p^(-val(u_p - v_p))) for p in Primes.
        """
        max_dist = 0.0
        
        for p in self.primes:
            u_coord = vectors.get(u, {}).get(p, 0)
            v_coord = vectors.get(v, {}).get(p, 0)
            
            diff = u_coord - v_coord
            val = self._get_valuation(diff, p)
            
            # Distance = p^(-val)
            # Higher valuation -> Closer -> Smaller Distance
            dist = pow(p, -val)
            if dist > max_dist:
                max_dist = dist
                
        return max_dist

    def depth_score(self, term, depths_map):
        """
        Lifting Depth: Inverse of Tree Level (Harmonic Mean across Primes).
        Directive: "High Depth = Root".
        Level 0 (Root) -> Score 1/1 = 1.0 per prime.
        Level 4 (Leaf) -> Score 1/5 = 0.2 per prime.
        Total Score = Sum(1 / (depth_p + 1)).
        """
        total_score = 0.0
        for p in self.primes:
            # depth is 0-indexed (Root=0)
            d = depths_map.get(term, {}).get(p, 20) # Default to deep (leaf) if unknown
            total_score += 1.0 / (d + 1.0)
        return total_score

    def solve_manifold(self):
        """
        Main execution point for V.40.
        Returns list of (Term, Persistence)
        """
        # 1. Identify Top Terms
        degrees = defaultdict(float)
        for (u,v), w in self.global_adjacency_memory.items():
            degrees[u] += w
            degrees[v] += w
            
        top_terms = sorted(degrees.keys(), key=degrees.get, reverse=True)[:2000]
        if not top_terms:
            return {}

        # 2. Build Strict Matrix & Counts
        matrix = self._build_matrix_from_memory(top_terms)
        raw_counts = {}
        for t in top_terms:
            key = t.replace(" ", "_")
            raw_counts[key] = degrees[t]
            
        term_vectors = defaultdict(dict)
        term_depths = defaultdict(dict) # {term: {prime: depth}}
        
        # 3. Solvers (Generate Coordinates & Depths)
        for p in self.primes:
            try:
                print(f"     > Running Solver (p={p})...")
                res = self.solvers[p].solve(matrix, top_terms, raw_counts.copy())
                coords = res.get('coordinates', {})
                depths = res.get('depths', {})
                
                for t, c in coords.items():
                    term_vectors[t][p] = c
                
                for t, d in depths.items():
                    term_depths[t][p] = d
                    
            except Exception as e:
                print(f"       ! Solver (p={p}) Failed: {e}")
                
        # 4. Run TDA
        print("   > Running Ultrametric TDA...")
        persistence_map = self.calculate_persistent_homology(top_terms, term_vectors)
        
        # 5. Depth
        print("   > Calculating Lifting Depth (Harmonic)...")
        depth_map = {t: self.depth_score(t, term_depths) for t in top_terms}
        
        # Merge
        final_output = {}
        for t in top_terms:
            stats = persistence_map.get(t, {'b0': 0, 'b1': 0})
            final_output[t] = {
                'b0': stats.get('b0', 0),
                'b1': stats.get('b1', 0),
                'depth': depth_map.get(t, 0.0)
            }
            
        return final_output

    def _get_top_terms(self, limit):
        degrees = defaultdict(float)
        for (u,v), w in self.global_adjacency_memory.items():
            degrees[u] += w
            degrees[v] += w
        return sorted(degrees.keys(), key=degrees.get, reverse=True)[:limit]

    def _build_matrix_from_memory(self, terms):
        n = len(terms)
        matrix = [[0.0] * n for _ in range(n)]
        term_idx = {t: i for i, t in enumerate(terms)}
        
        count = 0 
        for (u,v), w in self.global_adjacency_memory.items():
            if u in term_idx and v in term_idx:
                i, j = term_idx[u], term_idx[v]
                matrix[i][j] = w
                matrix[j][i] = w
                count += 1
        return matrix

    def calculate_persistent_homology(self, terms, vectors, iterations=20, sample_size=40):
        """
        RANSAC TDA with Ultrametric Distance and B0/B1 Tracking.
        """
        term_stats = defaultdict(lambda: {'b0': [], 'b1': []})
        
        for it in range(iterations):
            current_n = min(len(terms), sample_size)
            sample = random.sample(terms, current_n)
            
            edges = []
            for i in range(current_n):
                for j in range(i + 1, current_n):
                    u, v = sample[i], sample[j]
                    dist = self.p_adic_distance(u, v, vectors)
                    edges.append((dist, i, j))
            
            edges.sort()
            
            parent = list(range(current_n))
            death_times = {} 
            
            def find(i):
                if parent[i] == i: return i
                parent[i] = find(parent[i])
                return parent[i]

            def union(i, j, time):
                root_i = find(i)
                root_j = find(j)
                if root_i != root_j:
                    parent[root_j] = root_i
                    death_times[root_j] = time
                    return True
                return False

            adj = defaultdict(set)
            node_h1_score = defaultdict(float)
            
            for dist, u, v in edges:
                is_tree = union(u, v, dist)
                
                if not is_tree:
                    # Pure Ultrametric Cycle Check:
                    # In strict ultrametric, triangles are isosceles.
                    # Cycles are "filled" if they form a consistent hierarchy plane.
                    # Heuristic: Check if edge creates immediate triangle.
                    common_neighbors = adj[u].intersection(adj[v])
                    if not common_neighbors:
                         node_h1_score[u] += 1.0
                         node_h1_score[v] += 1.0

                adj[u].add(v)
                adj[v].add(u)
                
            max_d = edges[-1][0] if edges else 1.0
            
            for i in range(current_n):
                term = sample[i]
                d_time = death_times.get(i, max_d)
                term_stats[term]['b0'].append(d_time)
                term_stats[term]['b1'].append(node_h1_score[i])
                
        results = {}
        for t, stats in term_stats.items():
            b0 = statistics.mean(stats['b0']) if stats['b0'] else 0.0
            b1 = statistics.mean(stats['b1']) if stats['b1'] else 0.0
            results[t] = {'b0': b0, 'b1': b1}
            
        return results
