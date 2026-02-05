import zlib
import re
from collections import Counter
from src.logic_miner.core.ultrametric import UltrametricBuilder

def get_ncd(x, y):
    """
    Normalized Compression Distance.
    NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
    """
    if x == y: return 0.0
    
    x_bytes = x.encode('utf-8')
    y_bytes = y.encode('utf-8')
    xy_bytes = x_bytes + y_bytes
    
    cx = len(zlib.compress(x_bytes))
    cy = len(zlib.compress(y_bytes))
    cxy = len(zlib.compress(xy_bytes))
    
    ncd = (cxy - min(cx, cy)) / max(cx, cy)
    return max(0.0, min(1.0, ncd)) # Clamp to [0,1]

def canonicalize_structural_terms(text):
    """
    Maps natural language structural terms to algebraic tokens.
    Preserves geometric relationships that are usually lost during stopword removal.
    """
    # Order matters: Longest matches first
    mappings = [
        (r'\b(is not|are not|was not|were not|differs from|unlike)\b', '__NEQ__'),
        (r'\b(defined as|refers to|means|correspond to|matches)\b', '__EQ__'),
        (r'\b(is a|are a|was a|were a|is an|are an)\b', '__EQ__'), # "Is a" is usually identity/instantiation
        (r'\b(is|are|was|were)\b', '__EQ__'), # Fallback copula
        (r'\b(consists of|contains|includes|has a|have a)\b', '__INC__'),
        (r'\b(part of|belongs to|member of)\b', '__SUB__'),
    ]
    
    processed = text
    for pattern, token in mappings:
        processed = re.sub(pattern, token, processed, flags=re.IGNORECASE)
        
    return processed

def process_unformatted_text(raw_text):
    """
    Handles unformatted text streams.
    1. Identify Candidate Entities (Proper Nouns).
    2. Build Context Documents (Sentences containing the entity).
    3. Compute NCD.
    """
    print("Processing Unformatted Text...")
    
    # 0. Canonicalize Structure (The "Universal" step)
    # We do this BEFORE splitting so the structure is embedded in the raw geometry
    # But wait - we need original sentences for Entity Extraction to avoid messing up capitalization heuristics?
    # Actually, we can do it on the Context capture phase, OR we do it now.
    # Let's do it on the sentence chunks to be safe.
    
    # 1. Split Sentences (Primitive Regex)
    # Split on . ? ! followed by space
    sentences = re.split(r'(?<=[.!?])\s+', raw_text)
    
    # 2. Identify Entities (Heuristic: Capitalized words that are frequent)
    words = []
    # Stoplist for capitalization check (Start of sentence words usually capitalized)
    ignore = {'The', 'A', 'An', 'This', 'It', 'They', 'He', 'She', 'But', 'And', 'In', 'On', 'For', 'When', 'If', 'As'}
    
    # Also standard English stopwords (EXPANDED but preserving our Tokens)
    # Note: our tokens like __EQ__ are not in this list, so they survive.
    stop_words = {'the', 'a', 'an', 'of', 'and', 'in', 'to', 'with', 'for', 'it', 'has', 'that', 'which', 'be', 'by', 'on', 'at', 'have', 'from', 'as', 'can'}
    # Removed 'is', 'are' from stop_words because they are now tokens (or if missed, we want to see them?)
    # actually canonicalize handles them.

    for s in sentences:
        tokens = s.split()
        for i, w in enumerate(tokens):
            clean = w.strip('.,;:"\'()')
            if not clean: continue
            
            # Heuristic: Capitalized inside sentence -> Strong Entity
            # Capitalized at start -> Weak Entity (unless frequent globally)
            if clean[0].isupper() and len(clean) > 2:
                if i == 0 and clean in ignore:
                    continue
                words.append(clean)
                
    counts = Counter(words)
    # Filter: Top 150 entities
    # Note: NCD Matrix is O(N^2). 
    # N=20 -> 400 calcs (Instant).
    # N=100 -> 10,000 calcs (~2-5 sec).
    # N=500 -> 250,000 calcs (~2 min).
    
    # Strict ban on common stopwords
    strict_ignore = {'The', 'A', 'An', 'This', 'It', 'They', 'These', 'Those', 'He', 'She', 'But', 'And', 'Or', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'From', 'By'}
    
    candidates = [w for w, c in counts.most_common(150) if c > 1 and w not in strict_ignore]
    
    print(f"Auto-Detected Entities: {len(candidates)} (Top 150)")
    
    labels = []
    descriptions = []
    
    for entity in candidates:
        # Build Context Doc
        context = []
        for s in sentences:
            if entity in s: # substring match? dangerous. "Cat" in "Caterpillar".
                # Word boundary match needed?
                # Simple check: s contains entity
                
                # Apply Canonicalization HERE -> The Geometry Phase
                canon_s = canonicalize_structural_terms(s)
                context.append(canon_s)
        
        full_desc = " ".join(context)
        
        # Stop Words cleanup for NCD
        clean_words = []
        for w in full_desc.lower().replace('.', ' ').split():
            # Check if it matches our tokens (uppercase check for safety if lowercased above)
            # Actually we lowercased entire string. So our tokens became __eq__.
            # That's fine, as long as they aren't in stop_words.
            if w not in stop_words:
                clean_words.append(w)
                
        labels.append(entity)
        # Signal Boost: Repeat content to overcome zlib header overhead
        descriptions.append(" ".join(clean_words) * 10) 
        
    return labels, descriptions

