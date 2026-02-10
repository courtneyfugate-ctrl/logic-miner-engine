import math
from collections import defaultdict, Counter, deque

class GlobalAggregator:
    """
    Protocol V.18: Global Sheaf Aggregator.
    Aggregates local manifolds into a unified global ontology.
    """
    def __init__(self, p=2):
        self.p = p
        self.global_edges = defaultdict(float) # (A, B) -> CumWeight
        self.node_counts = Counter()
        
    def aggregate(self, spline_trace):
        """
        Builds the weighted global graph from local traces.
        """
        print(f"     > Aggregating {len(spline_trace)} local manifolds...")
        for entry in spline_trace:
            edges = entry.get('ramified_edges', {})
            for u in edges:
                self.node_counts[u] += 1
                for v, weight in edges[u].items():
                    self.global_edges[(u, v)] += 1.0
        print(f"     > Global edges found: {len(self.global_edges)}")

    def prune(self, threshold=1):
        """Removes low-consensus edges."""
        original_count = len(self.global_edges)
        self.global_edges = {k: v for k, v in self.global_edges.items() if v >= threshold}
        print(f"     > Pruning (Threshold {threshold}): {original_count} -> {len(self.global_edges)} edges remaining.")

    def compute_pagerank(self, iterations=30, d=0.85):
        """
        Manual Power Iteration for PageRank on the weighted graph.
        """
        nodes = set()
        for u, v in self.global_edges:
            nodes.add(u)
            nodes.add(v)
            
        if not nodes: 
            print("     ! PageRank: No nodes in graph.")
            return {}
        
        print(f"     > Running PageRank on {len(nodes)} nodes...")
        n = len(nodes)
        node_list = list(nodes)
        rank = {node: 1.0 / n for node in node_list}
        
        # Build out-degree weights
        out_weights = defaultdict(float)
        for (u, v), w in self.global_edges.items():
            out_weights[u] += w
            
        for _ in range(iterations):
            new_rank = defaultdict(float)
            dangling_weight = 0.0
            
            for node in node_list:
                if out_weights[node] == 0:
                    dangling_weight += rank[node]
                else:
                    # Distribute rank to targets
                    for (u, v), w in self.global_edges.items():
                        if u == node:
                            new_rank[v] += d * rank[node] * (w / out_weights[node])
                            
            # Redistribute dangling rank and damping factor
            share = (1.0 - d) / n + (d * dangling_weight / n)
            for node in node_list:
                new_rank[node] += share
                
            rank = new_rank
            
        return rank

    def solve_global_ontology(self, threshold=1):
        """
        Performs the final global anchoring.
        """
        self.prune(threshold)
        
        # Calculate Weighted Out-Degree (Generative Power)
        out_weights = defaultdict(float)
        for (u, v), w in self.global_edges.items():
            out_weights[u] += w
            
        if not out_weights:
            print("     ! Global Aggregator: No outgoing edges found.")
            return {}
            
        # Sort by Out-Weight to find global roots (The Sources)
        sorted_nodes = sorted(out_weights.keys(), key=lambda n: out_weights[n], reverse=True)
        root = sorted_nodes[0]
        print(f"     > Global Root Found (Source): '{root}' (Out-Weight: {out_weights[root]:.1f})")
        
        # Global Valuation Drift (BFS from root)
        ontology = {root: 0} 
        queue = deque([root])
        visited = {root}
        
        # Build adjacency for drift
        adj = defaultdict(list)
        for (u, v) in self.global_edges:
            adj[u].append(v)
            
        while queue:
            curr = queue.popleft()
            depth = ontology[curr]
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    ontology[neighbor] = depth + 1
                    queue.append(neighbor)
        
        print(f"     > Global Ontology constructed: {len(ontology)} nodes.")
        return ontology

from collections import deque
