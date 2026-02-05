
import sys
import os

def reconstruct_lineage(addr, p=5):
    """
    Given a p-adic address, yield the sequence of ancestor addresses.
    addr = sum(a_k * p^k)
    Ancestors are truncation points.
    """
    lineage = []
    temp = addr
    # Coefficients calculation
    coeffs = []
    # Find max k such that p^k <= addr
    # But BFE is 1 + ...
    # Simple way: subtract 1, then base p conversion
    val = addr - 1
    k = 0
    while val > 0 or k == 0:
        digit = val % p
        coeffs.append(digit)
        val //= p
        k += 1
    
    # Reconstruct prefixes
    # Prefix_depth = 1 + sum_{i=1}^{depth} coeffs[i] * p^i
    current = 1
    lineage.append(current)
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
    
    # Audit Specific Path: Oxygen and Combustion
    target_concepts = ["Oxygen", "Combustion", "Matter", "Elements", "Reaction"]
    
    print("--- [Skeptical Audit: Lineage Reconstruction] ---")
    
    for concept, addr in concepts:
        if concept in target_concepts:
            lineage_addrs = reconstruct_lineage(addr)
            path = []
            for a in lineage_addrs:
                names = addr_to_concept.get(a, ["Unknown"])
                path.append(f"{names[0]} ({a})")
            print(f"Path for {concept}: {' -> '.join(path)}")

    # Search for logical failures (Collisions at depth)
    print("\n--- [Audit: Collision Analysis] ---")
    for addr, names in addr_to_concept.items():
        if len(names) > 1:
            print(f"Collision at Addr {addr}: {', '.join(names)}")

if __name__ == "__main__":
    audit_v28()