def research_nlp_tree():
    print("### NLP TREE MINING VIA NCD ###")
    
    labels = []
    descriptions = []
    
    # Check for 'custom.txt' first
    try:
        with open('sandbox/data/custom.txt', 'r', encoding='utf-8') as f:
            print("Loading sandbox/data/custom.txt...")
            raw_text = f.read()
            labels, descriptions = process_unformatted_text(raw_text)
    except FileNotFoundError:
        print("Custom text not found, falling back to animals.txt...")
        # Fallback to animals.txt (Formatted)
        try:
            with open('sandbox/data/animals.txt', 'r', encoding='utf-8') as f:
                raw_text = f.read()
                # Use naive paragraph splitter for animals.txt as it was designed for it
                paragraphs = raw_text.split('\n\n')
                for p in paragraphs:
                    p = p.strip()
                    if not p: continue
                    first_sent = p.split('.')[0]
                    words_raw = first_sent.split()
                    name = "Unknown"
                    if words_raw[0].lower() == 'the':
                         name = words_raw[1]
                         if name.lower() in ['great', 'bald', 'house']: 
                             name = words_raw[1] + " " + words_raw[2]
                    else:
                         name = words_raw[0]
                    name = name.lower().replace(',', '')
                    labels.append(name)
                    
                    stop_words = {'the', 'a', 'an', 'is', 'of', 'and', 'in', 'to', 'with', 'for', 'it', 'has', 'that', 'are', 'which', 'be', 'by', 'on', 'at', 'have'}
                    clean_words = []
                    for w in p.lower().replace('.', ' ').replace(',', ' ').split():
                        if w not in stop_words:
                             clean_words.append(w)
                    descriptions.append(" ".join(clean_words) * 10)
        except FileNotFoundError:
            print("Error: No data found.")
            return

    if not labels:
        print("No entities found.")
        return
            
    print(f"Entities: {labels}")
    
    # 3. Compute Distance Matrix (NCD)
    n = len(labels)
    matrix = [[0.0] * n for _ in range(n)]
    
    print(f"\nComputing NCD Matrix for {n} entities ({n*n} comparisons)...")
    for i in range(n):
        if i % 10 == 0: print(f"  > Processing Row {i}/{n}...")
        for j in range(i+1, n):
            dist = get_ncd(descriptions[i], descriptions[j])
            matrix[i][j] = dist
            matrix[j][i] = dist
            
    # 4. Build Tree
    print("\nBuilding Ultrametric Tree...")
    builder = UltrametricBuilder()
    tree = builder.build_tree(labels, matrix)
    
    print("\n[RESULT TREE]")
    print(tree)

if __name__ == "__main__":
    research_nlp_tree()
