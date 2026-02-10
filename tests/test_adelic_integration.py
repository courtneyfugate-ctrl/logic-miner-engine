import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.logic_miner.core.serial_synthesis import SerialManifoldSynthesizer
import logging

class TestAdelicIntegration(unittest.TestCase):
    def test_adelic_pipeline(self):
        # Create Synthesizer with p=2
        synth = SerialManifoldSynthesizer(p=2, chunk_size=50)
        
        # Text with strong p=2 arithmetic structure (Powers of 2 repetitions)
        # "A is Root" x 16
        # "B is Branch" x 8
        # "A is B" x 8 (B is sub-component of A?)
        # "C is Leaf" x 2
        # "B is C" x 2
        
        text = ("Root yields Branch. " * 8) + ("Branch yields Leaf. " * 4) + ("Root yields Leaf. " * 2)
        text += ("Root is Base. " * 16) # High frequency root
        
        # We expect:
        # Featurizer extracts entities: Root, Branch, Leaf.
        # Arithmetic Feats:
        # v_2(Root) ~ 0 (Unit)
        # v_2(Branch) > 0
        # v_2(Leaf) > v_2(Branch)
        # I(Root, Branch) > 0 (v_2(gcd(16, 8)) = 3?)
        
        # Process Block
        result = synth._process_block_sheaf(text, 0)
        # V.31+ Update: Expect Ramified Mode
        # result = local_result['mode']
        # We expect "RAMIFIED_5ADIC" or similar

        # Check if we got coordinates
        coords = result['coordinates'] # Changed from local_result to result
        self.assertTrue(len(coords) > 0)

        # Check hierarchy
        # Root (v=0) should be at base (val=1)
        # Branch (v>0) should be deeper (val > 1)
        root_coord = coords['Root']
        branch_coord = coords['Branch']
        leaf_coord = coords['Leaf']

        print(f"Adelic Coordinates: {coords}")

        # In V.31, Root is 1. Branch should be 1 + digit*p^k.
        self.assertTrue(root_coord == 1)
        self.assertTrue(branch_coord > root_coord)
        self.assertTrue(leaf_coord > branch_coord)

        # Check Energy (Placeholder is 0.5 score -> 0.5 energy)
        # self.assertTrue(local_result['energy'] < 1.0)
        self.assertTrue(result['analytic_score'] > 0.0) # Changed from local_result to result

        if root_coord and branch_coord: # Changed from root_c, branch_c to root_coord, branch_coord
            # P-adic expansion: children add p^k terms
            # BFE: child = parent + digit * p^(depth+1)
            # So val(child) should be close to val(parent) in p-adic distance (congruent)
            # But magnitude might be larger/different
            pass
            
        # Check energy trace
        self.assertTrue(len(synth.energy_history) > 0)
        print(f"Energy: {synth.energy_history[-1]}")

if __name__ == '__main__':
    unittest.main()
