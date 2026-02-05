
import math

class LogicInterpreter:
    """
    Protocol V.23: Logic Interpreter.
    Translates abstract polynomials into human-readable insights.
    Uses p-adic sensitivity and attractor dynamics.
    """
    def __init__(self, p=5):
        self.p = p

    def compute_derivative(self, poly):
        """
        Computes the formal derivative f'(x) of polynomial f(x).
        poly = [a0, a1, a2, ..., an] where f(x) = sum(ai * x^i)
        """
        # f'(x) = sum(i * ai * x^(i-1))
        deriv = []
        for i in range(1, len(poly)):
            deriv.append(i * poly[i])
        return deriv

    def evaluate_poly(self, poly, x):
        """
        Evaluates polynomial at point x.
        """
        val = 0
        for i, coeff in enumerate(poly):
            val += coeff * (x ** i)
        return val

    def get_padic_valuation(self, n):
        """
        Returns v_p(n).
        """
        if n == 0: return 100 # Infinity
        v = 0
        temp = abs(n)
        while temp > 0 and temp % self.p == 0:
            v += 1
            temp //= self.p
        return v

    def get_padic_norm(self, n):
        """
        Returns |n|_p = p^-v_p(n).
        """
        if n == 0: return 0.0
        v = self.get_padic_valuation(n)
        return float(self.p ** (-v))

    def sensitivity_probe(self, poly, coordinates):
        """
        Feature A: The Sensitivity Probe.
        Interpretation of |f'(x)|_p.
        """
        print("--- [Interpreter] Sensitivity Probe (Derivative Check) ---")
        deriv = self.compute_derivative(poly)
        results = {}
        
        for term, x in coordinates.items():
            slope = self.evaluate_poly(deriv, x)
            norm = self.get_padic_norm(slope)
            
            # Interpretation
            if norm < 1e-10: # Near zero in p-adic terms
                interp = "Universal Truth (Analytic Anchor)"
            elif norm <= 1.0 / self.p:
                interp = "Stable Law"
            else:
                interp = "Context-Dependent Detail"
            
            results[term] = {
                'x': x,
                'f_prime_x': slope,
                'norm': norm,
                'interpretation': interp
            }
        return results

    def attractor_scan(self, poly, iterations=100, seeds=None):
        """
        Feature B: The Attractor Scan.
        Axiom discovery via dynamics.
        """
        print("--- [Interpreter] Attractor Scan (Dynamics) ---")
        fixed_points = set()
        
        if seeds is None:
            seeds = [0, 1, self.p, self.p**2, 125]
            
        for x_start in seeds:
            curr = x_start
            path = [curr]
            seen = {curr}
            
            for _ in range(iterations):
                # x_{n+1} = f(x_n)
                # Note: f(x) often overflows in standard integers for high-deg.
                # In p-adics, we usually work in Z_p or Mod p^k.
                # However, our f(x) is derived as Product(x-ci), so f(ci)=0.
                # This means Core Concepts are ROOTS, not necessarily Fixed Points 
                # unless we define dynamics as x_{n+1} = x_n - f(x_n)/f'(x_n) [Newton].
                
                # If we use x_{n+1} = f(x_n), we are looking for mapping stability.
                # If f(x) is the characteristic poly, f(root) = 0.
                # Fixed point f(x*) = x* would imply a different structure.
                
                # USER logic: "Find fixed points x* where f(x*) = x*."
                try:
                    next_x = self.evaluate_poly(poly, curr)
                    if next_x == curr:
                        fixed_points.add(curr)
                        break
                    if next_x in seen:
                        # Cycle detected
                        break
                    curr = next_x
                    seen.add(curr)
                except OverflowError:
                    break
        
        return list(fixed_points)

    def discover_axioms(self, poly, coordinates, tolerance=1e-5):
        """
        Identifies concepts that serve as Fixed Points or roots.
        """
        results = []
        for term, x in coordinates.items():
            val = self.evaluate_poly(poly, x)
            # Concept is a Root by definition of our construction
            # But is it an Attractor? f(x) = x
            if abs(val - x) < tolerance:
                results.append(term)
        return results
