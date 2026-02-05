
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis import SerialManifoldSynthesizer

def test_audit_partial():
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    print(f"--- [Test] Partial Audit Configuration ---")
    
    # Initialize Synthesizer with limits
    # Limit to 50 pages for quick test
    synthesizer = SerialManifoldSynthesizer(p=5, chunk_size=25)
    
    try:
        # Run with max_pages=50
        result = synthesizer.fit_stream(pdf_path, max_pages=50)
        
        print("\n--- [Test Results] ---")
        print(f"   > Success! Ran on subset of pages.")
        print(f"   > Anchors: {len(result['anchors'])}")
        print(f"   > Global Energy: {result['energy']:.4f}")
        
    except Exception as e:
        print(f"!!! Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audit_partial()
