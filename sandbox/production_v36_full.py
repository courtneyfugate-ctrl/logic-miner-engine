
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v36 import SerialSynthesizerV36
from pypdf import PdfReader

def get_system_documentation():
    return """
======================================================================
   LOGIC MINER ENGINE - PROTOCOL V.36 FLOW CONSERVATION
   "The Semantic Fluid"
======================================================================

1. FLOW CONSERVATION ARCHITECTURE
   This Protocol builds on V.35 Conservation by adding:

   A. Flow-Balanced Solver (Conservative Fluid)
      To prevent High-Degree Process Terms ("Reaction") from dominating Low-Degree Entities ("Hydrogen"),
      we enforce Kirchhoff's Law / Flow Balance (Sum In = Sum Out) via Sinkhorn-Knopp normalization
      on the adjacency matrix. This creates a "Doubly Stochastic" semantic field where influence
      is conserved locally.

   B. V.35 Features Retained
      - Norm-Constrained Solver (Vacuum Stabilizer)
      - Stable Prime Field (Q5 x Q7 x Q11)
      - Matrix Momentum & Grammar Suppression

2. GOAL
   To balance the "Semantic Fluid" so that "Reaction" (Process) and "Hydrogen" (Entity) 
   separate naturally based on internal structure, rather than graph volume.

======================================================================
"""

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append(get_system_documentation())
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - FLOW CONSERVATION AUDIT (PROTOCOL V.36)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Pages Processed: {page_count}")
    
    report.append("\n" + "-"*70)
    report.append("ONTOLOGY TRACE: FLOW BALANCED LATTICE (V.36)")
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
    report.append("   V.36 FLOW CONSERVATION AUDIT COMPLETE")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.36 - Flow Conservation Run] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating V.36 Synthesis on FULL TEXT ({total_pages} pages)...")
    
    # Instantiate V36 with Momentum, Resolution=0.5
    synthesizer = SerialSynthesizerV36(chunk_size=50, momentum=0.3, resolution=0.5)
    
    result = synthesizer.fit_stream(reader)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v36_flow_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Flow Conservation Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
