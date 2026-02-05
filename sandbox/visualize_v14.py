
import os
import json
import sys
from collections import defaultdict

# FIX: Add Graphviz to PATH if not present
graphviz_path = r"C:\Program Files (x86)\Graphviz\bin"
if os.path.exists(graphviz_path) and graphviz_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + graphviz_path


# Try imports
try:
    import matplotlib.pyplot as plt
    try:
        import numpy as np 
    except ImportError:
        pass
except Exception:
    pass

try:
    import plotly.graph_objects as go
except Exception:
    pass
    
try:
    import graphviz
except Exception:
    pass

def load_sheaf_data(filepath="sandbox/sheaf_data.json"):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_sheaf_viz(data, output_dir="sandbox/viz"):
    """
    Generates 3 separate DOT files for p=3, 5, 7.
    Implements P-adic Cone Fitting & Garbage Collection (Active Nodes Only).
    """
    print("   > Generating Adelic Sheaf Visualization (p=3, 5, 7)...")
    primes = [3, 5, 7]
    ensure_dir(output_dir)
    
    # 1. Aggregate Global Map from Splines
    global_sheaf = defaultdict(lambda: {})
    classification = data.get('classification', {})
    
    for s in data['splines']:
        for term, vec in s['map'].items():
            # Filter Strategy: Only visualize CONCEPTs
            # If classification exists, use it.
            if classification:
                ctype = classification.get(term, "CONCEPT")
                if ctype != "CONCEPT":
                    continue 

            # vec is {3:c3, 5:c5...}
            for p_str, coord in vec.items():
                p = int(p_str)
                global_sheaf[term][p] = coord
                
    # 2. Build 3 Trees
    for p in primes:
        dot_path = os.path.join(output_dir, f"sheaf_p{p}.dot")
        with open(dot_path, 'w', encoding='utf-8') as f:
            f.write(f'digraph Sheaf_P{p} {{\n')
            f.write(f'    label="Adelic Fiber p={p}";\n')
            f.write('    rankdir=BT;\n') 
            
            # Identify Levels
            levels = defaultdict(list)
            for term, vec in global_sheaf.items():
                if p not in vec: continue
                coord = vec[p]
                v = 0
                temp = coord
                if temp != 0:
                    while temp % p == 0: v += 1; temp //= p
                levels[v].append((term, coord))
                
            # Edges (Cone Fitting)
            # Garbage Collection: We only keep ACTIVE nodes (Degree > 0)
            active_nodes = set()
            edges = []
            
            sorted_levels = sorted(levels.keys())
            for i in range(len(sorted_levels)-1):
                v_low = sorted_levels[i]
                v_high = sorted_levels[i+1] 
                
                for term_child, c_child in levels[v_low]:
                    for term_parent, c_parent in levels[v_high]:
                        if c_parent == 0: continue
                        if c_parent % c_child == 0:
                            # Child divides Parent (Arrow Parent->Child)
                            active_nodes.add(term_child)
                            active_nodes.add(term_parent)
                            edges.append(f'    "{term_parent}" -> "{term_child}";')

            # Nodes (Only Active - Pruning Orphans)
            for v, items in levels.items():
                active_items = [x for x in items if x[0] in active_nodes]
                if not active_items: continue
                
                f.write(f'    subgraph cluster_L{v} {{\n')
                f.write(f'        label="Valuation v_{p}={v}";\n')
                f.write('        rank=same;\n')
                for term, c in active_items:
                    label = f"{term}\\n{c}"
                    f.write(f'        "{term}" [label="{label}", shape=box];\n')
                f.write('    }\n')
            
            for e in edges:
                f.write(f'{e}\n')
                
            f.write('}\n')
            
    print("     > Generated Sheaf DOT files.")
    
    if 'graphviz' in sys.modules:
        for p in primes:
            fname = f"sheaf_p{p}.dot"
            try:
                graphviz.Source.from_file(os.path.join(output_dir, fname)).render(format='png', cleanup=False)
            except Exception:
                pass


