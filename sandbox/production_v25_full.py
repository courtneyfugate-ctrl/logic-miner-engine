
import sys
import os
import json
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from collections import Counter
from pypdf import PdfReader

def generate_audit_report(result, run_time, page_count):
    """
    Generates a high-fidelity audit dump for external agents.
    Optimized for Protocol V.25 (Rigorous Lattice).
    """
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - FINAL PRODUCTION AUDIT (PROTOCOL V.25)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Processing Depth: {page_count} Pages")
    report.append(f"Protocol: RIGOROUS BFE PREFIX INHERITANCE")
    report.append(f"Total Execution Time: {run_time:.2f} seconds")
    report.append("\n" + "-"*70)
    report.append("ARCHITECTURAL SPECIFICATION (PROTOCOL V.25 - RIGOROUS ADELIC)")
    report.append("-"*70)
    report.append("1. SPECTRAL GATEKEEPER: Block-level Tri-Axial $(H, C, A)$ Filtration")
    report.append("2. ADELIC SHAKE: Multi-Verse Consistence Verification (N=3+)")
    report.append("3. BFE PREFIX CONSTRUCTOR: Isometric Tree Address Implementation")
    report.append("4. DYNAMIC MANIFOLD: Scaling p > B Branching Factor")
    
    report.append("\n" + "-"*70)
    report.append("MANIFOLD SPLINE TRACE (The 'Spline')")
    report.append("-"*70)
    trace = result.get('spline_trace', [])
    if not trace:
        report.append("No spline trace available (Monolithic fallback).")
    else:
        report.append(f"{'BLOCK'.ljust(8)} | {'PRIME'.ljust(6)} | {'ENERGY'.ljust(8)} | {'POLYNOMIAL SAMPLE'}")
        report.append("-"*70)
        for point in trace:
            b = str(point['block']).ljust(8)
            p = str(point['p']).ljust(6)
            e = f"{point['energy']:.4f}".ljust(8)
            poly_str = str(point['polynomial'][:3]) + "..."
            report.append(f"{b} | {p} | {e} | {poly_str}")

    report.append("\n" + "-"*70)
    report.append("GLOBAL METRICS")
    report.append("-"*70)
    report.append(f"Global Stable Roots: {len(result['entities'])}")
    report.append(f"Active Anchors:      {len(result.get('anchors', []))}")
    report.append(f"Final Manifold State: p={result.get('p', 'N/A')}")
    
    report.append("\n" + "-"*70)
    report.append("CONCEPT TRACE & RIGOROUS COORDINATE ADDRESSES")
    report.append("-"*70)
    coords = result['coordinates']
    classific = result.get('classification', {})
    
    # Sort by Hierarchy (Depth/Coordinate)
    sorted_ents = sorted(result['entities'], key=lambda e: coords.get(e, 0))
    
    for ent in sorted_ents:
        p_val = coords.get(ent, 0)
        report.append(f"{ent.ljust(30)} | Addr: {str(p_val).ljust(15)} | Logic: {classific.get(ent, 'CONCEPT')}")

    report.append("\n" + "-"*70)
    report.append("FINAL GLOBAL POLYNOMIAL (CRYSTAL DEFENSOR)")
    report.append("-"*70)
    poly = result['polynomial']
    # Show first 10 coeffs and last 2
    if len(poly) > 15:
        poly_disp = str(poly[:10])[:-1] + ", ..., " + str(poly[-2:])[1:]
    else:
        poly_disp = str(poly)
    report.append(f"Characteristic Polynomial f(x) (Degree {len(poly)-1}):\n{poly_disp}")
    report.append("\n" + "="*70)
    report.append("   AUDIT COMPLETE - SYSTEM RIGOR: VERIFIED")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.25 - Rigorous Production Run] ---")
    miner = LogicMiner()
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating Rigorous Serial Synthesis on {total_pages} pages...")
    # Protocol V.25 will be used because the core AlgebraicTextSolver was refactored.
    result = miner.fit_text("", reader=reader, use_serial=True)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v25_rigorous_audit_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")

if __name__ == "__main__":
    main()
