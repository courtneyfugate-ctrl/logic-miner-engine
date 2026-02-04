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
        Computes Mahler coefficients a_n using Forward Differences.
        Ideally requires inputs to be 0, 1, 2, ... N.
        If inputs are sparse, this naive implementation might fail.
        Current assumption: inputs are consecutive integers starting at 0 (Logic Traces).
        """
        # Map inputs to outputs dictionary
        data_map = {x: y for x, y in zip(inputs, outputs)}
        
        # Check if we have 0..max_degree
        # If not, we can't easily compute n-th difference at 0.
        # We limit max_degree to available data length.
        limit = min(max_degree, len(data_map))
        
        # Forward Difference Table
        # diffs[0] = row of f(x)
        row = [data_map.get(i, 0) for i in range(limit)]
        
        coeffs = []
        
        # a_0 = f(0)
        coeffs.append(row[0])
        
        for n in range(1, limit):
            # Compute next row of differences
            new_row = []
            for i in range(len(row) - 1):
                diff = row[i+1] - row[i]
                new_row.append(diff)
            
            row = new_row
            if not row: break
            
            # a_n = delta^n f(0) = row[0]
            coeffs.append(row[0])
            
        return coeffs

    def predict(self, x, coeffs):
        y = 0
        for n, a_n in enumerate(coeffs):
            term = a_n * self.binomial(x, n)
            y += term
        return int(y)

    def validation_metric(self, coeffs):
        """
        Checks Mahler Decay condition: |a_n|_p -> 0.
        Returns a score: Higher is better decay.
        """
        # We want to see if valuation increases as n increases.
        # v(a_n) should grow.
        normalized_valuations = []
        
        for n, a_n in enumerate(coeffs):
            if a_n == 0:
                normalized_valuations.append(100) # Infinite valuation
            else:
                v = 0
                temp = abs(a_n)
                while temp > 0 and temp % self.p == 0:
                    v += 1
                    temp //= self.p
                normalized_valuations.append(v)
                
        # Metric: Slope of valuation growth?
        # Or simple check: Is v(last) >> v(first)?
        if not normalized_valuations: return 0
        
        # Check trend
        score = 0
        for i in range(len(normalized_valuations) - 1):
            if normalized_valuations[i+1] > normalized_valuations[i]:
                score += 1
            if normalized_valuations[i+1] >= 2: # High valuation implies convergence
                score += 0.5
                
        # Normalize by length
        return score / len(coeffs)
