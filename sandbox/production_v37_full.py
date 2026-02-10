
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v37 import SerialSynthesizerV37
from pypdf import PdfReader

def get_system_documentation():
    return """
======================================================================
   LOGIC MINER ENGINE - PROTOCOL V.37 TOPOLOGICAL FILTER
   "Crystalline Sediment"
======================================================================

1. TOPOLOGICAL FILTER ARCHITECTURE
   This Protocol builds on V.36 Flow Conservation by adding:

   A. Local Clustering Coefficient Filter (Ci)
      To resolve the "Pooling" issue where Scaffolding ("Introduction") and Concepts ("Atoms")
      share flow potentials, we calculate the Local Clustering Coefficient for each node.
      - Concepts (Hubs) connect dense cliques -> High Ci.
      - Scaffolding (Bridges) connect disjoint clusters -> Low Ci.
      
      Nodes with Ci < (Mean - StdDev) are identified as Sediment/Bridges and suppressed
      with a high "Viscosity Mask" (weight x 0.1) before the Flow Solver runs.

   B. V.36 Features Retained
      - Flow-Balanced Solver (Sinkhorn-Knopp)
      - Norm-Constrained Solver (Vacuum Stabilizer)
      - Stable Prime Field (Q5 x Q7 x Q11)

2. GOAL
   To crystallize the "Sediment Layer" by forcing a separation between structural bridges
   and conceptual hubs.

======================================================================
"""

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append(get_system_documentation())
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - TOPOLOGICAL AUDIT (PROTOCOL V.37)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Pages Processed: {page_count}")
    
    report.append("\n" + "-"*70)
    report.append("ONTOLOGY TRACE: CRYSTALLINE LATTICE (V.37)")
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
    report.append("   V.37 TOPOLOGICAL AUDIT COMPLETE")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.37 - Crystalline Sediment Run] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating V.37 Synthesis on FULL TEXT ({total_pages} pages)...")
    
    # Instantiate V37
    synthesizer = SerialSynthesizerV37(chunk_size=50, momentum=0.3, resolution=0.5)
    
    result = synthesizer.fit_stream(reader)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v37_topological_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Topological Filter Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
