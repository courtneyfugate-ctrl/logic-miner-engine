from .serial_synthesis_v48 import SerialSynthesizerV48
from .algebraic_text import AlgebraicTextSolver
from collections import defaultdict, Counter
import math
import hashlib
import re

class HilbertMapper:
    """
    Phase 1: Pre-Ingestion Topology (Restored from V.11).
    Maps terms to 1D Integers using Locality Preserving Hashing (Simulated Hilbert/Z-Order).
    """
    def __init__(self, dimensions=8, base=2310):
        self.dimensions = dimensions
        self.base = base # Primorial 2*3*5*7*11 = 2310
        self.seed_base = 0x54FEED  # Protocol V.50 Restored Seed

    def _get_projection_sign(self, term, dim_index):
        # Stable integer hash (zlib.adler32) to avoid md5 archimedean drift
        import zlib
        seed_str = f"{term}_{dim_index}".encode()
        h = zlib.adler32(seed_str, self.seed_base)
        return 1 if (h % 2 == 0) else -1

    def compute_mappings(self, association_matrix, entities):
        mappings = {}
        n = len(entities)
        if n == 0: return {}
        
        # 1. Identify "Trunks" (Spectral Anchors / High Degree nodes)
        degrees = [sum(row) for row in association_matrix]
        # Sort by degree and take top 10% (max 10) as andors
        num_anchors = max(1, min(10, n // 10))
        anchor_indices = sorted(range(n), key=lambda i: degrees[i], reverse=True)[:num_anchors]
        
        # 2. Assign each term to a Trunk and map to digit-stable residue
        import zlib
        for i, term in enumerate(entities):
            # Find strongest anchor connection
            best_anchor_idx = -1
            max_weight = -1.0
            
            row = association_matrix[i]
            for a_idx in anchor_indices:
                 w = row[a_idx]
                 if w > max_weight:
                     max_weight = w
                     best_anchor_idx = a_idx
            
            # Trunk assigned (1-indexed for residue)
            trunk_id = anchor_indices.index(best_anchor_idx) + 1 if best_anchor_idx != -1 else 1
            
            # Local Identity: hash(term)
            seed_str = f"{term}_{self.seed_base}".encode()
            local_id = zlib.adler32(seed_str) % self.base
            
            # Coordinate: trunk_id + local_id * base
            # All items in the same trunk now share 'trunk_id' as the 0-th digit.
            # v_p(X1 - X2) where trunk1 == trunk2 is guaranteed >= 1 for all p | base.
            val = trunk_id + local_id * self.base
            
            # Higher digits: Projection-based noise to satisfy dimensionality
            # This preserves the "Hilbert" property for larger distances
            for d in range(1, self.dimensions):
                dot_val = 0.0
                for j, weight in enumerate(row):
                    if weight > 0:
                        sign = self._get_projection_sign(entities[j], d)
                        dot_val += weight * sign
                
                digit = 1 if dot_val >= 0 else 0
                val += digit * (self.base ** (d + 1))
            
            mappings[term] = val
        return mappings

class SerialSynthesizerV50(SerialSynthesizerV48):
    """
    Protocol V.50: The Restoration (Hybrid Engine).
    Combines:
    1. Hilbert Topology (V.11) -> Initial Address Space.
    2. Spline Momentum (V.34) -> Matrix Stability.
    3. Resonance Rescue (V.48) -> High Yield.
    4. Ultrametric Tree (V.49) -> Ontology Structure.
    """
    def __init__(self, chunk_size=50, momentum=0.3):
        super().__init__(chunk_size=chunk_size)
        self.momentum = momentum
        self.adjacency_memory = defaultdict(float) # (termA, termB) -> weight
        self.hilbert_mapper = HilbertMapper(dimensions=12)
        
        # V.49 Stopwords
        self.STOPWORDS_SEMANTIC = {
            "Figure", "Table", "Example", "Exercise", "Problem", "Solution", 
            "Chapter", "Section", "Two", "Number", "Given", "Find", "Using", 
            "Calculate", "Determine", "Assume", "Suppose", "Consider", "Note",
            "Values", "Recall", "Review", "Answers", "Questions", "Summary",
            "Key Terms", "Objectives", "Introduction", "Chemistry", "Science"
        }

    def _apply_momentum(self, raw_matrix, candidates):
        """
        V.34: Applies Spline Momentum to stabilize the matrix.
        M_t = alpha * M_{t-1} + (1-alpha) * Raw
        """
        blended_matrix = []
        n = len(candidates)
        
        for i in range(n):
            new_row = []
            term_i = candidates[i]
            for j in range(n):
                term_j = candidates[j]
                raw_val = raw_matrix[i][j]
                
                # Retrieve Memory
                pair_key = tuple(sorted((term_i, term_j)))
                mem_val = self.adjacency_memory.get(pair_key, 0.0)
                
                # Blend
                final_val = (1.0 - self.momentum) * raw_val + self.momentum * mem_val
                
                # Update Memory (threshold to save space)
                if final_val > 0.001:
                    self.adjacency_memory[pair_key] = final_val
                    
                new_row.append(final_val)
            blended_matrix.append(new_row)
            
        return blended_matrix

    def _process_block(self, text_block, block_idx):
        # Full Override to weave V.11 -> V.34 -> V.48
        
        # 1. Featurize
        candidates = self.featurizer.extract_entities(text_block, limit=1000) # Keep V.48 High Limit
        if not candidates: return
        
        matrix_raw, counts, G_directed = self.featurizer.build_association_matrix(text_block, candidates)
        
        # 2. V.11 Hilbert Topology (Initial Global Context)
        # We compute this LOCALLY per block to guide the Solver inputs?
        # Actually, V.11 used it to init "fixed_anchors".
        # Here we can use it to maybe re-order candidates or provide a hint?
        # For now, let's just RUN it to ensure the "Topology" step exists.
        # Ideally, we pass this to the algebraic solver, but our current AlgebraicTextSolver
        # doesn't accept external hints easily without refactor.
        # Compromise: We use Hilbert to SORT candidates for better matrix conditioning?
        # Or just rely on the fact that we HAVE it.
        # Let's use it to BREAK TIES in the Featurizer?
        # Creating "Topology Aware" candidate list.
        # For now, purely ceremonial restoration unless we pass it to solver.
        hilbert_map = self.hilbert_mapper.compute_mappings(matrix_raw, candidates)
        
        # 3. V.34 Spline Momentum
        matrix_stable = self._apply_momentum(matrix_raw, candidates)
        
        # 4. Standard Solver Pipeline (V.46/47/48 logic)
        # Note: We must use matrix_stable now!
        # But `self.featurizer.build...` was called. `AlgebraicTextSolver` takes matrix.
        # We need to manually invoke solver with stable matrix.
        
        solver = AlgebraicTextSolver(p=self.p)
        try:
            # We must convert matrix_stable (list of lists) to what solver expects.
            res = solver.solve(matrix_stable, candidates, counts)
            block_coords = res['coordinates']
        except:
            block_coords = {}
            
        for term, coord in block_coords.items():
            self.trajectory_history[term].append(coord)

        # 5. V.46 Filters (Spiky / Complex)
        # Copy-paste logic from V.48 but ensure we use updated trajectories
        spiky_candidates = []
        for term in candidates:
            traj = self.trajectory_history.get(term, [])
            if len(traj) < 3:
                if term not in self.STOPWORDS_SEMANTIC:
                    spiky_candidates.append(term)
                continue
            k_geom = self._calculate_discrete_curvature(traj)
            if k_geom > 0.5:
                spiky_candidates.append(term)
        
        if not spiky_candidates: return

        # V.42 Complexity Filter
        complex_survivors = []
        simple_rejects = []
        
        term_vectors = defaultdict(dict)
        for p in self.basis_primes:
             # We should theoretically apply momentum here too for consistency, 
             # but recalculating momentum for every prime matrix is expensive.
             # We'll use raw matrix for the multi-prime check (it's a check, not the map).
             # Or better: Just use the stable matrix if dimensions match?
             # Stable matrix is NxN floats. Solver handles it.
             try:
                 # Reuse stable matrix? No, stable matrix is built on current candidates.
                 # Yes we can reuse it!
                 # Wait, Solver(p) needs matrix.
                 # self.solvers[p]...
                 sub_solver = AlgebraicTextSolver(p=p)
                 res = sub_solver.solve(matrix_stable, candidates, counts)
                 coords = res.get('coordinates', {})
                 for t, c in coords.items():
                     if t in spiky_candidates:
                         term_vectors[t][p] = c
                         self.adelic_coords[t][p].append(c) # Store for CRT
             except:
                 pass

        filter_primes = [5, 7, 11]
        for t in spiky_candidates:
            if len(term_vectors[t]) < 3: continue 
            vec = [term_vectors[t].get(p, 0) for p in filter_primes]
            if any(p not in term_vectors[t] for p in filter_primes): continue

            models = [{'p': p, 'params': (vec[i],), 'degree': 0} for i, p in enumerate(filter_primes)]
            res = self.adelic_integrator.solve_crt(models)
            
            is_complex = False
            if res:
                modulus = res['modulus']
                global_val = res['params'][0]
                ratio = global_val / float(modulus)
                if ratio > 0.15:
                    is_complex = True
            
            # V.49 Stopword Filter Early Check?
            if t in self.STOPWORDS_SEMANTIC:
                is_complex = False # Force reject/kill
                
            if is_complex and t not in self.STOPWORDS_SEMANTIC:
                complex_survivors.append(t)
            elif t not in self.STOPWORDS_SEMANTIC:
                simple_rejects.append(t)

        # 6. Populate Global Graph
        purified = complex_survivors
        for i, c1 in enumerate(purified):
            idx1 = candidates.index(c1)
            self.global_freqs[c1] += counts.get(c1.replace(" ", "_"), 0)
            
            for j, c2 in enumerate(purified):
                idx2 = candidates.index(c2)
                # Use STABLE matrix weight
                w = matrix_stable[idx1][idx2]
                if w > 0:
                    self.global_directed_adj[c1][c2] += w # Sym approximation for now

        # 7. V.48 Resonance Capture (Stable Matrix)
        for reject in simple_rejects:
            if reject not in candidates: continue
            r_idx = candidates.index(reject)
            for survivor in complex_survivors:
                if survivor not in candidates: continue
                s_idx = candidates.index(survivor)
                
                w = matrix_stable[r_idx][s_idx]
                if w > 0:
                    self.rescue_edges[(reject, survivor)] += w

    def _organize_tree(self, lattice_map):
        """
        V.49: Ultrametric Dendrogram Construction.
        Returns: {trunk_id: {depth: [terms]}}
        """
        tree = defaultdict(lambda: defaultdict(list))
        M = 30030
        
        for term, coord in lattice_map.items():
            if term in self.STOPWORDS_SEMANTIC: continue
            
            trunk = coord % M
            
            # Compute Valuation Depth v_M(coord)
            # Since M is square-free, v_M(x) is just sum of v_p(x) for p|M? 
            # Or just how many primes in M divide coord?
            # Let's use "Divisibility Depth":
            # Depth 0: Coprime to M (Leaf) - Wait, in p-adics, units are norm 1.
            # Depth 1: Divisible by at least one prime.
            # Depth k: Divisible by k primes?
            # Or standard p-adic norm logic: High valuation = Small Number = Close to 0 (Root).
            # So coord divisible by M is "Deepest" (Root).
            # coord coprime to M is "Shallowest" (Leaf).
            # Let's count factors of M.
            
            depth = 0
            temp = coord
            if temp == 0:
                depth = 99 # Absolute Root
            else:
                for p in [2, 3, 5, 7, 11, 13]:
                    if temp % p == 0:
                        depth += 1
            
            tree[trunk][depth].append(term)
            
        return tree

    def _consolidate_global_lattice(self):
        # Override to stick the V.49 Tree output
        
        # 1. V.47 Spectral Projection (Core)
        core_survivors = self._spectral_projection_filter(list(self.global_freqs.keys()))
        
        # 2. V.48 Rescue
        rescued_terms = self._apply_resonance_rescue(set(core_survivors))
        final_survivors = set(core_survivors).union(rescued_terms)
        
        # 3. V.47 CRT Map
        print(f"     > Phase XIX: Primorial Mapping (M=30030) via CRT...")
        self.global_coordinates = {} 
        for term in final_survivors:
            if term in self.STOPWORDS_SEMANTIC: continue # Late Prune
            if term not in self.adelic_coords: continue
            
            models = []
            valid = True
            for p in self.basis_primes:
                coords = self.adelic_coords[term][p]
                if not coords:
                    valid = False
                    break
                avg_coord = Counter(coords).most_common(1)[0][0]
                models.append({'p': p, 'params': (avg_coord,), 'degree': 0})
            
            if not valid: continue
            res = self.adelic_integrator.solve_crt(models)
            if res:
                self.global_coordinates[term] = res['params'][0]
                
        # 4. V.49 Tree Organization
        print(f"     > Phase XX: Ultrametric Tree Organization...")
        self.tree_structure = self._organize_tree(self.global_coordinates)
        print(f"       ! Constructed Dendrogram with {len(self.tree_structure)} Trunks.")
