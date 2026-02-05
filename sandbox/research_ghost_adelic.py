from src.logic_miner.core.real import RealSolver
from src.logic_miner.core.solver import ModularSolver

def research_ghost_adelic():
    print("### Proposal 5: Adelic Verification for Ghost Terms ###")
    
    # 1. True Linear
    # y = x
    X = list(range(20))
    Y_true = X
    
    # 2. Ghost Linear (Mod 5)
    # y = x^5
    # Mod 5: x^5 = x. So it looks like y=x.
    Y_ghost = [x**5 for x in X]
    
    print("\n--- Testing p=5 Perspective ---")
    solver = ModularSolver(5)
    
    # Mod 5 view
    d_mod_true = [(x, y%5) for x, y in zip(X, Y_true)]
    res_true = solver.ransac(d_mod_true, max_degree=1)
    print(f"True Linear (Mod 5): {res_true['ratio']:.2f} params={res_true['model']}")
    
    d_mod_ghost = [(x, y%5) for x, y in zip(X, Y_ghost)]
    res_ghost = solver.ransac(d_mod_ghost, max_degree=1)
    print(f"Ghost Linear (Mod 5): {res_ghost['ratio']:.2f} params={res_ghost['model']}")
    # Expect both to be Perfect (1.00)
    
    print("\n--- Testing Real (Adelic) Perspective ---")
    real_solver = RealSolver()
    
    res_real_true = real_solver.solve(X, Y_true)
    print(f"True Linear (Real): Type={res_real_true['type']} Fid={res_real_true['fidelity']:.2f}")
    
    res_real_ghost = real_solver.solve(X, Y_ghost)
    # x^5 grows extremely fast. Linear fit should fail horribly.
    print(f"Ghost Linear (Real): Type={res_real_ghost['type']} Fid={res_real_ghost['fidelity']:.2f}")
    
    if res_real_true['fidelity'] > 0.9 and res_real_ghost['fidelity'] < 0.2:
        print("[SUCCESS] Adelic Verification distinguished True vs Ghost logic.")
    else:
        print("[FAIL] Could not distinguish.")

if __name__ == "__main__":
    research_ghost_adelic()
