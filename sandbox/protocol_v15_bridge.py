
import random
import re
import math
import sys
import os
import json
from collections import defaultdict, Counter

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
try:
    from logic_miner.core.text_featurizer import TextFeaturizer
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
    from logic_miner.core.text_featurizer import TextFeaturizer

def calculate_local_clustering(term, adjacency_matrix, entities):
    """
    Calculates the Local Clustering Coefficient (C) for a node.
    C = (2 * Edges_Between_Neighbors) / (k * (k-1))
    Low C = Bridge (Neighbors don't know each other).
    High C = Clique member.
    """
    if term not in entities: return 0.0
    
    idx = entities.index(term)
    row = adjacency_matrix[idx]
    
    # 1. Identify Neighbors
    neighbors = []
    for j, weight in enumerate(row):
        if weight > 0 and j != idx:
            neighbors.append(j)
            
    k = len(neighbors)
    if k < 2: return 0.0
    
    # 2. Count Edges Between Neighbors
    edges_between = 0
    for i in range(len(neighbors)):
        n1 = neighbors[i]
        for j in range(i+1, len(neighbors)):
            n2 = neighbors[j]
            # Check if n1 and n2 are connected
            if adjacency_matrix[n1][n2] > 0:
                edges_between += 1
                
    max_edges = (k * (k-1)) / 2
    if max_edges == 0: return 0.0
    
    c = edges_between / max_edges
    return c, neighbors

def extract_reactions(text):
    """
    Scans for Process Patterns: Noun + Interaction + Noun -> Noun
    Simple heuristic parser.
    """
    reactions = []
    # Interaction Verbs
    verbs = ["yields", "forms", "produces", "reacts with"]
    
    # Split into sentences
    sentences = re.split(r'[.!?]', text)
    
    for sent in sentences:
        sent = sent.strip()
        if not sent: continue
        
        lower_sent = sent.lower()
        if any(v in lower_sent for v in verbs):
            # Found a candidate sentence
            # Naive Extraction: Look for "A and B form C" or "A reacts with B to yield C"
            
            # Pattern 1: "... produce [Result]"
            if "produce" in lower_sent:
                parts = sent.split("produce")
                reactants_raw = parts[0]
                products_raw = parts[1]
                
                # Cleanup
                if "react" in reactants_raw.lower():
                    # "Hydrogen and Oxygen react to produce..."
                    reactants_raw = reactants_raw.replace("react to", "")
                    
                reactions.append({
                    "raw": sent,
                    "type": "Production",
                    "input": reactants_raw.strip(),
                    "output": products_raw.strip()
                })

            # Pattern 2: "yields"
            if "yields" in lower_sent:
                 parts = sent.split("yields")
                 if len(parts) > 1:
                     reactions.append({
                        "raw": sent,
                        "type": "Yield",
                        "input": parts[0].strip(),
                        "output": parts[1].strip()
                    })
                
    return reactions

class SkepticalBridgeAuditor:
    def __init__(self):
        self.featurizer = TextFeaturizer()
        
    def run_audit(self, pdf_path, targets=["Energy"]):
        print(f"--- [Protocol V.15: Bridge & Process Audit] ---")
        
        # 1. Ingestion
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = ""
        # Read a good chunk (e.g. first 50 pages) to get density
        for i in range(min(50, len(reader.pages))):
            text += reader.pages[i].extract_text() + "\n"
            
        ents = self.featurizer.extract_entities(text, limit=500)
        # Normalize ents for check
        ents_lower = {e.lower(): e for e in ents}
        
        print(f"     > Debug: Top 20 Entities Found: {ents[:20]}")
        if "energy" in ents_lower:
            print(f"     > 'energy' detected as '{ents_lower['energy']}'")
        else:
            print(f"     > 'energy' NOT detected in Top 500. Force-adding for test.")
            ents.append("energy")
            ents_lower["energy"] = "energy"
        
        matrix, _ = self.featurizer.build_association_matrix(text, ents)
        
        # 2. Bridge Score (Sheaf Blow-Up Pre-requisite)
        print("\n   > Phase 1: Bridge Score Audit (Topological Singularity)")
        for target in targets:
            # Check mixed case
            target_key = target.lower()
            if target_key in ents_lower:
                actual_term = ents_lower[target_key]
                c, neighbors_idx = calculate_local_clustering(actual_term, matrix, ents)
                neighbor_terms = [ents[i] for i in neighbors_idx]
                
                print(f"     > Target '{actual_term}':")
                print(f"       - Degree (k): {len(neighbor_terms)}")
                print(f"       - Clustering Coeff (C): {c:.4f}")
                
                if c < 0.1:
                    print(f"       ! LOW CLUSTERING (Bridge Detected). Neighbors are disjoint.")
                    print(f"       ! Recommendation: BLOW UP NODE '{actual_term}' into {actual_term}_1, {actual_term}_2")
                    print(f"       - Neighbors: {neighbor_terms[:10]}...")
                elif c > 0.5:
                    print(f"       - High Clustering (Clique Member). Stable Concept.")
                else:
                    print(f"       - Moderate Clustering. Semantic Hub.")
            else:
                print(f"     > Target '{target}' not found (Top 500).")

        # 3. Process Graph
        print("\n   > Phase 2: Process Graph (Reaction Extraction)")
        reactions = extract_reactions(text)
        print(f"     > Extracted {len(reactions)} Candidate Reactions.")
        for r in reactions[:5]:
            print(f"       - [{r['type']}] {r['input']} -> {r['output']}")
            
if __name__ == "__main__":
    base_path = "d:/Dropbox/logic-miner-engine/"
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    
    if not os.path.exists(pdf_path):
        # Fallback
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    auditor = SkepticalBridgeAuditor()
    auditor.run_audit(pdf_path, targets=["Energy", "Atom", "Matter", "Mass"])
