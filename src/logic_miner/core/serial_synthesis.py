from .text_featurizer import TextFeaturizer
from .algebraic_text import AlgebraicTextSolver
from .adelic import AdelicMapper
from .mahler import MahlerSolver
import math
from collections import Counter, defaultdict, deque
import hashlib

class SerialManifoldSynthesizer:
    """
    Protocol V.22: Serial Spline Synthesis.
    Ingests text in streams, applying Spectral Purification and Adelic Shaking per block.
    Maintains a Global Crystal and rotates the manifold (Prime Switching) to minimize energy.
    """
    def __init__(self, p=5, chunk_size=50):
        self.p = p 
        self.chunk_size = chunk_size
        self.global_coordinates = {} 
        self.anchors = set() 
        self.global_freqs = Counter() 
        self.global_variances = defaultdict(list) # Track local centrality per block
        self.global_adj = {} # (node1, node2) -> weight
        self.eternal_root = None
        self.eternal_addr = 1
        self.energy_history = []
        self.spline_trace = [] # Records [BlockIdx, Prime, Energy, SamplePoly]
        
        # Dependencies
        self.featurizer = TextFeaturizer()
        
    def fit_stream(self, text=None, reader=None, max_pages=None):
        """
        Fits logic from a stream of text or a PdfReader.
        V.28: Includes Final Global BFE Walk.
        """
        print(f"--- [Serial Global Synthesis V.28] ---")
        
        if reader:
            total_pages = len(reader.pages)
            effective_total_pages = min(total_pages, max_pages) if max_pages else total_pages
            
            for start_idx in range(0, effective_total_pages, self.chunk_size):
                end_idx = min(start_idx + self.chunk_size, effective_total_pages)
                print(f"\n   > Processing Block {start_idx}-{end_idx}...")
                
                # 1. Extract Text Block
                text_block = ""
                for i in range(start_idx, end_idx):
                    text_block += reader.pages[i].extract_text() + "\n"
                
                self._process_block(text_block, start_idx)
        elif text:
            # Fallback for raw text: Split by segments
            lines = text.split('\n')
            block_size = 2000 # lines
            for i in range(0, len(lines), block_size):
                text_block = "\n".join(lines[i:i+block_size])
                self._process_block(text_block, i // block_size)

        # Final Global BFE Walk (Protocol V.28)
        print("\n   > Phase XVIII: Final Global BFE Walk (Lattice Consolidation)...")
        self._consolidate_global_lattice()

        print("\n--- [Synthesis Complete] ---")
        return {
            'coordinates': self.global_coordinates,
            'p': self.p,
            'energy': self.energy_history[-1] if self.energy_history else 0.0,
            'anchors': list(self.anchors),
            'spline_trace': self.spline_trace,
            'classification': {e: "CONCEPT" for e in self.global_coordinates},
            'entities': list(self.global_coordinates.keys()),
            'polynomial': self.spline_trace[-1]['polynomial'] if self.spline_trace else []
        }

    def _process_block(self, text_block, block_idx):
        # 1. Spectral Purification
        print(f"     > Spectral Purification...")
        candidates = self.featurizer.extract_entities(text_block, limit=400)
        matrix, counts, graphs = self.featurizer.build_association_matrix(text_block, candidates)
        if not candidates: return
        
        metrics = self.featurizer.calculate_spectral_metrics(candidates, graphs[0], graphs[1], counts)
        classifications = self.featurizer.classify_terms(metrics)
        purified = [c for c in candidates if classifications.get(c) == "CONCEPT"]
        
        if not purified: return

        # Update Global Freqs & Edges (Protocol V.28)
        # V.29: Track local centrality for variance analysis
        for i, c1 in enumerate(purified):
            self.global_freqs[c1] += counts.get(c1, 0)
            
            # Simple local centrality: sum of row / max possible connections
            local_deg = sum(matrix[candidates.index(c1)])
            self.global_variances[c1].append(local_deg)

            for j, c2 in enumerate(purified):
                if i == j: continue
                # We use the original indices in 'matrix' which correspond to 'candidates'
                orig_i = candidates.index(c1)
                orig_j = candidates.index(c2)
                w = matrix[orig_i][orig_j]
                if w > 0:
                    pair = tuple(sorted((c1, c2)))
                    self.global_adj[pair] = self.global_adj.get(pair, 0) + w

        # 2. Local Trace (for Spline Monitoring)
        solver = AlgebraicTextSolver(p=self.p)
        p_matrix, p_counts, _ = self.featurizer.build_association_matrix(text_block, purified)
        local_result = solver.solve(p_matrix, purified, p_counts)
        
        # 3. Energy Analysis
        current_energy = 1.0 - local_result['analytic_score']
        self.energy_history.append(current_energy)
        self.spline_trace.append({
            'block': block_idx, 'p': self.p, 'energy': current_energy, 'polynomial': local_result['polynomial']
        })
        print(f"     > Global Energy: {current_energy:.4f} (p={self.p})")

    def _consolidate_global_lattice(self):
        """
        Protocol V.30: Adelic Forest Consolidation.
        Breaks the "Single Root" monolith by discovering disjoint components
        and assigning them to distinct p-adic congruence classes (trunks).
        """
        if not self.global_adj: return
        
        # 0. Vaporization (Scaffolding removal)
        meta_discourse = {
            "Access", "University", "College", "Figure", "Table", "Preface", 
            "Appendix", "Index", "Name", "Names", "Introduction",
            "Example", "Exercise", "Problem", "Section", "Chapter"
        }
        
        # 1. Build Adjacency Graph with Adaptive Threshold
        weights = list(self.global_adj.values())
        avg_w = sum(weights) / len(weights) if weights else 0
        threshold = avg_w * 0.5
        
        adj_dict = defaultdict(list)
        nodes = set()
        for (u, v), w in self.global_adj.items():
            if u in meta_discourse or v in meta_discourse: continue
            if w >= threshold:
                adj_dict[u].append(v)
                adj_dict[v].append(u)
                nodes.add(u)
                nodes.add(v)
        
        # 2. Graph Partitioning: Find Disjoint Components (Peers)
        components = []
        visited_global = set()
        for node in sorted(list(nodes)):
            if node not in visited_global:
                comp = []
                q = deque([node])
                visited_global.add(node)
                while q:
                    u = q.popleft()
                    comp.append(u)
                    for v in adj_dict[u]:
                        if v not in visited_global:
                            visited_global.add(v)
                            q.append(v)
                components.append(comp)
        
        print(f"     > Adelic Forest: Discovered {len(components)} independent logical components.")
        
        # 3. Multi-Root Assignment (Fiber Partitioning)
        # Sort components by cumulative centrality to pick roots
        roots_dict = {}
        forest_tree = defaultdict(list)
        forest_entities = []
        
        for i, comp in enumerate(sorted(components, key=len, reverse=True)):
            # Pick root for this component based on local centrality
            comp_nodes = sorted(comp, key=lambda n: len(adj_dict[n]), reverse=True)
            root = comp_nodes[0]
            
            # Use congruence classes 1, 2, 3, 4, 0 (modulo p)
            # We use (i % self.p) as the root coordinate
            # Let's use 1..p-1 if possible, then 0
            cong_class = (i % (self.p - 1)) + 1 if self.p > 1 else 1
            roots_dict[root] = cong_class
            
            # Build local tree for this component
            comp_tree, comp_visited = self._build_trial_tree(root, adj_dict)
            forest_tree.update(comp_tree)
            forest_entities.extend(list(comp_visited))
            
            print(f"       - Component {i+1}: Root '{root}' -> Congruence Class {cong_class} (Size: {len(comp)})")
            if i >= self.p - 1: # Limit number of roots to p-1 for now to avoid collision
                break

        # 4. Final Multi-Root BFE Walk
        solver = AlgebraicTextSolver(p=self.p)
        self.global_coordinates = solver._assign_bfe_coordinates(forest_tree, forest_entities, roots_dict)
        
        # Synchronize prime
        if solver.p != self.p:
            self.p = solver.p
            
        print(f"     > Global BFE Forest Walk: {len(self.global_coordinates)} nodes at p={self.p}.")

    def _build_trial_tree(self, root, global_adj_dict):
        """Builds a local BFS tree from a subset of the graph."""
        tree = defaultdict(list)
        visited = {root}
        queue = deque([root])
        
        while queue:
            parent = queue.popleft()
            # In V.30 we already filtered by threshold in the component step
            neighbors = sorted(
                [v for v in global_adj_dict[parent] if v not in visited],
                key=lambda v: len(global_adj_dict[v]), reverse=True
            )
            for child in neighbors:
                tree[parent].append(child)
                visited.add(child)
                queue.append(child)
        return tree, visited

    def _compute_manifold_energy(self, coords, p):
        """Computes energy of a coordinate set under prime p."""
        unique_coords = list(set(coords.values()))
        if not unique_coords: return 1.0
        solver = AlgebraicTextSolver(p=p)
        poly = solver._compute_polynomial_from_coords(unique_coords[:40]) # Sample for speed
        ms = MahlerSolver(p)
        return 1.0 - ms.validation_metric(poly)

    def _compute_global_energy(self):
        coords = list(set(self.global_coordinates.values()))
        if not coords: return 1.0
        # Characterize the crystal under current prime
        solver = AlgebraicTextSolver(p=self.p)
        # Use first 30 for speed in audit energy check
        poly = solver._compute_polynomial_from_coords(coords[:30]) 
        ms = MahlerSolver(self.p)
        return 1.0 - ms.validation_metric(poly)

    def _rotate_manifold(self):
        candidates = [2, 3, 5, 7, 13, 17, 31]
        best_p = self.p
        min_energy = 1.0
        
        coords = list(set(self.global_coordinates.values()))[:30]
        solver = AlgebraicTextSolver(p=5)
        poly = solver._compute_polynomial_from_coords(coords)
        
        for p in candidates:
            ms = MahlerSolver(p)
            energy = 1.0 - ms.validation_metric(poly)
            if energy < min_energy:
                min_energy = energy
                best_p = p
        
        if best_p != self.p:
            print(f"     ! ROTATION: p={self.p} -> p={best_p} (Min Energy: {min_energy:.4f})")
            self.p = best_p
