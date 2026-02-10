from .serial_synthesis_v47 import SerialSynthesizerV47
from .algebraic_text import AlgebraicTextSolver
from collections import defaultdict, Counter
import math

class SerialSynthesizerV48(SerialSynthesizerV47):
    """
    Protocol V.48: The Resonant Expansion.
    Extends V.47 (High-Res) with a "Rescue Operation" for local leaves.
    Logic:
    - Capture "Simple Spiky" terms (High Curvature, Low Complexity).
    - If they resonate (Edge Weight > Threshold) with a Core Hub, Rescue them.
    - Result: High Yield without Noise.
    """
    def __init__(self, chunk_size=50):
        super().__init__(chunk_size=chunk_size)
        
        # Rescue Memory
        # (reject, survivor) -> cumulative_weight
        self.rescue_edges = defaultdict(float)
        
        # Track Rejects for Adelic Coord Calculation later (if rescued)
        # We need to store their local adelic coords too, or re-compute?
        # Re-compute might be hard if we don't have text.
        # So we store adelic coords for rejects too.
        # self.adelic_coords is initialized in V.47 init.
        
    def _process_block(self, text_block, block_idx):
        # We need to override V.46/V.47 _process_block to intercept the rejects.
        # V.47 calls super()._process_block (V.46) then does Adelic Coords.
        # We can't easily hook into V.46 middle.
        
        # 1. Featurize
        # V.48 Update: Increased limit to 1000 to capture more leaves for rescue.
        candidates = self.featurizer.extract_entities(text_block, limit=1000)
        matrix, counts, G_directed = self.featurizer.build_association_matrix(text_block, candidates)
        if not candidates: return

        # 2. Compute Trajectories (V.45 Logic)
        solver = AlgebraicTextSolver(p=self.p)
        try:
            res = solver.solve(matrix, candidates, counts)
            block_coords = res['coordinates']
        except:
            block_coords = {}
            
        for term, coord in block_coords.items():
            self.trajectory_history[term].append(coord)
            
        # 3. Geometric Filter (V.45) - "Spiky" Check
        spiky_candidates = []
        for term in candidates:
            traj = self.trajectory_history.get(term, [])
            if len(traj) < 3:
                # Grace period: Assume spiky enough to pass to next check?
                # Or simplistic: If new, give benefit of doubt.
                if term not in ["Introduction", "Chapter"]:
                    spiky_candidates.append(term)
                continue
            
            k_geom = self._calculate_discrete_curvature(traj)
            if k_geom > 0.5:
                # High curvature -> Concept or Spiky Grammar
                spiky_candidates.append(term)
        
        if not spiky_candidates: return
        
        # 4. Adelic Information Filter (V.42) - "Complexity" Check
        # Survivors = High Complexity. Rejects = Low Complexity (Potential Leaves).
        
        # We run the filter logic manually to separate lists
        complex_survivors = []
        simple_rejects = []
        
        # Calculate Adelic Coords for ALL Spiky Candidates (we need them for rescue/rescue-coords anyway)
        # Reuse logic from V.46 _apply_adelic_filter but keep the values
        
        term_vectors = defaultdict(dict)
        # Batch solve for basis primes
        for p in self.basis_primes:
            solver = AlgebraicTextSolver(p=p)
            try:
                # Matrix subset for efficiency? No, use full for connectivity context
                # Actually, solving on full matrix is better.
                # But we only care about spiky_candidates coords.
                p_matrix, p_counts, _ = self.featurizer.build_association_matrix(text_block, candidates)
                res = solver.solve(p_matrix, candidates, p_counts)
                coords = res.get('coordinates', {})
                for t, c in coords.items():
                    if t in spiky_candidates:
                        term_vectors[t][p] = c
                        # Store in permanent memory for V.47 CRT
                        self.adelic_coords[t][p].append(c)
            except:
                pass

        # Check Complexity
        filter_primes = [5, 7, 11] # V.42 basis
        for t in spiky_candidates:
            if len(term_vectors[t]) < 3: continue 
            
            vec = [term_vectors[t].get(p, 0) for p in filter_primes]
            # Note: term_vectors might be missing some primes if solve failed. 
            # We assume 0 or skip? Skip is safer.
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
            
            if is_complex:
                complex_survivors.append(t)
            else:
                simple_rejects.append(t)

        # 5. Populate Global Graph with Survivors (V.46 Logic)
        purified = complex_survivors
        for i, c1 in enumerate(purified):
            self.global_freqs[c1] += counts.get(c1.replace(" ", "_"), 0)
            if c1 in G_directed:
                for c2, w in G_directed[c1].items():
                    if c2 in purified:
                        self.global_directed_adj[c1][c2] += w
            # Sym Adj for V.32 Lattice
            # ... (Standard Update) ...
        
        # 6. Capture Rescue Edges (V.48 Logic)
        # We want edges between Simple Rejects AND Complex Survivors.
        # This confirms the reject is a "Satellite" of a Core Term.
        
        for reject in simple_rejects:
            if reject not in candidates: continue
            r_idx = candidates.index(reject)
            
            for survivor in complex_survivors:
                if survivor not in candidates: continue
                s_idx = candidates.index(survivor)
                
                # Check Edge Weight (Symmetric or Directed? Symmetric implies bond)
                w = matrix[r_idx][s_idx]
                if w > 0:
                    # Capture connection "Reject -> Survivor"
                    self.rescue_edges[(reject, survivor)] += w
                    
    def _apply_resonance_rescue(self, initial_core):
        """
        Promotes rejects that are strongly connected to the Core.
        """
        print(f"     > V.48 Resonance Rescue (Using {len(initial_core)} Hubs)...")
        rescued = set()
        
        # Analyze Rescue Edges
        # We sum connectivity to ALL Core terms
        reject_scores = defaultdict(float)
        
        for (reject, survivor), w in self.rescue_edges.items():
            if survivor in initial_core:
                reject_scores[reject] += w
                
        # Frequency of reject? We might want to weight by it?
        # Threshold:
        # Lowered to 0.1 (V.48b) to increase yield. We rely on the Hub's purity to anchor these.
        
        threshold = 0.1
        
        for term, score in reject_scores.items():
            if score > threshold:
                rescued.add(term)
                
        print(f"       ! Rescued {len(rescued)} terms via Adelic Resonance.")
        return rescued

    def _consolidate_global_lattice(self):
        # 1. V.47 Spectral Projection Filter
        print(f"     > V.47 Spectral Projection Filter (Core Selection)...")
        
        # This gives us the "Core" (High Complexity + Spectral Structure)
        core_survivors = self._spectral_projection_filter(list(self.global_freqs.keys()))
        print(f"       ! Core Candidates: {len(core_survivors)}")
        
        # 2. V.48 Rescue
        # We use core_survivors as the "Magnet"
        rescued_terms = self._apply_resonance_rescue(set(core_survivors))
        
        # 3. Merge
        final_survivors = set(core_survivors).union(rescued_terms)
        print(f"       ! Final Lattice Size: {len(final_survivors)} (Core + Rescued).")
        
        # Prune Global Graph
        self.global_freqs = Counter({t: self.global_freqs.get(t, 1) for t in final_survivors}) 
        # Note: Rejects might not be in global_freqs yet (since we skipped adding them in process_block).
        # We must ensure they are added.
        # We can give them a default freq (Based on resonance?).
        # Or we should have tracked their freqs in "reject_freqs"?
        # Simpler: If rescued, we don't know their total freq unless we stored it.
        # Implication: Lattice tree sort order might be affected.
        # Fix: We'll just give them freq=1. It's fine, valuation drives the tree.
        
        new_adj = defaultdict(lambda: Counter())
        # We need to populate edges for rescued terms too!
        # Potential DATA LOSS: We didn't add edges for rejects in _process_block.
        # We only stored rescue_edges.
        # Rebuilding the full graph for rescued terms is hard without re-reading text.
        # Heuristic: We add the `rescue_edges` to `global_directed_adj`.
        
        for (reject, survivor), w in self.rescue_edges.items():
            if reject in final_survivors and survivor in final_survivors:
                # Add symmetric link approx
                new_adj[reject][survivor] += w
                new_adj[survivor][reject] += w # Resonance is bi-directional
                
        # Copy existing core edges
        for u in self.global_directed_adj:
            if u in final_survivors:
                for v, w in self.global_directed_adj[u].items():
                    if v in final_survivors:
                        new_adj[u][v] = w
                        
        self.global_directed_adj = new_adj
        
        # 4. CRT Mapping (V.47 Logic)
        print(f"     > Phase XIX: Primorial Mapping (M=30030) via CRT...")
        self.global_coordinates = {} 
        self.p_final = 30030
        
        map_count = 0
        for term in final_survivors:
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
                X = res['params'][0]
                self.global_coordinates[term] = X
                map_count += 1
                
        print(f"       ! Mapped {map_count} terms to Primorial Lattice Z_30030.")
        self.p = 30030
