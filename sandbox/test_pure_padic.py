import unittest
from src.logic_miner.engine import LogicMiner

class TestPurePadic(unittest.TestCase):
    def setUp(self):
        self.miner = LogicMiner()
        
    def test_density_derivation(self):
        """
        Verify that Co-occurrence Density -> Algebraic Proximity.
        Cat/Dog appear together often -> Should have SMALL distance (High Valuation).
        Cat/Car never appear together -> Should have LARGE distance (Low Valuation).
        """
        # Text with clear co-occurrence clusters
        # Cluster 1: Cat, Dog, Pet
        # Cluster 2: Car, Truck, Road
        text = """
        The Cat and the Dog played in the park.
        My Pet is a Cat. My Pet is a Dog.
        The Cat sat. The Dog ran.
        
        The Car drove on the Road.
        The Truck drove on the Road.
        The Car and Truck are vehicles.
        """
        
        print("\n--- Running Pure P-adic Reconstruction on Density Text ---")
        res = self.miner.fit(text)
        
        # 1. Check Mode
        self.assertEqual(res['mode'], 'ALGEBRAIC_TEXT')
        
        # 2. Check Distances in the Matrix (Input to Lifter)
        # We need to find indices of entities
        # LogicMiner fit_text calls AlgebraicTextSolver.
        # But fit() returns the TreeResult. The 'matrix' key might be lost in fit_text wrapper?
        # fit_text in engine.py returns: tree_result which HAS 'coordinates'.
        
        # We can infer distance from coordinates: d(x,y) = |x - y|_p
        coords = res['coordinates']
        p = 5 # Default
        
        def padic_dist(x, y):
            diff = x - y
            if diff == 0: return 0
            v = 0
            while diff % p == 0:
                diff //= p
                v += 1
            return p ** (-v)
            
        d_cat_dog = padic_dist(coords.get('Cat',0), coords.get('Dog',0))
        d_cat_car = padic_dist(coords.get('Cat',0), coords.get('Car',0))
        
        print(f"Derived Distance(Cat, Dog): {d_cat_dog}")
        print(f"Derived Distance(Cat, Car): {d_cat_car}")
        
        # Expectation: Cat-Dog should be closer than Cat-Car
        self.assertLess(d_cat_dog, d_cat_car, "Algebraic Distance Violation: Linked entities should be closer.")
        
    def test_godel_mapping(self):
        """Verify entities are mapped to Integers (not vectors)."""
        text = "Alpha Beta. Alpha Beta."
        res = self.miner.fit(text)

        coords = res['coordinates']
        for k, v in coords.items():
            self.assertIsInstance(v, int, "Coordinates must be Integers (Z_p field elements).")

if __name__ == "__main__":
    unittest.main()
