
import math
import sys
import os
import re
from collections import defaultdict, Counter
from pypdf import PdfReader

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
try:
    from logic_miner.core.text_featurizer import TextFeaturizer
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
    from logic_miner.core.text_featurizer import TextFeaturizer

class SpectralAnalyzer:
    def __init__(self):
        self.featurizer = TextFeaturizer()
        
    def build_directed_graph(self, text, entities):
        """
        Builds a directed graph based on order.
        A -> B if A precedes B in a small window (e.g., 5 words).
        """
        G = defaultdict(lambda: Counter()) # Out-neighbors
        In_G = defaultdict(lambda: Counter()) # In-neighbors
        
        words = re.findall(r'\b\w+\b', text)
        
        # Entity mapping (Multi-word handling simplified: just use unigrams or strict string match)
        # For robustness, we'll map entity strings to IDs or just use the raw strings if distinct
        # Let's use the provided entities list as the vocabulary of interest.
        vocab_set = set(entities)
        
        # Scan window
        window_size = 5
        for i in range(len(words)):
            current_word = words[i]
            # Check if current word starts an entity? (Simplified for single/double tokens)
            # To be efficient, just check if word is in vocab_set (partial match issue strictly)
            # Let's assume entities are mostly single words for this metric test, 
            # or we do a pass to tokenize entities.
            
            # Simple approach: Check unigrams against vocab
            if current_word in vocab_set:
                u = current_word
                # Look ahead
                for j in range(1, window_size + 1):
                    if i + j < len(words):
                        v = words[i+j]
                        if v in vocab_set:
                            G[u][v] += 1
                            In_G[v][u] += 1
                            
        return G, In_G

    def calculate_entropy(self, neighbors_counter):
        """
        H(x) = - Sum p(i) log2 p(i)
        """
        total = sum(neighbors_counter.values())
        if total == 0: return 0.0
        
        entropy = 0.0
        for count in neighbors_counter.values():
            p = count / total
            entropy -= p * math.log2(p)
            
        return entropy

    def calculate_clustering(self, term, G, In_G, entities_set):
        """
        Local Clustering Coeff (Undirected version usually).
        C = 2 * E_neighbors / k(k-1)
        We treat G as undirected for this metric.
        """
        neighbors = set()
        # Union of In and Out
        if term in G:
            neighbors.update(G[term].keys())
        if term in In_G:
            neighbors.update(In_G[term].keys())
            
        k = len(neighbors)
        if k < 2: return 0.0
        
        # Count edges between neighbors
        edges = 0
        neighbor_list = list(neighbors)
        for i in range(k):
            u = neighbor_list[i]
            for j in range(i+1, k):
                v = neighbor_list[j]
                
                # Check u-v connection (undirected)
                connected = False
                if u in G and v in G[u]: connected = True
                elif v in G and u in G[v]: connected = True
                
                if connected:
                    edges += 1
                    
        possible = k * (k - 1) / 2
        return edges / possible if possible > 0 else 0.0

    def calculate_asymmetry(self, term, G, In_G):
        """
        A = |In - Out| / (In + Out)
        """
        out_degree = sum(G[term].values()) if term in G else 0
        in_degree = sum(In_G[term].values()) if term in In_G else 0
        
        total = out_degree + in_degree
        if total == 0: return 0.0
        
        return abs(in_degree - out_degree) / total

    def run_analysis(self, pdf_path):
        print(f"--- [Protocol V.18: Tri-Axial Spectral Filter] ---")
        
        # 1. Ingestion
        reader = PdfReader(pdf_path)
        text = ""
        for i in range(min(50, len(reader.pages))): 
            text += reader.pages[i].extract_text() + "\n"
        
        # Extract top 1% terms (simulated by extract_entities top list)
        vocab = self.featurizer.extract_entities(text, limit=1000)
        vocab_set = set(vocab)
        
        # 2. Build Graph
        print("   > Building Directed Graph...")
        G, In_G = self.build_directed_graph(text, vocab)
        
        # 3. Compute Metrics for Targets
        # Targets: 'Rice' (Boilerplate), 'Table' (Scaffold), 'Matter' (Concept), 'See' (Operator)
        targets = ["Rice", "Table", "Matter", "Energy", "See", "Figure", "University", "Chapter"]
        
        print("\n   > [Spectral Classification Results (H, C, A)]")
        print("     Format: Vector = [Entropy, Clustering, Asymmetry]")
        
        for t in targets:
            # Find closest match in vocab
            matches = [w for w in vocab if t.lower() in w.lower()]
            if not matches:
                print(f"     - '{t}': Not found in Top 1000.")
                continue
                
            term = matches[0] # Take first match
            
            # Entropy (Use Out-Neighbors distribution)
            h = self.calculate_entropy(G[term])
            
            # Clustering
            c = self.calculate_clustering(term, G, In_G, vocab_set)
            
            # Asymmetry
            a = self.calculate_asymmetry(term, G, In_G)
            
            # Classification
            classification = "UNKNOWN"
            if h < 2.0: # Arbitrary low entropy
                classification = "JUNK / BOILERPLATE (Cluster 1)"
            elif c < 0.1 and a > 0.5:
                classification = "STRUCTURAL / OPERATOR (Cluster 2)"
            elif h > 2.0 and c > 0.2:
                classification = "ROOT CONCEPT (Cluster 3)"
            else:
                 classification = "AMBIGUOUS"
                 
            print(f"     - '{term}': [{h:.2f}, {c:.2f}, {a:.2f}] -> {classification}")

if __name__ == "__main__":
    base_path = "d:/Dropbox/logic-miner-engine/"
    pdf_path = "d:/Dropbox/logic-miner-engine/texts/Chemistry2e-WEB.pdf"
    if not os.path.exists(pdf_path):
        pdf_path = "d:/Dropbox/logic-miner-engine/sandbox/chemistry_subset.pdf"
        
    analyzer = SpectralAnalyzer()
    analyzer.run_analysis(pdf_path)
