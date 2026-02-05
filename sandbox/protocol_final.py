
import math
import sys
import os
import re
import random
import hashlib
import json
import time
from collections import defaultdict, Counter
from pypdf import PdfReader
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
try:
    from logic_miner.core.text_featurizer import TextFeaturizer
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
    from logic_miner.core.text_featurizer import TextFeaturizer

# --- 1. Spectral Gatekeeper (V.18) ---
class SpectralGatekeeper:
    def __init__(self, vocab_limit=1000):
        self.vocab_limit = vocab_limit
        
    def build_graph(self, text, entities):
        G = defaultdict(lambda: Counter())
        In_G = defaultdict(lambda: Counter())
        words = re.findall(r'\b\w+\b', text)
        vocab_set = set(entities)
        
        window = 5
        for i in range(len(words)):
            if words[i] in vocab_set:
                u = words[i]
                for j in range(1, window + 1):
                    if i + j < len(words):
                        v = words[i+j]
                        if v in vocab_set:
                            G[u][v] += 1
                            In_G[v][u] += 1
        return G, In_G

    def analyze(self, text, featurizer):
        print("   > [Spectral Gatekeeper] Building Topology...")
        ents = featurizer.extract_entities(text, limit=self.vocab_limit)
        G, In_G = self.build_graph(text, ents)
        
        roots = []
        scaffolding = []
        junk = []
        
        # Calculate Tri-Axial Metrics
        for term in ents:
            # 1. Entropy
            out_counts = G[term]
            total = sum(out_counts.values())
            h = 0.0
            if total > 0:
                for count in out_counts.values():
                    p = count / total
                    h -= p * math.log2(p)
            
            # 2. Clustering
            neighbors = set(G[term].keys()) | set(In_G[term].keys())
            k = len(neighbors)
            c = 0.0
            if k >= 2:
                edges = 0
                n_list = list(neighbors)
                for i in range(k):
                    u = n_list[i]
                    for j in range(i+1, k):
                        v = n_list[j]
                        if (u in G and v in G[u]) or (v in G and u in G[v]):
                            edges += 1
                c = edges / (k * (k-1) / 2)
                
            # 3. Asymmetry
            in_d = sum(In_G[term].values())
            out_d = sum(G[term].values())
            tot_d = in_d + out_d
            a = abs(in_d - out_d)/tot_d if tot_d > 0 else 0.0
            
            # Classification Logic (V.18)
            if h < 1.5:
                junk.append(term)
            elif c < 0.15 and a > 0.4:
                scaffolding.append(term)
            elif h > 2.0 and c > 0.2:
                roots.append(term)
            else:
                # Ambiguous - Default to Scaffolding if highly frequent, else Junk
                if tot_d > 50: scaffolding.append(term)
                else: junk.append(term)
                
        print(f"     - Classified: {len(roots)} Roots, {len(scaffolding)} Scaffolding, {len(junk)} Junk.")
        return roots, scaffolding

# --- 2. Adelic Manifold Solver (V.14/15/16) ---
class AdelicMapper:
    def __init__(self, primes, seed_prefix="FINAL"):
        self.primes = primes
        self.seed_prefix = seed_prefix
        
    def _get_projection_sign(self, term, dim, prime):
        key = f"{self.seed_prefix}_{prime}_{term}_{dim}"
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return 1 if h % 2 == 0 else -1
        
    def compute_mappings(self, matrix, entities):
        mappings = defaultdict(dict)
        dims = 12
        for p in self.primes:
            for i, term in enumerate(entities):
                bits = 0
                row = matrix[i]
                for d in range(dims):
                    dot = 0.0
                    for j, w in enumerate(row):
                        if w > 0:
                            neigh = entities[j]
                            sign = self._get_projection_sign(neigh, d, p)
                            dot += w * sign
                    if dot >= 0: bits |= (1 << d)
                mappings[term][p] = bits
        return mappings

class Solver:
    def solve(self, matrix, entities, hints, primes):
        # Multi-Prime Relaxation
        current = defaultdict(dict)
        
        # Init
        for e in entities:
            for p in primes:
                if e in hints and p in hints[e]:
                    current[e][p] = hints[e][p] * p # Boost anchors
                else:
                    current[e][p] = 0
                    
        ent_idxs = {e: i for i,e in enumerate(entities)}
        
        # Iteration
        for _ in range(5):
            for e in entities:
                idx = ent_idxs[e]
                row = matrix[idx]
                
                for p in primes:
                    # Skip if anchored? No, soft constraints.
                    
                    sum_val = 0
                    sum_w = 0
                    for j, w in enumerate(row):
                        if w > 0:
                            neigh = entities[j]
                            sum_val += current[neigh][p] * w
                            sum_w += w
                    
                    if sum_w > 0:
                        current[e][p] = int(sum_val / sum_w)
                        
        return current

