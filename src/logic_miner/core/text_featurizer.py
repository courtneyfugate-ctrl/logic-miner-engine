import re
from collections import Counter, defaultdict

class TextFeaturizer:
    """
    Siloed Pre-processor for Natural Language.
    Converts Raw Text -> Mathematical Objects (Adjacency Matrix, Entity Set).
    Strictly devoid of logic solving.
    """
    def __init__(self):
        self.STOPWORDS = {
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'from', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'like', 'just', 'swims', 'swim', 'swam', 'swum', 'fly', 'flies', 'flew', 'flown', 'run', 'runs', 'ran', 'walk', 'walks', 'walked', 'crawls', 'jump', 'jumps', 'jumped',
            'animal', 'creature', 'beast', 'thing', 'something', 'anything', 'everything', 'nothing', 'someone', 'anyone', 'everyone', 'noone'
        }
        
        # User/Theorizer Optimization: "Part-of-Speech" Filter (Heuristic Blocklist)
        # Prevents command verbs from polluting the Hilbert Map
        self.VERB_BLOCKLIST = {
            'explain', 'describe', 'how', 'answer', 'calculate', 'determine', 'identify', 'use', 'using', 'state', 'give', 'finding', 'deriving',
            'predict', 'write', 'draw', 'complete', 'balancing', 'click', 'view', 'check', 'learning', 'performance', 'expectations',
            'define', 'solution', 'example', 'exercises', 'exercise', 'answers', 'key', 'terms', 'summary', 'introduction', 'chapter', 'section',
            'visit', 'watch', 'video', 'select', 'perform', 'make', 'build', 'consider', 'suppose', 'assume', 'compare'
        }
        
    def extract_entities(self, raw_text, limit=600):
        """
        Extracts recurring terms (Capitalized Phrases + Frequent Lowercase Terms).
        """
        # 1. Capitalized Phrases (High Signal)
        phrase_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        cap_candidates = re.findall(phrase_pattern, raw_text)
        
        # 2. Frequent Lowercase Words (Semantic Core)
        # Filtered by length and stopwords later
        all_words = re.findall(r'\b[a-z]{4,}\b', raw_text.lower())
        
        candidates = []
        # Process Capitalized
        for c in cap_candidates:
            parts = c.split()
            clean_parts = [p for p in parts if p.lower() not in self.STOPWORDS and p.lower() not in self.VERB_BLOCKLIST]
            if clean_parts:
                candidates.append(" ".join(clean_parts))
        
        # Process Lowercase (Frequency based)
        word_counts = Counter(all_words)
        for word, count in word_counts.most_common(limit):
            if word not in self.STOPWORDS and word not in self.VERB_BLOCKLIST:
                # Titlize for canonical form? Sure.
                candidates.append(word.capitalize())
                
        # Final Top Candidates
        counts = Counter(candidates)
        return [w for w, c in counts.most_common(limit) if c >= 2]

    def build_association_matrix(self, text, entities):
        """
        Constructs the Symmetric Adjacency Matrix from Co-occurrence blocks.
        Output: matrix (NxN float), raw_counts (dict)
        """
        # 1. Segment text
        segments = re.split(r'(?<=[.!?])\s+|,\s+|\s+and\s+|\s+but\s+', text) 
        
        # 2. Atomic Bonding (Replace "Blue Whale" -> "Blue_Whale")
        sorted_ents = sorted(entities, key=len, reverse=True)
        merged_segments = []
        for s in segments:
            temp_s = s
            for e in sorted_ents:
                if " " in e and e in temp_s:
                    bond = e.replace(" ", "_")
                    temp_s = temp_s.replace(e, bond)
            merged_segments.append(temp_s)
        
        ent_set = set(e.replace(" ", "_") for e in entities)
        ent_map_idx = {e.replace(" ", "_"): i for i, e in enumerate(entities)}
        
        links = {}
        counts = Counter() 
        
        # Directed Graph for Spectral Metrics
        G = defaultdict(lambda: Counter())
        In_G = defaultdict(lambda: Counter())
        
        for s in merged_segments:
            tokens = [t.strip('.,;:"\'') for t in s.split()]
            found = []
            for t in tokens:
                if t in ent_set:
                     found.append(ent_map_idx[t])
                     counts[t] += 1
            
            # Update Directed Graph (Order matters for Asymmetry)
            for i in range(len(found)-1):
                u_idx, v_idx = found[i], found[i+1]
                u_name = entities[u_idx]
                v_name = entities[v_idx]
                G[u_name][v_name] += 1
                In_G[v_name][u_name] += 1

            # Symmetric Clique for Matrix
            found_unique = list(set(found)) 
            if len(found_unique) > 1:
                for i in range(len(found_unique)):
                    for j in range(i+1, len(found_unique)):
                        idx1, idx2 = found_unique[i], found_unique[j]
                        pair = tuple(sorted((idx1, idx2)))
                        links[pair] = links.get(pair, 0) + 1

        # Build Matrix
        n = len(entities)
        matrix = [[0.0]*n for _ in range(n)]
        for (i,j), count in links.items():
            metric = 1.0 / (count + 1) 
            matrix[i][j] = metric
            matrix[j][i] = metric
            
        return matrix, counts, (G, In_G)

    def calculate_spectral_metrics(self, entities, G, In_G, counts):
        """
        Computes [H, C, A, F] for each entity.
        H: Entropy, C: Clustering, A: Asymmetry, F: Frequency.
        """
        import math
        metrics = {}
        max_f = max(counts.values()) if counts else 1
        for term in entities:
            # 1. Entropy (H)
            out_c = G[term]
            tot = sum(out_c.values())
            h = 0.0
            if tot > 0:
                for c in out_c.values():
                    p = c / tot
                    h -= p * math.log2(p)
            
            # 2. Clustering (C)
            neighbors = set(G[term].keys()) | set(In_G[term].keys())
            k = len(neighbors)
            c_val = 0.0
            if k >= 2:
                edges = 0
                nl = list(neighbors)
                for i in range(k):
                    u = nl[i]
                    for j in range(i+1, k):
                        v = nl[j]
                        if (u in G and v in G[u]) or (v in G and u in G[v]):
                            edges += 1
                c_val = edges / (k * (k-1) / 2)
            
            # 3. Asymmetry (A)
            in_d = sum(In_G[term].values())
            out_d = sum(G[term].values())
            tot_d = in_d + out_d
            a = abs(in_d - out_d) / tot_d if tot_d > 0 else 0.0
            
            # 4. Relative Frequency (F)
            f = counts.get(term, 0) / max_f
            
            metrics[term] = (h, c_val, a, f)
        return metrics

    def classify_terms(self, metrics):
        """
        Algebraic Classification into Roots, Scaffolding, Junk.
        Refined V.20 Thresholds with Frequency Protection.
        """
        classification = {}
        for term, (h, c, a, f) in metrics.items():
            # 1. Frequency Protection: If very frequent, it's likely a CORE concept even if low entropy
            is_protected = f > 0.15 
            
            # 2. Junk: Near-zero entropy
            if h < 0.8 and not is_protected:
                classification[term] = "JUNK"
            # 3. Scaffolding: High Asymmetry
            elif a > 0.7:
                classification[term] = "SCAFFOLDING"
            # 4. Concept: Interconnected knowledge
            elif (h > 1.0 or is_protected) and c > 0.03:
                if h > 2.0 or is_protected:
                    classification[term] = "CONCEPT"
                else:
                    classification[term] = "SCAFFOLDING" if a > 0.4 else "CONCEPT"
            else:
                classification[term] = "JUNK"
        return classification

