from src.logic_miner.engine import LogicMiner
from src.logic_miner.core.solver import ModularSolver
import random

def research_trolley():
    print("### PROPOSAL: MULTIVARIATE LOGIC (TROLLEY PROBLEM) ###")
    
    # We use ModularSolver directly for now as Engine integration for multivariate 
    # requires Discovery to pass tuple-inputs, which it might not support natively yet.
    # So we unit-test the Solver first.
    
    p = 7
    solver = ModularSolver(p)
    
    print("\n--- Scenario A: Modular Valuation ---")
    # "Swerve Score" = 2*Men + 3*Children + 4 (Bias)  (Mod 7)
    # Inputs: (Men, Children)
    
    data = []
    for _ in range(50):
        m = random.randint(0, 10)
        c = random.randint(0, 10)
        
        # y = 2m + 3c + 4
        y = (2*m + 3*c + 4) % p
        data.append( ([m, c], y) )
        
    print(f"Data: {len(data)} decisions.")
    print("Example:", data[0])
    
    res = solver.ransac(data, iterations=100)
    print("Result:", res)
    
    beta = res['model']
    if beta:
        # beta is [b0, b1, b2] -> [Bias, Men, Children]
        print(f"Recovered Weights: Bias={beta[0]}, Men={beta[1]}, Children={beta[2]}")
        if beta == [4, 2, 3]:
            print("[SUCCESS] Recovered Ethical Weights exacty!")
        else:
            print("[FAIL] Weights do not match.")
    else:
        print("[FAIL] No model found.")


    print("\n--- Scenario B: Boolean Decision (Parity) ---")
    # Swerve (1) if (Men + Children) is Odd.
    # Logic: y = 1*M + 1*C + 0 (Mod 2)
    p2 = 2
    solver2 = ModularSolver(p2)
    
    data2 = []
    for _ in range(50):
        m = random.randint(0, 10)
        c = random.randint(0, 10)
        y = (m + c) % 2
        data2.append( ([m, c], y) )
        
    res2 = solver2.ransac(data2)
    beta2 = res2['model']
    print(f"Recovered Weights: {beta2}")
    
    if beta2 == [0, 1, 1]:
        print("[SUCCESS] Recovered Parity Decision Rule (M+C is Odd).")

if __name__ == "__main__":
    research_trolley()
