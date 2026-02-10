
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from logic_miner.core.serial_synthesis import SerialManifoldSynthesizer

class MockPage:
    def __init__(self, text):
        self.text = text
    def extract_text(self):
        return self.text

class MockReader:
    def __init__(self, pages):
        self.pages = pages

def test_flow():
    print("--- Testing Sheaf Flow ---")
    synth = SerialManifoldSynthesizer(p=5, chunk_size=2)
    
    # Create text with heavy repetition to trigger 'frequencies'
    # Chunk 1 (Pages 0-2): 
    #   Concepts: A, B
    #   Logic: A co-occurs with B
    # Chunk 2 (Pages 1-3): (Overlap is Page 1)
    #   Concepts: B, C
    #   Logic: B co-occurs with C
    
    # We need simple text that featurizer picks up. 
    # Featurizer usually picks Capitalized words.
    
    text_a = "Alpha Beta " * 50
    text_b = "Beta Gamma " * 50
    text_c = "Gamma Delta " * 50
    
    # Page 0: A B
    # Page 1: B C (Overlap region effectively?)
    # Page 2: C D
    
    # With chunk_size=2, step=1.
    # Window 1: P0, P1 -> "Alpha Beta... Beta Gamma..."
    # Window 2: P1, P2 -> "Beta Gamma... Gamma Delta..."
    
    # Overlap terms: Beta, Gamma.
    # If logic is consistent (Beta same valuation), they should glue.
    
    p0 = MockPage(text_a)
    p1 = MockPage(text_b)
    p2 = MockPage(text_c)
    
    reader = MockReader([p0, p1, p2])
    
    result = synth.fit_stream(reader=reader)
    
    print("Result Keys:", result.keys())
    print("Sheaves Count:", result.get('sheaves_count'))
    print("Global Entities:", result.get('entities'))
    
    if result.get('sheaves_count') == 1:
        print("SUCCESS: Glued into single sheaf.")
    else:
        print(f"SPLIT: {result.get('sheaves_count')} sheaves.")

if __name__ == "__main__":
    test_flow()
