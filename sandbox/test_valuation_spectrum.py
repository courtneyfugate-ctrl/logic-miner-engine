
import os
import sys
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v50 import HilbertMapper
from collections import Counter
import math

def test_valuation_spectrum():
    print("--- [Test] Valuation Spectrum Audit (Phase 5.1) ---")
    
    # Simulate a semantic cluster: "Metals" and specific metals
    entities = ["Metal", "Iron", "Copper", "Aluminum", "Lead", "Car", "Apple", "Blue"]
    
    # Simple semantic matrix: Metals are related to 'Metal'
    n = len(entities)
    matrix = [[0.0] * n for _ in range(n)]
    
    # Metals (0..4) are strongly linked to each other
    for i in range(5):
        for j in range(5):
            if i != j:
                matrix[i][j] = 1.0
                
    # Randoms (5..7) have sparse links and internal noise
    matrix[5][6] = 0.1
    matrix[6][5] = 0.1
    matrix[7][7] = 0.5 # Some self-noise
    matrix[0][5] = 0.05 # Some faint noise
    
    # Initialize Hilbert Mapper with Primorial Base
    mapper = HilbertMapper(dimensions=6, base=2310)
    
    print(f" > Projecting {len(entities)} terms into Base-{mapper.base}...")
    mappings = mapper.compute_mappings(matrix, entities)
    
    primes = [2, 3, 5, 7, 11]
    
    def get_vp(n, p):
        if n == 0: return 10
        v = 0
        temp = abs(n)
        while temp > 0 and temp % p == 0:
            v += 1
            temp //= p
        return v

    print("\n > Pairwise Valuation Audit:")
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            e1, e2 = entities[i], entities[j]
            x1, x2 = mappings[e1], mappings[e2]
            diff = x1 - x2
            
            v_scores = [get_vp(diff, p) for p in primes]
            avg_v = sum(v_scores) / len(primes)
            
            relation = "RELATED" if i < 5 and j < 5 else "DISTANT"
            print(f"   [{relation}] {e1} vs {e2}: Diff={diff}, v_p={v_scores}, Avg_v={avg_v:.2f}")

    # Aggregated Stat
    related_v = []
    distant_v = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            e1, e2 = entities[i], entities[j]
            x1, x2 = mappings[e1], mappings[e2]
            diff = x1 - x2
            v_sum = sum(get_vp(diff, p) for p in primes)
            if i < 5 and j < 5:
                related_v.append(v_sum)
            else:
                distant_v.append(v_sum)
                
    print(f"\n > FINAL CONFORMANCE:")
    print(f"   Avg Related v_p Sum: {sum(related_v)/len(related_v):.2f}")
    print(f"   Avg Distant v_p Sum: {sum(distant_v)/len(distant_v):.2f}")
    
    if sum(related_v)/len(related_v) > sum(distant_v)/len(distant_v):
        print("\n [SUCCESS] Arithmetic Bridge Restored: Related terms share residue classes.")
    else:
        print("\n [FAILURE] Arithmetic Bridge Flattened: No residue significance detected.")

if __name__ == "__main__":
    test_valuation_spectrum()
