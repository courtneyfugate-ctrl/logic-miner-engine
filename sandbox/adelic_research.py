import collections
from src.logic_miner.core.solver import ModularSolver
from src.logic_miner.engine import LogicMiner

class TheorizerAdelic:
    """
    Experimental Adelic Integrator.
    Uses Hasse Principle (Local -> Global) and CRT.
    """
    
    def solve_crt(self, models):
        """
        Synthesize local models into a global composite model using CRT.
        models: list of dict {'p': p, 'val': v} meaning x = v (mod p)
        
        Example: x = 1 (mod 2), x = 2 (mod 3) -> x = 5 (mod 6).
        """
        # Simplified for Constant Logic y = C
        # If models predict y(x) = A_p * x + B_p
        # We try to find global A, B such that A = A_p (mod p).
        
        # 1. Check consistency of degree.
        # If degrees differ, Hasse principle might say "No Global Polynomial" 
        # (unless reduced mod p).
        
        # Let's assume linear logic: y = a*x + b
        # We need to solve for 'a' and 'b' using CRT.
        
        M = 1
        for m in models:
            M *= m['p']
            
        # Standard CRT:
        # X = sum (a_i * M_i * y_i) (mod M)
        # where M_i = M/p_i, y_i = inv(M_i, p_i)
        
        def crt(remainders, moduli):
            sum_val = 0
            prod = 1
            for n in moduli: prod *= n
            
            for r, n in zip(remainders, moduli):
                p = prod // n
                # Inverse of p modulo n
                inv = pow(p, -1, n)
                sum_val += r * p * inv
            return sum_val % prod

        coeffs_a = []
        coeffs_b = []
        moduli = []
        
        for m in models:
            if m['degree'] != 1: return None # Complexity mismatch
            coeffs_a.append(m['params'][0])
            coeffs_b.append(m['params'][1])
            moduli.append(m['p'])
            
        global_a = crt(coeffs_a, moduli)
        global_b = crt(coeffs_b, moduli)
        
        return {'degree': 1, 'params': (global_a, global_b), 'modulus': M}

    def global_consensus(self, inputs, outputs, primes=[2, 3, 5]):
        """
        Product Formula Approach:
        A point is a TRUE inlier only if it is an inlier in ALL valid local fields.
        """
        # 1. Get inlier sets for each prime
        inlier_sets = []
        
        for p in primes:
            solver = ModularSolver(p)
            # Correct method call
            res = solver.ransac([(x, y % p) for x, y in zip(inputs, outputs)], iterations=50, max_degree=1)
            
            # Extract params from result
            # Result format: {'model': (degree, (a, b)), 'ratio': ...}
            # Extract params using correct key structure
            # ransac returns {'degree': d, 'model': params, ...}
            degree = res.get('degree', -1)
            params = res.get('model')
            
            if degree == 1 and params:
                a, b = params
            elif degree == 0 and params:
                a = 0
                b = params[0]
            else:
                continue
            inliers = set()
            for i, (x, y) in enumerate(zip(inputs, outputs)):
                if (a*x + b - y) % p == 0:
                    inliers.add(i)
            inlier_sets.append(inliers)
            
        # 2. Intersect
        if not inlier_sets: return set()
        global_inliers = set.intersection(*inlier_sets)
        
        return global_inliers

def run_experiment():
    print("### ADELIC RESEARCH: Hasse Principle & Product Formula ###")
    theo = TheorizerAdelic()
    
    # --- Experiment A: Composite Moduli (Mod 12) ---
    print("\n[Exp A] Composite Moduli (Mod 12)")
    print("Logic: y = 5x + 3 (mod 12)")
    # Local Decomposition:
    # Mod 4 (2-adic): 5x + 3 = 1x + 3 (mod 4) -> y = x + 3
    # Mod 3 (3-adic): 5x + 3 = 2x + 0 (mod 3) -> y = 2x
    
    X = list(range(20))
    Y = [(5*x + 3) % 12 for x in X]
    
    # 1. Solve locally
    s2 = ModularSolver(2) # Actually mod 4 is deeper than mod 2. 
    # LogicMiner usually does Mod p. 
    # For Mod 12, we need Mod 4 and Mod 3.
    # Solver(2) gives Mod 2. y = 1x + 1 (mod 2).
    # Solver(3) gives Mod 3. y = 2x + 0.
    
    # Note: 5x+3 mod 2 -> 1x+1.
    # 5x+3 mod 3 -> 2x.
    
    # Let's simulated "Discovered Local Models"
    models = [
        {'p': 4, 'degree': 1, 'params': (1, 3)}, # Derived from Lifting p=2 dept 2?
        {'p': 3, 'degree': 1, 'params': (2, 0)}
    ]
    
    # Theorizer attempts CRT
    try:
        global_model = theo.solve_crt(models)
        print(f"Hasse Synthesis: {global_model}")
        
        # Verify
        ga, gb = global_model['params']
        M = global_model['modulus']
        print(f"Synthesized: y = {ga}x + {gb} (mod {M})")
        
        matches = 0
        for x, y in zip(X, Y):
            if (ga*x + gb) % M == y: matches += 1
        print(f"Fidelity: {matches/len(X):.2%}")
        
    except Exception as e:
        print(f"Hasse Failed: {e}")

    # --- Experiment B: global_consensus (Product Formula) ---
    print("\n[Exp B] Global Consensus (Product Formula)")
    # Logic: y = 2x + 1 (Global)
    # Noise Type 1: Multiples of 2 (Invisible to p=2)
    # Noise Type 2: Multiples of 3 (Invisible to p=3)
    # A single solver might accept the noise. Intersection should drop it.
    
    X = list(range(20))
    True_Y = [2*x + 1 for x in X]
    Noisy_Y = list(True_Y)
    
    # Corrupt index 5: Add 2 (Valid in p=2, Invalid in p=3)
    Noisy_Y[5] += 2 
    # Corrupt index 10: Add 3 (Valid in p=3, Invalid in p=2)
    Noisy_Y[10] += 3
    
    # Standard Miner on p=2 alone might keep index 5.
    
    inliers = theo.global_consensus(X, Noisy_Y, primes=[2, 3])
    print(f"Global Inliers Count: {len(inliers)}/{len(X)}")
    
    # Check if 5 and 10 are excluded
    if 5 not in inliers and 10 not in inliers:
        print("[PASS] Intersection excluded local noise (Product Formula Effect).")
    else:
        print(f"[FAIL] Inliers contained noise: 5 in? {5 in inliers}, 10 in? {10 in inliers}")

if __name__ == "__main__":
    run_experiment()
