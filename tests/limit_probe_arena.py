import math
import random
from src.logic_miner.engine import LogicMiner
from src.logic_miner.core.mahler import MahlerSolver

class Theorizer:
    """
    Generates complex logic datasets to stump the engine.
    """
    def generate(self, logic_type, n=100):
        X = list(range(n))
        Y = []
        name = logic_type
        
        if logic_type == 'CUBIC':
            # y = x^3 + x^2 + 1
            # Current engine is capped at Quadratic (Deg 2) for Poly-Morph.
            # Mahler should handle this? (Polynomials are finite in Mahler basis too).
            Y = [x**3 + x**2 + 1 for x in X]
            
        elif logic_type == 'MODULAR_CLOCK':
            # y = (5x + 3) % 12
            # This is periodic. Mahler should handle periods.
            Y = [(5*x + 3) % 12 for x in X]
            
        elif logic_type == 'BITWISE_XOR':
            # y = x ^ 85 (0x55)
            # Bitwise ops are 2-adic continuous?
            # XOR with constant is 1-Lipschitz in 2-adic? 
            # |(x^k) - (y^k)|_2 <= |x-y|_2? Yes.
            Y = [x ^ 85 for x in X]
            
        elif logic_type == 'STEP_FUNCTION':
            # y = floor(x / 10)
            # Locally constant. Mahler loves this.
            Y = [x // 10 for x in X]
            
        elif logic_type == 'FIBONACCI':
            # y = Fib(x) mod 1000
            # Linear recurrence.
            fib = [0, 1]
            for i in range(2, n):
                fib.append((fib[-1] + fib[-2]) % 1000)
            Y = fib[:n]
            
        return {'name': name, 'X': X, 'Y': Y}

class Skeptical:
    """
    Runs the engine blindly and reports results.
    """
    def probe(self, dataset):
        print(f"\n[Skeptical] Probing dataset: {dataset['name']}...")
        X, Y = dataset['X'], dataset['Y']
        
        miner = LogicMiner()
        try:
            # We assume no noise for these logic probes to test pure expressivity.
            result = miner.fit(X, Y, min_consensus=0.85)
            
            p = result['p']
            mode = result.get('mode', 'POLYNOMIAL')
            conf = result.get('discovery_confidence', 0.0)
            
            print(f"  > Discovered: p={p}, Mode={mode}, Conf={conf:.2f}")
            
            # Verify Fidelity
            fidelity = self.verify_prediction(X, Y, result)
            print(f"  > Fidelity: {fidelity:.2%}")
            
            return {
                'success': fidelity > 0.99,
                'p': p,
                'mode': mode,
                'fidelity': fidelity
            }
            
        except Exception as e:
            print(f"  > FAILED: {e}")
            return {'success': False, 'error': str(e)}

    def verify_prediction(self, X, Y, result):
        # Reconstruct predictor
        mode = result.get('mode', 'POLYNOMIAL')
        p = result['p']
        
        coeffs = result.get('coefficients') # Used by Mahler directly
        trace = result.get('logic_trace') # Used by Poly
        
        hits = 0
        n = len(X)
        
        if mode == 'MAHLER':
            from src.logic_miner.core.mahler import MahlerSolver
            ms = MahlerSolver(p)
            # Mahler prediction
            for i, x in enumerate(X):
                pred = ms.predict(x, coeffs)
                if pred == Y[i]: hits += 1
        
        else:
            # Polynomial Reconstruction
            if not trace: return 0.0
            coeffs_list = trace['coefficients']
            
            for i, x in enumerate(X):
                total_y = 0
                current_p_pow = 1
                for level in coeffs_list:
                    deg = level['degree']
                    params = level['params']
                    val = 0
                    if deg == 0: val = params[0]
                    elif deg == 1: val = params[0]*x + params[1]
                    elif deg == 2: val = params[0]*x**2 + params[1]*x + params[2]
                    
                    total_y += val * current_p_pow
                    current_p_pow *= p
                
                if total_y == Y[i]: hits += 1
                
        return hits / n

def run_arena():
    theo = Theorizer()
    skep = Skeptical()
    
    logics = ['CUBIC', 'MODULAR_CLOCK', 'BITWISE_XOR', 'STEP_FUNCTION', 'FIBONACCI']
    results = {}
    
    print("=== LIMIT PROBE ARENA START ===")
    
    for logic in logics:
        data = theo.generate(logic, n=50) # Small N for speed, sufficient for logic
        res = skep.probe(data)
        results[logic] = res
        
    print("\n=== ARENA REPORT ===")
    for logic, res in results.items():
        status = "PASS" if res.get('success') else "FAIL"
        print(f"[{status}] {logic}: p={res.get('p')}, Mode={res.get('mode')}")

if __name__ == "__main__":
    run_arena()
