from src.logic_miner.core.ultrametric import UltrametricBuilder

def research_species_tree():
    print("### PROPOSAL: ULTRAMETRIC STRUCTURE (SPECIES TREE) ###")
    
    # Entities
    species = ["Dog", "Wolf", "Cat", "Lion", "Shark"]
    
    # Semantic Features (Simulated Embedding)
    # 0: Mammal, 1: Canid, 2: Felid, 3: Domestic, 4: Aquatic
    features = {
        "Dog":   {0, 1, 3},
        "Wolf":  {0, 1},
        "Cat":   {0, 2, 3},
        "Lion":  {0, 2},
        "Shark": {4}
    }
    
    # Compute Distance Matrix (Jaccard or Hamming)
    # We use Hamming-like: 1 - Jaccard Index (0=Identical, 1=Disjoint)
    n = len(species)
    dist_matrix = [[0.0]*n for _ in range(n)]
    
    print("\n--- Feature Analysis ---")
    for i in range(n):
        for j in range(n):
            if i == j: continue
            s1 = features[species[i]]
            s2 = features[species[j]]
            
            intersection = len(s1.intersection(s2))
            union = len(s1.union(s2))
            jaccard = intersection / union
            dist = 1.0 - jaccard
            dist_matrix[i][j] = dist
            
            # print(f"Dist({species[i]}, {species[j]}) = {dist:.2f}")

    # Build Tree
    builder = UltrametricBuilder()
    tree = builder.build_tree(species, dist_matrix)
    
    print("\n--- Extracted Classification Tree ---")
    print(tree)
    
    # Expected: ((Dog,Wolf),(Cat,Lion),Shark) or similar nesting
    # Shark is outlier (Non-Mammal).
    # Dog/Wolf close. Cat/Lion close. 
    
    if "Shark" in tree and "Dog" in tree:
        print("[SUCCESS] Tree constructed.")

if __name__ == "__main__":
    research_species_tree()