def generate_consensus_graph(data, output_dir="sandbox/viz"):
    """
    V.14 The Consensus Map
    Generates a graph containing ONLY edges that exist in >= 2 Prime Fibers.
    ("The Hard Logic")
    """
    print("   > Generating Consensus Graph (Intersection Map)...")
    ensure_dir(output_dir)
    dot_path = os.path.join(output_dir, "sheaf_consensus.dot")
    
    global_sheaf = defaultdict(lambda: {})
    classification = data.get('classification', {})

    for s in data['splines']:
        for term, vec in s['map'].items():
            if classification:
                ctype = classification.get(term, "CONCEPT")
                if ctype != "CONCEPT": continue
                
            for p_str, coord in vec.items():
                p = int(p_str)
                global_sheaf[term][p] = coord
                
    # Collect all edges from all primes
    # edge_counts[(parent, child)] = {3, 5}
    edge_counts = defaultdict(set)
    
    primes = [3, 5, 7]
    for p in primes:
        levels = defaultdict(list)
        for term, vec in global_sheaf.items():
            if p not in vec: continue
            coord = vec[p]
            v = 0
            if coord != 0:
                temp = coord
                while temp % p == 0: v += 1; temp //= p
            levels[v].append((term, coord))
            
        sorted_levels = sorted(levels.keys())
        for i in range(len(sorted_levels)-1):
            v_low = sorted_levels[i]
            v_high = sorted_levels[i+1]
            for term_child, c_child in levels[v_low]:
                for term_parent, c_parent in levels[v_high]:
                    if c_parent == 0: continue
                    if c_parent % c_child == 0:
                        edge_counts[(term_parent, term_child)].add(p)

    # Filter for Consensus
    consensus_edges = []
    active_nodes = set()
    
    for (parent, child), prime_set in edge_counts.items():
        if len(prime_set) >= 2: # Consensus Threshold
            # Color code based on which primes agree?
            # 3,5 = Physics+Chem = GOLD
            # 3,7 = Physics+Struct = PURPLE
            # 5,7 = Chem+Struct = TEAL
            # 3,5,7 = UNIVERSAL = BLACK BOLD
            
            color = "black"
            penwidth = 2.0
            p_str = ",".join(map(str, sorted(prime_set)))
            
            if 3 in prime_set and 5 in prime_set and 7 in prime_set:
                color = "black" # Universal
                penwidth = 3.0
            elif 3 in prime_set and 5 in prime_set:
                color = "#DAA520" # Goldenrod (Phys+Chem)
            elif 3 in prime_set and 7 in prime_set:
                color = "#800080" # Purple
            elif 5 in prime_set and 7 in prime_set:
                color = "#008080" # Teal
                
            active_nodes.add(parent)
            active_nodes.add(child)
            consensus_edges.append(f'    "{parent}" -> "{child}" [color="{color}", penwidth={penwidth}, label="p={p_str}"];')

    # Write Grap
    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write('digraph ConsensusSheaf {\n')
        f.write('    label="Adelic Consensus (Edges in >= 2 Fibers)";\n')
        f.write('    rankdir=BT;\n') 
        f.write('    node [shape=box, style="filled,rounded", fillcolor="#fff8e1", fontname="Arial"];\n')
        
        for term in active_nodes:
            f.write(f'    "{term}" [label="{term}"];\n')
            
        for e in consensus_edges:
            f.write(f'{e}\n')
            
        f.write('}\n')
        
    print("     > Generated Consensus DOT.")
    if 'graphviz' in sys.modules:
        try:
            # Use 'neato' for Consensus Graph (Concept Cloud layout)
            # 'dot' tends to flatten disconnected components into a wide line.
            graphviz.Source.from_file(dot_path, engine='neato').render(format='png', cleanup=False)
        except Exception:
            pass

