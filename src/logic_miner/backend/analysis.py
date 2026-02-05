
import math
from .interpreter import LogicInterpreter

class FitAnalyzer:
    """
    Protocol V.23: Fit Analyzer.
    Validates Semantic Fidelity of the models using Predictive Splining.
    """
    def __init__(self, p=5):
        self.p = p
        self.interpreter = LogicInterpreter(p=p)

    def predictive_spline_test(self, poly_n, entities_n_plus_1, coords_n_plus_1):
        """
        Feature A: The Predictive Spline Test.
        Tests f_block_n on Block n+1 data.
        """
        print(f"--- [Analyzer] Predictive Spline Test (p={self.p}) ---")
        
        errors = {}
        total_error = 0.0
        
        for term, x in coords_n_plus_1.items():
            # If the term exists in block n+1 but we follow the logic of block n
            # We evaluate f_n(x). In our characteristic poly construction,
            # f(x) = product(x - ci) is the "Identity" f(ci)=0.
            
            # For a "Predictive Law", the relationship should persist.
            # If y = f(x) represents a rule, we check y_new vs f(x_new).
            
            # In our current "Algebraic Text" mode, f(x) IS the structure.
            # So "Prediction" means: Does the coordinate x of a term in block n+1
            # satisfy the polynomial of block n?
            
            val = self.interpreter.evaluate_poly(poly_n, x)
            norm = self.interpreter.get_padic_norm(val)
            
            errors[term] = norm
            total_error += norm

        avg_error = total_error / len(coords_n_plus_1) if coords_n_plus_1 else 1.0
        
        # Interpretation
        # If error is low, the polynomial from block n successfully "zeros" or "explains" block n+1.
        classification = "Descriptive (Historical Fact)"
        if avg_error < (1.0 / self.p):
            classification = "Predictive (Scientific Law)"
            
        return {
            'avg_error': avg_error,
            'classification': classification,
            'details': errors
        }

    def semantic_fidelity_report(self, spline_trace, global_coords):
        """
        Runs continuity checks across the entire spline.
        """
        report = []
        report.append("--- [Analyzer] Semantic Fidelity Report ---")
        
        for i in range(len(spline_trace) - 1):
            block_curr = spline_trace[i]
            block_next = spline_trace[i+1]
            
            # Predict next block using current polynomial
            # We need coordinates of elements in the next block
            # This requires tracking which entities belonged to which block.
            # In V.22 synthesis, we merge them into global_coords.
            
            # For the report, we summarize the shift.
            p_curr = block_curr['p']
            energy_curr = block_curr['energy']
            energy_next = block_next['energy']
            
            shift = abs(energy_next - energy_curr)
            report.append(f"Shift {block_curr['block']} -> {block_next['block']}: Energy Delta {shift:.4f}")
            
        return "\n".join(report)
