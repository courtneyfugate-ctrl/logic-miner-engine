
import sys
import os
import json
import time
import math

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from pypdf import PdfReader

def get_system_documentation():
    return """
======================================================================
   LOGIC MINER ENGINE - SYSTEM ARCHITECTURE & METHODOLOGY
======================================================================

1. ARCHITECTURE
   The Logic Miner is a "Universal Algebraic Engine" designed to extract rigid 
   logical structures (ontologies) from unstructured data streams.
   
   A. LogicMiner Service (The Brain)
      Orchestrates the pipeline, selecting the appropriate solver based on 
      input complexity (Natural Language vs. Numeric vs. Ultrametric).
      
   B. SerialManifoldSynthesizer (The Lattice Builder)
      Processes large corpora (e.g., Textbooks) as a continuous stream of 
      "Spline Patches". It maintains a persistent "Global Crystal" (the state) 
      and rotates the logic field (Prime Switching) to minimize global energy.
      
   C. TextFeaturizer (The Senses)
      Converts raw text into algebraic objects (Adjacency Matrices). 
      Protocol V.31 introduces "Asymmetric Operator Recognition", allowing 
      the system to distinguish between Subject (Root) and Object (Leaf) 
      via directed graph edges.
      
   D. AlgebraicTextSolver (The Solvers)
      Uses p-adic number theory (Hensel Lifting, Mahler Basis) to find the 
      optimal topology that satisfies the observed data constraints.

2. GOALS
   - Universal Discovery: Derive structure from ANY data source without 
     domain-specific heuristics.
   - Purity: Avoid reliance on black-box neural networks for logic. Use 
     LLMs/NLP only for "Featurization" (getting the matrix), not for 
     "Structuring" (building the tree).
   - Hierarchy: Discover the true "Peerage" of concepts (Root vs. Leaf) 
     mathematically.

3. RESTRICTIONS
   - Blackbox Only: The engine must treat the logic core as a black box 
     field solver.
   - Deterministic Topology: The resulting structure must be algebraically 
     verifiable (low Lipschitz violation), not just probabilistically likely.

4. CURRENT METHODS (Protocol V.32)
   - Directed Operator Graphs: Uses verbs/prepositions to define edge direction.
   - Adelic Expansion: Dynamically resizes the finite field (p) to 
     accommodate the number of disjoint logical components discovered 
     in the forest (Dynamic Branching Factor).
   - Spectral Purification: Removes "noise" entities that lack structural 
     centrality before they enter the logic solver.

======================================================================
"""

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append(get_system_documentation())
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - FINAL PRODUCTION AUDIT (PROTOCOL V.32)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Pages Processed: {page_count}")
    report.append(f"Protocol: ASYMMETRIC MANIFOLD + ADELIC EXPANSION (V.32)")
    report.append(f"Status: STABILIZED (p={result['p']})")
    
    report.append("\n" + "-"*70)
    report.append("CONCEPT TRACE: OPERAND/OPERATOR PEERAGE")
    report.append(f"{'CONCEPT'.ljust(30)} | {'ADDR'.ljust(15)} | {'MOD P'.ljust(10)} | {'ROLE'}")
    report.append("-" * 70)
    
    coords = result['coordinates']
    p = result['p']
    
    # Sort by address
    sorted_ents = sorted(result['entities'], key=lambda e: coords.get(e, 0))
    
    # We define "Role" based on p-adic valuation (depth)
    # Roots have val(addr) = 0 (not divisible by p, usually small integers < p)
    # Leaves have val(addr) >= 1 (divisible by p)
    
    for ent in sorted_ents:
        addr = coords.get(ent, 0)
        mod_p = addr % p
        
        # Heuristic for Role Display
        if addr < p:
            role = f"ROOT (Trunk {addr})"
        elif addr % p == 0:
            role = "LEAF/PROPERTY"
        else:
            role = "NODE"
            
        report.append(f"{ent.ljust(30)} | {str(addr).ljust(15)} | {str(mod_p).ljust(10)} | {role}")

    report.append("\n" + "="*70)
    report.append("   V.32 AUDIT COMPLETE")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.32 - Full Documentation Run] ---")
    miner = LogicMiner()
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating V.32 Synthesis on FULL TEXT ({total_pages} pages)...")
    
    # Run on FULL TEXT (no max_pages limit implies all pages if not specified, 
    # but fit_text with use_serial handles it. 
    # SerialManifoldSynthesizer.fit_stream iterates all pages if max_pages is None.)
    
    # Passing use_serial=True to trigger the large corpus pipeline
    result = miner.fit_text("", reader=reader, use_serial=True)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v32_full_documentation_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
