
import sys
import os
import time
from collections import defaultdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.serial_synthesis_v42 import SerialSynthesizerV42
from logic_miner.core.algebraic_text import AlgebraicTextSolver
from logic_miner.core.adelic import AdelicIntegrator
from pypdf import PdfReader

def check_term_complexity(term, vectors, integrator):
    """
    Computes K(x) for a term given its p-adic vectors.
    """
    primes = [5, 7, 11]
    if len(vectors) < 3:
        return None, "Missing Primes"
        
    vec = [vectors[p] for p in primes]
    models = [{'p': p, 'params': (vec[i],), 'degree': 0} for i, p in enumerate(primes)]
    
    res = integrator.solve_crt(models)
    if not res:
        return None, "CRT Failed"
        
    modulus = res['modulus']
    global_val = res['params'][0]
    k = global_val / float(modulus)
    
    return k, f"Val={global_val}/Mod={modulus}"

def main():
    print("--- [V.42 Filter Debugger] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    # Extract raw text from first 50 pages
    text = ""
    for i in range(50):
        text += reader.pages[i].extract_text() + "\n"
        
    print(f"   > Extracted {len(text)} chars.")
    
    # 1. Get Candidates
    from logic_miner.core.text_featurizer import TextFeaturizer
    featurizer = TextFeaturizer()
    candidates = featurizer.extract_entities(text, limit=100)
    print(f"   > Candidates: {len(candidates)}")
    
    # 2. Get Vectors
    term_vectors = defaultdict(dict)
    primes = [5, 7, 11]
    
    for p in primes:
        print(f"   > Solving Mod {p}...")
        solver = AlgebraicTextSolver(p=p)
        try:
            # Quick matrix build
            mat, counts, _ = featurizer.build_association_matrix(text, candidates)
            res = solver.solve(mat, candidates, counts)
            coords = res['coordinates']
            for t, c in coords.items():
                term_vectors[t][p] = c
        except Exception as e:
            print(f"     ! Mod {p} failed: {e}")
            
    # 3. Analyze Complexity
    integrator = AdelicIntegrator()
    results = []
    
    for t in candidates:
        k, note = check_term_complexity(t, term_vectors[t], integrator)
        if k is not None:
            results.append((t, k, note))
            
    # Sort by Complexity
    results.sort(key=lambda x: x[1])
    
    print("\n   [Adelic Complexity Report]")
    print(f"   {'TERM'.ljust(30)} | {'K(x)'.ljust(10)} | {'DETAILS'}")
    print("-" * 70)
    
    for t, k, note in results:
        status = "KEEP" if k < 0.2 else "DROP"
        print(f"   {t.ljust(30)} | {f'{k:.4f}'.ljust(10)} | {note} [{status}]")

if __name__ == "__main__":
    main()
