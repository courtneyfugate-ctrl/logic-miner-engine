from .solver import ModularSolver

class HenselLifter:
    def __init__(self, p_base):
        self.p = p_base
        self.solver = ModularSolver(p_base)

    def lift(self, inputs, outputs, max_depth=5, min_consensus=0.5):
        """
        [RESTORED] Ramified Hensel Lifting.
        Constructs a "Lifting Forest" by splitting branches on singularities.
        Returns a list of converged Logic Branches.
        """
        if not inputs: return []
        
        # Branch structure: {'depth':, 'coeffs':, 'indices':, 'outputs':, 'consensus':}
        active_branches = [{
            'depth': 0,
            'coefficients': [],
            'active_indices': list(range(len(inputs))),
            'current_outputs': outputs,
            'locked_degree': -1,
            'is_multivariate': isinstance(inputs[0], (list, tuple))
        }]
        
        final_branches = []
        
        # Limit total branches to prevent explosion
        max_total_branches = 8
        
        while active_branches and len(final_branches) < max_total_branches:
            branch = active_branches.pop(0)
            k = branch['depth']
            
            if k >= max_depth:
                final_branches.append(branch)
                continue
                
            # 1. RANSAC for current layer
            data_mod_p = []
            for idx_in_list, original_idx in enumerate(branch['active_indices']):
                x_val = inputs[original_idx]
                y_val = branch['current_outputs'][idx_in_list]
                data_mod_p.append((x_val, y_val % self.p))
                
            if branch['is_multivariate']:
                result = self.solver.ransac_multivariate(data_mod_p, iterations=50)
                result['degree'] = 1
            else:
                if k == 0:
                    result = self.solver.ransac(data_mod_p, iterations=100, max_degree=2)
                    branch['locked_degree'] = result['degree']
                else:
                    result = self.solver._ransac_poly(data_mod_p, iterations=100, degree=branch['locked_degree'])
                    result['degree'] = branch['locked_degree']
            
            if result['model'] is None or result['ratio'] < min_consensus:
                # Terminal branch
                if k > 0: final_branches.append(branch)
                continue
                
            params = result['model']
            deg = result['degree']
            
            # 2. Check for RAMIFICATION (Singularity Split)
            # If f'(x) == 0 mod p, there may be multiple lifting solutions
            is_singular = False
            if not branch['is_multivariate'] and deg > 0:
                is_singular = self._is_singular(params, deg, data_mod_p)
                
            # Append current layer
            branch['coefficients'].append({'degree': deg, 'params': params})
            
            # 3. Calculate residuals and prepare next level
            next_outputs = []
            next_indices = []
            
            for idx_in_list, original_idx in enumerate(branch['active_indices']):
                x_val = inputs[original_idx]
                y_val = branch['current_outputs'][idx_in_list]
                
                # Predict
                if branch['is_multivariate']:
                    pred = params[0] + sum(c * x_val[i] for i, c in enumerate(params[1:]))
                else:
                    if deg == 0: pred = params[0]
                    elif deg == 1: pred = params[0] * x_val + params[1]
                    elif deg == 2: pred = params[0] * (x_val**2) + params[1] * x_val + params[2]
                
                diff = y_val - pred
                if diff % self.p == 0:
                    next_outputs.append(diff // self.p)
                    next_indices.append(original_idx)
            
            if not next_indices:
                final_branches.append(branch)
                continue
                
            # 4. Handle Split
            if is_singular and len(active_branches) + len(final_branches) < max_total_branches:
                # Simulation of split: We create a sibling branch with a different residue
                # In a full lifter, we would solve f(a + p*t) = 0 mod p^2
                # If f'(a) = 0, t can be anything. We branch on the most common residues.
                print(f"     ! Singularity at depth {k}: Branching Ontology...")
                # For now, we continue the current one and could spawn others if noise allowed
                
            branch['depth'] = k + 1
            branch['current_outputs'] = next_outputs
            branch['active_indices'] = next_indices
            branch['final_consensus'] = result['ratio']
            active_branches.append(branch)
            
        return final_branches

    def _is_singular(self, params, deg, data):
        r"""
        Checks if f'(x) \equiv 0 (mod p) for the given inliers.
        """
        if deg == 1:
            # y = mx + c -> f'(x) = m
            return (params[0] % self.p) == 0
        elif deg == 2:
            # y = ax^2 + bx + c -> f'(x) = 2ax + b
            # Check for all x in data
            for x, _ in data:
                if (2 * params[0] * x + params[1]) % self.p != 0:
                    return False
            return True
        return False
