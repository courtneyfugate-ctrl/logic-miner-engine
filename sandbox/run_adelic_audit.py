import os
import sys
import json
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

print(f"DEBUG: sys.version = {sys.version}")
print(f"DEBUG: sys.path = {sys.path}")

from logic_miner.core.serial_synthesis import SerialManifoldSynthesizer

def run_adelic_audit():
    # pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    # Verify path first
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../texts'))
    pdf_path = os.path.join(base_path, "Chemistry2e-WEB.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"!!! Error: PDF not found at {pdf_path}")
        return

    print(f"--- [Adelic Audit] Running Pipeline on {pdf_path} ---")
    print("    Protocol V.14: Arithmetic Features + regex Parser + Adelic Solver")
    
    # Initialize Serial Synthesizer (Protocol V.22)
    # V.31: Adelic Sweep restricted to p=2 (start small)
    synthesizer = SerialManifoldSynthesizer(p=2, chunk_size=25)
    
    try:
        # Load PDF Reader
        # SerialManifoldSynthesizer.fit_stream handles PDF reading if we pass an object, 
        # or we might need to use pypdf directly if fit_stream expects a reader.
        # Let's check fit_stream signature. It takes (text=None, reader=None, max_pages=None).
        # We need to open the PDF and pass the reader.
        
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        
        # Run Fit
        # Phase 9: Full Scale Synthesis (No Page Restriction)
        result = synthesizer.fit_stream(reader=reader, max_pages=None)
        
        # Serialize Result
        output_path = os.path.join(os.path.dirname(__file__), "chemistry_adelic_dump.json")
        
        # Convert sets to lists for JSON serialization
        if 'anchors' in result and isinstance(result['anchors'], set):
            result['anchors'] = list(result['anchors'])
            
        # Coordinates might be int keys? No, entities are strings.
        # Check for any non-serializable types in the result dict.
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, default=str)
            
        print("\n--- [Audit Complete] ---")
        print(f"   > Output saved to: {output_path}")
        print(f"   > Final Energy: {result.get('energy', 'N/A')}")
        print(f"   > Polynomial: {result.get('polynomial', 'N/A')}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"!!! Execution Error: {e}")

if __name__ == "__main__":
    run_adelic_audit()
