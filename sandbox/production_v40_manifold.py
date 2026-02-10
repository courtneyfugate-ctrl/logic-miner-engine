
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v40 import SerialSynthesizerV40
from pypdf import PdfReader

def main():
    print("--- [Logic Miner V.40 - The Manifold Protocol (Strict Ultrametric)] ---")
    print("   > Principle: P-adic Values, Ultrametric Distance, TDA (B0/B1/Depth)")
    print("   > Directive: NO Euclidean Metrics. NO Variance.")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    pages_to_scan = 400
    
    start_time = time.time()
    
    print(f"   > Learning Point Cloud from first {pages_to_scan} pages...")
    
    synthesizer = SerialSynthesizerV40(chunk_size=50, momentum=0.3, resolution=0.5)
    
    count = 0
    text_buffer = ""
    
    for i, page in enumerate(reader.pages):
        if i >= pages_to_scan: break
        text = page.extract_text()
        if text:
            text_buffer += text + "\n"
            
        if len(text_buffer) > 5000:
            synthesizer._process_block(text_buffer)
            text_buffer = ""
            count += 1
            if count % 20 == 0:
                print(f"     Processed {count} blocks...")
                
    print(f"   > Point Cloud Built. Memory Size: {len(synthesizer.global_adjacency_memory)} edges.")
    
    print("   > Calculating Persistent Homology & Depth (Barcodes)...")
    persistence_map = synthesizer.solve_manifold()
    
    # Sort: Primary Sort by DEPTH (Lifting), then B0 (Persistence)
    sorted_terms = sorted(persistence_map.items(), key=lambda x: (x[1]['depth'], x[1]['b0']), reverse=True)
    
    dump_path = "sandbox/v40_manifold_barcodes.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write("========================================================================================\n")
        f.write("   LOGIC MINER V.40 - STRICT ULTRAMETRIC BARCODES\n")
        f.write("========================================================================================\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Configuration: P-adic Vectors (5,7,11) | Ultrametric Distance | Lifting Depth\n")
        f.write("----------------------------------------------------------------------------------------\n")
        f.write(f"{'TERM'.ljust(30)} | {'DEPTH (LIFTING)'.ljust(15)} | {'B0 (PERSISTENCE)'.ljust(18)} | {'B1 (LOOPINESS)'.ljust(15)} | {'INTERPRETATION'}\n")
        f.write("----------------------------------------------------------------------------------------\n")
        
        for term, stats in sorted_terms:
            b0 = stats['b0']
            b1 = stats['b1']
            depth = stats['depth']
            
            interp = "NOISE"
            if depth > 50.0 and b0 > 0.05: 
                interp = "ROOT CONCEPT (HIGH DEPTH)"
            elif b1 > 0.5:
                interp = "SCAFFOLDING (LOOP)"
            elif b0 < 0.0001:
                interp = "ARTIFACT (TRIVIAL)"
                
            f.write(f"{term.ljust(30)} | {f'{depth:.2f}'.ljust(15)} | {f'{b0:.6f}'.ljust(18)} | {f'{b1:.4f}'.ljust(15)} | {interp}\n")
            
    print(f"   > Analysis Complete. Barcodes saved to: {dump_path}")
    print(f"   > Time Elapsed: {time.time() - start_time:.2f}s")
    
    # Debug
    print("\n   [DEBUG SHOT]")
    targets = ["Atom", "Access", "Combustion", "Chapter", "Introduction"]
    for t in targets:
        s = persistence_map.get(t, {'b0':0,'b1':0, 'depth':0})
        print(f"   {t}: Depth={s['depth']:.2f}, B0={s['b0']:.6f}, B1={s['b1']:.4f}")

if __name__ == "__main__":
    main()
