import random
from src.logic_miner.core.lifter import HenselLifter

# ==========================================
# ADVERSARY AGENT: CIRCULAR LOGIC
# ==========================================
def generate_circular_logic(n=100, cycle_len=3):
    """
    Generates a repeating sequence: 0, 1, 2, 0, 1, 2...
    y = x % cycle_len
    """
    inputs = list(range(n))
    outputs = [x % cycle_len for x in inputs]
    return inputs, outputs

def generate_full_noise(n=100, p=7):
    inputs = list(range(n))
    outputs = [random.randint(0, p-1) for _ in range(n)]
    return inputs, outputs

def run_test():
    print("--- ADVERSARY AGENT REPORT ---")
    lifter = HenselLifter(p_base=7)
    
    # 1. Circular Logic Test
    # The 'Complex Cycle' (0,1,2 repeating) is actually Linear Mod 3 (y=x).
    # But we are viewing it Mod 7.
    # Pattern: 0, 1, 2, 0, 1, 2...
    # Mod 7: 0, 1, 2, 0, 1, 2...
    # Can we find y = Ax + B (mod 7)?
    # x=0,y=0; x=1,y=1; x=2,y=2 -> y=x works for first 3.
    # x=3,y=0; -> 0 = 3? No.
    # x=4,y=1; -> 1 = 4? No.
    # x=6,y=0; -> 0 = 6? No.
    # x=7,y=1; -> 1 = 7=0? No.
    # y=x matches exactly 1/3rd of the data (where x % 3 == y).
    # Consensus should be ~33%.
    
    print("\n[Scenario 1] Complex Cycle (y = x % 3) viewed in Z_7")
    c_in, c_out = generate_circular_logic(n=100, cycle_len=3)
    res_cycl = lifter.lift(c_in, c_out, max_depth=1, min_consensus=0.30)
    
    print(f"Status: {res_cycl['status']}")
    if res_cycl['status'] == 'CONVERGED':
        print(f"Detected Pseudo-Logic: {res_cycl['coefficients']}")
    else:
        print(f"Result: Rejected as Noise (Consensus < Threshold)")
        
    print(f"Final Consensus Rate: {res_cycl.get('final_consensus', 'N/A')}")

    # 2. Stochastic Noise Test
    print("\n[Scenario 2] Stochastic Noise (Uniform Random in Z_7)")
    n_in, n_out = generate_full_noise(n=100, p=7)
    res_noise = lifter.lift(n_in, n_out, max_depth=1, min_consensus=0.30)
    
    print(f"Status: {res_noise['status']}")
    print(f"Final Consensus Rate: {res_noise.get('final_consensus', 'N/A')}")
    
    # Conclusion
    rate_cycl = res_cycl.get('final_consensus', 0) if isinstance(res_cycl.get('final_consensus'), float) else 0
    rate_noise = res_noise.get('final_consensus', 0) if isinstance(res_noise.get('final_consensus'), float) else 0
    
    print("\n[Adversary Conclusion]")
    diff = rate_cycl - rate_noise
    if diff > 0.15: # Significant difference
        print(f"SUCCESS: Engine distinguished Cycle ({rate_cycl:.2%}) from Noise ({rate_noise:.2%}).")
        print("The 'Complex Cycle' exhibits partial structural coherence (linear segments) compared to pure entropy.")
    else:
        print("FAILURE: Engine could not distinguish Cycle from Noise.")

if __name__ == "__main__":
    run_test()
