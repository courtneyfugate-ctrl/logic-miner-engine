
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.core.serial_synthesis_v41 import SerialSynthesizerV41
from pypdf import PdfReader

def main():
    print("--- [Logic Miner V.41 - Adelic Restoration (The Global Concept)] ---")
    print("   > Principle: Hasse Principle (Local p-adic -> Global Integer)")
    print("   > Metric: Kolmogorov Complexity K(x) = |GlobalVal| / Modulus")
    
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    reader = PdfReader(pdf_path)
    
    pages_to_scan = 400
    
    start_time = time.time()
    
    print(f"   > Learning Point Cloud from first {pages_to_scan} pages...")
    
    # Use V.41 Synthesizer
    synthesizer = SerialSynthesizerV41(chunk_size=50, momentum=0.3, resolution=0.5)
    
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
    
    print("   > Solving Adelic Manifold (CRT Stitching)...")
    adelic_map = synthesizer.solve_adelic_manifold()
    
    # Sort by Complexity (Low to High)
    # Ideally: Concepts -> 0.0, Artifacts -> 0.5
    sorted_terms = sorted(adelic_map.items(), key=lambda x: x[1]['complexity'])
    
    dump_path = "sandbox/v41_adelic_integrity.txt"
    with open(dump_path, "w", encoding='utf-8') as f:
        f.write("========================================================================================\n")
        f.write("   LOGIC MINER V.41 - ADELIC INTEGRITY REPORT\n")
        f.write("========================================================================================\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Configuration: Global Integers (Mod 5*7*11=385 if degree 0) | Hasse Principle\n")
        f.write("----------------------------------------------------------------------------------------\n")
        f.write(f"{'TERM'.ljust(30)} | {'COMPLEXITY'.ljust(12)} | {'GLOBAL VAL'.ljust(12)} | {'MODULUS'.ljust(10)} | {'FIBER (5,7,11)'}\n")
        f.write("----------------------------------------------------------------------------------------\n")
        
        for term, stats in sorted_terms:
            comp = stats['complexity']
            g_val = stats['global_val']
            mod = stats['modulus']
            fiber = stats['fiber']
            
            f_str = f"({fiber.get(5,0)}, {fiber.get(7,0)}, {fiber.get(11,0)})"
            
            f.write(f"{term.ljust(30)} | {f'{comp:.4f}'.ljust(12)} | {str(g_val).ljust(12)} | {str(mod).ljust(10)} | {f_str}\n")
            
    print(f"   > Analysis Complete. Report saved to: {dump_path}")
    print(f"   > Time Elapsed: {time.time() - start_time:.2f}s")
    
    # Debug Shot
    print("\n   [DEBUG SHOT]")
    targets = ["Atom", "Access", "Combustion", "Chapter", "Introduction"]
    for t in targets:
        s = adelic_map.get(t, {'complexity': 1.0, 'global_val': -1, 'modulus': 1})
        print(f"   {t}: K={s['complexity']:.4f}, Val={s['global_val']}, Mod={s['modulus']}")

if __name__ == "__main__":
    main()
