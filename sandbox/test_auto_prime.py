import math
from collections import Counter

def detect_prime_from_density(counts):
    """
    Given a list of co-occurrence counts (raw integers),
    detect the intrinsic prime 'p' that best explains the hierarchy.
    
    Logic:
    If the hierarchy is p-adic, then meaningful clusters appear at 
    distances d = p^-k.
    The 'counts' correspond to inverse distances: C ~ p^k.
    We look for the GCD of the counts? Or the most frequent discrete base?
    
    Actually, Logic Miner uses d = 1 / (count + 1).
    So detection should look at the counts directly.
    """
    display_counts = counts
    # Transform: We care about the denominator p^k = count + 1
    denominators = [c + 1 for c in counts]
    print(f"Analyzing Denominators (Count+1): {denominators}")
    
    # 2. Base Detection via Factorization
    # We want a p that divides the DENOMINATORS.
    candidates = [2, 3, 5, 7, 11, 13, 17]
    scores = {p: 0 for p in candidates}
    
    for val in denominators:
        if val <= 1: continue
        for p in candidates:
            # Does p divide val?
            if val % p == 0:
                scores[p] += 1
            # Is val a power of p?
            l = math.log(val, p)
            if abs(l - round(l)) < 0.001:
                scores[p] += 3 # Stronger signal for exact power
                
    print(f"Prime Scores: {scores}")

                
    print(f"Prime Scores: {scores}")
    best_p = max(scores, key=scores.get)
    return best_p

def run_test():
    # Scenario A: Base 5 (Mammal-like)
    # Counts: 4, 24, 124 (implying d = 1/5, 1/25, 1/125)
    print("\n--- Test Case A (Base 5) ---")
    counts_a = [4, 24, 4, 124, 4] 
    # Logic: d = 1/(4+1)=0.2=5^-1. d=1/(24+1)=0.04=5^-2.
    # Note: The counts in the miner are raw integers.
    # Ideally we'd see '4' (dist 1/5), '24' (dist 1/25).
    # wait, if count is 4, d=0.2. 
    # If count is 24, d=0.04.
    p_a = detect_prime_from_density(counts_a)
    print(f"Detected: {p_a} (Expected: 5)")
    
    # Scenario B: Base 2 (Binary Tree)
    # Counts: 1, 3, 7, 15 (d = 1/2, 1/4, 1/8, 1/16)
    print("\n--- Test Case B (Base 2) ---")
    counts_b = [1, 3, 7, 15, 3, 1]
    p_b = detect_prime_from_density(counts_b)
    print(f"Detected: {p_b} (Expected: 2)")

    # Scenario C: Base 3
    print("\n--- Test Case C (Base 3) ---")
    counts_c = [2, 8, 26, 80]
    p_c = detect_prime_from_density(counts_c)
    print(f"Detected: {p_c} (Expected: 3)")

if __name__ == "__main__":
    run_test()
