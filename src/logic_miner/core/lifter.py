from .solver import ModularSolver

class HenselLifter:
    def __init__(self, p_base):
        self.p = p_base
        self.solver = ModularSolver(p_base)

    def lift(self, inputs, outputs, max_depth=5, min_consensus=0.5):
        """
        Iteratively constructs the logic function F(x).
        Supports variable degrees per level (PolyMorph).
        """
        current_outputs = outputs
        coefficients = [] # List of {'degree': d, 'params': (...)}
        active_indices = list(range(len(inputs)))
        
        # Lock degree after Level 0
        locked_degree = -1
        
        is_multivariate = inputs and isinstance(inputs[0], (list, tuple))
        
        for k in range(max_depth):
            # 1. Construct RANSAC Data
            data_mod_p = []
            for idx_in_list, original_idx in enumerate(active_indices):
                x_val = inputs[original_idx]
                y_val = current_outputs[idx_in_list]
                
                # If multivariate, x_val is already tuple/list.
                data_mod_p.append((x_val, y_val % self.p))
            
            # 2. Run Poly-Morph RANSAC
            if k == 0:
                result = self.solver.ransac(data_mod_p, iterations=100, max_degree=2)
                if result['model'] is not None:
                    locked_degree = result['degree']
            else:
                if is_multivariate:
                     # For Multivariate, we assume Linear Form structure persists
                     # Or we re-run ransac?
                     # solver.ransac auto-detects multivariate.
                     # But _ransac_poly doesn't.
                     # We should use ransac_multivariate directly or use ransac generic.
                     result = self.solver.ransac_multivariate(data_mod_p, iterations=50) 
                     result['degree'] = 1 # Multivariate Linear
                else:
                     result = self.solver._ransac_poly(data_mod_p, iterations=100, degree=locked_degree)
                     result['degree'] = locked_degree
            
            if result['model'] is None or result['ratio'] < min_consensus:
                return {
                    'coefficients': coefficients,
                    'status': 'PHASE_SHIFT',
                    'depth': k,
                    'final_consensus': result['ratio']
                }
            
            deg = result['degree']
            params = result['model']
            
            # --- Ghost Term Check (Adaptive) ---
            # Skip for Multivariate
            if k == 0 and not is_multivariate:
                from .adaptive import GhostDetector
                gd = GhostDetector(self.p)
                ghost = gd.check_ghost_terms(inputs, outputs, params, deg)
                
                if ghost and ghost['suggestion'] == 'UPGRADE_DEGREE':
                    new_deg = ghost['new_degree']
                    print(f"[GhostDetector] Retroactive Upgrade: Deg {deg} -> {new_deg} (Conf {ghost['confidence']:.2f})")
                    if deg == 0 and new_deg == 1: params = (0, params[0])
                    elif deg == 0 and new_deg == 2: params = (0, 0, params[0])
                    elif deg == 1 and new_deg == 2: params = (0, params[0], params[1])
                    deg = new_deg
                    locked_degree = new_deg
                    result['degree'] = new_deg
                    result['model'] = params
            
            coefficients.append({'degree': deg, 'params': params})
            
            # 3. Hensel Step
            next_outputs = []
            next_active_indices = []
            
            # Inlier Set Logic
            # Multivariate: (tuple_x, y_mod_p)
            # Univariate: (scalar_x, y_mod_p)
            inlier_set = set() 
            # Note: result['inliers'] contains tuples (x, y) where x might be tuple or scalar
            # We need to ensure hashability (tuples are hashable, lists aren't).
            # If inputs are lists, convert to tuples?
            # Assuming inputs are tuples if multivariate (from test data).
            for d_in in result['inliers']:
                x_in, y_in = d_in
                if isinstance(x_in, list): x_in = tuple(x_in)
                inlier_set.add((x_in, y_in))

            for idx_in_list, original_idx in enumerate(active_indices):
                x_val = inputs[original_idx]
                y_val = current_outputs[idx_in_list]
                
                # Make x hashable for check
                x_key = tuple(x_val) if isinstance(x_val, list) else x_val
                
                if (x_key, y_val % self.p) in inlier_set:
                    
                    # Calculate Predicted
                    predicted_val = 0
                    if is_multivariate:
                         # params is [b0, b1, b2...]
                         # x_val is [x1, x2...]
                         predicted_val = params[0]
                         for i, c in enumerate(params[1:]):
                             predicted_val += c * x_val[i]
                    else:
                        if deg == 0: predicted_val = params[0]
                        elif deg == 1: predicted_val = params[0] * x_val + params[1]
                        elif deg == 2: predicted_val = params[0] * (x_val**2) + params[1] * x_val + params[2]
                        
                    diff = y_val - predicted_val
                    
                    if diff % self.p == 0:
                        next_outputs.append(diff // self.p)
                        next_active_indices.append(original_idx)
            
            current_outputs = next_outputs
            active_indices = next_active_indices
            
            if not active_indices:
                break
            
        return {
            'coefficients': coefficients,
            'status': 'CONVERGED',
            'depth': k + 1,
            'final_consensus': result['ratio']
        }
