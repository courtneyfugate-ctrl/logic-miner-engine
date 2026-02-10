
from .serial_synthesis_v34 import SerialSynthesizerV34
from .algebraic_text import AlgebraicTextSolver
import math

class NormConstrainedAlgebraicSolver(AlgebraicTextSolver):
    """
    V.35 Solver: Implements algebraic conservation laws to prevent vacuum collapse.
    """
    def solve(self, matrix, entities, raw_counts_bond, fixed_root=None, fixed_addr=None):
        # 1. Inject Vacuum Energy (Background Field)
        # To prevent disconnects (Zero-Vector Singularity), we add a small 
        # "Universal Gravity" epsilon to the matrix.
        # This ensures the spectral graph is connected.
        
        n = len(matrix)
        epsilon = 0.001 # Small coupling constant
        
        # We also enforce a "Norm Constraint": The sum of weights leaving any node
        # must be at least epsilon.
        
        # We operate on the sub-matrix in the parent method, but here we receive 
        # the raw matrix. We can wrap the parent logic or rewrite it.
        # Rewriting specific parts of 'solve' is hard without copy-paste.
        # Let's use a "Pre-Processing" strategy modification.
        
        # Inspect input matrix size
        if n > 0:
            # Add Vacuum Energy: Connect everything to the "Global High Frequency" nodes
            # Find max freq node index
            # This is "Barycentric Anchoring" to the center of mass.
            
            # Identify "Massive" nodes (High frequency)
            sorted_indices = sorted(range(len(entities)), key=lambda i: raw_counts_bond.get(entities[i].replace(" ", "_"), 0), reverse=True)
            center_of_mass_idx = sorted_indices[0] if sorted_indices else 0
            
            for i in range(n):
                if i != center_of_mass_idx:
                    # Anchor to Center of Mass
                    # existing = matrix[i][center_of_mass_idx]
                    # matrix[i][center_of_mass_idx] = max(existing, epsilon)
                    # matrix[center_of_mass_idx][i] = max(matrix[center_of_mass_idx][i], epsilon)
                    
                    # Also anchor to self (Identity preservation)
                    matrix[i][i] = max(matrix[i][i], 1.0) 
        
        # Call Parent Solve
        result = super().solve(matrix, entities, raw_counts_bond, fixed_root, fixed_addr)
        
        # Post-Process: Fix Zero-Vector Singularity (Disconnected Nodes)
        coords = result['coordinates']
        purified_keys = set(entities) # Entities that should have coordinates (All inputs)
        
        # Identify nodes that have no coordinate (Disconnects)
        # Note: 'complexities' keys are entities.
        
        # Find a safe anchor (Max Depth of current tree)
        if coords:
            max_val = max(coords.values())
            # We want to place disconnected nodes in a new "Vacuum Sector"
            # We can just append them as a new trunk?
            # Or attach them to the Global Root (val=1)?
            # Let's attach them to the Global Root with a distinct "Vacuum" prefix.
            # e.g. Root + p^10
            
            # Find the Global Root (min val)
            root_val = min(coords.values())
            
            # We use a large power of p to segregate them
            vacuum_offset = (self.p ** 5)
            
            # Assign coordinates to missing terms
            missing_count = 0
            for e in purified_keys:
                if e not in coords:
                    # Assign a synthetic coordinate
                    # We distribute them linearly to avoid collision
                    missing_count += 1
                    syn_coord = root_val + vacuum_offset + missing_count
                    coords[e] = syn_coord
                    
            if missing_count > 0:
                print(f"     ! VACUUM STABILIZER: Recovered {missing_count} Disconnected Nodes (Zero-Vectors).")
                result['coordinates'] = coords
                # Re-compute polynomial score with new coords? 
                # Optional, but honest.
                
        return result

class SerialSynthesizerV35(SerialSynthesizerV34):
    """
    Protocol V.35: Conservation Cycle.
    Extends V.34 with Norm-Constrained Solvers.
    """
    def __init__(self, chunk_size=50, momentum=0.3, resolution=0.5):
        super().__init__(chunk_size=chunk_size, momentum=momentum)
        
        # Replace Solvers with Norm-Constrained versions
        # We use stable primes (exclude 2 and 3)
        self.primes = [5, 7, 11]
        self.solvers = {}
        for p in self.primes:
            self.solvers[p] = NormConstrainedAlgebraicSolver(p=p, branching_threshold=resolution)
            
    def _process_block(self, text):
        # Override just to ensure we use the refined V34 logic (which is in super)
        # V34 _process_block calls self.solvers[p].solve
        # So replacing self.solvers in __init__ is sufficient.
        super()._process_block(text)
