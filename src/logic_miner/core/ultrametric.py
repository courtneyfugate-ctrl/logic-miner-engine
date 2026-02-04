class UltrametricBuilder:
    """
    Builds p-adic / hierarchical trees from distance matrices.
    Implements standard Agglomerative Clustering which constructs the 
    Bruhat-Tits tree (p-adic building).
    """
    def __init__(self):
        pass

    def build_tree(self, labels, distance_matrix):
        """
        labels: list of strings (e.g. Species Names)
        distance_matrix: NxN matrix of floats/ints.
        Returns: Newick string format of the tree.
        """
        if not labels: return ""
        n = len(labels)
        
        # Clusters: initially each label is a cluster
        clusters = {i: labels[i] for i in range(n)}
        
        # Active indices
        active = set(range(n))
        
        # Working distance dict: (i, j) -> dist
        dists = {}
        for i in range(n):
            for j in range(i+1, n):
                dists[(i,j)] = distance_matrix[i][j]
                
        while len(active) > 1:
            # Find closest pair (Strongest p-adic correlation)
            min_dist = float('inf')
            pair = None
            
            for (i, j), d in dists.items():
                if i in active and j in active:
                    if d < min_dist:
                        min_dist = d
                        pair = (i, j)
            
            if pair is None: break
            
            i, j = pair
            # Merge i and j
            new_cluster = f"({clusters[i]},{clusters[j]})"
            
            # Update Cluster Name
            clusters[i] = new_cluster # Keep i as the merged ID
            active.remove(j)          # Remove j
            
            # Update distances (Complete Linkage / Ultrametric Inequality)
            # D(new, k) = max(D(i, k), D(j, k)) -> Maintains Ultrametricity
            for k in list(active):
                if k == i: continue
                # Dist (i, k) and (j, k)
                d_ik = dists.get(tuple(sorted((i,k))), float('inf'))
                d_jk = dists.get(tuple(sorted((j,k))), float('inf'))
                
                new_dist = max(d_ik, d_jk)
                dists[tuple(sorted((i,k)))] = new_dist
                
        return clusters[list(active)[0]] + ";"
