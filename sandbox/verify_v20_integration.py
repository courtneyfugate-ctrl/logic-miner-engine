
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner

def main():
    print("--- [Verification: Integrated Protocol V20] ---")
    miner = LogicMiner()
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    text = ""
    # Test on 100 pages for speed
    for i in range(100):
        text += reader.pages[i].extract_text() + "\n"
        
    print(f"   > Processing {pdf_path} (100 Pages)...")
    
    # Run V20 fit_text (Uses Spectral Filter + Shake + Reactions)
    result = miner.fit_text(text, use_adelic_shake=True)
    
    print("\n   > [Final V20 Result Summary]")
    print(f"     - Mode: {result['mode']}")
    print(f"     - Entities identified: {len(result['entities'])}")
    print(f"     - Reactions identified: {len(result.get('reactions', []))}")
    print(f"     - Classification stats: {Counter(result['classification'].values()) if 'classification' in result else 'N/A'}")
    
    # Audit for key chemistry concepts and ghosts
    targets = ["Matter", "Energy", "Reaction", "Atom", "Grand Prix"]
    print("\n   > [Target Identity Verification]")
    for t in targets:
        found = False
        for ent in result['entities']:
            if t.lower() in ent.lower():
                found = True
                spectral = result['classification'].get(ent, "UNKNOWN")
                print(f"     - '{ent}': FOUND ({spectral})")
                break
        if not found:
             print(f"     - '{t}': NOT FOUND (Correctly Pruned if Ghost)")

    # Save a small JSON for inspection
    with open("sandbox/v20_verification_result.json", "w") as f:
        # Convert non-serializable to strings
        serializable = {k: str(v) for k, v in result.items() if k != 'matrix'}
        json.dump(serializable, f, indent=2)
        
    print("\n   > Verification Complete. Results cached in sandbox/v20_verification_result.json.")

from collections import Counter
if __name__ == "__main__":
    main()
