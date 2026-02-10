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
        self.global_directed_adj = defaultdict(lambda: Counter()) # V.31: u -> v -> weight
        self.eternal_root = None
        self.eternal_addr = 1
        self.energy_history = []
        self.spline_trace = [] # Records [BlockIdx, Prime, Energy, SamplePoly]
        
        # Dependencies
        self.featurizer = TextFeaturizer()
        
    def fit_stream(self, text=None, reader=None, max_pages=None):
        """
        Fits logic from a stream of text or a PdfReader.
        Protocol V.13: Sheaf Splining (Overlapping Windows + Rigid Lock).
        """
        print(f"--- [Sheaf Splining Protocol V.13] ---")
        
        from .sheaf_core import SheafScanner
        scanner = SheafScanner(p=self.p)
        
        # Sheaf State
        self.active_sheaf = None # The current growing logic component
        self.sheaves = [] # List of finalized components
        
        blocks = []

        if reader:
            total_pages = len(reader.pages)
            effective_total_pages = min(total_pages, max_pages) if max_pages else total_pages
            
            # Use 50% Overlap (Step = Chunk/2)
            step_size = max(1, self.chunk_size // 2)
            
            for start_idx in range(0, effective_total_pages, step_size):
                # Ensure we don't go past end in a weird way, though overlap is intended
                if start_idx + (step_size//2) >= effective_total_pages: break
                
                end_idx = min(start_idx + self.chunk_size, effective_total_pages)
                print(f"\n   > Processing Window {start_idx}-{end_idx} (Overlap Mode)...")
                
                # 1. Extract Text
                text_block = ""
                for i in range(start_idx, end_idx):
                    text_block += reader.pages[i].extract_text() + "\n"
                
                # 2. Process to Local Manifold
                local_manifold = self._process_block_sheaf(text_block, start_idx)
                if not local_manifold: continue
                
                # Protocol V.13: Spline Curvature Filter (Reject Noise/Flat Logic)
                # If analytic_score < 0.6 (Energy > 0.4), the logic is too weak/noisy.
                if local_manifold['analytic_score'] < 0.6:
                    print(f"     ! REJECTED: Weak Logic (Score: {local_manifold['analytic_score']:.2f}). Noise Filter Active.")
                    continue
                
                # 3. Sheaf Glue / Cut Logic
                if self.active_sheaf is None:
                    self.active_sheaf = local_manifold
                    print(f"     + Initialized New Sheaf (Base: {len(local_manifold['coordinates'])} terms)")
                else:
                    # Check Overlap
                    overlap_terms = set(self.active_sheaf['coordinates'].keys()).intersection(local_manifold['coordinates'].keys())
                    is_compatible, disagreements = scanner.verify_overlap(self.active_sheaf, local_manifold, overlap_terms)
                    
                    if is_compatible:
                        # GLUE
                        self.active_sheaf = scanner.glue_manifolds(self.active_sheaf, local_manifold)
                        print(f"     + Extension Verified: Sheaf grew to {len(self.active_sheaf['coordinates'])} concepts.")
                    else:
                        # CUT
                        print(f"     ! LOGIC CUT DETECTED: {len(disagreements)} contradictions on overlap.")
                        print(f"       (e.g., '{disagreements[0]['term']}': v={disagreements[0]['v_a']} vs v={disagreements[0]['v_b']})")
                        self.sheaves.append(self.active_sheaf)
                        self.active_sheaf = local_manifold # Start new
                        
        elif text:
            # Fallback (Line based)
            lines = text.split('\n')
            block_line_size = 2000
            step_line = 1000
            
            for i in range(0, len(lines), step_line):
                if i + 500 >= len(lines): break
                text_block = "\n".join(lines[i:i+block_line_size])
                
                local_manifold = self._process_block_sheaf(text_block, i // step_line)
                if not local_manifold: continue
                
                if self.active_sheaf is None:
                    self.active_sheaf = local_manifold
                else:
                    overlap_terms = set(self.active_sheaf['coordinates'].keys()).intersection(local_manifold['coordinates'].keys())
                    is_compatible, disagreements = scanner.verify_overlap(self.active_sheaf, local_manifold, overlap_terms)
                    
                    if is_compatible:
                        self.active_sheaf = scanner.glue_manifolds(self.active_sheaf, local_manifold)
                    else:
                        print(f"     ! LOGIC CUT: {len(disagreements)} disagreements.")
                        self.sheaves.append(self.active_sheaf)
                        self.active_sheaf = local_manifold

        # Finalize last sheaf
        if self.active_sheaf:
            self.sheaves.append(self.active_sheaf)

        # 4. Phase 8: Global Sheaf Gluing (Weighted Aggregation)
        from .global_aggregator import GlobalAggregator
        aggregator = GlobalAggregator(p=self.p)
        aggregator.aggregate(self.spline_trace)
        # Threshold 1: Initial verification (No consensus pruning required)
        global_ontology = aggregator.solve_global_ontology(threshold=1)
        
        # Select Dominant Result for Global State
        if global_ontology:
            self.global_coordinates = global_ontology
            print(f"\n   > Synthesis Complete. Global Ontology Recovered: {len(global_ontology)} nodes.")
            # Verify Titanium Demotion if present
            if 'titanium atoms' in global_ontology:
                print(f"     ! Global Audit: 'titanium atoms' rank-anchored at v={global_ontology['titanium atoms']}")
            
            # Export Global Ontology
            import json
            with open("sandbox/global_ontology.json", "w") as f:
                json.dump(global_ontology, f, indent=4)
            print(f"     > Global Ontology exported to sandbox/global_ontology.json")
        elif self.sheaves:
            longest_sheaf = max(self.sheaves, key=lambda s: len(s['coordinates']))
            self.global_coordinates = longest_sheaf['coordinates']
            print(f"\n   > Synthesis Complete. Recovered {len(self.sheaves)} Logic Sheaves. Largest: {len(longest_sheaf['coordinates'])} nodes.")
        else:
            self.global_coordinates = {}

        return {
            'coordinates': self.global_coordinates,
            'p': self.p,
            'energy': self.energy_history[-1] if self.energy_history else 0.0,
            'anchors': list(self.anchors),
            'spline_trace': self.spline_trace,
            'classification': {e: "CONCEPT" for e in self.global_coordinates},
            'entities': list(self.global_coordinates.keys()),
            'sheaves_count': len(self.sheaves)
        }

    def _process_block(self, text_block, block_idx):
        # 1. Spectral Purification
        print(f"     > Spectral Purification...")
        candidates = self.featurizer.extract_entities(text_block, limit=400)
        # 2. Association & Spectral Analysis
        # V.31: Now returns a Directed Operator Graph
        matrix, counts, G_directed = self.featurizer.build_association_matrix(text_block, candidates)
        if not candidates: return
        
        metrics = self.featurizer.calculate_spectral_metrics(candidates, G_directed, counts)
        classifications = self.featurizer.classify_terms(metrics)
        purified = [c for c in candidates if classifications.get(c) == "CONCEPT"]
        
        if not purified: return

        # Update Global Freqs & Edges (Protocol V.28)
        # V.29: Track local centrality for variance analysis
        for i, c1 in enumerate(purified):
            self.global_freqs[c1] += counts.get(c1.replace(" ", "_"), 0)
            
            # Simple local centrality
            local_deg = sum(matrix[candidates.index(c1)])
            self.global_variances[c1].append(local_deg)

            for j, c2 in enumerate(purified):
                if i == j: continue
                # Update Symmetric Matrix (Legacy Support)
                orig_i = candidates.index(c1)
                orig_j = candidates.index(c2)
                w = matrix[orig_i][orig_j]
                if w > 0:
                    pair = tuple(sorted((c1, c2)))
                    self.global_adj[pair] = self.global_adj.get(pair, 0) + w
        
        # V.31: Accumulate Directed Operator Edges
        for u in G_directed:
            if u not in purified: continue
            for v, w in G_directed[u].items():
                if v not in purified: continue
                self.global_directed_adj[u][v] += w

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
        
        # 1. Build Adjacency Graph from Directed Operator Edges
        adj_dict = defaultdict(list)
        undirected_adj = defaultdict(set)
        nodes = set()
        
        # We use a threshold on the directed weights
        all_weights = []
        for u in self.global_directed_adj:
            for v, w in self.global_directed_adj[u].items():
                all_weights.append(w)
        
        avg_w = sum(all_weights) / len(all_weights) if all_weights else 0
        threshold = avg_w * 0.5
        
        for u in self.global_directed_adj:
            if u in meta_discourse: continue
            for v, w in self.global_directed_adj[u].items():
                if v in meta_discourse: continue
                if w >= threshold:
                    adj_dict[u].append(v)
                    undirected_adj[u].add(v)
                    undirected_adj[v].add(u)
                    nodes.add(u)
                    nodes.add(v)
        
        # 2. Graph Partitioning: Find Disjoint Components
        components = []
        visited_global = set()
        for node in sorted(list(nodes)):
            if node not in visited_global:
                comp = []
                q = deque([node])
                visited_global.add(node)
                while q:
                    curr = q.popleft()
                    comp.append(curr)
                    for neighbor in undirected_adj[curr]:
                        if neighbor not in visited_global:
                            visited_global.add(neighbor)
                            q.append(neighbor)
                components.append(comp)
        
        print(f"     > Adelic Forest (V31): Discovered {len(components)} logical components via Directed Flow.")

        # V.31 FIX: Dynamic Prime Expansion to accommodate all trunks
        # CRITICAL UPDATE (User Request): Do NOT scan p > 5.
        # High primes act as strict filters on sparse datasets.
        # We disable expansion and force wrapping if needed.
        
        # if num_components >= self.p:
        #      old_p = self.p
        #      # Simple next-prime or just sufficient size
        #      def is_prime(n):
        #          if n < 2: return False
        #          for i in range(2, int(math.isqrt(n)) + 1):
        #              if n % i == 0: return False
        #          return True
        #      
        #      new_p = num_components + 1
        #      while not is_prime(new_p):
        #          new_p += 1
        #          
        #      self.p = new_p
        #      print(f"     ! ADELIC EXPANSION (V31): Increasing p={old_p} -> {self.p} to accommodate {num_components} forest trunks.")
        
        # 3. Multi-Root Assignment (Source Strength Detection)
        roots_dict = {}
        forest_tree = defaultdict(list)
        forest_entities = []
        
        for i, comp in enumerate(sorted(components, key=len, reverse=True)):
            # V.31: Pick root based on "Source Strength" (Out-degree - In-degree)
            # A node that points to many sub-concepts but is pointed to by few is likely a root.
            def get_source_strength(n):
                outs = sum(self.global_directed_adj[n].values())
                ins = 0
                for u in self.global_directed_adj:
                    if n in self.global_directed_adj[u]:
                        ins += self.global_directed_adj[u][n]
                return outs - ins
            
            comp_nodes = sorted(comp, key=get_source_strength, reverse=True)
            root = comp_nodes[0]
            
            # Now self.p is large enough, so we won't wrap/collide aggressively
            cong_class = (i % (self.p - 1)) + 1 
            roots_dict[root] = cong_class
            
            # Build directed local tree
            comp_tree, comp_visited = self._build_trial_tree(root, adj_dict)
            forest_tree.update(comp_tree)
            forest_entities.extend(list(comp_visited))
            
            print(f"       - Component {i+1}: Root '{root}' (Strength: {get_source_strength(root):.1f}) -> Trk {cong_class}")
            # Loop runs for all components now (or until p-1 if we still wanted to limit, but we expanded p)
            # if i >= self.p - 1: break # We allow wrapping now

        # 4. Final Multi-Root BFE Walk
        solver = AlgebraicTextSolver(p=self.p)
        self.global_coordinates, _ = solver._assign_bfe_coordinates(forest_tree, forest_entities, roots_dict)
        
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
            # In V.31 we respect the directed graph: parent -> child
            # We also include neighbors that might be "reversing" but were connected
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
        candidates = [2, 3, 5] # Was [2, 3, 5, 7, 13, 17, 31]
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
                
        # Only switch if improvement is significant? Or just greedy.
        # If best_p != self.p:
        print(f"     ! ROTATION: p={self.p} -> p={best_p} (Min Energy: {min_energy:.4f})")
        self.p = best_p

    def _process_block_sheaf(self, text_block, block_idx):
        """
        Process a text block and return its local manifold (AlgebraicTextSolver result).
        Does NOT update global adjacency (Siloed Local Logic).
        """
        # 1. Spectral Purification
        try:
            # 1. Adelic Separation & Gatekeeper Removal
            # V.15: Every triad (S, V, O) is proof of relevance. Bypass frequency filters.
            
            # Use a dummy entity list to trigger structural parsing in extract_arithmetic_features
            # It will dynamically discover nodes from triads.
            target_primes = sorted(list(set([2, 3, 5, self.p])))
            adelic_features, all_entities = self.featurizer.extract_arithmetic_features(text_block, [], primes=target_primes)
            
            if not all_entities: return None
            
            # 2. Topology Computation (Local Clustering Coefficient)
            # We need G_directed and counts for the expanded entity set
            # Build matrices for the full set of nodes derived from triads
            matrix, counts, G_directed = self.featurizer.build_association_matrix(text_block, all_entities)
            metrics = self.featurizer.calculate_spectral_metrics(all_entities, G_directed, counts)
            classifications = self.featurizer.classify_terms(metrics)
            
            # Adelic Separation: Separate Archimedean Scaffolding from Non-Archimedean Logic
            archimedean = [c for c in all_entities if classifications.get(c) == "ARCHIMEDEAN"]
            non_archimedean = [c for c in all_entities if classifications.get(c) == "NON_ARCHIMEDEAN"]
            
            print(f"     > Adelic Separation: {len(non_archimedean)} Non-Archimedean nodes, {len(archimedean)} Archimedean tags.")
            
            if not non_archimedean: 
                # If everything is star-topology junk, we fallback to the full set or reject block
                print("     ! WARNING: No Non-Archimedean cliques found. Block may be pure scaffolding.")
                return None
            
            # 3. Solver Refactor: Pass the full non-archimedean set directly to the Adelic Solver
            # We need to re-extract features aligned specifically to the non-archimedean clique
            final_features, purified = self.featurizer.extract_arithmetic_features(text_block, non_archimedean, primes=target_primes, strict_entities=True)
            local_counts = final_features.get('counts', {})
            
            # 3. Local Manifold Solution
            solver = AlgebraicTextSolver(p=self.p)
            
            print(f"     > Solving Ramified Manifold: {len(purified)} terms...")
            local_result = solver.solve(final_features, purified, local_counts)
            
            # 4. Energy Trace
            current_energy = 1.0 - local_result['analytic_score']
            self.energy_history.append(current_energy)
            self.spline_trace.append({
                'block': block_idx, 
                'p': self.p, 
                'energy': current_energy, 
                'polynomial': local_result['polynomial'],
                'ramified_edges': local_result.get('ramified_edges', {})
            })
            print(f"     > Local Energy: {current_energy:.4f} (p={self.p})")
            
            return local_result
            
        except Exception as e:
            import sys
            import traceback
            print(f"     ! Error in Block Processing: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None
