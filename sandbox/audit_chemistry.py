
import os
import sys
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from pypdf import PdfReader

def audit_chemistry():
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    print(f"--- [Audit] Chemistry Textbook Protocol V.9 (Infinite Lift) ---")
    print(f"   > Reading PDF: {pdf_path}")
    
    try:
        reader = PdfReader(pdf_path)
        print(f"   > Pages: {len(reader.pages)}")
        
        # Extract Text from a dense section (Pages 100-200)
        # Assuming Chapter 1-3 range.
        text = ""
        # Let's grab 50 pages from index 100.
        print("   > Extracting text (Pages 100-150)...")
        for i in range(100, 150):
            page = reader.pages[i]
            text += page.extract_text() + "\n"
            
        print(f"   > Extracted {len(text)} characters.")
        
        miner = LogicMiner()
        print("   > Initializing Logic Miner (Protocol V.8)...")
        
        result = miner.fit_text(text)
        
        print("\n--- [Chemistry Audit Results] ---")
        print(f"   > Logic Mode: {result.get('mode', 'Unknown')}")
        print(f"   > Dominant Prime: {result.get('dominant_prime', 'N/A')}")
        print(f"   > Global Score: {result['analytic_score']:.4f}")
        print(f"   > Collapsed Degree: {result.get('collapsed_degree', 'N/A')}")
        
        print("\n   > Discovered Chemical Topology:")
        coords = result['coordinates']
        # Sort by coordinate
        sorted_c = sorted(coords.items(), key=lambda x: x[1])
        for k, v in sorted_c:
            print(f"     {k}: {v}")
            
        # Hasse Divergence Check
        print("\n   > Hasse Product Audit (Select):")
        # Check standard chemical terms if present
        targets = ["Atom", "Molecule", "Electron", "Bond", "Reaction", "Energy", "Acid", "Base"]
        
        def get_hasse_prod(n, primes=[2,3,5,7]):
            if n==0: return 0.0
            prod = 1.0
            for p in primes:
                v = 0
                temp = abs(n)
                while temp > 0 and temp % p == 0:
                    v += 1
                    temp //= p
                prod *= (p ** -v)
            return prod

        for t in targets:
            # Find closest match in keys
            match = None
            for k in coords.keys():
                if t in k: # Substring match
                    match = k
                    break
            
            if match:
                c = coords[match]
                hp = get_hasse_prod(c)
                print(f"     > {match} ({c}): Hasse Product {hp:.5f}")
        
        # Dump
        with open("sandbox/chemistry_dump.txt", "w", encoding="utf-8") as f:
            f.write(str(result))
            
    except Exception as e:
        print(f"!!! Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    audit_chemistry()
