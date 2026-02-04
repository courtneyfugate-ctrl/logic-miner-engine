import math
import random

class RealSolver:
    """
    Solver for Archimedean (Real) Logic.
    Handles p = infinity.
    Upgraded with Robust RANSAC.
    """
    def __init__(self):
        pass
        
    def solve(self, inputs, outputs):
        """
        Attempts to model data using Real-valued logic.
        1. Robust Linear Regression (RANSAC)
        2. Robust Step Function (RANSAC)
        """
        n = len(inputs)
        if n < 2: return {'type': 'TRIVIAL', 'fidelity': 1.0}
        
        best_type = 'NO_FIT'
        best_fid = 0.0
        best_params = None
        
        # --- 1. Robust Linear (RANSAC) ---
        linear_fid, linear_params = self._ransac_linear(inputs, outputs)
        if linear_fid > best_fid:
            best_fid = linear_fid
            best_type = 'LINEAR_REAL'
            best_params = linear_params
            
        # --- 2. Robust Step Function (RANSAC) ---
        # Heuristic: Step functions have discrete values.
        step_fid, step_params = self._ransac_step(inputs, outputs)
        if step_fid > best_fid:
            best_fid = step_fid
            best_type = 'STEP_FUNCTION'
            best_params = step_params
            
        return {
            'type': best_type,
            'fidelity': best_fid,
            'params': best_params
        }
        
    def _ransac_linear(self, inputs, outputs, iterations=50, threshold=0.5):
        best_fid = 0.0
        best_params = None
        n = len(inputs)
        
        for _ in range(iterations):
            if n < 2: break
            # Sample 2 points
            idxs = random.sample(range(n), 2)
            x1, y1 = inputs[idxs[0]], outputs[idxs[0]]
            x2, y2 = inputs[idxs[1]], outputs[idxs[1]]
            
            if x2 == x1: continue
            
            m = (y2 - y1) / (x2 - x1)
            c = y1 - m * x1
            
            # Score
            hits = 0
            for x, y in zip(inputs, outputs):
                pred = m*x + c
                if abs(pred - y) <= threshold: hits += 1
                
            fid = hits / n
            if fid > best_fid:
                best_fid = fid
                best_params = (m, c)
                
        return best_fid, best_params

    def _ransac_step(self, inputs, outputs, iterations=50):
        # Scan for periodicity k
        # y = floor(x/k)*h + c
        # Simplified: Just check if y is constant over intervals?
        # Or brute force period k=2..20
        best_fid = 0.0
        best_params = None
        n = len(inputs)
        
        for k in range(2, 21):
            # Transform x -> z = floor(x/k)
            # Then it becomes y = h*z + c (Linear logic on z!)
            z_vals = [x // k for x in inputs]
            
            # Run fast RANSAC on (z, y)
            fid, params = self._ransac_linear(z_vals, outputs, iterations=20, threshold=0.5)
            
            if fid > best_fid:
                best_fid = fid
                best_params = (k, params[0], params[1]) # k, h, c
                
        return best_fid, best_params
