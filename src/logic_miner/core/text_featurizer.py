import re
from collections import Counter

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
        
    def extract_entities(self, raw_text):
        """
        Extracts Atomic Entities from text using Capitalized Phrase Heuristic.
        """
        phrase_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        raw_candidates = re.findall(phrase_pattern, raw_text)
        
        candidates = []
        for c in raw_candidates:
            parts = c.split()
            clean_parts = [p for p in parts if p.lower() not in self.STOPWORDS]
            if not clean_parts: continue
            
            entity = " ".join(clean_parts)
            if len(entity) > 2:
                candidates.append(entity)
                
        # Filter Frequency > 1 (or 1 if sparse)
        counts = Counter(candidates)
        # Return unique list
        return [w for w, c in counts.most_common(150) if c >= 1]

    def build_association_matrix(self, text, entities):
        """
        Constructs the Symmetric Adjacency Matrix from Co-occurrence blocks.
        Output: matrix (NxN float), raw_counts (dict)
        """
        # 1. Segment text
        segments = re.split(r'(?<=[.!?])\s+|,\s+|\s+and\s+|\s+but\s+', text) 
        
        # 2. Atomic Bonding (Replace "Blue Whale" -> "Blue_Whale")
        # To avoid partial matching issues
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
        counts = Counter() # Counts of bonded entities
        
        for s in merged_segments:
            tokens = [t.strip('.,;:"\'') for t in s.split()]
            found = []
            for t in tokens:
                if t in ent_set:
                     found.append(ent_map_idx[t])
                     counts[t] += 1
            
            # Symmetric Clique
            found = list(set(found)) 
            if len(found) > 1:
                for i in range(len(found)):
                    for j in range(i+1, len(found)):
                        idx1, idx2 = found[i], found[j]
                        pair = tuple(sorted((idx1, idx2)))
                        links[pair] = links.get(pair, 0) + 1

        # Build Matrix (Abstract Object)
        n = len(entities)
        matrix = [[0.0]*n for _ in range(n)]
        
        for (i,j), count in links.items():
            metric = 1.0 / (count + 1) 
            matrix[i][j] = metric
            matrix[j][i] = metric
            
        return matrix, counts
