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
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am',
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'animal', 'creature', 'beast', 'thing', 'something', 'anything', 'everything', 'nothing', 'someone', 'anyone', 'everyone', 'noone'
        }
        
        # V.31: Logical Operators (The "Arrows" of the manifold)
        self.LOGICAL_OPERATORS = {
            'of', 'for', 'in', 'is', 'are', 'was', 'were', 'be',
            'contains', 'measures', 'represents', 'defines', 'includes', 'produces',
            'yields', 'requires', 'causes', 'changes', 'increases', 'decreases'
        }
        
        self.VERB_BLOCKLIST = {
            'explain', 'describe', 'how', 'answer', 'calculate', 'determine', 'identify', 'use', 'using', 'state', 'give', 'finding', 'deriving',
            'predict', 'write', 'draw', 'complete', 'balancing', 'click', 'view', 'check', 'learning', 'performance',
            'visit', 'watch', 'video', 'select', 'perform', 'make', 'build', 'consider', 'suppose', 'assume', 'compare'
        }
        
        self.SCAFFOLDING_BLACKLIST = {
            'figure', 'table', 'example', 'problem', 'exercise', 'page', 'chapter', 'section',
            'that', 'which', 'who', 'whom', 'where', 'when', 'how', 'why',
            'this', 'these', 'those', 'there', 'here',
            'following', 'above', 'below', 'given', 'using', 'used', 'shows', 'shown'
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

    def extract_logical_triplets(self, text, entities):
        """
        V.31: Extracts directed triplets: (Subject) -> [Operator] -> (Object).
        """
        ent_set = set(e.replace(" ", "_").lower() for e in entities)
        ent_map = {e.replace(" ", "_").lower(): e for e in entities}
        
        # Segment and tokenize
        segments = re.split(r'(?<=[.!?])\s+|,\s+|\s+and\s+|\s+but\s+', text)
        triplets = []
        
        for s in segments:
            # Atomic Bonding
            temp_s = s.lower()
            sorted_ents = sorted(entities, key=len, reverse=True)
            for e in sorted_ents:
                if " " in e and e.lower() in temp_s:
                    bond = e.replace(" ", "_").lower()
                    temp_s = temp_s.replace(e.lower(), bond)
            
            tokens = re.findall(r'\b\w+\b', temp_s)
            
            for i in range(len(tokens) - 2):
                t1, op, t2 = tokens[i], tokens[i+1], tokens[i+2]
                if t1 in ent_set and op in self.LOGICAL_OPERATORS and t2 in ent_set:
                    subj = ent_map[t1]
                    obj = ent_map[t2]
                    triplets.append((subj, op, obj))
                    
        return triplets

    def build_association_matrix(self, text, entities):
        """
        Constructs the Symmetric Adjacency Matrix + Directed Operator Graph.
        """
        # 1. Triplet Extraction (Asymmetric)
        triplets = self.extract_logical_triplets(text, entities)
        
        # 2. Symmetric Clique for Matrix (Legacy fallback)
        segments = re.split(r'(?<=[.!?])\s+|,\s+|\s+and\s+|\s+but\s+', text) 
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
        G_directed = defaultdict(lambda: Counter())
        
        for subj, op, obj in triplets:
            # Protocol Fix: Direction is an ALGEBRAIC discovery, not a Grammatical one.
            # We treat all operators as undirected potential links for the Featurizer.
            # The Solver will minimize Energy to find the true arrow.
            u, v = subj, obj
                
            # Weighting (Keep significance weighting)
            weight = 2.0 if op in {'is', 'are', 'be', 'represents', 'defines', 'is_a'} else 1.0
            G_directed[u][v] += weight
            counts[subj.replace(" ","_")] += 1
            counts[obj.replace(" ","_")] += 1

        for s in merged_segments:
            tokens = [t.strip('.,;:"\'') for t in s.split()]
            found = []
            for t in tokens:
                if t in ent_set:
                     found.append(ent_map_idx[t])
                     if t not in counts: counts[t] += 1
            
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
            
        return matrix, counts, G_directed

    def calculate_spectral_metrics(self, entities, G_directed, counts):
        """
        Computes [H, C, A, F] from the directed operator graph.
        """
        import math
        metrics = {}
        max_f = max(counts.values()) if counts else 1
        
        # Build In_G for Asymmetry calculation
        In_G = defaultdict(lambda: Counter())
        for u in G_directed:
            for v, w in G_directed[u].items():
                In_G[v][u] += w

        for term in entities:
            # 1. Entropy (H)
            out_c = G_directed[term]
            tot = sum(out_c.values())
            h = 0.0
            if tot > 0:
                for c in out_c.values():
                    p = c / tot
                    h -= p * math.log2(p)
            
            # 2. Clustering (C)
            neighbors = set(G_directed[term].keys()) | set(In_G[term].keys())
            k = len(neighbors)
            c_val = 0.0
            if k >= 2:
                edges = 0
                nl = list(neighbors)
                for i in range(k):
                    u = nl[i]
                    for j in range(i+1, k):
                        v = nl[j]
                        if (u in G_directed and v in G_directed[u]) or (v in G_directed and u in G_directed[v]):
                            edges += 1
                c_val = edges / (k * (k-1) / 2)
            
            # 3. Asymmetry (A)
            in_d = sum(In_G[term].values())
            out_d = sum(G_directed[term].values())
            tot_d = in_d + out_d
            a = abs(in_d - out_d) / tot_d if tot_d > 0 else 0.0
            
            # 4. Relative Frequency (F)
            f = counts.get(term.replace(" ", "_"), 0) / max_f
            
            metrics[term] = (h, c_val, a, f, k)
        return metrics

    def classify_terms(self, metrics):
        """
        Protocol V.15: Relaxed Adelic Separation.
        Bifurcation between Archimedean (Isolated/Blacklisted) and Non-Archimedean (Semantic Core).
        """
        classification = {}
        for term, (h, c, a, f, k) in metrics.items():
            t_low = term.lower()
            if k == 0 or t_low in self.SCAFFOLDING_BLACKLIST or t_low in self.STOPWORDS:
                # Isolated or blacklisted: Archimedean scaffolding
                classification[term] = "ARCHIMEDEAN"
            else:
                # Participates in graph: Non-Archimedean semantic core
                classification[term] = "NON_ARCHIMEDEAN"
        return classification

    def extract_arithmetic_features(self, text, entities, primes=[2, 3, 5], strict_entities=False):
        """
        Protocol V.14: Extracts Arithmetic Invariants (Divisibility, Valuation, Ramification).
        Input: Raw Text + Entity List + Primes.
        Output: Dictionary containing Adelic Features for each prime.
        """
        import math
        
        # Helper for p-adic valuation
        def get_valuation(n, p):
            if n == 0: return 0 # Or inf? For text freq 0 means max valuation (inf) 
            # But here n is count. 
            # If count is 0, it doesn't exist.
            v = 0
            while n > 0 and n % p == 0:
                v += 1
                n //= p
            return v

        # 0. Structural Parsing
        try:
            from .parsers import StructuralParser
            if not hasattr(self, 'parser'):
                self.parser = StructuralParser()
            triads = self.parser.extract_triads(text)
        except ImportError:
            print("! StructuralParser not found. Falling back to internal triplet extraction.")
            triads = self.extract_logical_triplets(text, entities)

        # 1. Triad-Induced Entity Discovery (Ensures overlap)
        if not strict_entities:
            triad_terms = set()
            for s, r, o in triads:
                # Basic cleanup: Remove "the", "a" etc. if they are prefixes
                s_clean = re.sub(r'^(The|A|An)\s+', '', s, flags=re.I)
                o_clean = re.sub(r'^(The|A|An)\s+', '', o, flags=re.I)
                triad_terms.add(s_clean)
                triad_terms.add(o_clean)
            
            # Merge with existing entities (uniquely)
            combined_entities = list(entities)
            existing_norm = set(e.lower() for e in entities)
            for t in triad_terms:
                t_low = t.lower()
                if t_low not in existing_norm and len(t) > 3 and t_low not in self.STOPWORDS:
                    combined_entities.append(t)
            entities = combined_entities
        
        # Index Entities
        ent_to_idx = {e: i for i, e in enumerate(entities)}
        n = len(entities)
        
        print(f"     > Arithmetic Extraction: {len(triads)} triads, {n} entities.")
        
        # 2. Accumulate Counts & Order
        counts = defaultdict(int)        # N(A)
        co_counts = defaultdict(int)     # N(A, B) Symmetric
        directed_counts = defaultdict(int) # N(A->B) Asymmetric
        
        # Process Triads
        for s, r, o in triads:
            # Case-Insensitive Matching
            s_low = s.lower()
            o_low = o.lower()
            subjs = [e for e in entities if e.lower() in s_low or s_low in e.lower()]
            objs = [e for e in entities if e.lower() in o_low or o_low in e.lower()]
            subjs.sort(key=len, reverse=True)
            objs.sort(key=len, reverse=True)
            
            if not subjs or not objs: continue
            
            u_term = subjs[0]
            v_term = objs[0]
            
            if u_term == v_term: continue
            
            u = ent_to_idx[u_term]
            v = ent_to_idx[v_term]
            
            # u = ent_to_idx[u_term]
            # v = ent_to_idx[v_term]
            
            # Protocol V.14 Weighted Injection: 
            # We scale the count by the operating primes (effectively adding p to the valuation)
            # This ensures that a single high-quality triad is NOT rejected as noise.
            # Since we have multiple primes, we use a generic scale of 30 (divisible by 2, 3, 5).
            weight = 30 
            
            counts[u] += weight
            counts[v] += weight
            
            pair = tuple(sorted((u, v)))
            co_counts[pair] += weight
            directed_counts[(u, v)] += weight

        # 3. Compute Adelic Invariants (Multi-Prime)
        adelic_features = {}
        max_c = max(counts.values()) if counts else 1
        
        # A. Commutator (Prime Independent Integer)
        # K_AB = N(A->B) - N(B->A)
        commutator_matrix = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j: continue
                n_ij = directed_counts[(i, j)]
                n_ji = directed_counts[(j, i)]
                commutator_matrix[i][j] = float(n_ij - n_ji)

        # B. Prime-Specific Features
        for p in primes:
            # 1. Valuation Shells
            # v_p(A) = floor(log_p(max_count / count(A)))
            valuations = {}
            for idx, term in enumerate(entities):
                c = counts[idx]
                if c == 0:
                    valuations[term] = 99.0 
                else:
                    # Explicit Valuation Shell
                    ratio = max_c / c
                    if ratio < 1: ratio = 1
                    vals = math.floor(math.log(ratio, p))
                    valuations[term] = float(vals)

            # 2. Inclusion Matrix (GCD Divisibility)
            # I_AB = v_p(gcd(N_AB, N_B))
            # Represents structural alignment in prime field p
            inclusion_matrix = [[0.0]*n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    if i == j: 
                        inclusion_matrix[i][j] = 0.0 # Diagonal is 0 valuation (unit)? Or Max?
                        continue
                    
                    pair = tuple(sorted((i, j)))
                    n_ab = co_counts[pair]
                    n_b = counts[j] # B is column j
                    
                    # If no co-occurrence, no link
                    if n_ab == 0:
                        inclusion_matrix[i][j] = -1.0 # Indicator for No Link
                        continue

                    # gcd(N_AB, N_B)
                    common = math.gcd(n_ab, n_b)
                    
                    # v_p(common)
                    val = get_valuation(common, p)
                    inclusion_matrix[i][j] = float(val)

            adelic_features[p] = {
                'valuations': valuations,
                'inclusion_matrix': inclusion_matrix
                # Commutator can be analyzed mod p later if needed
            }

        return {
            'primes': adelic_features,
            'commutator_matrix': commutator_matrix,
            'entities': entities,
            'counts': dict(counts) # Useful for debugging
        }, entities

