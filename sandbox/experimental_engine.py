
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from sandbox.frontend_experiment.v60_lib.engine import V60Engine, TriadParser
from sandbox.frontend_experiment.v60_lib.term_normalizer import TermNormalizer

class ExperimentalParser(TriadParser):
    def _get_phase(self, relation: str) -> complex:
        """
        Overridden Phase Map to include Causal Flows.
        """
        r = relation.lower().strip()
        print(f"DEBUG PHASE: '{r}'") 
        
        # Original Map
        if r in ['cause', 'causes', 'lead', 'trigger', 'produce', 'yield']:
            return 1j # Rotation by 90 degrees (Causality)
        if r in ['is-not', 'differ', 'distinct', 'unlike']:
            return -1 # Rotation by 180 degrees (Negation)
        if r in ['correlate', 'associate', 'link']:
            return 1+1j # 45 degrees (Correlation/Entanglement)
            
        # NEW: Explicit Mapping for Nightmare Cycle
        if r in ['leads to', 'lead to', 'result in', 'results in']:
            return 1j 
            
        return 1 # Identity

class ExperimentalEngine(V60Engine):
    """
    Phase XXXV Experimental Engine.
    Uses ExperimentalParser.
    """
    def __init__(self):
        # Init base components (duplicated from V60Engine.__init__ but with swapped parser)
        # Verify V60Engine init signature. It usually sets self.parser
        super().__init__()
        # Swap the parser
        self.parser = ExperimentalParser()
