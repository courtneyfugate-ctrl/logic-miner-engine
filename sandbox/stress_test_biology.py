from src.logic_miner.engine import LogicMiner
import time

def run_stress_test():
    """
    Stress Test for V.3 Pure P-adic Pipeline.
    Corpus: Biological Taxonomy (3 Groups, ~20 Entities).
    Goal: Verify if topological density alone is sufficient to recover the 3 distinct branches.
    """
    miner = LogicMiner()
    
    # 1. Construct Corpus (Dense Co-occurrences within groups, Sparse between)
    # Groups: Mammals, Birds, Fish
    mammals = ["Lion", "Tiger", "Bear", "Wolf", "Dog", "Cat"]
    birds = ["Eagle", "Hawk", "Parrot", "Pigeon", "Sparrow"]
    fish = ["Shark", "Salmon", "Tuna", "Goldfish"]
    
    text = ""
    
    # Generate dense intra-group sentences
    import random
    random.seed(42)
    
    print("--- Generative Biological Corpus ---")
    
    # Mammal Contexts
    for _ in range(20):
        # Pick 2-3 random mammals
        subset = random.sample(mammals, k=3)
        text += f"The {subset[0]} and the {subset[1]} are mammals like the {subset[2]}. "
    
    # Bird Contexts
    for _ in range(20):
        subset = random.sample(birds, k=3)
        text += f"The {subset[0]} is a bird, just like the {subset[1]} and {subset[2]}. "
        
    # Fish Contexts
    for _ in range(20):
        subset = random.sample(fish, k=3)
        text += f"The {subset[0]} swims with the {subset[1]} and {subset[2]}. "
        
    # Rare Cross-over (Noise)
    text += "The Bear catches the Salmon. "
    text += "The Eagle hunts the Rabbit. " # Rabbit not in list, auto-ignored or added?
    text += "The Shark eats the Tuna. "
    
    print(f"Generated {len(text)} chars of text.")
    
    # 2. Run Algo
    start = time.time()
    res = miner.fit(text)
    end = time.time()
    
    print(f"\n--- Execution Time: {end - start:.4f}s ---")
    print(f"Mode: {res['mode']}")
    print(f"Rectification Energy: {res['energy']:.4f}")
    
    coords = res['coordinates']
    
    # 3. Validation: Intra-group distance vs Inter-group distance
    def get_avg_dist(group_a, group_b):
        dists = []
        # Need p from the solver... assumed 5?
        p = res.get('p', 5)
        for a in group_a:
            if a not in coords: continue
            for b in group_b:
                if b not in coords: continue
                if a == b: continue
                
                # dist = p^-val(diff)
                diff = coords[a] - coords[b]
                v = 0
                while diff != 0 and diff % p == 0:
                    diff //= p
                    v += 1
                if diff == 0: d = 0
                else: d = p**(-v)
                dists.append(d)
        if not dists: return 1.0
        return sum(dists)/len(dists)

    print("\n--- Topological Distances ---")
    mm_dist = get_avg_dist(mammals, mammals)
    bb_dist = get_avg_dist(birds, birds)
    ff_dist = get_avg_dist(fish, fish)
    
    mb_dist = get_avg_dist(mammals, birds)
    mf_dist = get_avg_dist(mammals, fish)
    
    print(f"Avg Dist(Mammal, Mammal): {mm_dist:.4f}")
    print(f"Avg Dist(Bird, Bird):     {bb_dist:.4f}")
    print(f"Avg Dist(Fish, Fish):     {ff_dist:.4f}")
    print(f"Avg Dist(Mammal, Bird):   {mb_dist:.4f}")
    print(f"Avg Dist(Mammal, Fish):   {mf_dist:.4f}")
    
    # Assertion
    if mm_dist < mb_dist and ff_dist < mf_dist:
        print("\n>>> [PASS] V.3 Pipeline Successfully recovered Taxonomy from Density.")
    else:
        print("\n>>> [FAIL] Taxonomy collapsed or mixed.")

if __name__ == "__main__":
    run_stress_test()
