
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.serial_synthesis_v54 import SerialSynthesizerV54
from pypdf import PdfReader

def generate_tree_report_v54(synthesizer, run_time, page_count):
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - PROTOCOL V.54: ULTRAMETRIC CORRECTION")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Protocol: ULTRAMETRIC CORRECTION (Hilbert Primary, Peeling, Depth=10)")
    report.append(f"Fixes:")
    report.append(f"  1. Hilbert coordinates as PRIMARY signal (not frequency rank)")
    report.append(f"  2. Iterative RANSAC peeling for multi-modal logic")
    report.append(f"  3. Hensel lifting depth=10 (was 3)")
    report.append(f"  4. Tree from p-adic valuations (not frequency)")
    
    report.append("\n" + "-"*80)
    report.append("P-ADIC DENDROGRAM: V.54 ULTRAMETRIC TREE")
    report.append(f"{'HIERARCHY'.ljust(60)} | {'FREQ'.ljust(10)}")
    report.append("-" * 80)
    
    tree_data = synthesizer.tree_structure
    tree = tree_data.get('tree', {})
    roots = tree_data.get('roots', [])
    
    total_yield = len(synthesizer.final_vectors)
    total_roots = len(roots)
    
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

    visited_global = set()
    for root in roots[:20]:  # Top 20 roots
        print_node(root, 0, visited_global)
        report.append("")

    report.append("\n" + "="*80)
    report.append(f"   [STATS] Total Yield (Ultrametric Verified): {total_yield}")
    report.append(f"   [STATS] Total Roots: {total_roots}")
    report.append(f"   [STATS] Runtime: {run_time:.2f}s")
    report.append("="*80)
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.54 - Ultrametric Correction] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    pages_to_run = 1200
    
    start_time = time.time()
    
    print(f"   > Initiating V.54 Synthesis (Ultrametric Corrections)...")
    
    synthesizer = SerialSynthesizerV54(chunk_size=50, momentum=0.3)
    synthesizer.fit_stream(reader=reader, max_pages=pages_to_run)
    
    synthesizer._consolidate_global_lattice()
    
    end_time = time.time()
    run_time = end_time - start_time
    
    report_content = generate_tree_report_v54(synthesizer, run_time, pages_to_run)
    
    dump_path = "sandbox/v54_ultrametric_audit.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")
    print(f"   > Ultrametric Yield: {len(synthesizer.final_vectors)} terms")
    print(f"   > Roots: {len(synthesizer.tree_structure.get('roots', []))}")

if __name__ == "__main__":
    main()
