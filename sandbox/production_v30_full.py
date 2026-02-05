
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
    report.append("   LOGIC MINER ENGINE - FINAL PRODUCTION AUDIT (PROTOCOL V.30)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Processing Depth: {page_count} Pages")
    report.append(f"Protocol: THE ADELIC FOREST (V.30)")
    report.append(f"Status: MULTI-ROOT LATTICE STABILIZED (p={result['p']})")
    report.append(f"Total Execution Time: {run_time:.2f} seconds")
    
    report.append("\n" + "-"*70)
    report.append("CONCEPT TRACE & FOREST COORDINATE ADDRESSES")
    report.append(f"{'CONG CLASS (Base p)'.ljust(30)} | {'ROOT'}")
    report.append("-" * 70)
    
    coords = result['coordinates']
    p = result['p']
    
    # Identify Roots (Addresses < p)
    roots = [(c, a) for c, a in coords.items() if a < p]
    for r_name, r_addr in sorted(roots, key=lambda x: x[1]):
        report.append(f"{str(r_addr).ljust(30)} | {r_name}")

    report.append("\n" + "-"*70)
    report.append("FULL LATTICE DISTRIBUTION")
    report.append("-" * 70)
    
    # Sort by address
    sorted_ents = sorted(result['entities'], key=lambda e: coords.get(e, 0))
    
    report.append(f"{'CONCEPT'.ljust(30)} | {'ADDR'.ljust(15)} | {'MOD P'.ljust(10)} | {'TYPE'}")
    report.append("-" * 70)
    for ent in sorted_ents:
        addr = coords.get(ent, 0)
        mod_p = addr % p
        report.append(f"{ent.ljust(30)} | {str(addr).ljust(15)} | {str(mod_p).ljust(10)} | CONCEPT")

    report.append("\n" + "="*70)
    report.append("   V.30 AUDIT COMPLETE - THE FOREST IS ESTABLISHED")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.30 - The Adelic Forest Run] ---")
    miner = LogicMiner()
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    start_time = time.time()
    
    print(f"   > Initiating V.30 Forest Synthesis on {total_pages} pages...")
    result = miner.fit_text("", reader=reader, use_serial=True)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, total_pages)
    
    dump_path = "sandbox/v30_rigorous_audit_dump.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")

if __name__ == "__main__":
    main()
