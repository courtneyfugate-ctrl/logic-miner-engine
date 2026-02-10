
from .serial_synthesis_v35 import SerialSynthesizerV35, NormConstrainedAlgebraicSolver
import math

class FlowBalancedAlgebraicSolver(NormConstrainedAlgebraicSolver):
    """
    V.36 Solver: Implements Flow Conservation (Conservative Semantic Fluid).
    Uses Sinkhorn-Knopp balancing to ensure Inflow = Outflow.
    """
    def _sinkhorn_balance(self, matrix, iterations=10):
        # Sinkhorn-Knopp Algorithm: Alternating Row/Col Normalization
        # Transforms matrix A into a doubly stochastic matrix D1 * A * D2
        # We'll just do simple iterative normalization for the semantic fluid approximation.
        
        n = len(matrix)
        if n == 0: return matrix
        
        # Work on a copy
        # Deep copy
        balanced = [row[:] for row in matrix]
        
        for _ in range(iterations):
            # Row Normalization (Outgoing Flow = 1)
            for i in range(n):
                row_sum = sum(balanced[i])
                if row_sum > 0:
                    balanced[i] = [x / row_sum for x in balanced[i]]
            
            # Column Normalization (Incoming Flow = 1)
            # Create col sums
            col_sums = [0.0] * n
            for i in range(n):
                for j in range(n):
                    col_sums[j] += balanced[i][j]
            
            for j in range(n):
                if col_sums[j] > 0:
                    for i in range(n):
                        balanced[i][j] /= col_sums[j]
                        
        return balanced
        
    def solve(self, matrix, entities, raw_counts_bond, fixed_root=None, fixed_addr=None):
        print(f"     > Flow Conservation: Balancing Semantic Fluid (Sinkhorn-Knopp)...")
        
        # 1. Apply Flow Conservation (Sinkhorn Balancing)
        # This modifies the matrix so that every node has roughly equal influence (In=Out).
        # This prevents "Reaction" (High Out-Degree) from dominating simply by volume.
        
        balanced_matrix = self._sinkhorn_balance(matrix, iterations=5)
        
        # 2. Call Parent Solve (V.35 Norm Constrained)
        # We pass the BALANCED matrix.
        # The V.35 solver will still apply "Vacuum Stabilization" if needed.
        # Note: V.35 solve modifies the matrix in place for Vacuum Energy.
        # It's fine to do that on the balanced matrix.
        
        result = super().solve(balanced_matrix, entities, raw_counts_bond, fixed_root, fixed_addr)
        
        return result

class SerialSynthesizerV36(SerialSynthesizerV35):
    """
    Protocol V.36: Flow Conservation Cycle.
    Extends V.35 with Flow-Balanced Solvers.
    """
    def __init__(self, chunk_size=50, momentum=0.3, resolution=0.5):
        super().__init__(chunk_size=chunk_size, momentum=momentum, resolution=resolution)
        
        # Replace Solvers with Flow-Balanced versions
        self.primes = [5, 7, 11]
        self.solvers = {}
        for p in self.primes:
            self.solvers[p] = FlowBalancedAlgebraicSolver(p=p, branching_threshold=resolution)
            
    def _process_block(self, text):
        super()._process_block(text)
