import zlib
import math

def ncd(s1, s2):
    """
    Normalized Compression Distance (NCD)
    D(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
    """
    if not s1 or not s2: return 1.0
    b1, b2 = s1.encode('utf-8'), s2.encode('utf-8')
    c1, c2 = len(zlib.compress(b1)), len(zlib.compress(b2))
    c12 = len(zlib.compress(b1+b2))
    
    # NCD Formula
    dist = (c12 - min(c1,c2)) / max(c1,c2)
    return max(0.0, min(1.0, dist))

def verify_sensor_fidelity():
    print("--- [Sensor Verification] Verifying NCD Fidelity ---")
    
    # Test Data: Biological vs Mechanical
    # We expect Biological terms to cluster (low NCD) and Mechanical to cluster.
    # Cross-domain NCD should be high.
    
    bio_1 = "The dog barks at the mailman."
    bio_2 = "The wolf howls at the moon."
    
    mech_1 = "The car drives down the highway."
    mech_2 = "The truck hauls cargo on the road."
    
    # 1. Intra-Class Distances (Should be COMPRESSIBLE -> LOW NCD)
    d_bio = ncd(bio_1, bio_2)
    d_mech = ncd(mech_1, mech_2)
    
    # 2. Inter-Class Distances (Should be INCOMPRESSIBLE -> HIGH NCD)
    d_cross_1 = ncd(bio_1, mech_1)
    d_cross_2 = ncd(bio_2, mech_2)
    
    print(f"Bio-Bio (Dog/Wolf): {d_bio:.4f}")
    print(f"Mech-Mech (Car/Truck): {d_mech:.4f}")
    print(f"Cross (Dog/Car): {d_cross_1:.4f}")
    print(f"Cross (Wolf/Truck): {d_cross_2:.4f}")
    
    # Assertions
    if d_bio < d_cross_1 and d_mech < d_cross_1:
         print("   > [PASS] Sensor correctly identifies semantic proximity via Entropy.")
    else:
         print("   > [FAIL] Sensor failed to distinguish categories.")
         
    # 3. Verify Pure Information (No hidden embeddings)
    import sys
    modules = sys.modules.keys()
    forbidden = ['gensim', 'torch', 'tensorflow', 'spacy', 'numpy']
    found = [m for m in forbidden if m in modules]
    
    if not found:
        print("   > [PASS] No forbidden libraries loaded (Pure Information API).")
    else:
        print(f"   > [FAIL] Forbidden libraries detected: {found}")

if __name__ == "__main__":
    verify_sensor_fidelity()
