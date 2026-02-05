
import os
import sys

# Add sandbox to path to find protocol_v11
sys.path.append(os.path.dirname(__file__))

from protocol_v11 import SplineManifold

def test_v11_chemistry():
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    print(f"--- [Test] Protocol V.11 Chemistry Audit ---")
    
    # Run on first 150 pages to cover ~3 patches (Chunk 50, Overlap 0.5 -> Stride 25)
    # Patches: 0-50, 25-75, 50-100, 75-125, 100-150...
    
    manifold = SplineManifold(p=5, chunk_size=50, overlap=0.5)
    
    try:
        manifold.run_pipeline(pdf_path, max_pages=150)
        
    except Exception as e:
        print(f"!!! Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_v11_chemistry()
