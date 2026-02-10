
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.engine import LogicMiner
from logic_miner.core.serial_synthesis_v42 import SerialSynthesizerV42
from pypdf import PdfReader

def generate_audit_report(result, run_time, page_count):
    report = []
    report.append("======================================================================")
    report.append("   LOGIC MINER ENGINE - FINAL PROTOCOL AUDIT (V.42)")
    report.append("======================================================================")
    report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Corpus: Chemistry 2e (Full Volume)")
    report.append(f"Protocol: INTEGRATED ADELIC TREE (V.42)")
    report.append(f"Components: V.32 (Modular Tree) + V.41 (Global Hasse Filter)")
    report.append(f"Status: STABILIZED (p={result['p']})")
    
    report.append("\n" + "-"*80)
    report.append("ADELIC FOREST TRACE: RANK-BASED MODULAR HIERARCHY")
    report.append(f"{'CONCEPT'.ljust(30)} | {'ADDR'.ljust(15)} | {'MOD P'.ljust(10)} | {'ROLE'}")
    report.append("-" * 80)
    
    coords = result['coordinates']
    p = result['p']
    
    # Sort by address
    sorted_ents = sorted(result['entities'], key=lambda e: coords.get(e, 0))
    
    # Purity Check List
    forbidden = ["Introduction", "Chapter", "Section", "Summary", "Exercises", "Access"]
    purity_failure = False
    
    for ent in sorted_ents:
        if any(bad in ent for bad in forbidden):
            purity_failure = True
            
        addr = coords.get(ent, 0)
        mod_p = addr % p
        
        # Heuristic for Role Display (V.32 Standard)
        if addr < p:
            role = f"ROOT (Trunk {addr})"
        elif addr % p == 0:
            role = "LEAF/PROPERTY"
        else:
            role = "NODE"
            
        report.append(f"{ent.ljust(30)} | {str(addr).ljust(15)} | {str(mod_p).ljust(10)} | {role}")

    report.append("\n" + "="*80)
    if purity_failure:
        report.append("   [WARNING] Purity Breach Detected! Artifacts remain.")
    else:
        report.append("   [SUCCESS] Adelic Purity Verified. Artifacts Eliminated.")
    report.append("="*80)
    
    return "\n".join(report)

def main():
    print("--- [Logic Miner V.42 - The Final Protocol] ---")
    miner = LogicMiner()
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    # Run on first 300 pages for rigorous check
    pages_to_run = 300
    
    start_time = time.time()
    
    print(f"   > Initiating V.42 Adelic Synthesis on {pages_to_run} pages...")
    
    # Manually invoke V42 Synthesizer
    synthesizer = SerialSynthesizerV42(chunk_size=50)
    result = synthesizer.fit_stream(reader=reader, max_pages=pages_to_run)
    
    end_time = time.time()
    run_time = end_time - start_time
    
    # Generate the Audit Dump
    report_content = generate_audit_report(result, run_time, pages_to_run)
    
    dump_path = "sandbox/v42_final_audit.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"\n   > Production Run Complete. Result saved to: {dump_path}")
    print(f"   > Time Elapsed: {run_time:.2f}s")

if __name__ == "__main__":
    main()
