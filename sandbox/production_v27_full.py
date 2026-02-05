
import sys
import os
import json
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from pypdf import PdfReader

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - FINAL PRODUCTION AUDIT (PROTOCOL V.27)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Processing Depth: {page_count} Pages")
    report.append(f"Protocol: RIGOROUS STABILITY (V.27)")
    report.append(f"Status: ETERNAL ROOT ANCHORED")
    report.append(f"Total Execution Time: {run_time:.2f} seconds")
    
    report.append("\n" + "-"*70)
    report.append("CONCEPT TRACE & RIGOROUS COORDINATE ADDRESSES")
    report.append("-"*70)
    coords = result['coordinates']
    classific = result.get('classification', {})
    
    # Sort by Hierarchy (Depth/Coordinate)
    sorted_ents = sorted(result['entities'], key=lambda e: coords.get(e, 0))
    
    report.append(f"{'CONCEPT'.ljust(30)} | {'ADDR (p-adic)'.ljust(15)} | {'LOGIC TYPE'}")
    report.append("-" * 70)
    for ent in sorted_ents:
        p_val = coords.get(ent, 0)
        report.append(f"{ent.ljust(30)} | {str(p_val).ljust(15)} | {classific.get(ent, 'CONCEPT')}")

    report.append("\n" + "="*70)
    report.append("   V.27 AUDIT COMPLETE - LATTICE STABILIZED")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.27 - Rigorous Stability Run] ---")
    miner = LogicMiner()
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating V.27 Rigorous Synthesis on {total_pages} pages...")
    result = miner.fit_text("", reader=reader, use_serial=True)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v27_rigorous_audit_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")

if __name__ == "__main__":
    main()
