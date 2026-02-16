
import sys
import os
import json
import random

# Add project root to path
sys.path.append(os.getcwd())

from sandbox.synthetic.synthetic_generator import SyntheticTextGenerator
from sandbox.frontend_experiment.v60_lib.engine import V60Engine

def run_nightmare():
    print("=== Phase XXXIII: The Nightmare Gauntlet ===")
    
    # 1. Design The Nightmare Ontology
    ontology = {}
    
    # A. The Tower of Babel (Depth = 20)
    # Testing accumulation decay and deep lifting
    ontology["Root"] = {"initiates": ["Level_1"]}
    for i in range(1, 20):
        ontology[f"Level_{i}"] = {"generates": [f"Level_{i+1}"]}
    ontology["Level_20"] = {"fades-into": ["Void"]}
    
    # B. The Gordian Knot (Dense Clique)
    # Testing Phase Cancellation and Hub Logic
    clique_nodes = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
    for n in clique_nodes:
        ontology[n] = {}
        for other in clique_nodes:
            if n == other: continue
            # Randomize relation type (Phase stress)
            rel = random.choice(["links-to", "opposes", "causes", "correlates"])
            ontology[n][rel] = ontology[n].get(rel, []) + [other]
            
    # C. The Hydra (Extreme Polysemy)
    # "Scale" appears in Music, Fish, and Measurement contexts
    ontology["Music"] = {"uses": ["Scale", "Note"]}
    ontology["Fish"] = {"has": ["Scale", "Fin"]}
    ontology["Map"] = {"defined-by": ["Scale", "Legend"]}
    
    # D. The Ouroboros (Cycle)
    ontology["Creation"] = {"leads-to": ["Preservation"]}
    ontology["Preservation"] = {"leads-to": ["Destruction"]}
    ontology["Destruction"] = {"leads-to": ["Rebirth"]}
    ontology["Rebirth"] = {"leads-to": ["Creation"]}
    
    # E. The Void (Sink)
    ontology["Void"] = {"is": ["Nothing", "Empty", "Null"]}
    
    # 2. Generate Nightmare Text (30 Pages ~ 90k chars)
    # We boost the repetition of the Clique to scream "Structure"
    print("   > Generating 30 pages of Nightmare text...")
    gen = SyntheticTextGenerator(ontology)
    
    # To hit 30 pages, we need ~90000 chars.
    # Default generator is random. We might need to loop.
    # The generator has a length param.
    text = gen.generate_text(length_chars=100000)
    
    # 3. Run V.60 Engine
    print(f"   > Running V.60 Engine on {len(text)} chars...")
    engine = V60Engine()
    result = engine.process(text)
    inferred_metric = result['metric']
    
    # 4. Prepare Dump
    print("   > Exporting Nightmare Dump...")
    
    metric_export = {}
    # Convert GaussianInt/Complex to dict for JSON
    def serialize_complex(val):
        if hasattr(val, 'real') and hasattr(val, 'imag'):
            return {"r": int(val.real), "i": int(val.imag)} # Compact
        return val

    # Serialize Inferred Lattice
    inferred_export = {}
    for pair, p_vals in inferred_metric.items():
        k_str = f"{pair[0]}--{pair[1]}"
        inferred_export[k_str] = {str(p): serialize_complex(v) for p, v in p_vals.items()}

    # Serialize Ground Truth (Ontology)
    # Just output the adjacency list
    
    dump_data = {
        "metadata": {
            "description": "Phase XXXIII Nightmare Gauntlet",
            "text_length": len(text),
            "ontology_depth": 20,
            "features": ["Deep Chain", "Dense Clique", "Polysemy", "Cycle"]
        },
        "ground_truth_ontology": ontology,
        "generated_text": text,
        "inferred_lattice": inferred_export
    }
    
    with open("sandbox/nightmare_dump.json", "w") as f:
        json.dump(dump_data, f, indent=2)
        
    print("   > Nightmare Complete. Results in 'sandbox/nightmare_dump.json'.")

if __name__ == "__main__":
    run_nightmare()
