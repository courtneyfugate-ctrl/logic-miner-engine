from src.logic_miner.core.solver import ModularSolver

def debug_solver():
    print("### DEBUG SOLVER ###")
    p = 7
    solver = ModularSolver(p)
    
    # y = 6m + 3c (Mod 7)
    # Samples:
    # m=1, c=1 -> y = 6+3=9=2
    # m=0, c=1 -> y = 3
    # m=1, c=0 -> y = 6
    # m=0, c=0 -> y = 0
    
    X = [[1, 1], [0, 1], [1, 0]]
    y = [2, 3, 6] # Wait, we need 3 samples including intercept? 
    # y = 0 + 6m + 3c. Intercept is 0.
    # 3 unknowns (b0, b1, b2). 3 equations needed.
    
    beta = solver.solve_multivariate(X, y)
    print(f"Beta: {beta}")
    
    # Expected: [0, 6, 3]
    if beta == [0, 6, 3]: 
        print("SUCCESS")
    else:
        print("FAIL")

if __name__ == "__main__":
    debug_solver()
