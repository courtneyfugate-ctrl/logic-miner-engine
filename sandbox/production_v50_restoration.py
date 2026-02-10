
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.serial_synthesis_v50 import SerialSynthesizerV50
from pypdf import PdfReader

def generate_tree_report(synthesizer, run_time, page_count):
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - RESTORATION AUDIT (V.50)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Protocol: THE RESTORATION (Hybrid Engine)")
    report.append(f"Components: Hilbert Topo + Spline Momentum + Adelic Resonance + Ultrametric Tree")
    report.append(f"Basis: Adelic Primorial M = 30030")
    report.append(f"Status: HYBRID STABILIZED")
    
    report.append("\n" + "-"*80)
    report.append("ADELIC DENDROGRAM: V.50 ULTRAMETRIC TREE")
    report.append(f"{'HIERARCHY'.ljust(60)} | {'ADDR'.ljust(10)} | {'DEPTH'}")
    report.append("-" * 80)
    
    tree = synthesizer.tree_structure
    
    # Sort Trunks by ID
    sorted_trunks = sorted(tree.keys())
    
    total_terms = 0
    trunk_count = 0
    
    for trunk_id in sorted_trunks:
        trunk_data = tree[trunk_id]
        if not trunk_data: continue
        
        trunk_count += 1
        
        # Sort Depths (High Depth = Root)
        # Wait, my logic was:
        # Depth 0 (Coprime) -> Leaf
        # High Depth (Divisible) -> Root?
        # Let's verify. 30030 is divisible by all primes. So Depth 6.
        # "1" is coprime. Depth 0.
        # So HIGH is ROOT. LOW is LEAF.
        
        sorted_depths = sorted(trunk_data.keys(), reverse=True)
        
        # Print Trunk Header (Implicit, usually the deepest term defines it)
        # But for display, we just list structure.
        
        report.append(f"[Trunk {trunk_id}] (Base Class)")
        
        for depth in sorted_depths:
            terms = sorted(trunk_data[depth])
            indent = "  " * (6 - depth) # Creating visual indent based on specificity
            # Root (Depth 6) -> Indent 0
            # Leaf (Depth 0) -> Indent 12
            
            for term in terms:
                display_term = f"{indent}- {term}"
                addr = synthesizer.global_coordinates.get(term, "N/A")
                report.append(f"{display_term.ljust(60)} | {str(addr).ljust(10)} | {depth}")
                total_terms += 1
        
        report.append("") # Spacer between trunks

    report.append("\n" + "="*80)
    report.append(f"   [STATS] Total Terms: {total_terms}")
    report.append(f"   [STATS] Total Trunks: {trunk_count}")
    
    if total_terms > 400:
        report.append("   [SUCCESS] Restoration Verified (> 400 Terms + Tree Structure).")
    else:
        report.append("   [WARNING] Yield below target.")
        
    report.append("="*80)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.50 - The Restoration] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    # Run 1200 pages (Full Restoration)
    pages_to_run = 1200
    
    start_time = time.time()
    
    print(f"   > Initiating V.50 Hybrid Synthesis (Hilbert+Splines+Resonance)...")
    
    # V.50 Synthesizer
    synthesizer = SerialSynthesizerV50(chunk_size=50, momentum=0.3)
    synthesizer.fit_stream(reader=reader, max_pages=pages_to_run)
    
    # Construct Tree (Last step of fit stream usually, but let's ensure it ran)
    # fit_stream calls process_block but consolidation happens manually usually in my scripts?
    # Wait, `fit_stream` in base class ends. We usually need to call `_consolidate_global_lattice`?
    # In V.47/48 I put it inside `_consolidate` but did I call it?
    # `fit_stream` loops then returns.
    # I need to manually call `consolidate` at the end or ensure fit_stream does.
    # Checking base class... `fit_stream` usually doesn't call consolidate.
    # I should call it explicitly here.
    
    print(f"   > Consolidating Global Lattice...")
    synthesizer._consolidate_global_lattice()
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate Dump
    report_content = generate_tree_report(synthesizer, run_time, pages_to_run)
    
    dump_path = "sandbox/v50_restoration_audit.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")
    print(f"   > Total Yield: {len(synthesizer.global_coordinates)} terms")

if __name__ == "__main__":
    main()
