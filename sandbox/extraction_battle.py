
import re
from collections import Counter

# --- THE TEXT ---
TEXT = """
The Biological Architecture of the Class Mammalia
The biological world is organized through a series of nested innovations, where each level of the hierarchy incorporates the structural logic of its predecessors while adding specific constraints. At the foundation of our study is the Phylum Chordata, defined by the presence of a dorsal nerve cord. Within this phylum lies the Subphylum Vertebrata, where the nerve cord is encased in a protective spinal column. Every creature discussed hereafter is, fundamentally, a vertebrate chordate.

The Class Mammalia represents a major branching point in the vertebrate tree, defined by three "Parent" traits: the possession of mammary glands for nourishing young, the growth of hair or fur for thermoregulation, and the presence of three middle ear bones. These traits constitute the "Mammalian Signature," the root logic from which all diverse mammalian lineages diverge.

The Divergent Branches of Eutheria
The majority of modern mammals belong to the Infraclass Eutheria, or placental mammals. This branch is characterized by the innovation of the placenta, allowing for extended internal development.
The Proboscidea Branch: Represented by the Elephant, this lineage specializes in massive skeletal support and the development of the trunk, a fusion of the nose and upper lip.
The Chiroptera Branch: Represented by the Bat, this lineage demonstrates the extreme adaptation of mammalian limbs into wings, proving that the mammalian blueprint can achieve true flight while maintaining mammary glands and fur.
The Cetacea Branch: Represented by the Whale, this lineage shows the return to an aquatic environment. Despite their fish-like appearance, whales retain the core mammalian requirements of warm-bloodedness and nursing their young with milk.

The Taxonomic Exception: Monotremata
The hierarchy faces its most rigorous test with the Order Monotremata, specifically the Platypus. The platypus is a "Bridge Taxon" that sits at the earliest divergence of the mammalian tree. It serves as an exceptional case for a logic miner because it possesses the core "Parent" traits of Mammalia—it has fur and it produces milk—yet it retains the ancestral "Outlier" trait of laying leathery eggs, a characteristic typically reserved for reptiles and birds.
"""

# --- V1: CURRENT LOGIC (Capitalization Bias) ---
def extractor_v1(raw_text):
    sentences = re.split(r'(?<=[.!?])\s+', raw_text)
    words = []
    ignore = {'The', 'A', 'An', 'This', 'It', 'They', 'These', 'Those', 'He', 'She', 'But', 'And', 'Or', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'From', 'By', 'As', 'When', 'If'}
    
    for s in sentences:
        tokens = s.split()
        for i, w in enumerate(tokens):
            clean = w.strip('.,;:"\'()[]')
            if not clean: continue
            # Strict Capitalization
            if clean[0].isupper() and len(clean) > 2:
                if i == 0 and clean in ignore: continue
                words.append(clean)
                
    counts = Counter(words)
    return [w for w, c in counts.most_common(150) if c > 1 and w not in ignore]

# --- V2: PROPOSED LOGIC (Frequency + Expanded Stoplist) ---
def extractor_v2(raw_text):
    # Theoretical Improvements:
    # 1. Lowercase normalization (cat == Cat)
    # 2. Expanded Stoplist (Function words are noise for algebra)
    # 3. Frequency threshold > 1 (Algebra requires co-occurrence)
    
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'from', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself'
    }
    
    # Split by non-word chars
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', raw_text.lower())
    
    filtered = [t for t in tokens if t not in STOPWORDS]
    
    counts = Counter(filtered)
    
    # Return top entities with frequency > 1
    # Note: We return the strings.
    return [w for w, c in counts.most_common(150) if c > 1]

# --- THE BATTLE ---
def run_battle():
    print("--- [Theorizer] Analyzing Extraction Performance ---")
    
    res_v1 = extractor_v1(TEXT)
    res_v2 = extractor_v2(TEXT)
    
    print(f"\nV1 (Current) Count: {len(res_v1)}")
    print(f"V1 Entities: {sorted(res_v1)}")
    
    print(f"\nV2 (Proposed) Count: {len(res_v2)}")
    print(f"V2 Entities: {sorted(res_v2)}")
    
    # Critical Targets
    targets = {'mammalia', 'mammal', 'mammals', 'platypus', 'bat', 'whale', 'elephant', 'eggs', 'milk', 'fur', 'placenta'}
    
    print("\n--- Target Capture Analysis ---")
    
    def check_capture(res, label):
        found = set(w.lower() for w in res)
        hits = targets.intersection(found)
        misses = targets - found
        print(f"[{label}] Hits: {len(hits)}/{len(targets)}")
        print(f"   > Missed: {misses}")
        return len(hits)
        
    score_v1 = check_capture(res_v1, "V1")
    score_v2 = check_capture(res_v2, "V2")
    
    if score_v2 > score_v1:
        print("\n[Theorizer] Verdict: V2 is superior. Common nouns (traits) are critical for density.")
    else:
        print("\n[Theorizer] Verdict: V1 is robust enough.")

if __name__ == "__main__":
    run_battle()
