
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v35 import SerialSynthesizerV35
from pypdf import PdfReader

def get_system_documentation():
    return """
======================================================================
   LOGIC MINER ENGINE - PROTOCOL V.35 CONSERVATION
   "The Vacuum Stabilizer"
======================================================================

1. CONSERVATION ARCHITECTURE
   This Protocol builds on V.34 Refined by adding:

   A. Norm-Constrained Solver (Conservation Law)
      To prevent the "Zero-Vector Singularity" (Vacuum Collapse) observed in V.34,
      the solver now enforces a minimum energy floor.
      - "Vacuum Fluctuation": A universal coupling constant (epsilon) ensures
        no node is fully disconnected from the "Center of Mass".
      - "Simultaneous Barycentric Anchoring": All patches are anchored to 
        their local frequency center, preventing drift into the nullspace.

   B. Stable Prime Field
      Reverted to Q5 x Q7 x Q11 to avoid the "Gravity Well" of p=2.

   C. V.34 Features Retained
      - Matrix Momentum (Spline Continuity)
      - Grammar Suppression (Curvature Gating)

2. GOAL
   To recover the "Lost Ontology" (Atom, Bonding, Phosphine) that collapsed 
   to (0,0,0) in V.34, while maintaining the clean separation of Matter/Energy.

======================================================================
"""

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append(get_system_documentation())
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - CONSERVATION AUDIT (PROTOCOL V.35)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Pages Processed: {page_count}")
    
    report.append("\n" + "-"*70)
    report.append("ONTOLOGY TRACE: CONSERVATION LATTICE (V.35)")
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
    report.append("   V.35 CONSERVATION AUDIT COMPLETE")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.35 - Conservation Run] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating V.35 Synthesis on FULL TEXT ({total_pages} pages)...")
    
    # Instantiate V35 with Momentum & Norm Constraints
    synthesizer = SerialSynthesizerV35(chunk_size=50, momentum=0.3)
    
    result = synthesizer.fit_stream(reader)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v35_conservation_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Conservation Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
