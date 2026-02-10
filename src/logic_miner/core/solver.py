import random
import math
import concurrent.futures

class ModularSolver:
    def __init__(self, p):
        self.p = p

    def solve_polynomial(self, points, degree):
        """
        Solves y = poly(x) (mod p) given (degree+1) points.
        Supports degree 0, 1, 2.
        Returns coefficients (c,) or (m, c) or (a, b, c).
        """
        if degree == 0:
            # y = c
            # Need 1 point (x, y)
            if len(points) < 1: return None
            return (points[0][1] % self.p,)
            
        elif degree == 1:
            # y = mx + c
            # Need 2 points
            if len(points) < 2: return None
            (x1, y1), (x2, y2) = points[:2]
            
            dx = (x1 - x2) % self.p
            dy = (y1 - y2) % self.p
            
            if dx == 0: return None
            
            inv_dx = pow(dx, self.p - 2, self.p)
            m = (dy * inv_dx) % self.p
            c = (y1 - m * x1) % self.p
            return (m, c)
            
        elif degree == 2:
            # y = ax^2 + bx + c
            # Need 3 points
            if len(points) < 3: return None
            (x1, y1), (x2, y2), (x3, y3) = points[:3]
            
            # Using Lagrange Interpolation or direct generic solution?
            # For small degrees, direct formula is cleaner or elimination.
            # Let's use Lagrange logic for robustness or just direct elimination.
            # L(x) = sum( y_j * l_j(x) )
            # l_j(x) = prod( (x - x_k)/(x_j - x_k) )
            
            # Simplified for speed: Determinant method (Cramer)
            # System:
            # a*x1^2 + b*x1 + c = y1
            # a*x2^2 + b*x2 + c = y2
            # a*x3^2 + b*x3 + c = y3
            
            # Vandermonde matrix determinants
            # D = | x1^2 x1 1 |
            #     | x2^2 x2 1 |
            #     | x3^2 x3 1 |
            # D = (x1-x2)(x2-x3)(x1-x3) ? No, standard Vandermonde is (x2-x1)(x3-x1)(x3-x2)
            # Careful with order.
            
            # Let's solve m1 = (y2-y1)/(x2-x1) is not valid for quad.
            
            # Manual algebraic solution:
            # 1. Substitute c = y1 - a*x1^2 - b*x1
            # ... It's messy.
            
            # Let's use Python's built-in pow/ops but need to be careful with mod inverse.
            # If any (x_i - x_j) is 0 mod p, fail.
            if (x1 - x2) % self.p == 0 or (x2 - x3) % self.p == 0 or (x1 - x3) % self.p == 0:
                return None

            try:
                # Lagrange Basis Polynomials
                # P(x) = y1 * L1 + y2 * L2 + y3 * L3
                # L1 = (x-x2)(x-x3) / (x1-x2)(x1-x3)
                
                # We need coefficients a, b, c from P(x) = a x^2 + b x + c
                # L1 numerator = x^2 - (x2+x3)x + x2x3
                # L1 den = (x1-x2)(x1-x3)
                # inv_den1
                
                def inv(n): return pow(n, self.p - 2, self.p)
                
                inv_d1 = inv((x1-x2)*(x1-x3) % self.p)
                inv_d2 = inv((x2-x1)*(x2-x3) % self.p)
                inv_d3 = inv((x3-x1)*(x3-x2) % self.p)
                
                term1 = (y1 * inv_d1) % self.p
                term2 = (y2 * inv_d2) % self.p
                term3 = (y3 * inv_d3) % self.p
                
                # a = sum( y_i / den_i )
                a = (term1 + term2 + term3) % self.p
                
                # b = sum( -y_i * (sum other roots) / den_i )
                b = (term1 * -(x2+x3) + term2 * -(x1+x3) + term3 * -(x1+x2)) % self.p
                
                # c = sum( y_i * prod other roots / den_i )
                c = (term1 * (x2*x3) + term2 * (x1*x3) + term3 * (x1*x2)) % self.p
                
                return (a, b, c)
            except ValueError:
                return None
                
        elif degree == 3:
            # y = ax^3 + bx^2 + cx + d
            if len(points) < 4: return None
            pts = points[:4]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            
            # Check distinct x
            for i in range(4):
                for j in range(i+1, 4):
                    if (xs[i] - xs[j]) % self.p == 0: return None
                    
            def inv(n): return pow(n, self.p - 2, self.p)
            coeffs = [0]*4 # a, b, c, d
            
            for i in range(4):
                xi, yi = xs[i], ys[i]
                
                # Denominator
                den = 1
                roots = []
                for j in range(4):
                    if i == j: continue
                    den = (den * (xi - xs[j])) % self.p
                    roots.append(xs[j])
                    
                term = (yi * inv(den)) % self.p
                
                # Numerator Poly: (x-r1)(x-r2)(x-r3)
                # = x^3 - e1*x^2 + e2*x - e3
                r1, r2, r3 = roots
                e1 = (r1 + r2 + r3) % self.p
                e2 = (r1*r2 + r1*r3 + r2*r3) % self.p
                e3 = (r1*r2*r3) % self.p
                
                coeffs[0] = (coeffs[0] + term) % self.p       # x^3
                coeffs[1] = (coeffs[1] - term * e1) % self.p  # x^2
                coeffs[2] = (coeffs[2] + term * e2) % self.p  # x
                coeffs[3] = (coeffs[3] - term * e3) % self.p  # 1
                
            return tuple(coeffs)
            
        return None

    def _calculate_newton_slope(self, inliers):
        """
        [RESTORED] Analyzing the Newton Polygon of the Mahler expansion.
        The slope of the lower convex hull of (k, v_p(a_k)) defines ramification.
        """
        if not inliers or len(inliers) < 3: return 0.0, []
        
        # 1. Compute Mahler Coefficients for the inlier set
        # We sample up to 15 points to keep it efficient
        sample = inliers[:15]
        xs = [float(d[0]) for d in sample]
        ys = [float(d[1]) for d in sample]
        
        from .mahler import MahlerSolver
        msolver = MahlerSolver(self.p)
        coeffs = msolver.compute_coefficients(xs, ys, max_degree=len(sample)-1)
        
        # 2. Calculate Valuations v_p(a_k)
        def vp(n):
            if abs(n) < 1e-9: return 10.0
            # For Mahler coeffs, we look at the denominator-adjusted valuation
            # or simply the integer valuation if we can.
            # Here we use a log-based proxy for p-adic magnitude.
            return -math.log(abs(n), self.p) if abs(n) > 0 else 10.0

        v_profile = [vp(c) for c in coeffs]
        
        # 3. Calculate Slope of the Hull
        # Simple linear fit of the valuations (proxy for lower convex hull slope)
        if len(v_profile) < 2: return 0.0, v_profile
        
        slope = (v_profile[-1] - v_profile[0]) / (len(v_profile) - 1)
        return slope, v_profile

    def ransac_iterative(self, data, min_size=5, min_ratio=0.5):
        """
        Multimodal RANSAC (Iterative Peeling).
        Extracts dominant logic, removes it, and repeats to find secondary branches.
        Returns List of Logic Results.
        """
        if not data: return []
        
        layers = []
        remaining_data = list(data)
        
        # Max 5 layers to prevent infinite loops on noise
        for layer_idx in range(5):
            if len(remaining_data) < min_size:
                break
                
            res = self.ransac(remaining_data, iterations=100)
            
            # Acceptance Criteria
            # Must have found a model
            # Must have decent ratio (relative to CURRENT buffer)
            # OR absolute count?
            
            if not res['model']:
                break
                
            if res['ratio'] < min_ratio:
                 # If ratio is low, is it noise?
                 # Example: 100 points. 10 outliers. Ratio 0.1?
                 # No, ransac ratio is relative to input size.
                 # If input is 100 noise, ratio -> 2/100 (degree).
                 # We need a cutoff.
                 break
                 
            # Store Layer
            # Add metadata 'layer_index' and Newton Metrics
            res['layer_index'] = layer_idx
            slope, profile = self._calculate_newton_slope(res['inliers'])
            res['valuation_slope'] = slope
            res['newton_profile'] = profile
            layers.append(res)
            
            # Peel
            # Remove Inliers
            # Inliers are tuples. Need robust removal.
            # Assuming data is hashable or simple equality.
            inlier_set = set() 
            # Note: inliers can be ([x1,x2], y). List not hashable.
            # Convert to tuple for set logic
            for d in res['inliers']:
                if isinstance(d[0], list):
                    inlier_set.add( (tuple(d[0]), d[1]) )
                else:
                    inlier_set.add(d)
                    
            new_data = []
            for d in remaining_data:
                key = (tuple(d[0]), d[1]) if isinstance(d[0], list) else d
                if key not in inlier_set:
                    new_data.append(d)
                    
            if len(new_data) == len(remaining_data):
                # No reduction? Infinite loop guard.
                break
                
            remaining_data = new_data
            
        return layers
    def solve_multivariate(self, X_batch, y_batch):
        """
        Solves y = b0 + b1*x1 + ... + bn*xn (mod p).
        X_batch: list of lists/tuples [ [x1, x2..], ... ]
        y_batch: list of ints
        Returns: coefficients (b0, b1, ... bn) or None.
        Note: b0 is the constant (intercept).
        """
        if not X_batch or not y_batch: return None
        n_samples = len(X_batch)
        n_features = len(X_batch[0])
        
        # We need N >= K+1 samples (K features + 1 intercept)
        if n_samples < n_features + 1: return None
        
        # Construct Design Matrix A: [1, x1, x2...]
        A = []
        for row in X_batch:
            A.append([1] + list(row))
            
        # Select subset for exact system?
        # Gaussian Elim handles overdetermined if we limit rows
        # Or we act deterministically on first K+1
        
        subset_size = n_features + 1
        A_sub = A[:subset_size]
        y_sub = y_batch[:subset_size]
        
        beta = self.gaussian_elimination(A_sub, y_sub)
        
        # Validate on rest (RANSAC style usually handles this, but here we just fit)
        if beta and len(y_batch) > subset_size:
             # Quick check on one other point?
             # For now, just return candidate.
             pass
             
        return beta

    def gaussian_elimination(self, A, y):
        """
        Solves A * x = y (mod p). A is list of lists.
        """
        rows = len(A)
        if rows == 0: return None
        cols = len(A[0])
        
        # Augment
        M = [row[:] + [val] for row, val in zip(A, y)]
        
        pivot_row = 0
        col_pivots = []
        
        for j in range(cols):
            if pivot_row >= rows: break
            
            # Find pivot
            curr = pivot_row
            while curr < rows and M[curr][j] % self.p == 0:
                curr += 1
                
            if curr == rows: continue
            
            # Swap
            M[pivot_row], M[curr] = M[curr], M[pivot_row]
            
            # Normalize
            try:
                inv = pow(M[pivot_row][j], self.p - 2, self.p)
            except:
                return None
                
            M[pivot_row] = [(x * inv) % self.p for x in M[pivot_row]]
            
            # Eliminate
            for i in range(rows):
                if i != pivot_row:
                    factor = M[i][j]
                    M[i] = [(M[i][k] - factor * M[pivot_row][k]) % self.p for k in range(cols + 1)]
                    
            col_pivots.append(j)
            pivot_row += 1
            
        beta = [0] * cols
        for i in range(len(col_pivots)):
            beta[col_pivots[i]] = M[i][-1]
            
        return beta

    def ransac(self, data, iterations=100, max_degree=2):
        """
        Poly-Morph RANSAC.
        Supports 1D Inputs (x,y) AND Multivariate Inputs ([x1,x2], y).
        """
        # Detect Multivariate
        if data and isinstance(data[0][0], (list, tuple)):
             return self.ransac_multivariate(data, iterations)
             
        # ... Original 1D Logic ...
        best_overall = {'model': None, 'degree': -1, 'inliers': [], 'ratio': 0.0}
        
        for degree in range(max_degree + 1):
            if len(data) < degree + 1: continue
            
            res = self._ransac_poly(data, iterations, degree)
            
            if res['ratio'] > 0.70:
                res['degree'] = degree
                return res
            
            if res['ratio'] > best_overall['ratio']:
                best_overall = res
                best_overall['degree'] = degree
                
        return best_overall

    def ransac_multivariate(self, data, iterations):
        # Data is list of ([x1, x2..], y)
        n_features = len(data[0][0])
        min_samples = n_features + 1
        
        best_model = None
        best_inliers = []
        
        for _ in range(iterations):
            try:
                sample = random.sample(data, min_samples)
            except ValueError: continue
            
            X_s = [d[0] for d in sample]
            y_s = [d[1] for d in sample]
            
            beta = self.solve_multivariate(X_s, y_s)
            
            if beta is not None:
                # Score
                current_inliers = []
                for d in data:
                    x_vec = d[0]
                    y_true = d[1]
                    
                    # Dot product with beta (beta[0] is intercept)
                    pred = beta[0] 
                    for k in range(n_features):
                        pred += beta[k+1] * x_vec[k]
                    
                    if pred % self.p == y_true:
                        current_inliers.append(d)
                
                if len(current_inliers) > len(best_inliers):
                    best_inliers = current_inliers
                    best_model = beta
                    
        return {
            'model': best_model,
            'degree': 1, # Multivariate Linear
            'type': 'MULTIVARIATE_LINEAR',
            'inliers': best_inliers,
            'ratio': len(best_inliers) / len(data) if data else 0
        }


    def ransac_parallel(self, data, iterations=100, workers=4, max_degree=2):
        # Parallel logic could apply here, but "Poly-Morph" adds complexity.
        # For this revision, we keep it simple: Sequential degree check, parallel within degree?
        # Or just default to the robust standard ransac for now.
        return self.ransac(data, iterations, max_degree)

    def _ransac_poly(self, data, iterations, degree):
        best_model = None
        best_inliers = []
        n_sample = degree + 1
        
        for _ in range(iterations):
            try:
                sample = random.sample(data, n_sample)
            except ValueError:
                continue 
            
            model = self.solve_polynomial(sample, degree)
            if model is None: continue
            
            # Score
            # Evaluate poly at x
            current_inliers = []
            
            # Optimization: 
            # D0: y = c
            # D1: y = mx + c
            # D2: y = ax^2 + bx + c
            
            if degree == 0:
                c = model[0]
                current_inliers = [d for d in data if d[1] == c]
            elif degree == 1:
                m, c = model
                current_inliers = [d for d in data if (m * d[0] + c) % self.p == d[1]]
            elif degree == 2:
                a, b, c = model
                # (ax^2 + bx + c) % p
                current_inliers = [d for d in data if (a * d[0]**2 + b * d[0] + c) % self.p == d[1]]
            elif degree == 3:
                a, b, c, d_coeff = model
                # (ax^3 + bx^2 + cx + d) % p
                current_inliers = [pt for pt in data if (a * pt[0]**3 + b * pt[0]**2 + c * pt[0] + d_coeff) % self.p == pt[1]]
                
            if len(current_inliers) > len(best_inliers):
                best_inliers = current_inliers
                best_model = model
            
        slope, profile = self._calculate_newton_slope(best_inliers)
        return {
            'model': best_model,
            'inliers': best_inliers,
            'ratio': len(best_inliers) / len(data) if data else 0,
            'valuation_slope': slope,
            'newton_profile': profile
        }
