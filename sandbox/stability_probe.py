
import sys
import os
import cmath
import math

# Add project root to path
sys.path.append(os.getcwd())

from sandbox.experimental_engine import ExperimentalEngine
from sandbox.synthetic.synthetic_generator import SyntheticTextGenerator

def run_stability_probe():
    print("=== Phase XXXV: Stability Probe ===")
    
    # 1. The Ouroboros Test (Cycle Holonomy)
    print("\n[Probe 1] Cycle Holonomy Check")
    ontology = {
        "Creation": {"leads-to": ["Preservation"]},
        "Preservation": {"leads-to": ["Destruction"]},
        "Destruction": {"leads-to": ["Rebirth"]},
        "Rebirth": {"leads-to": ["Creation"]}
    }
    
    # Generate focused text for the cycle
    gen = SyntheticTextGenerator(ontology)
    text = gen.generate_text(length_chars=10000) # Short burst
    
    # Run Experimental Engine
    print("   > Running Experimental Engine (Expanded Phase Map)...")
    engine = ExperimentalEngine()
    result = engine.process(text)
    metric = result['metric']
    
    # Calculate Holonomy
    # Path: Creation -> Preservation -> Destruction -> Rebirth -> Creation
    path = [("creation", "preservation"), ("preservation", "destruction"), 
            ("destruction", "rebirth"), ("rebirth", "creation")]
            
    total_phase = 1+0j
    
    print("   > Tracing Path Phases:")
    valid_path = True
    for u, v in path:
        # Find edge
        edge_data = None
        
        # Check u--v or v--u
        pair1 = tuple(sorted((u, v)))
        if pair1 in metric:
            # We need to know DIRECTION to assign phase correctly?
            # The tensor stores "u--v" with a complex value.
            # If relation is "leads to" (i), then A->B is i. B->A is -i?
            # V.60 Engine stores undirected pairs but with complex weights.
            # The weight represents the "Link Type".
            # For Holonomy, we multiply the link types.
            # If A->B is encoded as 'i', and we traverse A->B, we multiply by 'i'.
            
            # Extract strongest prime component
            vals = metric[pair1]
            # Just take the first one
            p = list(vals.keys())[0]
            val = vals[p]
            
            # Convert to complex
            if hasattr(val, 'real'):
                c = complex(val.real, val.imag)
            else:
                c = val
                
            print(f"     Edge {u}->{v}: {c}")
            
            # Normalize to Unit Phase for Angle
            if abs(c) > 0:
                phase = c / abs(c)
                print(f"       -> Unit Phase: {phase}")
                total_phase *= phase
            else:
                print("       -> Zero Magnitude (Broken)")
                valid_path = False
        else:
            print(f"     Edge {u}->{v}: MISSING")
            valid_path = False
            
    if valid_path:
        print(f"\n   > Total Holonomy (Path Product): {total_phase}")
        
        # Check against Identity (1)
        # Constructive Cycle: 1?
        # Causal Cycle: i * i * i * i = 1?
        # Yes, i^4 = 1.
        
        dist_1 = abs(total_phase - 1.0)
        print(f"   > Deviation from Identity (1.0): {dist_1:.4f}")
        
        if dist_1 < 0.1:
            print("   > SUCCESS: Cycle is Topologically Closed.")
        else:
            print("   > FAILURE: Cycle is Open or Twisted.")
            
    # 2. Persistence / Completeness
    print("\n[Probe 2] Phase Coverage")
    # Check if 'leads to' was actually mapped
    # We can infer this from the phases above.
    # If they are stuck at 1.0, it failed.
    pass

if __name__ == "__main__":
    run_stability_probe()
