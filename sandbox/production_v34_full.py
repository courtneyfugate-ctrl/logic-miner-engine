
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v34 import SerialSynthesizerV34
from pypdf import PdfReader

def get_system_documentation():
    return """
======================================================================
   LOGIC MINER ENGINE - PROTOCOL V.34 REFINED
   "The Semantic Purifier"
======================================================================

1. REFINED ARCHITECTURE
   This Protocol builds on V.33 Experimental by adding:

   A. Matrix Momentum (Spline Continuity)
      To prevent "Logical Fracturing" in late chapters, the Adjacency 
      Matrix of Block N is initialized with a decayed version of Block N-1.
      M_new = (1 - alpha) * M_raw + alpha * M_prev
      alpha = 0.3

   B. Grammar Suppression (Curvature-Weighted Adjacency)
      The engine tracks the "Discrete Curvature" of coordinates over time.
      Terms with high volatility (instability) are flagged as "Grammar Parasites"
      (e.g., "Given", "In", "As").
      Their adjacency weights are penalized (w * 0.1), preventing them from 
      acting as false roots.

   C. Multi-Adelic + Divisibility Core (V.33)
      Retains the Q5xQ7xQ11 field and Divisibility Lattice.

2. GOAL
   To produce the cleanest, most biologically and chemically accurate 
   ontology to date, separating "Matter" (Root) from "Description" (Leaf).

======================================================================
"""

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append(get_system_documentation())
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - REFINED AUDIT (PROTOCOL V.34)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Pages Processed: {page_count}")
    report.append(f"Momentum: 0.3")
    
    report.append("\n" + "-"*70)
    report.append("ONTOLOGY TRACE: REFINED LATTICE (V.34)")
    report.append(f"{'CONCEPT'.ljust(30)} | {'VECTORS (v5,v7,v11)'.ljust(25)} | {'ROLE'}")
    report.append("-" * 70)
    
    tree = result['tree']['tree']
    roots = result['tree']['roots']
    vectors = result['vectors']
    
    # Recursive Print
    def print_node(node, depth=0):
        vec = vectors.get(node, (0,0,0))
        vec_str = f"({vec[0]},{vec[1]},{vec[2]})"
        indent = "  " * depth
        role = "ROOT" if depth == 0 else "NODE"
        
        line = f"{indent}{node}".ljust(30)
        report.append(f"{line} | {vec_str.ljust(25)} | {role}")
        
        children = tree.get(node, [])
        for child in children:
            print_node(child, depth+1)
            
    # Print Roots 
    for root in sorted(roots):
        print_node(root, 0)

    report.append("\n" + "="*70)
    report.append("   V.34 REFINED AUDIT COMPLETE")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.34 - Refined Run] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    # Full Run implies all pages
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating V.34 Synthesis on FULL TEXT ({total_pages} pages)...")
    
    # Instantiate V34 with Momentum
    synthesizer = SerialSynthesizerV34(chunk_size=50, momentum=0.3)
    
    result = synthesizer.fit_stream(reader)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v34_refined_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Refined Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
