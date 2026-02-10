
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.serial_synthesis_v53 import SerialSynthesizerV53
from pypdf import PdfReader

def generate_tree_report_v53(synthesizer, run_time, page_count):
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - PROTOCOL V.53: COMPLIANCE")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Protocol: RANSAC-HENSEL COMPLIANCE")
    report.append(f"Components: PrimeSelector (Discovery) + HenselLifter (Refinement)")
    report.append(f"Basis: Dynamic (RANSAC Discovered)")
    
    report.append("\n" + "-"*80)
    report.append("ADELIC DENDROGRAM: V.53 COMPLIANT TREE")
    report.append(f"{'HIERARCHY'.ljust(60)} | {'FREQ'.ljust(10)}")
    report.append("-" * 80)
    
    tree_data = synthesizer.tree_structure # {'tree': dict, 'roots': list}
    tree = tree_data.get('tree', {})
    roots = tree_data.get('roots', [])
    
    total_yield = len(synthesizer.final_vectors)
    total_roots = len(roots)
    
    # Recursive Print Function
    def print_node(node, depth=0, visited=None):
        if visited is None: visited = set()
        if node in visited: return
        visited.add(node)
        
        indent = "  " * depth
        freq = synthesizer.global_freqs.get(node, 0)
        report.append(f"{indent}- {node.ljust(55-len(indent))} | {freq}")
        
        children = tree.get(node, [])
        children.sort(key=lambda c: synthesizer.global_freqs.get(c, 0), reverse=True)
        
        for child in children:
            print_node(child, depth + 1, visited)

    # Sort Roots by Frequency
    roots.sort(key=lambda r: synthesizer.global_freqs.get(r, 0), reverse=True)
    
    visited_global = set()
    for root in roots:
        print_node(root, 0, visited_global)
        report.append("") 

    report.append("\n" + "="*80)
    report.append(f"   [STATS] Total Yield (RANSAC Survivors): {total_yield}")
    report.append(f"   [STATS] Total Roots: {total_roots}")
    
    report.append("="*80)
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.53 - The Compliance] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    # Run 1200 pages
    pages_to_run = 1200
    
    start_time = time.time()
    
    print(f"   > Initiating V.53 Synthesis (RANSAC + Hensel)...")
    
    # V.53 Synthesizer
    synthesizer = SerialSynthesizerV53(chunk_size=50, momentum=0.3)
    synthesizer.fit_stream(reader=reader, max_pages=pages_to_run)
    
    # Call Consolidate
    synthesizer._consolidate_global_lattice()
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate Dump
    report_content = generate_tree_report_v53(synthesizer, run_time, pages_to_run)
    
    dump_path = "sandbox/v53_compliance_audit.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")
    print(f"   > RANSAC Yield: {len(synthesizer.final_vectors)} terms")

if __name__ == "__main__":
    main()
