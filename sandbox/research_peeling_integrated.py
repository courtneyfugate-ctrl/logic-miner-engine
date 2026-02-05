from src.logic_miner.core.solver import ModularSolver
import random

def research_peeling_integrated():
    print("### INTEGRATED PEELING TEST ###")
    p = 17
    solver = ModularSolver(p)
    
    # Generate Mixed Data
    data = []
    # 90 Mammals (3x + 1)
    for _ in range(90):
        x = random.randint(0, 100)
        y = (3*x + 1) % p
        data.append( (x, y) )
    # 10 Platypuses (8x + 5)
    for _ in range(10):
        x = random.randint(0, 100)
        y = (8*x + 5) % p
        data.append( (x, y) )
    # 5 Noise
    for _ in range(5):
        data.append( (random.randint(0,100), random.randint(0,16)) )
    
    random.shuffle(data)
    
    # Run Iterative RANSAC
    print("Running solve.ransac_iterative...")
    layers = solver.ransac_iterative(data, min_size=5, min_ratio=0.1)
    
    print(f"Found {len(layers)} layers.")
    
    for i, res in enumerate(layers):
        print(f"Layer {i}: Model {res['model']}, Ratio {res['ratio']:.2f}, Inliers {len(res['inliers'])}")
        
    # Check
    if len(layers) >= 2:
        m1 = layers[0]['model']
        m2 = layers[1]['model']
        
        # Order usually dominant first
        if m1 == (3, 1) and m2 == (8, 5):
            print("[SUCCESS] Found Mammal then Platypus.")
        elif m1 == (3, 1) and list(m2) == [8, 5]:
             print("[SUCCESS] Found Mammal then Platypus.")
        elif list(m1) == [3, 1] and list(m2) == [8, 5]:
             print("[SUCCESS] Found Mammal then Platypus.")
        else:
            print(f"[PARTIAL] Found {m1} and {m2}.")
            if m1 == (3,1): print("Mammal OK.")
            if m2 == (8,5): print("Platypus OK.")

if __name__ == "__main__":
    research_peeling_integrated()
