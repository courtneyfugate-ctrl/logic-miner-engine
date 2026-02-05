import os
import json
import sys
from collections import defaultdict

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
    Implements P-adic Cone Fitting: Parent divides Child.
    """
    print("   > Generating Adelic Sheaf Visualization (p=3, 5, 7)...")
    primes = [3, 5, 7]
    ensure_dir(output_dir)
    
    # 1. Aggregate Global Map from Splines
    # We need a stable view. Let's take the LAST patch's map for visualization 
    # (or union? Union is better).
    global_sheaf = defaultdict(lambda: {})
    for s in data['splines']:
        for term, vec in s['map'].items():
            # vec is {3:c3, 5:c5...}
            for p_str, coord in vec.items():
                p = int(p_str)
                # Keep the last coordinate seen (evolution)
                global_sheaf[term][p] = coord
                
    # 2. Build 3 Trees
    for p in primes:
        dot_path = os.path.join(output_dir, f"sheaf_p{p}.dot")
        with open(dot_path, 'w', encoding='utf-8') as f:
            f.write(f'digraph Sheaf_P{p} {{\n')
            f.write(f'    label="Adelic Fiber p={p}";\n')
            f.write('    rankdir=BT;\n') # Bottom-Up (Roots at top usually, but usually P-adic is leaves at bottom)
            # Actually standard tree is Root Top.
            # Here "Root" is divisible.
            # L0 (Leaves) -> L1 -> L2 (Root)
            # So Edges Child -> Parent
            
            # Identify Levels
            levels = defaultdict(list)
            for term, vec in global_sheaf.items():
                if p not in vec: continue
                coord = vec[p]
                
                # Valuation
                v = 0
                temp = coord
                if temp != 0:
                    while temp % p == 0:
                        v += 1
                        temp //= p
                
                levels[v].append((term, coord))
                
            # Edges (Cone Fitting)
            # Pre-calculate to identify Active Nodes (Pruning Orphans)
            active_nodes = set()
            edges = []
            
            sorted_levels = sorted(levels.keys())
            for i in range(len(sorted_levels)-1):
                v_low = sorted_levels[i]
                v_high = sorted_levels[i+1] # Next available level (might skip)
                
                for term_child, c_child in levels[v_low]:
                    for term_parent, c_parent in levels[v_high]:
                        if c_parent == 0: continue
                        if c_parent % c_child == 0:
                            # Child divides Parent
                            active_nodes.add(term_child)
                            active_nodes.add(term_parent)
                            edges.append(f'    "{term_parent}" -> "{term_child}";')

            # Nodes (Only Active)
            for v, items in levels.items():
                # Filter items to only those in active_nodes
                active_items = [x for x in items if x[0] in active_nodes]
                if not active_items: continue
                
                f.write(f'    subgraph cluster_L{v} {{\n')
                f.write(f'        label="Valuation v_{p}={v}";\n')
                f.write('        rank=same;\n')
                for term, c in active_items:
                    tid = f"t_{v}_{hash(term) & 0xFFFFF}" 
                    label = f"{term}\\n{c}"
                    f.write(f'        "{term}" [label="{label}", shape=box];\n')
                f.write('    }\n')
            
            # Write Edges
            for e in edges:
                f.write(f'{e}\n')
                
            f.write('}\n')
            
    print("     > Generated Sheaf DOT files.")
    
    # Render PNGs
    if 'graphviz' in sys.modules:
        for p in primes:
            fname = f"sheaf_p{p}.dot"
            try:
                print(f"     > Attempting to render {fname}...")
                graphviz.Source.from_file(os.path.join(output_dir, fname)).render(format='png', cleanup=False)
            except Exception as e:
                print(f"       ! Failed to render {fname}: {e}")

def generate_combined_sheaf_viz(data, output_dir="sandbox/viz"):
    """
    Generates a UNIFIED Multigraph showing all 3 Prime Fibers simultaneously.
    Edges are colored by Prime: p=3 (Red), p=5 (Green), p=7 (Blue).
    This highlights 'Cross-Links' and 'Orphans'.
    """
    print("   > Generating Combined Adelic Multigraph...")
    ensure_dir(output_dir)
    dot_path = os.path.join(output_dir, "sheaf_combined.dot")
    
    # 1. Aggregate Global Map
    global_sheaf = defaultdict(lambda: {})
    for s in data['splines']:
        for term, vec in s['map'].items():
            for p_str, coord in vec.items():
                p = int(p_str)
                global_sheaf[term][p] = coord
    
    
    # 2. Identify Active Edges and Nodes (Pruning Orphans)
    active_nodes = set()
    edges = []
    
    colors = {3: "#ff0000", 5: "#00cc00", 7: "#0000ff"} # Red, Green, Blue
    primes = [3, 5, 7]
    for p in primes:
        color = colors.get(p, "black")
        
        # Style overrides for Structure (p=7)
        style_attr = ""
        if p == 7:
            style_attr = ', style="dotted", weight=0, constraint=false, color="#aaaaff"'
        else:
            style_attr = f', color="{color}", penwidth=1.5'

        # Reconstruct Levels for this p
        levels = defaultdict(list)
        for term, vec in global_sheaf.items():
            if p not in vec: continue
            coord = vec[p]
            v = 0
            temp = coord
            if temp != 0:
                while temp % p == 0: v += 1; temp //= p
            levels[v].append((term, coord))
            
        # Iterate Levels
        sorted_levels = sorted(levels.keys())
        for i in range(len(sorted_levels)-1):
            v_low = sorted_levels[i]
            v_high = sorted_levels[i+1]
            
            for term_c, c_c in levels[v_low]:
                for term_p, c_p in levels[v_high]:
                    if c_p == 0: continue
                    if c_p % c_c == 0: # Cone Fit
                        active_nodes.add(term_c)
                        active_nodes.add(term_p)
                        edges.append(f'    "{term_p}" -> "{term_c}" [label="p={p}" {style_attr}];')

    
    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write('digraph AdelicSheaf {\n')
        f.write('    label="Adelic Sheaf Multigraph (Pruned Orphans)";\n')
        f.write('    rankdir=BT;\n') # Bottom-Up
        f.write('    pack=true;\n') 
        f.write('    splines=true;\n') 
        f.write('    node [shape=box, style="filled,rounded", fillcolor="white", fontname="Arial"];\n')
        
        # Add ONLY active nodes
        for term in active_nodes:
            t_id = f'"{term}"'
            f.write(f'    {t_id} [label="{term}"];\n')
            
        # Add Edges
        for e in edges:
            f.write(f'{e}\n')
                            
        f.write('}\n')
    print("     > Generated Combined Sheaf DOT (Pruned).")
    
    if 'graphviz' in sys.modules:
        try:
            print("     > Attempting to render sheaf_combined.dot...")
            graphviz.Source.from_file(dot_path).render(format='png', cleanup=False)
        except Exception as e:
            print(f"       ! Failed to render combined sheaf: {e}")

def generate_sheaf_index(data, output_dir="sandbox/viz"):
    """
    Generates an Alphabetical Nested Index with Cross-References.
    Format:
    A
      Atom
        Physics (p=3): Parent of [Atomic Theory, Subatomic Particles]
        Chemistry (p=5): Child of [Matter]
        See also: Molecule (p=5 sibling)
    """
    print("   > Generating Sheaf Index...")
    ensure_dir(output_dir)
    
    # 1. Build Adjacency Map
    # adj[term][p] = {'parents': [], 'children': []}
    adj = defaultdict(lambda: defaultdict(lambda: {'parents': [], 'children': []}))
    global_sheaf = defaultdict(lambda: {})
    
    # Rebuild Global Map
    for s in data['splines']:
        for term, vec in s['map'].items():
            for p_str, coord in vec.items():
                p = int(p_str)
                global_sheaf[term][p] = coord
                
    # Build Tree Connections
    primes = [3, 5, 7]
    for p in primes:
        levels = defaultdict(list)
        for term, vec in global_sheaf.items():
            if p not in vec: continue
            coord = vec[p]
            v = 0
            temp = coord
            if temp != 0:
                while temp % p == 0: v += 1; temp //= p
            levels[v].append((term, coord))
            
        sorted_levels = sorted(levels.keys())
        for i in range(len(sorted_levels)-1):
            v_low = sorted_levels[i]
            v_high = sorted_levels[i+1] # Parent is higher valuation (divisible)
            
            for term_c, c_c in levels[v_low]:
                for term_p, c_p in levels[v_high]:
                    if c_p == 0: continue
                    if c_p % c_c == 0: # Parent Divides Child
                        adj[term_c][p]['parents'].append(term_p)
                        adj[term_p][p]['children'].append(term_c)

    # 2. Generate HTML
    sorted_terms = sorted(global_sheaf.keys())
    categories = defaultdict(list)
    for t in sorted_terms:
        first_char = t[0].upper()
        if not first_char.isalpha(): first_char = '#'
        categories[first_char].append(t)
        
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sheaf Manifold Index</title>
        <style>
            body { font-family: 'Georgia', serif; padding: 40px; max-width: 800px; margin: auto; background: #fdfdfd; color: #111; }
            h1 { text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; }
            .nav { text-align: center; margin-bottom: 30px; font-family: sans-serif; }
            .nav a { margin: 0 5px; text-decoration: none; color: #007bff; font-weight: bold; }
            .letter-section { margin-bottom: 40px; }
            .letter-header { font-size: 2em; border-bottom: 1px solid #ccc; margin-bottom: 15px; color: #555; }
            .term-block { margin-bottom: 15px; padding-left: 10px; }
            .term-title { font-weight: bold; font-size: 1.1em; color: #000; }
            .meta { font-size: 0.9em; color: #666; margin-left: 20px; font-style: italic; }
            .p-ref { margin-left: 20px; font-family: sans-serif; font-size: 0.85em; margin-top: 2px; }
            .badge { display: inline-block; padding: 1px 4px; border-radius: 3px; color: white; font-size: 0.7em; margin-right: 5px; }
            .bg-p3 { background-color: #d32f2f; }
            .bg-p5 { background-color: #388e3c; }
            .bg-p7 { background-color: #1976d2; }
            .see-also { margin-left: 20px; color: #444; font-size: 0.9em; margin-top: 2px; }
        </style>
    </head>
    <body>
        <h1>Sheaf Manifold Index</h1>
        <div class="nav">
    """
    
    # Nav
    for char in sorted(categories.keys()):
        html += f'<a href="#{char}">{char}</a> '
    html += '</div>'
    
    # Content
    for char in sorted(categories.keys()):
        html += f'<div id="{char}" class="letter-section"><div class="letter-header">{char}</div>'
        for term in categories[char]:
            connections = adj[term]
            if not connections: continue # Skip completely isolated terms? Or show them?
            
            html += f'<div class="term-block"><div class="term-title">{term}</div>'
            
            # Physics
            if 3 in connections:
                c = connections[3]
                rels = []
                if c['parents']: rels.append(f"Inside: {', '.join(c['parents'])}")
                if c['children']: rels.append(f"Contains: {', '.join(c['children'])}")
                if rels:
                    html += f'<div class="p-ref"><span class="badge bg-p3">PHY</span> {"; ".join(rels)}</div>'

            # Chemistry
            if 5 in connections:
                c = connections[5]
                rels = []
                if c['parents']: rels.append(f"Inside: {', '.join(c['parents'])}")
                if c['children']: rels.append(f"Contains: {', '.join(c['children'])}")
                if rels:
                    html += f'<div class="p-ref"><span class="badge bg-p5">CHEM</span> {"; ".join(rels)}</div>'

            # Structure
            if 7 in connections:
                c = connections[7]
                rels = []
                if c['parents']: rels.append(f"Inside: {', '.join(c['parents'])}")
                if c['children']: rels.append(f"Contains: {', '.join(c['children'])}")
                if rels:
                    html += f'<div class="p-ref"><span class="badge bg-p7">STR</span> {"; ".join(rels)}</div>'
            
            html += '</div>'
        html += '</div>'
        
    html += "</body></html>"
    
    with open(os.path.join(output_dir, "sheaf_index.html"), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"     > Saved Sheaf Index to sandbox/viz/sheaf_index.html")


