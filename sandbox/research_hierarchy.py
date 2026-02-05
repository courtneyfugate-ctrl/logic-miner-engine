import re
import zlib
from collections import Counter

def get_entities(raw_text):
    # Reuse previous logic
    sentences = re.split(r'(?<=[.!?])\s+', raw_text)
    words = []
    ignore = {'The', 'A', 'An', 'This', 'It', 'They', 'These', 'Those', 'He', 'She', 'But', 'And', 'Or', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'From', 'By', 'As'}
    
    for s in sentences:
        tokens = s.split()
        for i, w in enumerate(tokens):
            clean = w.strip('.,;:"\'()[]')
            if not clean: continue
            if clean[0].isupper() and len(clean) > 2:
                if i == 0 and clean in ignore: continue
                words.append(clean)
                
    counts = Counter(words)
    candidates = [w for w, c in counts.most_common(50) if c > 1 and w not in ignore]
    return candidates, sentences

def method_entropy_direction(entities, descriptions):
    print("\n--- Method A: Asymmetric Entropy (Theorizer) ---")
    # Hypothesis: P(Child|Parent) vs P(Parent|Child)
    # Actually: If Child IS A Parent, then Child description contains Parent keywords.
    # So Parent -> Child might verify containment?
    # Simple Containment Score: How much of Parent's description is in Child's?
    
    # Let's try zlib skew.
    # score(A->B) implies A is child of B?
    # If A is child, A is "More Complex" (Parent + Delta).
    # So C(A) > C(B).
    # And NCD(A, B) is small.
    
    pairs = []
    for i in range(len(entities)):
        for j in range(len(entities)):
            if i == j: continue
            
            # Text Length Heuristic: General concepts (Parent) often have shorter/broader definitions?
            # Or the other way used in the specific text provided? 
            # In "Architecture of Life": 
            # "Domain Eukaryota" (Section I). "Homo Sapiens" (Section VIII).
            # The structure is ordered.
            pass

def method_predicate_logic(entities, sentences):
    print("\n--- Method B: Predicate Logic (Skeptic) ---")
    # Look for "X ... [relation] ... Y"
    
    relations = [
        r"belong\w* to the (?:Domain|Kingdom|Phylum|Class|Order|Family|Genus|Species) ([\w]+)",
        r"classified as ([\w]+)",
        r"subspecies of ([\w]+)",
        r"is a (?:member of)? ([\w]+)",
        r"known as ([\w]+)",
        r"falls? under ([\w]+)"
    ]
    
    graph = [] # (Child, Parent, Relation)
    
    entity_set = set(entities)
    
    for s in sentences:
        s_clean = s.strip()
        
        # Check for relations
        for pattern in relations:
            match = re.search(pattern, s_clean, re.IGNORECASE)
            if match:
                target = match.group(1)
                clean_target = target.strip('.,;:')
                
                # Who is the subject?
                # Heuristic: The entity mentioned EARLIEST in the sentence? 
                # Or the entity mentioned in the PREVIOUS sentence? (Context)
                
                # Naive Subject: First entity in sentence that is NOT the target
                subject = None
                for w in s_clean.split():
                    w_clean = w.strip('.,;:"\'')
                    if w_clean in entity_set and w_clean != clean_target:
                        subject = w_clean
                        break
                
                if subject and clean_target in entity_set:
                    graph.append((subject, clean_target, pattern))
                    print(f"[FOUND] {subject} -> {clean_target} (via '{match.group(0)}')")

def main():
    try:
        with open('sandbox/data/custom.txt', 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except:
        print("No data.")
        return

    entities, sentences = get_entities(raw_text)
    print(f"Entities: {entities}")
    
    # We focus on Method B (Predicate) as Theorizer's Entropy direction is notoriously hard for short text without huge corpus.
    # But let's verify if Method B finds the taxonomy.
    
    method_predicate_logic(entities, sentences)

if __name__ == "__main__":
    main()
