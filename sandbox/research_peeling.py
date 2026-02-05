from src.logic_miner.core.solver import ModularSolver
import random

def research_peeling():
    print("### THEORIZER'S CHALLENGE: THE PLATYPUS ###")
    p = 17
    solver = ModularSolver(p)
    
    # 1. Generate Mixed Data
    # Majority Rule (Mammals): y = 3x + 1
    # Minority Rule (Platypuses): y = 8x + 5
    
    data = []
    
    # 90 Mammals
    for _ in range(90):
        x = random.randint(0, 100)
        y = (3*x + 1) % p
        data.append( (x, y) )
        
    # 10 Platypuses
    platypus_data = []
    for _ in range(10):
        x = random.randint(0, 100)
        y = (8*x + 5) % p
        entry = (x, y)
        data.append(entry)
        platypus_data.append(entry)
        
    # 5 Noise
    for _ in range(5):
        x = random.randint(0, 100)
        y = random.randint(0, p-1)
        data.append( (x, y) )
        
    random.shuffle(data)
    print(f"Total Data: {len(data)}. Mammals: 90, Platypus: 10, Noise: 5.")
    
    # 2. Standard Search
    print("\n--- Standard RANSAC ---")
    res1 = solver.ransac(data)
    print("Result:", res1)
    
    # Expecting 3x+1
    model1 = res1.get('model') 
    # model for line is [3, 1] or [1, 3] depending on degree?
    # Solver returns deg 1 params (a, b) -> ax + b.
    # Actually solver returns [a, b] for degree 1?
    # Let's check output.
    
    # 3. Peeling
    print("\n--- Iterative Peeling ---")
    
    # Filter Inliers
    inliers1 = set(res1['inliers']) # List of tuples
    print(f"Layer 1 Inliers: {len(inliers1)}")
    
    # Residual Data
    layer2_data = [d for d in data if d not in inliers1]
    print(f"Remaining Data: {len(layer2_data)}")
    
    # Run RANSAC on Layer 2
    if len(layer2_data) > 3:
        res2 = solver.ransac(layer2_data)
        print("Layer 2 Result:", res2)
        
        # Check if it matches Platypus (8x + 5)
        # 8x + 5 -> params (8, 5)
        m2 = res2.get('model')
        if m2 and m2 == (8, 5): 
             print("[SUCCESS] Found the Platypus! (8x+5)")
        elif m2 and list(m2) == [8, 5]:
             print("[SUCCESS] Found the Platypus! (8x+5)")
        else:
             print(f"[FAIL] Found {m2}, expected (8, 5).")
             
    else:
        print("Not enough data for Layer 2.")

if __name__ == "__main__":
    research_peeling()
