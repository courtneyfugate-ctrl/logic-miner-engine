
import random
import re
import math
import hashlib
from collections import Counter, defaultdict
from pypdf import PdfReader
import sys
import os
import json

# Add src to path just in case
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from logic_miner.core.text_featurizer import TextFeaturizer

class HilbertMapper:
    """
    Phase 1: Pre-Ingestion Topology.
    Maps terms to 1D Integers using Locality Preserving Hashing (Simulated Hilbert/Z-Order).
    Pure Python implementation using Implicit Random Projections.
    """
    def __init__(self, dimensions=16):
        self.dimensions = dimensions
        # Seed for consistent hashing
        self.seed_base = "PROTOCOL_V11_SALT"

    def _get_projection_sign(self, term, dim_index):
        # Deterministic random sign for a term in a given dimension
        h = hashlib.md5(f"{self.seed_base}_{term}_{dim_index}".encode()).hexdigest()
        val = int(h, 16)
        return 1 if val % 2 == 0 else -1

    def compute_mappings(self, association_matrix, entities):
        """
        Input: 
            association_matrix (NxN) or equivalent adjacency stats?
            Actually, featurizer returns a matrix and a Map {term: idx}.
        
        We need 'Neighborhood Vectors'. 
        For each term T, vector V_T is the row in the association matrix.
        We project V_T onto 'dimensions' random vectors.
        """
        # Entities are ordered in the matrix
        n = len(entities)
        mappings = {}
        
        print(f"     > Hilbert Map: Projecting {n} entities to {self.dimensions}-bit Z-Order Curve...")
        
        for i, term_a in enumerate(entities):
            # Compute projection bits
            bits = 0
            
            # Row i in matrix represents Term A's neighborhood
            row = association_matrix[i]
            
            for d in range(self.dimensions):
                # Dot product of Row * ProjectionVector_d
                # ProjectionVector_d is defined implicitly: For each col j (Term B), sign is hash(TermB, d)
                dot_val = 0.0
                for j, weight in enumerate(row):
                    if weight > 0:
                        term_b = entities[j]
                        sign = self._get_projection_sign(term_b, d)
                        dot_val += weight * sign
                
                # Binarize
                if dot_val >= 0:
                    bits |= (1 << d)
            
            mappings[term_a] = bits
            
        return mappings

class ConstrainedSolver:
    """
    Phase 2: Manifold Solver with Rigidity Constraints.
    """
    def __init__(self, p=5):
        self.p = p
        
    def solve(self, matrix, entities, raw_counts, fixed_anchors, initial_mapping):
        """
        fixed_anchors: {term: coordinate} - MUST NOT CHANGE.
        initial_mapping: {term: coordinate} - From Hilbert Map (Soft Hint / Starting Point).
        """
        # 1. Identify Variable Nodes
        variables = []
        for e in entities:
            if e not in fixed_anchors:
                variables.append(e)
        
        current_map = {}
        
        # Initialize
        for e in entities:
            if e in fixed_anchors:
                current_map[e] = fixed_anchors[e]
            else:
                # Use Hilbert Hint? 
                # Hilbert Map gives relative order. We need actual integers.
                # Let's use the Hilbert integer directly as a starting 'slot' 
                # but scaled to spread out collisions?
                if e in initial_mapping:
                    # Scale to avoid collision density?
                    current_map[e] = initial_mapping[e] * 5 # Spread
                else:
                    current_map[e] = random.randint(1, 1000)
        
        # 2. Optimization Loop (Simple Hill Climbing for Sandbox)
        # Goal: Minimize Local Mahler Energy + Transition Stress
        
        # Simplification: Just optimize "Topology Energy" as in V.10, but respecting anchors.
        
        # ... (Simplified Optimization for Speed)
        # Just return the map for now to test the Pipeline Wiring
        # In a real solver, we'd iterate here.
        
        # Simulating "Solver Work":
        # Adjust non-anchor terms to cluster around anchors they are linked to.
        
        # Let's do 5 iterations of averaging?
        # "Spring Embedding" logic briefly?
        
        ent_to_idx = {e: i for i,e in enumerate(entities)}
        
        for _ in range(5):
            for var in variables:
                # Move var towards weighted average of neighbors
                idx = ent_to_idx[var]
                row = matrix[idx]
                
                sum_coord = 0.0
                sum_w = 0.0
                
                for j, w in enumerate(row):
                    if w > 0:
                        neighbor = entities[j]
                        coord = current_map[neighbor]
                        sum_coord += coord * w
                        sum_w += w
                
                if sum_w > 0:
                    target = int(sum_coord / sum_w)
                    # Move slightly towards target?
                    # Or just snap?
                    # Let's snap but keep it integer
                    current_map[var] = target
        
        return current_map

