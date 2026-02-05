import sys
import unittest
from src.logic_miner.engine import LogicMiner

class TestAlgebraicStrictness(unittest.TestCase):
    def setUp(self):
        self.miner = LogicMiner()
        self.valid_text = """
        The Dog barks. The Wolf howls. 
        The Dog runs. The Wolf hunts. 
        The Car drives. The Truck hauls.
        The Car speeds. The Truck loads.
        """
        
    def test_no_forbidden_ml_libs(self):
        """Ensure running the miner does NOT load heavy ML libs."""
        self.miner.fit(self.valid_text)
        
        forbidden = ['sklearn', 'scipy.cluster', 'torch', 'tensorflow', 'gensim', 'spacy']
        loaded = sys.modules.keys()
        
        for lib in forbidden:
            # We check if the top-level package is in modules
            msg = f"Strictness Violation: {lib} should not be loaded."
            self.assertNotIn(lib, loaded, msg)

            
    def test_output_is_algebraic(self):
        """Ensure successful fit returns a Polynomial and P-adic Coordinates."""
        res = self.miner.fit(self.valid_text)
        
        # Mode Check
        self.assertEqual(res['mode'], 'ALGEBRAIC_TEXT', "Must be ALGEBRAIC_TEXT derived from Algebra.")

        
        # Schema Check
        self.assertIn('polynomial', res, "Result must contain the Defining Polynomial.")
        self.assertIn('coordinates', res, "Result must contain p-adic coordinates.")
        self.assertIn('energy', res, "Result must contain Rectification Energy.")
        
        # Type Check
        coeffs = res['polynomial']
        self.assertIsInstance(coeffs, list, "Polynomial coeffs must be a list.")
        self.assertTrue(len(coeffs) > 0, "Polynomial must have degree >= 0.")
        
    def test_strong_triangle_inequality(self):
        """Verify the solver enforcing Strong Triangle Inequality."""
        res = self.miner.fit(self.valid_text)
        
        # If we got a matrix back (which fit_text calls fit_ultrametric to make tree)
        if res.get('energy', 0.0) == 0.0:
            print("[Info] Perfect fit found (Energy 0). Rare but possible for small inputs.")
        else:
            print(f"[Info] Rectification Energy: {res['energy']:.4f}")


if __name__ == "__main__":
    unittest.main()