def generate_combined_sheaf_viz(data, output_dir="sandbox/viz"):
    # (Same as V.13 Combined logic, keeping for comparison)
    print("   > Generating Combined Adelic Multigraph...")
    ensure_dir(output_dir)
    dot_path = os.path.join(output_dir, "sheaf_combined.dot")
    
    global_sheaf = defaultdict(lambda: {})
    classification = data.get('classification', {})

    for s in data['splines']:
        for term, vec in s['map'].items():
            if classification:
                ctype = classification.get(term, "CONCEPT")
                if ctype != "CONCEPT": continue
            for p_str, coord in vec.items():
                p = int(p_str)
                global_sheaf[term][p] = coord
    
    active_nodes = set()
    edges = []
    colors = {3: "#ff0000", 5: "#00cc00", 7: "#0000ff"} 
    primes = [3, 5, 7]
    
    for p in primes:
        color = colors.get(p, "black")
        style_attr = ""
        if p == 7: # De-clutter V.13
            style_attr = ', style="dotted", weight=0, constraint=false, color="#aaaaff"'
        else:
            style_attr = f', color="{color}", penwidth=1.5'

        levels = defaultdict(list)
        for term, vec in global_sheaf.items():
            if p not in vec: continue
            coord = vec[p]
            v = 0
            if coord != 0:
                temp = coord
                while temp % p == 0: v += 1; temp //= p
            levels[v].append((term, coord))
            
        sorted_levels = sorted(levels.keys())
        for i in range(len(sorted_levels)-1):
            v_low = sorted_levels[i]
            v_high = sorted_levels[i+1]
            for term_c, c_c in levels[v_low]:
                for term_p, c_p in levels[v_high]:
                    if c_p == 0: continue
                    if c_p % c_c == 0: 
                        active_nodes.add(term_c)
                        active_nodes.add(term_p)
                        edges.append(f'    "{term_p}" -> "{term_c}" [label="p={p}" {style_attr}];')

    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write('digraph AdelicSheaf {\n')
        f.write('    label="Adelic Sheaf Multigraph (Pruned Orphans)";\n')
        f.write('    rankdir=BT;\n') 
        f.write('    splines=true;\n') 
        f.write('    node [shape=box, style="filled,rounded", fillcolor="white", fontname="Arial"];\n')
        for term in active_nodes:
            f.write(f'    "{term}" [label="{term}"];\n')
        for e in edges:
            f.write(f'{e}\n')
        f.write('}\n')
    
    if 'graphviz' in sys.modules:
        try:
            graphviz.Source.from_file(dot_path).render(format='png', cleanup=False)
        except Exception:
            pass

def generate_sheaf_index(data, output_dir="sandbox/viz"):
    # (Same Index logic)
    print("   > Generating Sheaf Index...")
    ensure_dir(output_dir)
    adj = defaultdict(lambda: defaultdict(lambda: {'parents': [], 'children': []}))
    global_sheaf = defaultdict(lambda: {})
    for s in data['splines']:
        for term, vec in s['map'].items():
            for p_str, coord in vec.items():
                p = int(p_str)
                global_sheaf[term][p] = coord
                
    primes = [3, 5, 7]
    for p in primes:
        levels = defaultdict(list)
        for term, vec in global_sheaf.items():
            if p not in vec: continue
            coord = vec[p]
            v = 0
            if coord != 0:
                temp = coord
                while temp % p == 0: v += 1; temp //= p
            levels[v].append((term, coord))
            
        sorted_levels = sorted(levels.keys())
        for i in range(len(sorted_levels)-1):
            v_low = sorted_levels[i]
            v_high = sorted_levels[i+1]
            for term_c, c_c in levels[v_low]:
                for term_p, c_p in levels[v_high]:
                    if c_p == 0: continue
                    if c_p % c_c == 0: 
                        adj[term_c][p]['parents'].append(term_p)
                        adj[term_p][p]['children'].append(term_c)

    # HTML Generation (Abbreviated)
    sorted_terms = sorted(global_sheaf.keys())
    categories = defaultdict(list)
    for t in sorted_terms:
        first_char = t[0].upper()
        if not first_char.isalpha(): first_char = '#'
        categories[first_char].append(t)
        
    html = """<!DOCTYPE html><html><head><title>Sheaf Index</title>
        <style>body{font-family:'Georgia';padding:40px;max-width:800px;margin:auto;}</style>
    </head><body><h1>Sheaf Index</h1>"""
    
    for char in sorted(categories.keys()):
        html += f'<h2>{char}</h2>'
        for term in categories[char]:
            connections = adj[term]
            if not connections: continue 
            html += f'<div style="margin-bottom:10px"><b>{term}</b>'
            if 3 in connections: html += " [PHY]"
            if 5 in connections: html += " [CHEM]"
            if 7 in connections: html += " [STR]"
            html += "</div>"
    html += "</body></html>"
    
    with open(os.path.join(output_dir, "sheaf_index.html"), 'w', encoding='utf-8') as f:
        f.write(html)


