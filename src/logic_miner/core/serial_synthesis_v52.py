from .serial_synthesis_v50 import SerialSynthesizerV50
from .algebraic_text import AlgebraicTextSolver
from collections import defaultdict, Counter
import math

class SerialSynthesizerV52(SerialSynthesizerV50):
    """
    Protocol V.52: The Grand Unification.
    Restores the 'Tree Logic' of V.33/V.34 while keeping V.50's Stability.
    
    Attributes:
        - Independent Primes [5, 7, 11] (No Primorial).
        - Trajectory Mode Stabilization.
        - Frequency-Directed Tree Construction.
    """
    def __init__(self, chunk_size=50, momentum=0.3):
        super().__init__(chunk_size=chunk_size, momentum=momentum)
        # Restore Classic Basis
        self.primes = [5, 7, 11] 
        self.final_vectors = {} # term -> {p: coord}
        
    def _process_block(self, text_block, block_idx):
        # 1. Standard Featurization + Momentum
        candidates = self.featurizer.extract_entities(text_block, limit=1000)
        if not candidates: return
        
        # Build Matrix
        matrix_raw, counts, _ = self.featurizer.build_association_matrix(text_block, candidates)
        
        # Apply Spline Momentum (V.50/V.34 Tech)
        matrix_stable = self._apply_momentum(matrix_raw, candidates)
        
        # Update Global Freqs
        for c in candidates:
            self.global_freqs[c] += counts.get(c.replace(" ", "_"), 0)

        # 2. Independent Prime Solving (V.33 Logic)
        for p in self.primes:
            solver = AlgebraicTextSolver(p=p)
            try:
                # We reuse the stable matrix for ALL primes. 
                # This is "The Manifold Hypothesis": One Structure, Many Views.
                res = solver.solve(matrix_stable, candidates, counts) # Use stable matrix!
                coords = res.get('coordinates', {})
                
                # Store Trajectory
                for term, c in coords.items():
                    # Ensure term exists in dict
                    if term not in self.adelic_coords:
                        self.adelic_coords[term] = defaultdict(list)
                        
                    self.adelic_coords[term][p].append(c)
                    
            except Exception as e:
                pass

    def _consolidate_global_lattice(self):
        """
        The Core Restoration: Build the Tree from Trajectories.
        """
        print(f"     > Phase XXI: Grand Unification (Tree Restoration)...")
        
        # 1. Stabilize Vectors (Mode Logic from V.33)
        print(f"       - Stabilizing Vectors via Trajectory Mode...")
        self.final_vectors = {}
        valid_terms = []
        
        # Filter Semantic Stopwords before vector construction
        stopwords = self.STOPWORDS_SEMANTIC 
        
        count = 0 
        for term, prime_map in self.adelic_coords.items():
            if term in stopwords: continue
            
            # Check sufficiency: Must have data for ALL basis primes?
            # V.33 required vectors to be complete?
            # Let's be slightly lenient: Allow if at least 2 primes present?
            # Actually, distance metric fails if missing prime.
            # Let's enforce strictness for Roots, leniency for Leaves?
            # No, strictness ensures quality. 
            if not all(p in prime_map and len(prime_map[p]) > 0 for p in self.primes):
                continue
                
            vector = {}
            for p in self.primes:
                traj = prime_map[p]
                # Use Mode (Most Frequent Coordinate)
                if traj:
                    mode_coord = Counter(traj).most_common(1)[0][0]
                    vector[p] = mode_coord
                else:
                    vector[p] = 0 # Default?
            
            self.final_vectors[term] = vector
            valid_terms.append(term)
            count += 1
            
        print(f"       - Stabilized {count} terms.")
        
        # 2. Build The Tree (Frequency-Directed)
        print(f"       - Constructing Frequency-Directed Hierarchy...")
        self.tree_structure = self._build_divisibility_tree(valid_terms)
        
    def _build_divisibility_tree(self, entities):
        # Restored V.33 Tree Logic
        
        # Sort by Global Frequency (The "Gravity" of the Concept)
        # High Freq -> Likely Root. Low Freq -> Likely Leaf.
        sorted_ents = sorted(entities, key=lambda e: self.global_freqs[e], reverse=True)
        
        tree = defaultdict(list)
        roots = []
        
        total = len(sorted_ents)
        print(f"       - Linking {total} terms...")
        
        for i, child in enumerate(sorted_ents):
            best_parent = None
            max_strength = -1
            
            # Look at higher-frequency terms (Potential Parents)
            # Limit search space for performance (Top 200 parents or previous 200?)
            # V.33 limit was 200.
            potential_parents = sorted_ents[:i]
            if len(potential_parents) > 200:
                potential_parents = sorted_ents[max(0, i-200):i] # Look at *recent* high freq parents?
                # Actually, "Atom" is at index 0. "Energy" at index 1.
                # A rare term at index 400 wants to link to "Atom".
                # So we should look at the TOP frequency terms.
                potential_parents = sorted_ents[:200]
                # Plus maybe local ones?
                # Let's just look at Top 200 global parents for everyone.
                # This ensures the Skeleton is formed by the Core.
            
            child_vec = self.final_vectors[child]
            
            for parent in potential_parents:
                if parent == child: continue
                parent_vec = self.final_vectors[parent]
                
                strength = self._calculate_connection_strength(child_vec, parent_vec)
                
                if strength > max_strength:
                    max_strength = strength
                    best_parent = parent
            
            # Threshold: Must share at least one p-factor logic (Strength >= 1)
            # In V.33 logic: strength = max_p valuation(diff).
            # If diff % p == 0, val >= 1.
            # So strength >= 1 means "Connected in at least one prime".
            if best_parent and max_strength >= 1:
                tree[best_parent].append(child)
            else:
                roots.append(child)
                
        return {'tree': tree, 'roots': roots}

    def _calculate_connection_strength(self, vec_a, vec_b):
        """
        Returns the maximum p-adic valuation of the difference.
        """
        max_v = -1
        for p in self.primes:
            try:
                diff = abs(vec_a[p] - vec_b[p])
                if diff == 0: 
                    v = 10 
                else:
                    v = 0
                    temp = diff
                    while temp % p == 0:
                        v += 1
                        temp //= p
                
                if v > max_v:
                    max_v = v
            except KeyError:
                continue
                
        return max_v
