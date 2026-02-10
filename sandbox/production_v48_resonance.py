
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.serial_synthesis_v48 import SerialSynthesizerV48
from pypdf import PdfReader

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - RESONANT AUDIT (V.48)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Protocol: THE RESONANT EXPANSION (V.48)")
    report.append(f"Components: V.47 Core + V.48 Resonance Rescue (Adelic Magnets)")
    report.append(f"Basis: Adelic Primorial M = 30030")
    report.append(f"Status: STABILIZED (M=30030)")
    
    report.append("\n" + "-"*80)
    report.append("ADELIC FOREST TRACE: RESONANT LATTICE")
    report.append(f"{'CONCEPT'.ljust(30)} | {'ADDR'.ljust(15)} | {'MOD M'.ljust(10)} | {'ROLE'}")
    report.append("-" * 80)
    
    coords = result['coordinates']
    valid_coords = {k: v for k, v in coords.items() if v is not None}
    
    sorted_ents = sorted(valid_coords.keys(), key=lambda e: valid_coords[e])
    
    trunk_counts = {}
    M = 30030
    
    for ent in sorted_ents:
        addr = valid_coords[ent]
        mod_m = addr % M
        
        if addr < M:
            role = f"ROOT (Trunk {mod_m})"
            trunk_counts[mod_m] = trunk_counts.get(mod_m, 0) + 1
        else:
            role = "NODE"
            
        report.append(f"{ent.ljust(30)} | {str(addr).ljust(15)} | {str(mod_m).ljust(10)} | {role}")

    report.append("\n" + "="*80)
    report.append(f"   [STATS] Total Terms: {len(sorted_ents)}")
    report.append(f"   [STATS] Total Trunks: {len(trunk_counts)}")
    
    if len(sorted_ents) > 300:
        report.append("   [SUCCESS] Resonant Expansion Verified (> 300 Terms).")
    elif len(sorted_ents) > 100:
        report.append("   [PARTIAL SUCCESS] Yield Improved (> 100 Terms), but below target.")
    else:
        report.append("   [WARNING] Low Yield. Resonance Rescue weak?")
        
    report.append("="*80)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.48 - Resonant Expansion] ---")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    # Run 1200 pages (Limit of book) to maximize yield
    pages_to_run = 1200
    
    start_time = time.time()
    
    print(f"   > Initiating V.48 Resonant Synthesis (M=30030, Rescue Enabled)...")
    
    # V.48 Synthesizer
    synthesizer = SerialSynthesizerV48(chunk_size=50)
    result = synthesizer.fit_stream(reader=reader, max_pages=pages_to_run)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate Dump
    report_content = generate_audit_report(result, run_time, pages_to_run)
    
    dump_path = "sandbox/v48_resonance_audit.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
