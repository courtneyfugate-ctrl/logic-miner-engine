
import sys
import os
import json
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v33 import SerialSynthesizerV33
from pypdf import PdfReader

def get_system_documentation():
    return """
======================================================================
   LOGIC MINER ENGINE - PROTOCOL V.33 EXPERIMENTAL
   "The Ontology Extractor"
======================================================================

1. EXPERIMENTAL ARCHITECTURE
   This run implements the unified "V.33" prototype, integrating three 
   research-grade upgrades:

   A. Multi-Adelic Decomposition
      Field: Q_5 x Q_7 x Q_11
      Concept Valuations are 3D vectors v(x) = (v_5, v_7, v_11).
      This allows separating heterogeneous concepts that collide in single-p fields.

   B. Curvature-Weighted Promotion
      Tracks the stability of coordinates across the text stream.
      High Curvature (k > 20.0) -> unstable meaning (Context-dependent).
      Low Curvature -> stable meaning (Eternal Anchor).
      Unstable terms are demoted from Root candidacy.

   C. Divisibility-Based Hierarchy
      Replaces geometric distance with algebraic generation.
      A node x is child of y iff y divides x maximally across the vector field.
      v(x, y) = max_i v_pi(x_i - y_i)

2. GOAL
   To produce a rigorous, noise-free ontology where trunks represent true 
   generative roots (Matter, Energy) rather than linguistic clusters.

======================================================================
"""

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append(get_system_documentation())
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - EXPERIMENTAL AUDIT (PROTOCOL V.33)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Pages Processed: {page_count}")
    report.append(f"Fields: {result['primes']}")
    
    report.append("\n" + "-"*70)
    report.append("ONTOLOGY TRACE: DIYISIBILITY LATTICE")
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
            
    # Print Roots (Limit top 20 for brevity if huge, but full dump requested)
    # Sort roots by global importance? Or assume alphabetical?
    # Let's sort roots alphabetically
    for root in sorted(roots):
        print_node(root, 0)

    report.append("\n" + "="*70)
    report.append("   V.33 EXPERIMENTAL AUDIT COMPLETE")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.33 - Experimental Run] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    # Full Run implies all pages
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating V.33 Synthesis on FULL TEXT ({total_pages} pages)...")
    
    synthesizer = SerialSynthesizerV33(chunk_size=50)
    
    # We can pass reader directly to V33 fit_stream
    result = synthesizer.fit_stream(reader)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v33_experimental_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Experimental Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
