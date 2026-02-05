
import os
import sys

# Add sandbox to path
sys.path.append(os.path.dirname(__file__))

from protocol_v11 import SplineManifold

def test_v12_experiments():
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    print(f"--- [Protocol V.12 Optimization Experiments] ---")
    
    # Experiment A: POS Filter Only (Chunk 50)
    print("\n>>> Experiment A: Chunk Size 50 (Baseline + POS Filter) <<<")
    manifold_a = SplineManifold(p=5, chunk_size=50, overlap=0.5)
    # Run shorter scan (100 pages is enough to test coefficients)
    manifold_a.run_pipeline(pdf_path, max_pages=100)
    
    # Experiment B: Coastline Fit (Chunk 10) - Smaller patches
    print("\n>>> Experiment B: Coastline Fit (Chunk Size 10) <<<")
    # Reduced overlap to 0.5 of 10 = 5 pages stride
    manifold_b = SplineManifold(p=5, chunk_size=10, overlap=0.5) 
    manifold_b.run_pipeline(pdf_path, max_pages=50) # 50 pages = 5 patches

if __name__ == "__main__":
    test_v12_experiments()
