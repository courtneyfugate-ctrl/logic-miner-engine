import math

class MahlerSolver:
    """
    Implements Mahler's Theorem for p-adic functions.
    f(x) = sum( a_n * binom(x, n) )
    """
    def __init__(self, p):
        self.p = p

    def binomial(self, x, n):
        """
        Computes binom(x, n) = x(x-1)...(x-n+1) / n!
        """
        if n < 0: return 0
        if n == 0: return 1
        
        numerator = 1
        for i in range(n):
            numerator *= (x - i)
        
        denominator = math.factorial(n)
        
        # In p-adic land, we usually work with integers.
        # Ideally, we return numerator // denominator.
        # But for modeling, we need float or p-adic numbers? 
        # No, for logic mining we deal with integer sequences.
        return numerator // denominator

    def compute_coefficients(self, inputs, outputs, max_degree=10):
        """
        [RESTORED] Computes coefficients using Newton's Divided Differences.
        Works for any set of distinct inputs.
        f[x0...xk] = (f[x1...xk] - f[x0...xk-1]) / (xk - x0)
        """
        n = len(inputs)
        if n == 0: return []
        
        limit = min(max_degree + 1, n)
        xs = inputs[:limit]
        ys = outputs[:limit]
        
        # Divided Difference Table
        table = [[0.0] * limit for _ in range(limit)]
        for i in range(limit):
            table[i][0] = float(ys[i])
            
        for k in range(1, limit):
            for i in range(limit - k):
                # Denominator: x[i+k] - x[i]
                den = (xs[i+k] - xs[i])
                if abs(den) < 1e-9:
                    table[i][k] = 0.0
                else:
                    table[i][k] = (table[i+1][k-1] - table[i][k-1]) / den
                    
        # Coefficients a_k = f[x0...xk]
        coeffs = [table[0][k] for k in range(limit)]
        return coeffs

    def predict(self, x, coeffs):
        y = 0
        for n, a_n in enumerate(coeffs):
            term = a_n * self.binomial(x, n)
            y += term
        return int(y)

    def validation_metric(self, coeffs):
        """
        [RESTORED] Checks Mahler Regularization: v_p(a_n) >= floor(math.log(n, p)).
        This prevents overfitting and ensures the p-adic tree preserves geometry.
        """
        if not coeffs: return 0.0
        
        valid_count = 0
        total_coeffs = len(coeffs)
        
        for n, a_n in enumerate(coeffs):
            if n == 0: 
                valid_count += 1
                continue
                
            # Log-bound: v_p(a_n) >= floor(log_p n)
            required_vp = math.floor(math.log(n, self.p))
            
            # Calculate actual valuation
            if a_n == 0:
                actual_vp = 100
            else:
                actual_vp = 0
                temp = abs(int(a_n))
                while temp > 0 and temp % self.p == 0:
                    actual_vp += 1
                    temp //= self.p
            
            if actual_vp >= required_vp:
                valid_count += 1
                
        # Return percentage of coefficients obeying the regular lattice
        return valid_count / total_coeffs
