
import sys
import os
from collections import defaultdict

def reconstruct_lineage(addr, p=48):
    lineage = []
    val = addr - 1
    # BFE: addr = 1 + c1*p^1 + c2*p^2 + ...
    # So (addr-1) in base p has digits [0, c1, c2, ...]
    
    coeffs = []
    temp = val
    if temp == 0:
        return [1]
        
    while temp > 0:
        coeffs.append(temp % p)
        temp //= p
    
    # Prefix Reconstruction
    current = 1
    lineage.append(current)
    # coeffs[0] corresponds to p^0, which should be 0 in BFE if root is at depth 0.
    # Actually, root is depth 0, children are depth 1.
    # Grandchild at depth 2 is 1 + c1*p^1 + c2*p^2
    for i, c in enumerate(coeffs):
        if i == 0: continue # Skip p^0 term
        current += c * (p**i)
        lineage.append(current)
    
    return lineage

def audit_v29():
    dump_path = 'sandbox/v29_rigorous_audit_dump.txt'
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
    
    print("--- [The Skeptical Audit V3: V.29 Lineage (Corrected p=48)] ---")
    
    targets = [
        "Oxygen", "Combustion", "Matter", "Elements", "Reaction", 
        "Enthalpy", "Energy", "Entropy", "Acid", "Bases", "Buffer",
        "Lewis", "Bonding", "Chemistry"
    ]
    
    for target in targets:
        addr = None
        for c, a in concepts:
            if c == target:
                addr = a
                break
        if addr is None: continue
        
        lineage = reconstruct_lineage(addr, p=48)
        path = []
        for a in lineage:
            names = addr_to_concept.get(a, ["Unknown"])
            path.append(f"{names[0]} ({a})")
        print(f"PATH: {' -> '.join(path)}")

if __name__ == "__main__":
    audit_v29()
