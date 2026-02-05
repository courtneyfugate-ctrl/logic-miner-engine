from src.logic_miner.core.algebraic_text import AlgebraicTextSolver
from src.logic_miner.core.adelic import AdelicIntegrator

def run_adelic_test():
    """
    Test Adelic/CRT Synthesis of two text logics.
    Goal: Combine p=3 logic and p=5 logic into Modulo 15 logic.
    """
    print("--- Adelic Synthesis Test ---")
    
    text = "The Cat and Dog are mammals."
    entities = ["Cat", "Dog", "Mammals"]
    
    # 1. Generate Model A (p=3)
    solver3 = AlgebraicTextSolver(p=3)
    # We cheat and map them consistently manually for the test to make sense?
    # No, let the solver map them. But for CRT to work, the "X" (Godel Number) must be consistent across models
    # OR we must assume the input X is the same entity.
    # The current Logic Miner maps entities 1..N based on list order.
    # So if we pass the SAME entity list, X is consistent.
    
    res3 = solver3.solve(text, entities)
    model3 = {
        'p': 3,
        'params': tuple(res3['polynomial']),
        'degree': len(res3['polynomial']) - 1
    }
    print(f"\nModel A (p=3): {model3['params']}")
    
    # 2. Generate Model B (p=5)
    solver5 = AlgebraicTextSolver(p=5)
    res5 = solver5.solve(text, entities)
    model5 = {
        'p': 5,
        'params': tuple(res5['polynomial']),
        'degree': len(res5['polynomial']) - 1
    }
    print(f"Model B (p=5): {model5['params']}")
    
    # 3. Integrate
    integrator = AdelicIntegrator()
    # Note: solve_crt expects normalized models (degree 1 or 0 usually).
    # Our text solver produces high degree polynomials (degree N).
    # AdelicIntegrator might reject high degree or mixed degree.
    # Let's see what happens. The code says: "If any cubic/quadratic, strict match required".
    
    global_model = integrator.solve_crt([model3, model5])
    
    if global_model:
        print(f"\n>>> [PASS] Global Logic Synthesized: {global_model}")
    else:
        print("\n>>> [FAIL] Synthesis Failed (Likely Degree mismatch or unsupported degree).")
        # Logic Miner polynomials are P(x) = (x-c1)(x-c2)...
        # These are degree N. AdelicIntegrator logic seems built for simple regressions (y=ax+b).
        # Theorizer note: We may need to synthesize the ROOTS, not the Coefficients?
        # Or synthesis is only valid for simple relations?

if __name__ == "__main__":
    run_adelic_test()
