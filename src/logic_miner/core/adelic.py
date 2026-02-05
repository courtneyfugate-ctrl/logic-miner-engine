import math
import hashlib
from collections import defaultdict

class AdelicMapper:
    """
    Coordinates Multi-Verse Projections.
    Uses random seed per prime to ensure rotational variance.
    """
    # Extended pool for Dynamic Manifold Sizing (V.21)
    EXTENDED_POOL = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    def __init__(self, primes=[3, 5, 7], seed_prefix="DEFAULT"):
        self.primes = primes
        self.seed_prefix = seed_prefix
        self.dimensions = 12

    def _get_projection_sign(self, term, dim, prime):
        key = f"{self.seed_prefix}_{prime}_{term}_{dim}"
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return 1 if h % 2 == 0 else -1

    def compute_mappings(self, matrix, entities):
        mappings = defaultdict(dict)
        for p in self.primes:
            for i, term in enumerate(entities):
                bits = 0
                row = matrix[i]
                for d in range(self.dimensions):
                    dot = 0.0
                    for j, w in enumerate(row):
                        if w > 0:
                            neigh = entities[j]
                            sign = self._get_projection_sign(neigh, d, p)
                            dot += w * sign
                    if dot >= 0: bits |= (1 << d)
                mappings[term][p] = bits
        return mappings

    @staticmethod
    def calculate_rpr(previous_set, current_set):
        """
        Root Preservation Rate: 
        Ratio of surviving concepts relative to the simpler manifold.
        """
        if not previous_set: return 1.0
        return len(current_set) / len(previous_set)

class AdelicSolver:
    """
    Algebraic Solver for the Sheaf Protocol.
    """
    def __init__(self, primes=[3, 5, 7]):
        self.primes = primes

    def solve(self, matrix, entities, hints):
        current = defaultdict(lambda: {p: 0 for p in self.primes})
        # Hints are anchored (boosted)
        for term, p_map in hints.items():
            for p, val in p_map.items():
                current[term][p] = val * p 

        ent_idxs = {e: i for i,e in enumerate(entities)}
        
        # Iterative Diffusion / Relaxation
        for _ in range(5):
            for e in entities:
                idx = ent_idxs[e]
                row = matrix[idx]
                for p in self.primes:
                    sum_val = 0
                    sum_w = 0
                    for j, w in enumerate(row):
                        if w > 0:
                            neigh = entities[j]
                            sum_val += current[neigh][p] * w
                            sum_w += w
                    if sum_w > 0:
                        current[e][p] = int(sum_val / sum_w)
        return current

