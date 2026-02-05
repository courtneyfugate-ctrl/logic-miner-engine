import math
from collections import Counter

def gcd_list(numbers):
    if not numbers: return 0
    result = numbers[0]
    for n in numbers[1:]:
        result = math.gcd(result, n)
    return result

def theorizers_gcd_approach(X, Y):
    print("--- Theorizer's GCD Approach ---")
    # Hypothesis: GCD of all differences reveals m?
    # Delta Y
    diffs = [abs(Y[i] - Y[i-1]) for i in range(1, len(Y))]
    
    # Filter 0s
    diffs = [d for d in diffs if d != 0]
    
    g = gcd_list(diffs)
    print(f"Global GCD of differences: {g}")
    return g

def skeptics_collision_approach(X, Y):
    print("\n--- Skeptic's Collision Approach ---")
    # Hypothesis: Collisions (y_i = y_j) imply a(x_i - x_j) = k*m.
    # If we have enough collisions, we might recover m.
    # y = ax + b (mod m)
    # y1 - y2 = a(x1 - x2) - k*m
    # If y1 = y2, then a(x1-x2) is a multiple of m.
    # GCD of all (x_i - x_j) for colliding pairs might reveal m / gcd(a,m).
    
    collisions = []
    # Find indices with same Y
    y_map = {}
    for i, y in enumerate(Y):
        if y not in y_map: y_map[y] = []
        y_map[y].append(X[i])
        
    intervals = []
    for y, indices in y_map.items():
        if len(indices) < 2: continue
        for i in range(len(indices)):
            for j in range(i+1, len(indices)):
                intervals.append(abs(indices[i] - indices[j]))
                
    if not intervals:
        print("No collisions found.")
        return None
        
    print(f"Found {len(intervals)} collision intervals: {intervals[:10]}...")
    g = gcd_list(intervals)
    print(f"GCD of collision intervals: {g}")
    return g

def run_experiment():
    # Setup: Large Prime Logic (p=1009)
    # y = 123x + 456 (mod 1009)
    p = 1009
    a = 123
    b = 456
    
    print(f"Target Logic: y = {a}x + {b} (mod {p})")
    
    X = list(range(200)) # Need enough range to get collisions? 
    # Logic repeats every p? No, y values map to 0..p-1.
    # Range 200 < 1009. We probably won't see collisions in y unless 'a' is small or we wrap?
    # y = ax + b mod m is a bijection if gcd(a,m)=1.
    # So Y values will represent a permutation of 0..p-1.
    # NO COLLISIONS will occur in X < p.
    # So Skeptic's collision approach works only if sample size > p.
    
    # What about Theorizer's Diff GCD?
    # Let's run it.
    
    Y = [(a*x + b) % p for x in X]
    
    g1 = theorizers_gcd_approach(X, Y)
    
    # Skeptic logic requires N > p. Let's extend X.
    X2 = list(range(p + 50))
    Y2 = [(a*x + b) % p for x in X2]
    g2 = skeptics_collision_approach(X2, Y2)
    
    # What if a is NOT coprime?
    # y = 10x (mod 100).
    # GCD(10) = 10.
    # Collisions every 10 steps.
    
    print("\n--- Non-Coprime Logic (y = 50x mod 100) ---")
    X3 = list(range(20))
    Y3 = [(50*x) % 100 for x in X3]
    # Y3: 0, 50, 0, 50...
    theorizers_gcd_approach(X3, Y3)
    skeptics_collision_approach(X3, Y3)

if __name__ == "__main__":
    run_experiment()
