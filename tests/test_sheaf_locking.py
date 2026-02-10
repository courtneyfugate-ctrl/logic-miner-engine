
import unittest
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from logic_miner.core.sheaf_core import SheafScanner

class TestSheafScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = SheafScanner(p=5)

    def test_rigid_lock_success(self):
        """
        Verify that identical valuations across windows are accepted.
        """
        # Manifold A: A=1 (v=0), B=5 (v=1)
        # Manifold B: B=5 (v=1), C=25 (v=2)
        # Overlap: B. v_p(5) = 1. Match.
        
        man_a = {'coordinates': {'A': 1, 'B': 5}, 'depths': {'A': 0, 'B': 1}}
        man_b = {'coordinates': {'B': 5, 'C': 25}, 'depths': {'B': 1, 'C': 2}}
        overlap = ['B']
        
        compatible, diffs = self.scanner.verify_overlap(man_a, man_b, overlap)
        self.assertTrue(compatible, f"Should be compatible. Diffs: {diffs}")
        
        merged = self.scanner.glue_manifolds(man_a, man_b)
        self.assertEqual(len(merged['coordinates']), 3)
        self.assertEqual(merged['coordinates']['C'], 25)

    def test_rigid_lock_failure(self):
        """
        Verify that conflicting valuations cause rejection.
        """
        # Manifold A: B=5 (v=1)
        # Manifold B: B=25 (v=2)
        # Contradiction: Window A says B is depth 1, Window B says B is depth 2.
        
        man_a = {'coordinates': {'A': 1, 'B': 5}, 'depths': {'A': 0, 'B': 1}}
        man_b = {'coordinates': {'B': 25, 'C': 125}, 'depths': {'B': 2, 'C': 3}}
        overlap = ['B']
        
        compatible, diffs = self.scanner.verify_overlap(man_a, man_b, overlap)
        self.assertFalse(compatible, "Should be incompatible due to valuation mismatch.")
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0]['term'], 'B')
        self.assertEqual(diffs[0]['v_a'], 1)
        self.assertEqual(diffs[0]['v_b'], 2)

    def test_disjoint_is_compatible(self):
        """
        Verify that lack of overlap is considered compatible (trivial glue).
        """
        man_a = {'coordinates': {'A': 1}, 'depths': {'A': 0}}
        man_b = {'coordinates': {'C': 1}, 'depths': {'C': 0}}
        overlap = []
        
        compatible, diffs = self.scanner.verify_overlap(man_a, man_b, overlap)
        self.assertTrue(compatible)
        
        merged = self.scanner.glue_manifolds(man_a, man_b)
        self.assertEqual(len(merged['coordinates']), 2)

    def test_multiple_overlap_partial_failure(self):
        """
        Verify that if *any* term contradicts, the whole link is rejected.
        """
        # Overlap: B (match), D (mismatch)
        man_a = {'coordinates': {'A': 1, 'B': 5, 'D': 10}, 'depths': {}}
        man_b = {'coordinates': {'C': 1, 'B': 5, 'D': 100}, 'depths': {}}
        
        # B: v=1 vs v=1 (OK)
        # D: v=1 (5 divides 10 once) vs v=2 (5 divides 100 twice) -> FAIL
        
        overlap = ['B', 'D']
        compatible, diffs = self.scanner.verify_overlap(man_a, man_b, overlap)
        self.assertFalse(compatible)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0]['term'], 'D')

if __name__ == '__main__':
    unittest.main()