class AdelicIntegrator:
    """
    Integrates local p-adic models into a global composite model using Hasse Principle (CRT).
    """
    def __init__(self):
        pass

    def solve_crt(self, models, inputs=None, outputs=None):
        print(f"[AdelicIntegrator] solve_crt called with {len(models)} models.")
        if inputs and outputs: print("[AdelicIntegrator] Inputs/Outputs provided for Lifting.")
        if not models: return None
        
        # 0. Split-Lift-Merge Phase
        # If data is available, attempt to lift each prime model to higher power
        # before synthesizing. This allows generating Mod 36 from Mod 2 and Mod 3.
        
        final_models = []
        if inputs and outputs:
            from .lifter import HenselLifter
            for m in models:
                p = m['p']
                # Try lifting
                lifter = HenselLifter(p)
                # Strict consensus required for CRT Composites (otherwise we lift noise)
                res = lifter.lift(inputs, outputs, max_depth=3, min_consensus=0.9)
                
                if res['status'] == 'CONVERGED' and res['depth'] > 1:
                     # Calculate lifted Modulus
                     p_k = p**res['depth']
                     
                     # Reconstruct Total Parameters Mod p^k
                     # F(x) = Sum (coeff_k * p^k)
                     # Assuming generic polynomial form: params are (a, b, c...)
                     
                     coeffs_list = res['coefficients']
                     if not coeffs_list: continue
                     
                     base_degree = coeffs_list[0]['degree']
                     num_params = len(coeffs_list[0]['params'])
                     
                     total_params = [0] * num_params
                     current_p_pow = 1
                     
                     valid_reconstruction = True
                     
                     for level_info in coeffs_list:
                         if level_info['degree'] != base_degree:
                             # Degree switching (PolyMorph) makes reconstruction hard 
                             # without explicit symbolic handling.
                             # For Composite Synthesis, we assume stability (Deg 1 -> Deg 1).
                             valid_reconstruction = False
                             break
                             
                         level_params = level_info['params']
                         for i in range(num_params):
                             total_params[i] += level_params[i] * current_p_pow
                             
                         current_p_pow *= p
                         
                     if valid_reconstruction:
                         # Success!
                         replaced_model = m.copy()
                         replaced_model['p'] = p_k # Treat p^k as the new "prime" base
                         replaced_model['modulus'] = p_k
                         replaced_model['params'] = tuple(total_params)
                         replaced_model['degree'] = base_degree
                         final_models.append(replaced_model)
                         continue
                
                # If lift failed or params missing, use base model
                final_models.append(m)
        else:
            final_models = models
            
        models = final_models
        
        # 1. Validate Degree Consistency
        degrees = set(m.get('degree', 1) for m in models)
        max_degree = max(degrees)
        min_degree = min(degrees)
        
        # Allow mixing Degree 0 and Degree 1 (Treat Constant as Linear with slope 0)
        if max_degree > 1:
             # If any cubic/quadratic, strict match required for now
             if len(degrees) > 1: return None
             
        # Normalize to Max Degree (0 or 1)
        normalized_models = []
        for m in models:
            d = m.get('degree', 1)
            p_params = m['params']
            
            new_params = p_params
            if max_degree == 1 and d == 0:
                # Pad: y=c -> y=0x + c
                new_params = (0, p_params[0])
                
            normalized_models.append({
                'p': m.get('modulus', m['p']),
                'params': new_params
            })
            
        degree = max_degree
        moduli = [m['p'] for m in normalized_models]

        # Check pairwise coprimality
        for i in range(len(moduli)):
            for j in range(i+1, len(moduli)):
                if math.gcd(moduli[i], moduli[j]) != 1:
                    return None
                    
        def crt(remainders, mods):
            M = 1
            for m in mods: M *= m
            
            sum_val = 0
            for r, n in zip(remainders, mods):
                p = M // n
                inv = pow(p, -1, n)
                sum_val += r * p * inv
            return sum_val % M
            
        M = 1
        for m in moduli: M *= m
        
        if degree == 1:
            # y = ax + b
            coeffs_a = [m['params'][0] for m in normalized_models]
            coeffs_b = [m['params'][1] for m in normalized_models]
            
            global_a = crt(coeffs_a, moduli)
            global_b = crt(coeffs_b, moduli)
            
            return {
                'type': 'COMPOSITE_LINEAR',
                'degree': 1,
                'params': (global_a, global_b), 
                'modulus': M,
                'note': f"Synthesized from {moduli}"
            }
            
        elif degree == 0:
            # y = c
            coeffs_c = [m['params'][0] for m in models]
            global_c = crt(coeffs_c, moduli)
            return {
                'type': 'COMPOSITE_CONSTANT',
                'degree': 0,
                'params': (global_c,), 
                'modulus': M,
                'note': f"Synthesized from {moduli}"
            }
            
        else:
            # Generic Degree N
            # Assume parameters correspond to coefficients of x^n, x^(n-1)... x^0
            # params = (an, an-1, ... a0)
            # We apply CRT to each position.
            
            num_coeffs = degree + 1
            global_coeffs = []
            
            for i in range(num_coeffs):
                # Extract i-th coefficient from all models
                # Verify length?
                local_coeffs = [m['params'][i] for m in normalized_models]
                g_c = crt(local_coeffs, moduli)
                global_coeffs.append(g_c)
                
            return {
                'type': 'COMPOSITE_POLYNOMIAL',
                'degree': degree,
                'params': tuple(global_coeffs),
                'modulus': M,
                'note': f"Synthesized Degree {degree} from {moduli}"
            }

    def check_product_formula(self, inputs, outputs, primes):
        # Placeholder for full product formula check if needed.
        # For now, CRT is the main production feature.
        pass
