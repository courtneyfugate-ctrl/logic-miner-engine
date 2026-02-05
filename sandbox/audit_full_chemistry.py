
import os
import sys
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis import SerialManifoldSynthesizer

def audit_full_chemistry():
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    print(f"--- [Audit] Full Chemistry Textbook Protocol V.10 (Serial Synthesis) ---")
    
    # Initialize Crystal Grower
    # Chunk size 50 pages.
    synthesizer = SerialManifoldSynthesizer(p=5, chunk_size=50)
    
    try:
        result = synthesizer.fit_stream(pdf_path)
        
        print("\n--- [Serial Audit Results] ---")
        print(f"   > Final Logic Mode: p={result['p']}")
        print(f"   > Final Global Energy: {result['energy']:.4f}")
        print(f"   > Anchors Locked: {len(result['anchors'])}")
        print(f"   > Anchors: {result['anchors'][:20]}...")
        
        print("\n   > Global Manifold Topology (Top 20):")
        coords = result['coordinates']
        sorted_c = sorted(coords.items(), key=lambda x: x[1])
        count = 0
        for k, v in sorted_c:
             print(f"     {k}: {v}")
             count += 1
             if count > 30: break
             
        # Check Hasse for Atoms/Molecules in the GLOBAL crystal
        targets = ["Atom", "Molecule", "Electron", "Bond", "Proton", "Neutron", "Table"]
        print("\n   > Global Hasse Audit:")
        
        def get_hasse_prod(n, p_val):
            if n==0: return 0.0
            v = 0
            temp = abs(n)
            while temp > 0 and temp % p_val == 0:
                v += 1
                temp //= p_val
            return p_val ** (-v)
            
        for t in targets:
             for k in coords:
                 if t in k:
                     c = coords[k]
                     hp = get_hasse_prod(c, result['p'])
                     print(f"     > {k} ({c}): Hasse Product {hp:.5f}")
                     
    except Exception as e:
        print(f"!!! Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    audit_full_chemistry()
