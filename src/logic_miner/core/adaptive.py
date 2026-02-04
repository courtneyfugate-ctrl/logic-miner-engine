from .solver import ModularSolver

class GhostDetector:
    def __init__(self, p):
        self.p = p
        self.solver = ModularSolver(p)

    def check_ghost_terms(self, inputs, outputs, current_model, current_degree):
        """
        Checks if residuals of the current model imply a higher degree logic.
        Ghost Term Example: y = 7x^2 + x (mod 7).
        L0 Model: y = x (Linear).
        Residuals: (y - x)/7 = x^2.
        
        If we fit residuals mod p, do we see a Quadratic?
        """
        # Calculate residuals scaled by p (The 'next' level, effectively)
        # But we act *before* the lifter moves on.
        # We want to know: "Is the current model DEGREE sufficient?"
        
        # 1. Compute errors
        residuals = []
        valid_indices = []
        
        # Unpack model
        params = current_model
        
        # Helper to predict
        def predict(x, deg, pars):
            if deg == 0: return pars[0]
            elif deg == 1: return pars[0]*x + pars[1]
            elif deg == 2: return pars[0]*x**2 + pars[1]*x + pars[2]
            return 0
            
        for i, x in enumerate(inputs):
            y = outputs[i]
            y_pred = predict(x, current_degree, params)
            
            diff = y - y_pred
            if diff % self.p == 0:
                # Residual for next level
                res = diff // self.p
                residuals.append((x, res % self.p))
                
        if len(residuals) < 5:
            return None # Not enough data
            
        # 2. Fit Higher Degree to Residuals
        # If current is Linear (1), check Quadratic (2).
        # if current is Constant (0), check Linear (1) or Quad (2).
        
        next_degree_check = current_degree + 1
        if next_degree_check > 2:
            return None # Cap at Quad for now
            
        # Run RANSAC on residuals with higher degree
        result = self.solver.ransac(residuals, iterations=100, max_degree=2)
        
        if result['model'] is None:
            return None
            
        # 3. Decision Logic
        # If the residuals have STRONG structure (high consensus) AND the best fit 
        # is a HIGHER degree than the current model, it implies a Ghost Term.
        # Why? Because standard lifting assumes the *shape* (degree) is constant.
        # If residuals require x^2, then the total logic requires x^2. 
        # Thus, the Base Model *should* be x^2 (even if coeff is 0 mod p).
        
        found_degree = result['degree']
        consensus = result['ratio']
        
        if consensus > 0.6 and found_degree > current_degree:
            return {
                'suggestion': 'UPGRADE_DEGREE',
                'new_degree': found_degree,
                'confidence': consensus,
                'reason': f"Residuals imply degree {found_degree} (conf {consensus:.2f})"
            }
            
        return None
