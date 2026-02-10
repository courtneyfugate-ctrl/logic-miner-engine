
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.serial_synthesis_v46 import SerialSynthesizerV46
from pypdf import PdfReader

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - UNIFIED AUDIT (V.46)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Protocol: THE UNIFIED FIELD (V.46)")
    report.append(f"Components: V.45 (Curvature) + V.42 (Adelic Complexity)")
    report.append(f"Status: STABILIZED (p={result['p']})")
    
    report.append("\n" + "-"*80)
    report.append("ADELIC FOREST TRACE: UNIFIED LATTICE")
    report.append(f"{'CONCEPT'.ljust(30)} | {'ADDR'.ljust(15)} | {'MOD P'.ljust(10)} | {'ROLE'}")
    report.append("-" * 80)
    
    coords = result['coordinates']
    p = result['p']
    sorted_ents = sorted(result['entities'], key=lambda e: coords.get(e, 0))
    
    purity_failure = False
    forbidden = ["Introduction", "Chapter", "In", "As"]
    
    for ent in sorted_ents:
        if any(bad == ent for bad in forbidden): # Strict match for "In", "As"
            purity_failure = True
            
        addr = coords.get(ent, 0)
        mod_p = addr % p
        
        if addr < p:
            role = f"ROOT (Trunk {addr})"
        elif addr % p == 0:
            role = "LEAF/PROPERTY"
        else:
            role = "NODE"
            
        report.append(f"{ent.ljust(30)} | {str(addr).ljust(15)} | {str(mod_p).ljust(10)} | {role}")

    report.append("\n" + "="*80)
    if purity_failure:
        report.append("   [WARNING] Purity Breach (Flat or Simple Terms Detected).")
    else:
        report.append("   [SUCCESS] Unified Purity Verified.")
    report.append("="*80)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.46 - The Unified Field] ---")
    miner = LogicMiner()
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    # Run 300 pages
    pages_to_run = 300
    
    start_time = time.time()
    
    print(f"   > Initiating V.46 Unified Synthesis (K_geom > 0.5 AND K_info > 0.15)...")
    
    # V.46 Synthesizer
    synthesizer = SerialSynthesizerV46(chunk_size=50)
    result = synthesizer.fit_stream(reader=reader, max_pages=pages_to_run)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate Dump
    report_content = generate_audit_report(result, run_time, pages_to_run)
    
    dump_path = "sandbox/v46_unified_audit.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
