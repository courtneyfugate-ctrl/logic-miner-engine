
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logic_miner.backend.interpreter import LogicInterpreter
from logic_miner.backend.analysis import FitAnalyzer

def main():
    print("--- [Verification: Backend Protocol V.23] ---")
    
    # Load the latest production result
    dump_json_path = "sandbox/v20_verification_result.json" 
    # v22 doesn't dump JSON by default, let's use the V20 result for the demo 
    # or create a temporary mock from the text dump logic.
    
    # Actually, I'll mock a small result for local verification of the math
    mock_poly = [-11392, 57159904, -166351965544, 311212893969370, -391922960664548032, 1]
    mock_coords = {
        'Matter': 25,
        'Mass': 125,
        'Atoms': 625,
        'Energy': 5  # Higher energy/Centrality
    }
    
    interpreter = LogicInterpreter(p=5)
    
    # 1. Sensitivity Probe
    sensitivity = interpreter.sensitivity_probe(mock_poly, mock_coords)
    for term, data in sensitivity.items():
        print(f"   > Concept: {term.ljust(10)} | Norm: {data['norm']:.4f} | Interpretation: {data['interpretation']}")
        
    # 2. Attractor Discovery
    axioms = interpreter.discover_axioms(mock_poly, mock_coords)
    print(f"\n   > Discovered Axioms (Roots/Fixed Points): {axioms}")
    
    # 3. Predictive Spline
    analyzer = FitAnalyzer(p=5)
    # Test poly on same coords (should be high fidelity)
    analysis = analyzer.predictive_spline_test(mock_poly, list(mock_coords.keys()), mock_coords)
    print(f"\n   > Predictive Status: {analysis['classification']} (Avg Error: {analysis['avg_error']:.4e})")

if __name__ == "__main__":
    main()
