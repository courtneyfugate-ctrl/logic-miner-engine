
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from logic_miner.core.algebraic_text import AlgebraicTextSolver

def check_degree():
    coords = []
    with open('sandbox/v28_rigorous_audit_dump.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line and 'ADDR' not in line and '---' not in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    try:
                        addr = int(parts[1].strip())
                        coords.append(addr)
                    except:
                        continue
    
    unique_coords = list(set(coords))
    if not unique_coords:
        print("No coordinates found.")
        return

    solver = AlgebraicTextSolver(p=5)
    poly = solver._compute_polynomial_from_coords(unique_coords)
    print(f"Number of unique coordinates: {len(unique_coords)}")
    print(f"Polynomial Degree: {len(poly) - 1}")
    print(f"Polynomial: {poly}")

if __name__ == "__main__":
    check_degree()