def generate_dashboard_html(output_dir="sandbox/viz"):
    """
    Updates dashboard to use:
    1. Consensus Graph
    2. Combined Graph
    3. Individual Fibers
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol V.14 Adelic Sheaf Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; padding: 0; margin: 0; background: #f8f9fa; }
            header { background: #333; color: white; padding: 15px 20px; display:flex; justify-content: space-between; align-items: center;}
            h1 { margin: 0; font-size: 24px; }
            .header-link { color: #fff; text-decoration: none; border: 1px solid #fff; padding: 5px 15px; border-radius: 4px; font-size: 14px; }
            
            .tabs { display: flex; background: white; border-bottom: 1px solid #ddd; padding: 0 20px; }
            .tab { padding: 15px 25px; cursor: pointer; border-bottom: 3px solid transparent; font-weight: 500; color: #666; }
            .tab:hover { background: #f0f0f0; }
            .tab.active { border-bottom: 3px solid #007bff; color: #007bff; }
            
            .content { padding: 20px; display: none; }
            .content.active { display: block; }
            
            .card { 
                background: white; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                overflow-x: auto; 
            }
            img { max-width: none; height: auto; display: block; margin-top: 10px; }
        </style>
        <script>
            function openTab(tabName, elmnt) {
                var i, content, tablinks;
                content = document.getElementsByClassName("content");
                for (i = 0; i < content.length; i++) {
                    content[i].classList.remove("active");
                }
                tablinks = document.getElementsByClassName("tab");
                for (i = 0; i < tablinks.length; i++) {
                    tablinks[i].classList.remove("active");
                }
                document.getElementById(tabName).classList.add("active");
                elmnt.classList.add("active");
            }
        </script>
    </head>
    <body>
        <header>
            <h1>Protocol V.14: Adelic Consensus Engine</h1>
            <a href="sheaf_index.html" target="_blank" class="header-link">📖 Open Index Book</a>
        </header>
        
        <div class="tabs">
            <div class="tab active" onclick="openTab('consensus', this)">1. Consensus Graph</div>
            <div class="tab" onclick="openTab('unified', this)">2. Unified (Context)</div>
            <div class="tab" onclick="openTab('p3', this)">3. Physics (p=3)</div>
            <div class="tab" onclick="openTab('p5', this)">4. Chemistry (p=5)</div>
            <div class="tab" onclick="openTab('p7', this)">5. Structure (p=7)</div>
        </div>

        <div id="consensus" class="content active">
            <div class="card">
                <h2>Consensus Sheaf (The Hard Logic)</h2>
                <p>Edges confirmed by at least 2 independent fibers (e.g. valid in Physics AND Chemistry). This is the highest truth standard.</p>
                <!-- CONSENSUS PLACEHOLDER -->
            </div>
        </div>

        <div id="unified" class="content">
            <div class="card">
                <h2>Unified Adelic Multigraph (Context)</h2>
                <p>Shows all connections. Semantic focus (Physics/Chemistry), Structure faded.</p>
                <!-- COMBINED PLACEHOLDER -->
            </div>
        </div>

        <div id="p3" class="content">
            <div class="card">
                <h3 style="color:#cc0000">p=3 Fiber (Physics)</h3>
                <!-- P3 PLACEHOLDER -->
            </div>
        </div>

        <div id="p5" class="content">
            <div class="card">
                <h3 style="color:#009900">p=5 Fiber (Chemistry)</h3>
                <!-- P5 PLACEHOLDER -->
            </div>
        </div>

        <div id="p7" class="content">
            <div class="card">
                <h3 style="color:#0000cc">p=7 Fiber (Structure)</h3>
                <!-- P7 PLACEHOLDER -->
            </div>
        </div>
        
    </body>
    </html>
    """
    
    def get_viz_content(filename):
        png_name = filename + '.png'
        png_path = os.path.join(output_dir, png_name)
        dot_path = os.path.join(output_dir, filename)
        
        if os.path.exists(png_path):
            return f'<img src="{png_name}" style="max_width:100%; border: 1px solid #eee;" />'
        elif os.path.exists(dot_path):
            with open(dot_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f'<p><i>Binary rendering failed. DOT source:</i></p><pre>{content}</pre>'
        return f"<p>Not found: {png_name} or {filename}</p>"

    html = html.replace("<!-- CONSENSUS PLACEHOLDER -->", get_viz_content("sheaf_consensus.dot"))
    html = html.replace("<!-- COMBINED PLACEHOLDER -->", get_viz_content("sheaf_combined.dot"))
    html = html.replace("<!-- P3 PLACEHOLDER -->", get_viz_content("sheaf_p3.dot"))
    html = html.replace("<!-- P5 PLACEHOLDER -->", get_viz_content("sheaf_p5.dot"))
    html = html.replace("<!-- P7 PLACEHOLDER -->", get_viz_content("sheaf_p7.dot"))
    
    with open(os.path.join(output_dir, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"   > Dashboard generated at {os.path.join(output_dir, 'index.html')}")

def main():
    print("--- [Protocol V.14 Visualization Suite] ---")
    data = load_sheaf_data()
    generate_sheaf_viz(data)
    generate_combined_sheaf_viz(data)
    generate_consensus_graph(data)
    generate_sheaf_index(data)
    generate_dashboard_html()

if __name__ == "__main__":
    main()
