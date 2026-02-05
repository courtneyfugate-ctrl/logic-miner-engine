from src.logic_miner.core.solver import ModularSolver
import random

def research_peeling_complex():
    print("### COMPLEX PEELING TEST (3 LAYERS) ###")
    p = 17
    solver = ModularSolver(p)
    
    # 1. Generate 3-Layer Logic
    data = []
    
    # Layer A: 60 points -> y = 3x + 1 (Linear)
    for _ in range(60):
        x = random.randint(0, 100)
        y = (3*x + 1) % p
        data.append( (x, y) )
        
    # Layer B: 30 points -> y = 8x + 5 (Linear)
    for _ in range(30):
        x = random.randint(0, 100)
        y = (8*x + 5) % p
        data.append( (x, y) )
        
    # Layer C: 10 points -> y = x^2 + 4 (Quadratic)
    for _ in range(10):
        x = random.randint(0, 100)
        y = (x**2 + 4) % p
        data.append( (x, y) )
        
    # Noise: 5 points
    for _ in range(5):
        data.append( (random.randint(0,100), random.randint(0,16)) )
        
    random.shuffle(data)
    print(f"Total Data: {len(data)}. Split: 60/30/10/5.")
    
    # Run Peeling
    print("\nRunning ransac_iterative...")
    # NOTE: We must ensure min_ratio is low enough for the last 10 points.
    # When 15 points remain (10 + 5 noise), 10/15 is 0.66.
    # So min_ratio=0.5 is safe.
    
    layers = solver.ransac_iterative(data, min_size=5, min_ratio=0.4)
    
    print(f"Found {len(layers)} layers.")
    
    for i, res in enumerate(layers):
        deg = res['degree']
        model = res['model']
        ratio = res['ratio']
        count = len(res['inliers'])
        print(f"Layer {i}: Deg {deg}, Model {model}, Inliers {count}, Ratio {ratio:.2f}")

    # Validation
    if len(layers) >= 3:
        # Check Models
        # M1: (3, 1) deg 1
        # M2: (8, 5) deg 1
        # M3: (1, 0, 4) deg 2? -> x^2 + 0x + 4.
        
        m1 = layers[0]['model']
        m2 = layers[1]['model']
        m3 = layers[2]['model']
        
        # Note: Order is by fit quality. 
        # L1 (60 pts) should be first.
        # L2 (30 pts) second.
        # L3 (10 pts) third.
        
        correct_L1 = (m1 == (3, 1) or list(m1) == [3, 1])
        correct_L2 = (m2 == (8, 5) or list(m2) == [8, 5])
        
        # Quadratic model params [a, b, c] for ax^2+bx+c
        # or [c, b, a]? Solver uses standard text order usually.
        # Let's inspect output.
        
        if correct_L1 and correct_L2:
             print("[SUCCESS] Found First 2 Layers correctly.")
             print("Checking Layer 3 (Quadratic)...")
             if len(m3) == 3 and m3[0] == 1 and m3[2] == 4:
                 print("[SUCCESS] Found Quadratic Layer (x^2+4)!")
             else:
                 print(f"[CHECK] Layer 3 params: {m3}")
    else:
        print("[FAIL] Did not find 3 layers.")

if __name__ == "__main__":
    research_peeling_complex()
