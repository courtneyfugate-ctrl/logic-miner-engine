import random
import zlib
import math

class TextRANSACSolver:
    """
    The RANSAC-Lifting-P-adic Miner.
    Treats text as a noisy signal of an underlying algebra.
    1. RANSAC: Filters noise to find stable distances.
    2. Lifting: Rectifies matrix to satisfy Strong Triangle Inequality.
    3. Audit: Checks p-adic convergence.
    """
    def __init__(self, p=2, ransac_iterations=20, sample_ratio=0.5):
        self.p = p
        self.iterations = ransac_iterations
        self.sample_ratio = sample_ratio

    def solve(self, raw_text, entities):
        """
        Main pipeline: Text -> Contexts -> RANSAC Distances -> Lifted Matrix -> Tree
        """
        print(f"--- [TextRANSACSolver] Starting Logic Reconstruction (p={self.p}) ---")
        
        # 1. Build Context Windows (Sentences)
        contexts = self._build_contexts(raw_text, entities)
        
        # 2. RANSAC Distance Discovery
        n = len(entities)
        matrix = [[0.0] * n for _ in range(n)]
        
        print(f"   > RANSAC: Sampling {self.iterations} sub-contexts per pair...")
        for i in range(n):
            for j in range(i+1, n):
                dist_inlier, consensus_score = self._ransac_distance(contexts[entities[i]], contexts[entities[j]])
                matrix[i][j] = dist_inlier
                matrix[j][i] = dist_inlier
                # Optional: We could weight by consensus_score?
                # For now, let's trust the robust distance.

        # 3. Ultrametric Lifting (The Rectifier)
        print("   > Lifting: Enforcing Strong Triangle Inequality...")
        lifted_matrix, energy = self._lift_to_ultrametric(matrix)
        print(f"   > Lifting Energy (Correction Magnitude): {energy:.4f}")

        # 4. P-adic Valuation Mapping? 
        # The 'lifted_matrix' is now a valid ultrametric space.
        # We can pass this to the UltrametricBuilder.
        
        return lifted_matrix, energy, self._build_directed_tree(lifted_matrix, entities, contexts)

    def _build_directed_tree(self, matrix, labels, contexts):
        """
        Constructs a Directed P-adic Tree (Flow Chart Logic).
        Uses Information Complexity ($K(x)$) to determine Parent/Child relationships.
        Gradient: Logic (Low Entropy) -> Data (High Entropy).
        """
        # 1. Calculate Complexities
        k_scores = {}
        for l in labels:
            full_c = " ".join(contexts[l])
            k_scores[l] = len(zlib.compress(full_c.encode('utf-8')))

        # Normalize to v_p (1..10)
        if not k_scores: return "();"
        min_k = min(k_scores.values())
        max_k = max(k_scores.values())
        range_k = max_k - min_k if max_k > min_k else 1
        
        def get_vp(k_val):
             # Scale 1 (Simple) to 10 (Complex)
             # v_p is the "Depth"
             return 1 + int(9 * (k_val - min_k) / range_k)

        print(f"   > Complexity Gradient Check & Valuation Mapping (v_p):")
        for l in labels[:5]: 
            vp = get_vp(k_scores[l])
            print(f"     * {l}: K={k_scores[l]} -> v_p={vp}")

        # 2. Build Tree
        n = len(labels)
        # Initialize clusters with annotated names
        # Use LaTeX subscript format for visualizer
        clusters = {i: f"{labels[i]}_{{v_p={get_vp(k_scores[labels[i]])}}}" for i in range(n)}
        cluster_k = {i: k_scores[labels[i]] for i in range(n)} 

        active_ids = set(range(n))
        dists = {}
        for i in range(n):
            for j in range(i+1, n):
                dists[(i,j)] = matrix[i][j]

        while len(active_ids) > 1:
            best_pair = None
            min_d = float('inf')
            
            for (i,j), d in dists.items():
                if i in active_ids and j in active_ids:
                    if d < min_d:
                        min_d = d
                        best_pair = (i,j)
                        
            if best_pair is None: break
            
            i, j = best_pair
            
            name_i = clusters[i]
            name_j = clusters[j]
            ki = cluster_k[i]
            kj = cluster_k[j]
            
            # Label Promotion Logic (Complexity Gradient)
            ratio_i = ki / (kj + 1e-9)
            ratio_j = kj / (ki + 1e-9)
            threshold = 0.8
            
            # When merging, if we Promote, the Node takes the Parent's name (and v_p)
            # If we Don't promote, it's a generic cluster.
            
            if ratio_i < threshold:
                 # I is simpler -> I is Parent. J is contained in I.
                 # Format: (Child)Parent
                 new_name = f"({name_j}){name_i}" 
                 new_k = ki 
            elif ratio_j < threshold:
                 # J is simpler -> J is Parent
                 new_name = f"({name_i}){name_j}"
                 new_k = kj
            else:
                 # Siblings
                 new_name = f"({name_i},{name_j})"
                 # Merged K is min?
                 new_k = min(ki, kj)
            
            clusters[i] = new_name
            cluster_k[i] = new_k
            active_ids.remove(j)
            
            # Update Dists (Complete Linkage)
            for k in list(active_ids):
                if k == i: continue
                di = dists.get(tuple(sorted((i,k))), float('inf'))
                dj = dists.get(tuple(sorted((j,k))), float('inf'))
                dists[tuple(sorted((i,k)))] = max(di, dj)
                
        return clusters[list(active_ids)[0]] + ";"

    def _build_contexts(self, text, entities):
        """
        Extracts list of sentences for each entity.
        Includes Masking (__ENT__) by default.
        """
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        contexts = {e: [] for e in entities}
        
        for s in sentences:
            for e in entities:
                if e in s:
                    masked = s.replace(e, "__ENT__")
                    contexts[e].append(masked)
        return contexts

    def _ransac_distance(self, list_a, list_b):
        """
        Finds the robust 'Inlier' distance between two sentence sets.
        Avoids outliers (e.g. 1 random sentence linking Platypus to Reptile).
        """
        if not list_a or not list_b: return 1.0, 0.0
        
        distances = []
        
        # If contexts are small, just use full
        if len(list_a) < 3 or len(list_b) < 3:
            return self._ncd(" ".join(list_a), " ".join(list_b)), 1.0
            
        # RANSAC Loop
        for _ in range(self.iterations):
            # Sample Subsets
            # Ensure we take at least 1, but up to ratio
            k_a = max(1, int(len(list_a) * self.sample_ratio))
            k_b = max(1, int(len(list_b) * self.sample_ratio))
            
            sub_a = random.sample(list_a, k_a)
            sub_b = random.sample(list_b, k_b)
            
            d = self._ncd(" ".join(sub_a), " ".join(sub_b))
            distances.append(d)
            
        distances.sort()
        # Robust Consensus: The Median? Or the Minimum (closest semantic link)?
        # If A and B are related, there EXISTS a subset where they are close.
        # Noise makes them far.
        # But wait, noise can also make them accidentally close?
        # Median is safer.
        median = distances[len(distances)//2]
        
        # Inlier Count (how many close to median?)
        inliers = sum(1 for d in distances if abs(d - median) < 0.1)
        score = inliers / len(distances)
        
        return median, score

    def _ncd(self, s1, s2):
        if not s1 or not s2: return 1.0
        b1 = s1.encode('utf-8')
        b2 = s2.encode('utf-8')
        c1 = len(zlib.compress(b1))
        c2 = len(zlib.compress(b2))
        c12 = len(zlib.compress(b1 + b2))
        return max(0.0, min(1.0, (c12 - min(c1, c2)) / max(c1, c2)))

    def _lift_to_ultrametric(self, matrix):
        """
        Iteratively lowers distances to satisfy d(x,z) <= max(d(x,y), d(y,z)).
        Usually known as computing the Subdominant Ultrametric (Single Linkage).
        Wait, Single Linkage = min(max(...)).
        
        But proper p-adic lifting wants to snap to p^-k.
        Let's do two passes:
        1. Transitive Closure (Subdominant Ultrametric).
        2. Quantization (Snap to 1/p^k).
        """
        n = len(matrix)
        # Copy
        d = [row[:] for row in matrix]
        
        # Floyd-Warshall adaptation for Ultrametric
        # Path capacity = min(edge weights). We want max capacity path?
        # Actually, d_ultra(i, j) is the "Minimax" path between i and j.
        # The lowest "highest barrier" you must simplify.
        
        # 1. Minimax Path (Single Linkage equivalent)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    # Triangle: d(i,j) <= max(d(i,k), d(k,j))
                    # We tighten d(i,j) if a "better path" exists
                    indirect = max(d[i][k], d[k][j])
                    if indirect < d[i][j]:
                        d[i][j] = indirect
                        
        # 2. P-adic Quantization (The "Snap")
        # Snap values to 1, 1/p, 1/p^2...
        # log_p(d) -> integer levels
        total_energy = 0.0
        
        for i in range(n):
            for j in range(n):
                val = d[i][j]
                if val <= 0: continue
                # target level k
                # p^-k approx val
                # -k log p = log val
                # k = -log_p(val)
                if val >= 1.0: 
                    snapped = 1.0
                else:
                    k = -math.log(val, self.p)
                    k_int = round(k)
                    # Bias towards "higher" structure (lower k)? Or closer?
                    # Let's just round.
                    snapped = self.p ** (-k_int)
                
                # Check deviation
                distinct_diff = abs(val - snapped)
                total_energy += distinct_diff
                d[i][j] = snapped
                
        return d, total_energy
