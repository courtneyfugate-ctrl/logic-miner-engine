import math

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
