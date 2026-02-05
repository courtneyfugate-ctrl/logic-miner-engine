
import os
import sys
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner

def test_protocol_v9():
    print("--- [Protocol V.9] Audit Start ---")
    
    # Use the Musical Manifold text as the Benchmark
    text = """
    The Morphological Architecture of the Musical Manifold

    Abstract.
    The Symphonic Consensus relies on a shared Acoustic Logic.
    Phylum Acoustica ($p=5$) defines the Harmonic Core.
    Within this structure, Class Organon provides the Orchestral Skeleton.
    
    Subphylum Instrumentalis represents the Pure Instrumental lineage.
    Order Sonata and Order Symphony diverge at $p^2$.
    
    Anomalies:
    - The "Ninth Symphony" (Taxonomic Exception).
    - "Wagnerian Music Drama" (Dramatic Outlier).
    - "Chorus" (Vocal Residue).
    
    Logic Gates:
    - "Whether" a work is Sonata or Symphony depends on Form.
    - "Every" Consonant Interval maps to the Integer Lattice.
    """
    
    miner = LogicMiner()
    print("   > Initializing Logic Miner (Protocol V.9)...")
    
    # Fit Text
    result = miner.fit_text(text)
    
    print("\n--- [Audit Results V.9] ---")
    print(f"   > Logic Mode: {result.get('mode', 'Unknown')}")
    print(f"   > Dominant Prime: {result.get('dominant_prime', 'N/A')}")
    print(f"   > Global Score: {result['analytic_score']:.4f}")
    
    print("\n   > Discovered p-adic Coordinates:")
    coords = result['coordinates']
    targets = ["Phylum Acoustica", "Subphylum Instrumentalis", "Ninth Symphony", "Wagnerian", "Whether", "Every", "Chorus"]
    
    for t in targets:
        # Find closest match
        match = None
        for k in coords.keys():
            if t in k:
                match = k
                break
        if match:
             print(f"     {match}: {coords[match]}")
        else:
             print(f"     {t}: [Not Found/Filtered]")

    # Check for Ghost Terms (Degree Check)
    # Ghost Terms should be ejected or have High Valuation Divergence
    print("\n   > Ghost Term Analysis (Target: Ninth Divergence):")
    # Calculate Valuation v5 for Instrumentalis vs Ninth
    
    def get_v5(n):
        if n == 0: return "Inf"
        v = 0
        while n > 0 and n % 5 == 0:
            v += 1
            n //= 5
        return v
        
    instr = [c for k, c in coords.items() if "Instrumentalis" in k]
    ninth = [c for k, c in coords.items() if "Ninth" in k]
    
    if instr and ninth:
         v_instr = get_v5(instr[0])
         v_ninth = get_v5(ninth[0])
         print(f"     > Instrumentalis v5: {v_instr}")
         print(f"     > Ninth v5: {v_ninth}")
         if v_instr != v_ninth:
             print("     ! PROOF: Ninth Divergence Confirmed (Ghost Term).")
         else:
             print("     ? WARNING: Ninth shares valuation.")
             
    print("\n   > Verification Complete.")
    # Dump results
    with open("sandbox/protocol_v9_dump.txt", "w", encoding="utf-8") as f:
        f.write(str(result))

if __name__ == "__main__":
    test_protocol_v9()
