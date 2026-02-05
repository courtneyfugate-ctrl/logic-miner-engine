
import sys
import os
from collections import defaultdict

def reconstruct_lineage(addr, p=5):
    lineage = []
    temp = addr
    val = addr - 1
    k = 0
    coeffs = []
    while val > 0 or k == 0:
        digit = val % p
        coeffs.append(digit)
        val //= p
        k += 1
    
    current = 1
    lineage.append(current)
    # The BFE prefix constructor in algebraic_text.py:
    # coords[child] = p_coord + c_val * (self.p ** (p_depth + 1))
    # where p_depth starts at 0 for root.
    # So child of root (depth 0+1=1) is 1 + c1 * 5^1
    # child of that (depth 1+1=2) is (1 + c1 * 5^1) + c2 * 5^2
    # So the coefficients in base p are [0, c1, c2, c3...]
    # Wait, 1 + c1*5 + c2*25...
    # c1 is coeff of 5^1.
    
    for i in range(1, len(coeffs)):
        current += coeffs[i] * (p**i)
        lineage.append(current)
    
    return lineage

def audit_v28():
    dump_path = 'sandbox/v28_rigorous_audit_dump.txt'
    addr_to_concept = {}
    concepts = []
    
    with open(dump_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line and 'ADDR' not in line and '---' not in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    try:
                        concept = parts[0].strip()
                        addr = int(parts[1].strip())
                        addr_to_concept.setdefault(addr, []).append(concept)
                        concepts.append((concept, addr))
                    except:
                        continue
    
    print("--- [The Skeptical Audit: Logical Traces] ---")
    
    targets = [
        "Oxygen", "Combustion", "Matter", "Elements", "Reaction", 
        "Enthalpy", "Energy", "Entropy", "Acid", "Bases", "Buffer",
        "Zinc", "Lewis", "Bonding"
    ]
    
    for target in targets:
        # Find addr for target
        addr = None
        for c, a in concepts:
            if c == target:
                addr = a
                break
        if addr is None: continue
        
        lineage = reconstruct_lineage(addr, p=5)
        path = []
        for a in lineage:
            names = addr_to_concept.get(a, ["Unknown"])
            path.append(f"{names[0]} ({a})")
        print(f"PATH: {' -> '.join(path)}")

if __name__ == "__main__":
    audit_v28()
