
from .text_featurizer import TextFeaturizer
from .algebraic_text import AlgebraicTextSolver
from collections import defaultdict, Counter
import math

class SerialSynthesizerV33:
    """
    Protocol V.33: The Ontology Extractor.
    Integrates:
    1. Multi-Adelic Fields (Q5 x Q7 x Q11)
    2. Curvature-Weighted Promotion
    3. Divisibility-Based Hierarchy
    """
    def __init__(self, chunk_size=50):
        self.primes = [5, 7, 11]
        self.chunk_size = chunk_size
        self.history = {p: defaultdict(list) for p in self.primes} # p -> entity -> [coords]
        self.global_freqs = Counter()
        self.final_vectors = {} # entity -> (v5, v7, v11)
        
        self.featurizer = TextFeaturizer()
        self.solvers = {p: AlgebraicTextSolver(p=p) for p in self.primes}
        
    def fit_stream(self, reader, max_pages=None):
        total_pages = len(reader.pages)
        effective = min(total_pages, max_pages) if max_pages else total_pages
        
        print(f"--- [V.33] Multi-Adelic Serial Synthesis ({effective} pages) ---")
        
        # 1. Serial Processing (Trajectory Assembly)
        for start_idx in range(0, effective, self.chunk_size):
            end_idx = min(start_idx + self.chunk_size, effective)
            print(f"   > Processing Block {start_idx}-{end_idx}...")
            
            text = ""
            for i in range(start_idx, end_idx):
                text += reader.pages[i].extract_text() + "\n"
                
            self._process_block(text)
            
        # 2. Curvature Gating & Vector Synthesis
        print("\n   > Phase II: Curvature Gating & Vector Synthesis...")
        entities = list(self.global_freqs.keys())
        purified_entities = []
        
        for e in entities:
            # Curvature Check
            is_stable = True
            curvature_score = 0
            
            vec = []
            for p in self.primes:
                traj = self.history[p].get(e, [])
                if not traj: 
                    vec.append(0)
                    continue
                
                # Compute Curvature
                k = 0
                if len(traj) >= 3:
                     for i in range(1, len(traj)-1):
                         k += abs(traj[i+1] - 2*traj[i] + traj[i-1])
                
                curvature_score += k
                # Average coordinate as the final valuation component?
                # Or the most recent? Or the mode?
                # Let's use the Mode (most frequent stable position)
                if traj:
                    mode_coord = Counter(traj).most_common(1)[0][0]
                    vec.append(mode_coord)
                else:
                    vec.append(0)
            
            # Gating Threshold: Normalize by length of trajectory?
            # Simple heuristic: If total curvature > 10 (very unstable), demote?
            # Research Note said: High curvature = unstable.
            # We'll store the score and sort later.
            
            self.final_vectors[e] = tuple(vec)
            if curvature_score < 20.0: # Permissive threshold for full run
                purified_entities.append(e)
            else:
                # print(f"     [Dropped] {e} (Curvature {curvature_score:.1f})")
                pass
                
        # 3. Divisibility Lattice Construction
        print("\n   > Phase III: Divisibility Lattice Construction...")
        tree = self._build_divisibility_tree(purified_entities)
        
        return {
            'tree': tree,
            'vectors': self.final_vectors,
            'primes': self.primes,
            'entities': purified_entities
        }

    def _process_block(self, text):
        # Featurize once
        candidates = self.featurizer.extract_entities(text, limit=400)
        if not candidates: return
        
        # Update Freqs
        _, counts, _ = self.featurizer.build_association_matrix(text, candidates)
        for c in candidates:
            # Simple count update
            self.global_freqs[c] += counts.get(c.replace(" ", "_"), 0)
            
        # Multi-Adelic Solving
        for p in self.primes:
            # We must rebuild matrix for each p? No, matrix is real/integer.
            # But purification might differ?
            # For efficiency, reuse matrix.
            
            # Simple Purification for solver stability
            # Top 100 per block
            local_cands = sorted(candidates, key=lambda x: counts.get(x.replace(" ", "_"), 0), reverse=True)[:100]
            
            # Build matrix for these
            mat, local_counts, _ = self.featurizer.build_association_matrix(text, local_cands)
            
            # Solve
            res = self.solvers[p].solve(mat, local_cands, local_counts)
            coords = res['coordinates']
            
            # Record Trajectory
            for e, c in coords.items():
                self.history[p][e].append(c)

    def _get_vp_diff(self, vec_x, vec_y):
        # Max p-adic valuation of difference across all fields
        # v(x, y) = max_i v_{pi}(x_i - y_i)
        
        max_v = -1
        
        for i, p in enumerate(self.primes):
            diff = abs(vec_x[i] - vec_y[i])
            if diff == 0: continue # Distinct check handled outside?
            
            v = 0
            temp = diff
            while temp > 0 and temp % p == 0:
                v += 1
                temp //= p
            
            if v > max_v:
                max_v = v
                
        return max_v

    def _build_divisibility_tree(self, entities):
        # Sort by Global Frequency (Generative Precedence)
        sorted_ents = sorted(entities, key=lambda e: self.global_freqs[e], reverse=True)
        
        tree = defaultdict(list)
        roots = [] 
        
        # Linkage
        for i, child in enumerate(sorted_ents):
            best_parent = None
            max_strength = -1
            
            # Look at higher frequency candidates
            # Limit scope to top 200 parents for speed in full run?
            potential_parents = sorted_ents[:i]
            if len(potential_parents) > 200:
                potential_parents = potential_parents[-200:] # Closest in frequency? Or top absolute?
                # Actually, parents should be truly fundamental, so maybe Top 200 absolute freq.
                potential_parents = sorted_ents[:200]
                if child in potential_parents: potential_parents = sorted_ents[:i]
            
            child_vec = self.final_vectors[child]
            
            for parent in potential_parents:
                if parent == child: continue
                parent_vec = self.final_vectors[parent]
                
                # Check divisibility
                strength = self._get_vp_diff(child_vec, parent_vec)
                
                if strength > max_strength:
                    max_strength = strength
                    best_parent = parent
                    
            if best_parent and max_strength >= 1:
                tree[best_parent].append(child)
            else:
                roots.append(child)
                
        return {'tree': tree, 'roots': roots}
