import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v55 import SerialSynthesizerV55
from pypdf import PdfReader

def generate_tree_report_v55(synthesizer, run_time, page_count):
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - PROTOCOL V.55: SHEAF SPLINING")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Protocol: SHEAF SPLINING (Rigid Overlap Verification)")
    report.append(f"Features:")
    report.append(f"  1. 50% Overlapping Windows (50 pages, step 25)")
    report.append(f"  2. Sheaf Lock: Coords must match EXACTLY on overlap")
    report.append(f"  3. Trajectory Mode: Discrete majority voting (not averaging)")
    report.append(f"  4. Only locked terms survive")
    
    report.append("\n" + "-"*80)
    report.append("SHEAF-VERIFIED DENDROGRAM: V.55 RIGID TREE")
    report.append(f"{'HIERARCHY'.ljust(60)} | {'LOCKS'.ljust(10)}")
    report.append("-" * 80)
    
    tree_data = synthesizer.tree_structure
    tree = tree_data.get('tree', {})
    roots = tree_data.get('roots', [])
    
    total_yield = len(synthesizer.final_vectors)
    total_roots = len(roots)
    total_rejected = len(synthesizer.rejected_links)
    
    def print_node(node, depth=0, visited=None):
        if visited is None: visited = set()
        if node in visited: return
        visited.add(node)
        
        indent = "  " * depth
        # Count how many windows this term appeared in (proxy for "locks")
        locks = len([1 for win_id, logic in synthesizer.window_logic.items() if node in logic])
        report.append(f"{indent}- {node.ljust(55-len(indent))} | {locks}")
        
        children = tree.get(node, [])
        children.sort(key=lambda c: len([1 for w in synthesizer.window_logic.values() if c in w]), reverse=True)
        
        for child in children:
            print_node(child, depth + 1, visited)

    visited_global = set()
    for root in roots[:20]:
        print_node(root, 0, visited_global)
        report.append("")

    report.append("\n" + "="*80)
    report.append(f"   [STATS] Total Yield (Sheaf-Locked): {total_yield}")
    report.append(f"   [STATS] Total Roots: {total_roots}")
    report.append(f"   [STATS] Rejected Links (Inconsistent): {total_rejected}")
    report.append(f"   [STATS] Runtime: {run_time:.2f}s")
    report.append("="*80)
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.55 - Sheaf Splining] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    pages_to_run = 1200
    
    start_time = time.time()
    
    print(f"   > Initiating V.55 Sheaf Synthesis (Overlapping Windows)...")
    
    synthesizer = SerialSynthesizerV55(chunk_size=50)
    synthesizer.fit_stream(reader=reader, max_pages=pages_to_run)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    report_content = generate_tree_report_v55(synthesizer, run_time, pages_to_run)
    
    dump_path = "sandbox/v55_sheaf_audit.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")
    print(f"   > Sheaf-Verified Yield: {len(synthesizer.final_vectors)} terms")
    print(f"   > Roots: {len(synthesizer.tree_structure.get('roots', []))}")
    print(f"   > Rejected: {len(synthesizer.rejected_links)} inconsistent links")

if __name__ == "__main__":
    main()
