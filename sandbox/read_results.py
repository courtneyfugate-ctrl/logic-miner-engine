
import os
import sys

def main():
    try:
        path = 'sandbox/v12_experiment_output_final.txt'
        if not os.path.exists(path):
            print(f"File not found: {os.path.abspath(path)}")
            return
            
        # Check size
        print(f"File size: {os.path.getsize(path)} bytes")
            
        with open(path, 'r', encoding='utf-16') as f:
            lines = f.readlines()
            
        print("--- PARSED RESULTS ---")
        for i, line in enumerate(lines):
            line = line.strip()
            if "Polynomial P" in line:
                print(f"[Line {i}] {line}")
                # Print next line (Coeffs) truncated
                if i+1 < len(lines):
                    coeffs = lines[i+1].strip()
                    print(f"       {coeffs[:100]} ... {coeffs[-20:]}")
            elif "Terms=" in line:
                print(f"[Line {i}] {line}")
            elif "Branching Factor:" in line:
                print(f"[Line {i}] {line}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
