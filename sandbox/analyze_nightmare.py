
import json
import sys
import math

def load_data(path):
    with open(path, "r") as f:
        return json.load(f)

def run_analysis():
    print("=== Nightmare Gauntlet Analysis ===")
    data = load_data("sandbox/nightmare_dump.json")
    
    ground_truth = data['ground_truth_ontology']
    inferred_raw = data['inferred_lattice']
    
    print(f"Ground Truth Nodes: {len(ground_truth)}")
    print(f"Inferred Edges: {len(inferred_raw)}")
    
    # Flatten Ground Truth to Edge List for comparison
    gt_edges = set()
    for source, relations in ground_truth.items():
        s = source.lower()
        for rel, targets in relations.items():
            r = rel.lower().replace("-", " ") # Normalize to space
            for t in targets:
                t_node = t.lower()
                gt_edges.add((s, r, t_node))
                
    print(f"Ground Truth Edges: {len(gt_edges)}")
    
    # Process Inferred Lattice
    # Format: "source--target": {"p": {"r": x, "i": y}}
    # We need to map back to (s, r, t) if possible, or just (s, t) connectivity.
    # The engine output is undirected in terms of keys usually, but let's check.
    
    inferred_adj = set()
    inferred_phases = {} # Store phase for stability check
    
    for key, val_dict in inferred_raw.items():
        # Key is "u--v"
        u, v = key.split("--")
        inferred_adj.add(tuple(sorted((u, v))))
        
        # Store primary phase (lowest prime/strongest link)
        # Just taking the first one for now as heuristic
        first_p = list(val_dict.keys())[0]
        c = val_dict[first_p]
        if isinstance(c, dict):
             phase = complex(c['r'], c['i'])
        else:
             phase = complex(c, 0) # Fallback
        inferred_phases[tuple(sorted((u, v)))] = phase

    # Metric 1: Connectivity Recall (Do GT edges exist in Inferred?)
    hits = 0
    misses = []
    
    for s, r, t in gt_edges:
        pair = tuple(sorted((s, t)))
        
        # Check for direct match
        if pair in inferred_adj:
            hits += 1
        else:
            # Check for split match (e.g. s--t_1 or s_1--t)
            # The engine splits polysemous nodes.
            found_split = False
            for inf_u, inf_v in inferred_adj:
                # Check coverage
                u_base = inf_u.split("_")[0]
                v_base = inf_v.split("_")[0]
                if tuple(sorted((u_base, v_base))) == pair:
                    found_split = True
                    break
            
            if found_split:
                hits += 1
            else:
                misses.append((s, r, t))
                
    recall = hits / len(gt_edges) if gt_edges else 0
    print(f"Connectivity Recall: {recall:.2%} ({hits}/{len(gt_edges)})")
    
    if misses:
        print("\nTop 5 Missed Connections:")
        for m in misses[:5]:
            print(f"  - {m}")
            
    # Metric 2: Topological Stability (Cycle Check)
    # Nightmare Cycle: Creation -> Preservation -> Destruction -> Rebirth -> Creation
    cycle_nodes = ["creation", "preservation", "destruction", "rebirth"]
    cycle_edges = [
        ("creation", "preservation"), 
        ("preservation", "destruction"), 
        ("destruction", "rebirth"), 
        ("rebirth", "creation")
    ]
    
    print("\nAdelic Cycle Check (The Ouroboros):")
    total_phase = 1+0j
    cycle_intact = True
    
    for u, v in cycle_edges:
        pair = tuple(sorted((u, v)))
        if pair in inferred_phases:
            ph = inferred_phases[pair]
            # If relation is "leads to", phase should be causal (1j)
            print(f"  Edge {u}-{v}: Phase {ph}")
            total_phase *= ph
        else:
            print(f"  Edge {u}-{v}: MISSING")
            cycle_intact = False
            
    if cycle_intact:
        print(f"  Total Holonomy (Residue): {total_phase}")
        # Ideal causal cycle of 4 steps: i * i * i * i = 1
        dist = abs(total_phase - 1)
        print(f"  Deviation from Unity: {dist:.4f}")
    
    # Metric 3: Depth Preservation (The Tower of Babel)
    # Check if Root is connected to Level_20
    # In a linear chain, transitive closure should exist? 
    # Or just check if the chain is unbroken.
    print("\nDepth Check (Tower of Babel):")
    chain_broken_at = None
    for i in range(1, 20):
        u = f"level_{i}"
        v = f"level_{i+1}"
        pair = tuple(sorted((u, v)))
        
        # Check splits
        found = False
        for inf_u, inf_v in inferred_adj:
             if inf_u.startswith(u) and inf_v.startswith(v):
                 found = True
             if inf_v.startswith(u) and inf_u.startswith(v):
                 found = True
        
        if not found:
            chain_broken_at = i
            break
            
    if chain_broken_at:
        print(f"  Chain broken at Level {chain_broken_at}")
    else:
        print("  Chain intact (Level 1 to 20)")

if __name__ == "__main__":
    run_analysis()