def generate_dashboard_html(output_dir="sandbox/viz"):
    """
    Updates dashboard to use a Tabbed Interface for better width management.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Protocol V.13 Adelic Sheaf Dashboard</title>
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
            
            .legend { padding: 10px; background: #fff; border: 1px solid #ccc; margin-bottom: 20px; border-radius: 4px; display: inline-block;}
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
            <h1>Protocol V.13: Adelic Sheaf Manifold</h1>
            <a href="sheaf_index.html" target="_blank" class="header-link">📖 Open Index Book</a>
        </header>
        
        <div class="tabs">
            <div class="tab active" onclick="openTab('unified', this)">1. Unified Multigraph</div>
            <div class="tab" onclick="openTab('p3', this)">2. Physics (p=3)</div>
            <div class="tab" onclick="openTab('p5', this)">3. Chemistry (p=5)</div>
            <div class="tab" onclick="openTab('p7', this)">4. Structure (p=7)</div>
            <div class="tab" onclick="openTab('explorer', this)">5. Interactive 3D</div>
        </div>

        <div id="unified" class="content active">
            <div class="card">
                <h2>Unified Adelic Multigraph (Semantic Focus)</h2>
                <div class="legend">
                    <span style="color:red; font-weight:bold;">● p=3 (Physics)</span> &nbsp;&nbsp;
                    <span style="color:green; font-weight:bold;">● p=5 (Chemistry)</span> &nbsp;&nbsp;
                    <span style="color:blue; font-weight:bold; opacity: 0.5;">● p=7 (Structure - Faint)</span>
                </div>
                <p>Structure (Blue) edges are now relaxed (dotted) to allow Physics and Chemistry trees to define the layout.</p>
                <!-- COMBINED PLACEHOLDER -->
            </div>
        </div>

        <div id="p3" class="content">
            <div class="card">
                <h3 style="color:#cc0000">p=3 Fiber (Physics Hierarchy)</h3>
                <!-- P3 PLACEHOLDER -->
            </div>
        </div>

        <div id="p5" class="content">
            <div class="card">
                <h3 style="color:#009900">p=5 Fiber (Chemistry Hierarchy)</h3>
                <!-- P5 PLACEHOLDER -->
            </div>
        </div>

        <div id="p7" class="content">
            <div class="card">
                <h3 style="color:#0000cc">p=7 Fiber (Structural/Metadata Hierarchy)</h3>
                <!-- P7 PLACEHOLDER -->
            </div>
        </div>
        
        <div id="explorer" class="content">
            <div class="card">
                <h3>Interactive Explorer (Plotly)</h3>
                <p><a href="interactive_manifold.html" target="_blank">Open Full Screen</a></p>
                <iframe src="interactive_manifold.html" width="100%" height="800px" style="border:none;"></iframe>
            </div>
        </div>

    </body>
    </html>
    """
    
    def get_viz_content(filename):
        # Graphviz 'render' appends .png to the full filename (e.g. file.dot -> file.dot.png)
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

    html = html.replace("<!-- COMBINED PLACEHOLDER -->", get_viz_content("sheaf_combined.dot"))
    html = html.replace("<!-- P3 PLACEHOLDER -->", get_viz_content("sheaf_p3.dot"))
    html = html.replace("<!-- P5 PLACEHOLDER -->", get_viz_content("sheaf_p5.dot"))
    html = html.replace("<!-- P7 PLACEHOLDER -->", get_viz_content("sheaf_p7.dot"))
    
    with open(os.path.join(output_dir, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"   > Dashboard generated at {os.path.join(output_dir, 'index.html')}")

def main():
    print("--- [Protocol V.13 Visualization Suite] ---")
    data = load_sheaf_data()
    generate_sheaf_viz(data)
    generate_combined_sheaf_viz(data)
    generate_sheaf_index(data)
    generate_dashboard_html()

if __name__ == "__main__":
    main()