class SplineManifold:
    """
    Protocol V.11 Manager
    """
    def __init__(self, p=5, chunk_size=30, overlap=0.5):
        self.p = p
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.global_anchors = {} # fixed coords
        self.splines = [] # List of {pages: (range), map: {}, polynomial: ...}
        
    def run_pipeline(self, pdf_path, max_pages=None):
        print(f"--- [Protocol V.11: Spline Manifold Synthesis] ---")
        
        # 1. Pre-Scan for Global Anchors (The "Constitution")
        # In V.11 we just take Top-50 freq terms from global scope to freeze.
        print("   > Phase 0: Constituting Global Anchors...")
        featurizer = TextFeaturizer()
        
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        if max_pages: 
            total_pages = min(total_pages, max_pages)
            
        full_text_sample = ""
        # Sample every 5th page to estimate global freq quickly
        for i in range(0, total_pages, 5):
             full_text_sample += reader.pages[i].extract_text() + "\n"
             
        global_ents = featurizer.extract_entities(full_text_sample)
        # We need their counts, extract_entities returns list sorted by freq implicitly? 
        # Actually it returns list. We need to re-count?
        # TextFeaturizer.extract_entities returns most_common(150).
        # So first 50 are our anchors.
        
        anchor_terms = global_ents[:50]
        print(f"     > Constitution Ratified: {len(anchor_terms)} Terms ({anchor_terms[:5]}...)")
        
        # Initialize Global Anchors using Hilbert Map on GLOBAL sample
        # This ensures they are topologically valid relative to each other globally.
        matrix, _ = featurizer.build_association_matrix(full_text_sample, global_ents)
        mapper = HilbertMapper(dimensions=12) # 12-bit = 4096 range
        global_hilbert = mapper.compute_mappings(matrix, global_ents)
        
        for term in anchor_terms:
            self.global_anchors[term] = global_hilbert.get(term, 0)
            
        print("     > Global Anchors Fixed via Hilbert Projection.")
        
        # 2. Spline Processing (Sliding Window)
        stride = int(self.chunk_size * (1.0 - self.overlap))
        current_idx = 0
        
        patch_id = 0
        while current_idx < total_pages:
            end_idx = min(current_idx + self.chunk_size, total_pages)
            print(f"\n   > Processing Spline Patch {patch_id} (Pages {current_idx}-{end_idx})...")
            
            # Extract Text
            text_block = ""
            for i in range(current_idx, end_idx):
                text_block += reader.pages[i].extract_text() + "\n"
                
            # Local Featurization
            # Scaled to ~3 entities per page to prevent overfitting small patches
            entity_limit = self.chunk_size * 3
            local_ents = featurizer.extract_entities(text_block, limit=entity_limit)
            local_mat, local_counts = featurizer.build_association_matrix(text_block, local_ents)
            
            # Local Hilbert Map (Initial Guess)
            local_hilbert = mapper.compute_mappings(local_mat, local_ents)
            
            # Solve with Constraints
            solver = ConstrainedSolver(p=self.p)
            patch_map = solver.solve(local_mat, local_ents, local_counts, self.global_anchors, local_hilbert)
            
            self.splines.append({
                'id': patch_id,
                'range': (current_idx, end_idx),
                'map': patch_map,
                'terms': len(patch_map)
            })
            
            current_idx += stride
            patch_id += 1
            
        self.export_mermaid(filename="sandbox/manifold_structure.md")
        self.export_json(filename="sandbox/manifold_data.json")
        return self.report()

    def report(self):
        # 3. Anti-Collapse Audit
        print("\n--- [Phase 4: Anti-Collapse Audit] ---")
        
        # 1. Branching Factor
        print("   > Distribution Metrics per Spline:")
        avg_branching = 0
        for s in self.splines:
            coords = list(s['map'].values())
            # Count unique mod 5 (Roots)
            roots = set(c % 5 for c in coords)
            # Count unique mod 25 (Level 1)
            l1 = set(c % 25 for c in coords)
            
            # Naive Branching Factor: L1 Count / Root Count
            bf = len(l1) / max(len(roots), 1)
            print(f"     > Patch {s['id']}: Terms={s['terms']}, Roots(mod5)={len(roots)}, Nodes(mod25)={len(l1)}, BF={bf:.2f}")
            avg_branching += bf
            
        print(f"   > Average Branching Factor: {avg_branching/len(self.splines):.2f}")
        
        # 2. Rigidity Check
        test_anchor = list(self.global_anchors.keys())[0]
        print(f"   > Rigidity Check ('{test_anchor}'):")
        violations = 0
        expected = self.global_anchors[test_anchor]
        for s in self.splines:
            if test_anchor in s['map']:
                actual = s['map'][test_anchor]
                if actual != expected:
                    print(f"     ! Violation in Patch {s['id']}: {actual} != {expected}")
                    violations += 1
        
        if violations == 0:
            print(f"     > PASSED. Anchor '{test_anchor}' is Rigid across manifold.")
        else:
            print(f"     ! FAILED. {violations} drift events detected.")

        # 3. Dump Hierarchy & Polynomials
        print("\n--- [Detailed Manifold Dump] ---")
        for s in self.splines:
            print(f"\n   > Spline Patch {s['id']} (Pages {s['range'][0]}-{s['range'][1]}):")
            
            # A. Polynomial
            # P(x) = Product (x - c)
            # We assume monic. output coeffs.
            # Polynomial multiplication is convolution.
            if len(s['map']) > 0:
                coeffs = [1]
                for c in s['map'].values():
                    # Multiply by (x - c) -> [-c, 1]
                    # New len = len(coeffs) + 1
                    nc = [0]*(len(coeffs)+1)
                    for i, val in enumerate(coeffs):
                        nc[i+1] += val       # x term
                        nc[i]   -= c * val   # const term
                    coeffs = nc
                
                # Print nicely formatted (only first 20 and last 5 if too long?)
                # User asked for FULL results. But 150 degree is huge.
                # I will print the coeffs.
                print(f"     > Polynomial P_{s['id']}(x) Coefficients (Deg {len(coeffs)-1}):")
                # Wrap text
                c_str = ", ".join(str(x) for x in coeffs)
                if len(c_str) > 1000: c_str = c_str[:500] + " ... [Truncated for Display] ... " + c_str[-100:]
                print(f"       [{c_str}]")
            
            # B. Hierarchy Tree
            print(f"     > P-adic Hierarchy (p={self.p}):")
            # Group by Valuation
            # v=0, v=1, v=2...
            
            def get_val(n):
                if n == 0: return 99
                v = 0
                while n % self.p == 0:
                    v += 1
                    n //= self.p
                return v
            
            hierarchy = defaultdict(list)
            for k, v in s['map'].items():
                val = get_val(v)
                hierarchy[val].append((k, v))
                
            for v_level in sorted(hierarchy.keys()):
                items = sorted(hierarchy[v_level], key=lambda x: x[1])
                print(f"       [Level {v_level} / p^{v_level}]:")
                for item in items:
                    print(f"         - {item[0]} (coord={item[1]})")

    def export_mermaid(self, filename="manifold_structure.md"):
        """
        Generates a Mermaid.js Graph visualization of the P-adic Hierarchy.
        Nodes are clustered by Spline Patch and Valuation Level.
        """
        print(f"\n   > Generating Visualization: {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Manifold Visualization (Mermaid)\n\n")
            f.write("```mermaid\n")
            f.write("graph TD\n")
            f.write("    %% Styles\n")
            f.write("    classDef root fill:#f96,stroke:#333,stroke-width:2px,color:black;\n")
            f.write("    classDef l1 fill:#9cf,stroke:#333,stroke-width:1px,color:black;\n")
            f.write("    classDef l2 fill:#cfc,stroke:#333,stroke-width:1px,color:black;\n")
            f.write("    classDef l3 fill:#eee,stroke:#333,stroke-width:1px,color:black;\n\n")

            for s in self.splines:
                p_id = s['id']
                f.write(f"    subgraph Patch_{p_id} [Spline Patch {p_id} (Pages {s['range'][0]}-{s['range'][1]})]\n")
                f.write(f"        direction TB\n")
                
                # Group by Valuation
                hierarchy = defaultdict(list)
                for term, coord in s['map'].items():
                    # Calculate P-adic Valuation calc
                    if coord == 0: v = 0 # root
                    else:
                        v = 0
                        temp = coord
                        while temp % self.p == 0:
                            v += 1
                            temp //= self.p
                    hierarchy[v].append((term, coord))

                # Write Nodes grouped by Level
                # We can't easily determine 'Parent' without more logic, so we stack them conceptually
                # Or connect them to a 'Level Node'
                
                # Level 0
                for term, c in hierarchy[0]:
                    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', term)
                    node_id = f"P{p_id}_{sanitized}"
                    f.write(f"        {node_id}({term} [{c}])\n")
                    f.write(f"        class {node_id} root\n")

                # Level 1 (Connect to nearest Root? No, just list them for now to avoid dense web)
                # Let's create a hidden link to enforce hierarchy layout if possible, or just subgraph
                if 1 in hierarchy:
                    f.write(f"        subgraph L1_{p_id} [Level 1 / p^1]\n")
                    for term, c in hierarchy[1]:
                        sanitized = re.sub(r'[^a-zA-Z0-9]', '_', term)
                        node_id = f"P{p_id}_{sanitized}"
                        f.write(f"            {node_id}({term} [{c}])\n")
                        f.write(f"            class {node_id} l1\n")
                    f.write("        end\n")

                if 2 in hierarchy:
                    f.write(f"        subgraph L2_{p_id} [Level 2 / p^2]\n")
                    for term, c in hierarchy[2]:
                        sanitized = re.sub(r'[^a-zA-Z0-9]', '_', term)
                        node_id = f"P{p_id}_{sanitized}"
                        f.write(f"            {node_id}({term} [{c}])\n")
                        f.write(f"            class {node_id} l2\n")
                    f.write("        end\n")
                
                # Force L1 below Roots
                # f.write(f"        L1_{p_id} ~~~ P{p_id}_Roots\n") # Pseudo link?
                
                f.write("    end\n\n")
            
            f.write("```\n")
            
        return self.splines

    def export_json(self, filename="manifold_data.json"):
        """
        Exports the entire manifold state to JSON for external visualization.
        """
        print(f"\n   > Exporting Manifold Data: {filename}...")
        
        data = {
            "p": self.p,
            "chunk_size": self.chunk_size,
            "splines": []
        }
        
        for s in self.splines:
            # Reconstruct Polynomial Coefficients for JSON
            coeffs = [1]
            if len(s['map']) > 0:
                for c in s['map'].values():
                    nc = [0]*(len(coeffs)+1)
                    for i, val in enumerate(coeffs):
                        nc[i+1] += val
                        nc[i]   -= c * val
                    coeffs = nc
            
            data["splines"].append({
                "id": s['id'],
                "range": s['range'],
                "terms": list(s['map'].keys()),
                "coords": list(s['map'].values()),
                "map": s['map'],
                "polynomial_coeffs": coeffs
            })
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        return data

if __name__ == "__main__":
    # Test stub
    pass