# --- 3. Polynomial Fitter ---
def fit_polynomial(primes, coords):
    """
    Fits a Lagrange polynomial f(x) such that f(p) = coord for each p.
    Returns string representation.
    """
    # Simple Lagrange implementation or numpy polyfit
    # Coordinates are (p, c)
    x = np.array(primes)
    y = np.array(coords)
    
    # Deg = len(primes) - 1
    deg = len(primes) - 1
    coeffs = np.polyfit(x, y, deg)
    
    # Convert to readable string f(x) = ax^n + ...
    terms = []
    for i, c in enumerate(coeffs):
        power = deg - i
        if abs(c) > 0.001:
            terms.append(f"{c:.2f}x^{power}")
            
    return " + ".join(terms) if terms else "0"

# --- Main Pipeline ---
class FinalAuditor:
    def run(self, pdf_path, output_file):
        out_f = open(output_file, "w", encoding="utf-8")
        out_f.write("=== FINAL AUDIT DUMP: CHEMISTRY ENGINE ===\n")
        out_f.write(f"Timestamp: {time.ctime()}\n")
        out_f.write(f"Source: {pdf_path}\n\n")
        
        print("--- [Final Production Run] ---")
        
        # 1. Ingestion (Full)
        print("   > Ingesting PDF (Full Text)...")
        reader = PdfReader(pdf_path)
        text = ""
        # FULL BOOK RUN
        limit_pages = len(reader.pages)
        out_f.write(f"Scope: Complete Textbook ({limit_pages} Pages)\n\n")
        
        for i in range(limit_pages):
            text += reader.pages[i].extract_text() + "\n"
            
        featurizer = TextFeaturizer()
        
        # 2. Spectral Filter
        gatekeeper = SpectralGatekeeper(vocab_limit=800)
        roots, scaffolding = gatekeeper.analyze(text, featurizer)
        
        out_f.write(f"--- SPECTRAL CLASSIFICATION ---\n")
        out_f.write(f"Roots (Concepts): {len(roots)} identified.\n")
        out_f.write(f"Scaffolding (Structure): {len(scaffolding)} identified.\n")
        out_f.write(f"Examples of Roots: {roots[:10]}\n")
        out_f.write(f"Examples of Scaffolding: {scaffolding[:10]}\n\n")
        
        # Combined Active Set for Solver
        active_entities = roots + scaffolding
        active_entities = list(set(active_entities)) # Dedup
        
        # Build Matrix
        matrix, _ = featurizer.build_association_matrix(text, active_entities)
        
        # 3. Multi-Prime Experiments
        prime_sets = [
            [3, 5, 7],
            [3, 5, 7, 11],
            [3, 5, 7, 11, 13]
        ]
        
        solver = Solver()
        
        for primes in prime_sets:
            label = f"{len(primes)}-PRIME MANIFOLD"
            print(f"   > Running {label}: {primes}...")
            out_f.write(f"=== {label} ===\n")
            out_f.write(f"Primes: {primes}\n")
            
            # Map
            mapper = AdelicMapper(primes)
            adelic_map = mapper.compute_mappings(matrix, active_entities)
            
            # Solve
            # Use adelic map as hints for Roots only? Or all?
            # Let's use mapped values as hints.
            hints = adelic_map # defaultdict(dict)
            
            start_t = time.time()
            solution = solver.solve(matrix, active_entities, hints, primes)
            end_t = time.time()
            
            out_f.write(f"Solve Time: {end_t - start_t:.2f}s\n")
            out_f.write("Term | Coordinates | Polynomial Trace\n")
            out_f.write("-" * 60 + "\n")
            
            # Dump Top Concepts (Roots)
            # Sort by frequency (proxy via matrix row sum) or just list
            for term in roots[:50]: # Dump top 50 roots
                coords = [solution[term][p] for p in primes]
                poly = fit_polynomial(primes, coords)
                coord_str = str(coords)
                out_f.write(f"{term:<20} | {coord_str:<20} | {poly}\n")
                
            out_f.write("\n")
            
        out_f.close()
        print(f"   > Dump written to {output_file}")

if __name__ == "__main__":
    base_path = "d:/Dropbox/logic-miner-engine/"
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    output_path = "d:/Dropbox/logic-miner-engine/sandbox/final_audit_dump.txt"
    
    if not os.path.exists(pdf_path):
        # Fallback
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    auditor = FinalAuditor()
    auditor.run(pdf_path, output_path)
