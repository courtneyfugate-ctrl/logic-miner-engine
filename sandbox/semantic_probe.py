from src.logic_miner.engine import LogicMiner
import math

class SemanticProbe:
    def __init__(self, miner):
        self.miner = miner
        
    def probe(self, system_logic_fn, variable_name, value_range=100):
        print(f"### SEMANTIC PROBE: Analyzing '{variable_name}' ###")
        
        # 1. Active Interrogation (Hybrid Strategy)
        # Geometric (for Polynomials) + Linear (for Modulo Cycles)
        inputs = set()
        
        # A. Geometric (1, 2, 4...)
        k = 0
        while True:
            val = pow(2, k)
            if val > value_range: break
            inputs.add(val)
            k += 1
            
        # B. Linear Sweep (0..30) to catch small cycles (like mod 15)
        for i in range(min(31, value_range)):
            inputs.add(i)
            
        inputs = sorted(list(inputs))
        print(f"   > Generated Active Queries ({len(inputs)}): {inputs[:10]}...")
        
        # 2. Mock LLM Interaction (The "Ear")
        answers = []
        for val in inputs:
            raw_response = system_logic_fn(val)
            answers.append(raw_response)
            
        print(f"   > Received Answers: {answers[:10]} ...")
        
        # 3. The Mapper (Semantic -> Integer)
        mapped_outputs = []
        has_positive = False
        for ans in answers:
            if ans.lower() == "yes": 
                mapped_outputs.append(1)
                has_positive = True
            elif ans.lower() == "no": mapped_outputs.append(0)
            else: mapped_outputs.append(0)
            
        print(f"   > Mapped Integers: {mapped_outputs[:10]}...")
        
        if not has_positive:
             print("   [WARN] No positive ('Yes') answers received. Logic appears to be 'Always No'.")
             return

        # 4. The Miner (Calculus)
        print("   > Mining Logic...")
        try:
            # We must handle the Lipschitz Exception if it's a Step Function
            result = self.miner.fit(inputs, mapped_outputs)
            
            # 5. Interpretation
            if result.get('p') == float('inf') or 'REAL' in result.get('mode', ''):
                print(f"   [RESULT] Logic is REAL/THRESHOLD based (e.g. {variable_name} > X).")
                print(f"   Details: {result}")
            elif result.get('p') == 2:
                 print(f"   [RESULT] Logic is BINARY/PARITY based (e.g. {variable_name} is Odd/Even).")
            else:
                 print(f"   [RESULT] Logic is MODULAR (Cycle of {result.get('p')}).")
                 
        except Exception as e:
            if "Lipschitz" in str(e):
                 print(f"   [RESULT] Logic is DISCONTINUOUS/THRESHOLD (e.g. {variable_name} >= X).")
                 print("   (Detected via Lipschitz Violation).")
            else:
                 print(f"   [FAIL] Could not determine logic: {e}")

# --- Simulation ---

def mock_bouncer_llm(age):
    # Hidden Logic: Age >= 21
    if age >= 21: return "Yes"
    return "No"

def mock_bus_schedule_llm(minute):
    # Hidden Logic: Every 15 minutes (x % 15 == 0)
    if minute % 15 == 0: return "Yes"
    return "No"

def run_semantic_demo():
    miner = LogicMiner()
    probe = SemanticProbe(miner)
    
    # Scenario A: Bouncer
    print("\n--- Scenario A: The Club Bouncer ---")
    probe.probe(mock_bouncer_llm, "Age", value_range=100)
    
    # Scenario B: Bus Schedule
    print("\n--- Scenario B: The Bus Schedule ---")
    probe.probe(mock_bus_schedule_llm, "Minute", value_range=60)

if __name__ == "__main__":
    run_semantic_demo()
