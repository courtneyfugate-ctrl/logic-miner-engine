import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.logic_miner.core.text_featurizer import TextFeaturizer

class TestArithmeticExtraction(unittest.TestCase):
    def setUp(self):
        self.featurizer = TextFeaturizer()

    def test_inclusion_logic(self):
        # "Cat is Animal" repeated implies Cat -> Animal connection
        text = "Cat is Animal. Dog is Animal. Tiger is Animal. Lion is Animal. Animal is Life."
        text += " Cat is fuzzy. Dog is loyal."
        
        entities = ["Cat", "Animal", "Dog", "Life"]
        
        # Test with p=5 (consistent with Bio)
        feats = self.featurizer.extract_arithmetic_features(text, entities, primes=[5])
        
        # Structure changed: feats['primes'][5]['inclusion_matrix']
        inc_matrix = feats['primes'][5]['inclusion_matrix']
        ent_list = feats['entities']
        
        cat_idx = ent_list.index("Cat")
        ani_idx = ent_list.index("Animal")
        
        # I_AB = v_p(gcd(Count(A,B), Count(B)))
        # Count(Cat) = 2. Count(Animal) = 5. Count(Cat,Animal) = 1.
        # Pair(Animal, Cat): gcd(1, 2) = 1. v_5(1) = 0.
        # Pair(Cat, Animal): gcd(1, 5) = 1. v_5(1) = 0.
        # Wait, the counts here are too small to show interesting gcd structure for p=5.
        # We need counts that are multiples of p.
        
        # Use a synthetic count injection or just larger text?
        # Let's mock the counts logic in a separate test or just rely on the math.
        # If I repeat the text 5 times.
        # Count(Cat) = 10. Count(Animal) = 25. Count(Cat,Animal) = 5.
        # Pair(Cat, Animal): B=Cat. gcd(5, 10) = 5. v_5(5) = 1.
        # Pair(Animal, Cat): B=Animal. gcd(5, 25) = 5. v_5(5) = 1.
        
        # If perfect subset: A subset B.
        # Count(A,B) = Count(A).
        # I_BA (B covers A) -> B is col. gcd(Count(A), Count(B)).
        # If Count(A)=5, Count(B)=25. gcd=5. v_5=1.
        
        # Let's adjust text to trigger p=2
        text2 = ("Cat is Animal. " * 4) + ("Dog is Animal. " * 4)
        feats2 = self.featurizer.extract_arithmetic_features(text2, entities, primes=[2])
        inc_matrix2 = feats2['primes'][2]['inclusion_matrix']
        
        # Count(Cat) = 4. Count(Animal) = 8. Count(Cat,Animal)=4.
        # Co-occur = 4.
        # Col Cat (A): B=Cat. gcd(4, 4) = 4. v_2(4) = 2.
        # Col Ani (B): B=Ani. gcd(4, 8) = 4. v_2(4) = 2.
        
        val_cat = inc_matrix2[ani_idx][cat_idx] # Col Cat
        val_ani = inc_matrix2[cat_idx][ani_idx] # Col Ani
        
        print(f"I(Animal|Cat) p=2: {val_cat}")
        print(f"I(Cat|Animal) p=2: {val_ani}")
        
        self.assertEqual(val_cat, 2.0)
        self.assertEqual(val_ani, 2.0)

    def test_ramification_commutator(self):
        # "Fire causes Smoke" repeated. Never "Smoke causes Fire".
        text = "Fire causes Smoke. " * 10
        text += "Water causes Steam. " * 5
        
        entities = ["Fire", "Smoke", "Water", "Steam"]
        feats = self.featurizer.extract_arithmetic_features(text, entities)
        comm_matrix = feats['commutator_matrix']
        ent_list = feats['entities']
        
        f_idx = ent_list.index("Fire")
        s_idx = ent_list.index("Smoke")
        
        # K_FS = N(Fire->Smoke) - N(Smoke->Fire)
        # N(Fire->Smoke) = 10
        # N(Smoke->Fire) = 0
        k_val = comm_matrix[f_idx][s_idx]
        
        print(f"Commutator(Fire, Smoke) = {k_val}")
        self.assertEqual(k_val, 10.0, "Ramification index should be 10")
        
    def test_valuation_shells(self):
        # Frequent word vs Rare word
        # "A" appears 128 times (2^7). "B" appears 4 times (2^2).
        # v_2(B) = floor(log_2(128/4)) = floor(log_2(32)) = 5.
        # v_2(A) = floor(log_2(128/128)) = 0.
        
        text = ("TokenA is TokenC. " * 128) + ("TokenB is TokenC. " * 4)
        entities = ["TokenA", "TokenB", "TokenC"]
        
        feats = self.featurizer.extract_arithmetic_features(text, entities, primes=[2])
        vals = feats['primes'][2]['valuations']
        
        v_a = vals["TokenA"]
        v_b = vals["TokenB"]
        
        print(f"Valuation(TokenA) p=2 = {v_a}")
        print(f"Valuation(TokenB) p=2 = {v_b}")
        
        self.assertEqual(v_a, 0.0)
        # Note: 128 occurrences of A. 4 occurrences of B.
        # Max count is maybe TokenC? 132.
        # log2(132/128) = log2(1.03) = 0.
        # log2(132/4) = log2(33) = 5.something -> floor 5.
        
        self.assertEqual(v_b, 5.0)

if __name__ == '__main__':
    unittest.main()
