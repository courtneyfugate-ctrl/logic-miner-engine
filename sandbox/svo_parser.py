import re

class SimpleSVOParser:
    """
    Deterministic SVO Parser for Logic Mining.
    Constraint: NO MACHINE LEARNING. Pure Regex/Grammar logic.
    
    Logic:
    1. Identify Verbs (is, are, has, have, lays, eating...)
    2. Split sentence around verb.
    3. Left = Subject, Right = Object.
    4. Filter by Entity List.
    """
    def __init__(self, entities):
        # We need the entities to know what to look for as S and O
        self.entities = set(e.lower() for e in entities)
        # Connector verbs that imply logical relation
        self.verbs = {
            'is', 'are', 'was', 'were', # Equivalence / Subsidy
            'has', 'have', 'had',       # Possession / Attribution
            'lays', 'eats', 'lives', 'inhabits' # Active relations
        }
        
    def extract_relations(self, text):
        """
        Returns list of (Subject, Verb, Object) tuples.
        """
        # Split by Sentence AND Clause boundaries
        # "It has fur and leads eggs" -> ["It has fur", "leads eggs"]
        # Note: "leads" needs a subject. If implicit, this parser might miss it.
        # But for "Fur lays eggs", splitting prevents "Fur" becoming subject.
        segments = re.split(r'(?<=[.!?])\s+|,\s+|\s+and\s+|\s+but\s+', text.lower())
        relations = []
        
        for s in segments:
            tokens = s.split()
            found = [] 
            
            for i, t in enumerate(tokens):
                clean = t.strip('.,;:"\'')
                if clean in self.entities:
                    found.append( (i, clean) )
                elif clean in self.verbs:
                    found.append( (i, '__VERB__:' + clean) )
                    
            # Scan E-V-E
            for i in range(len(found) - 2):
                s_token = found[i]
                v_token = found[i+1]
                o_token = found[i+2]
                
                if (not s_token[1].startswith('__VERB__') and
                    v_token[1].startswith('__VERB__') and
                    not o_token[1].startswith('__VERB__')):
                    
                    sub = s_token[1]
                    verb = v_token[1].split(':')[1]
                    obj = o_token[1]
                    
                    if (v_token[0] - s_token[0]) <= 3 and (o_token[0] - v_token[0]) <= 4:
                        relations.append( (sub, verb, obj) )
                        
        print(f"[SVO] Extracted {len(relations)} relations from {len(segments)} segments.")
        return relations

def run_comparison():
    print("--- V4 (Regex) vs V5 (SVO) Battle ---")
    
    text = """
    The Platypus is a mammal. It has fur and it lays eggs.
    The Bear is a mammal. The Bear has fur.
    The Eagle is a bird. The Eagle lays eggs.
    The Salmon is a fish. The Salmon swims.
    The Whale is a mammal. The Whale swims.
    """
    
    entities = ['platypus', 'mammal', 'fur', 'eggs', 'bear', 'eagle', 'bird', 'salmon', 'fish', 'whale', 'swims']
    
    # 1. V5 SVO Extraction
    parser = SimpleSVOParser(entities)
    rels = parser.extract_relations(text)
    print("\n[V5] SVO Relations Found:")
    for r in rels:
        print(f"  {r}")
        
    # Analysis of V5 Density
    # In V5, d(x,y) is low ONLY if linked by SVO.
    # d(Platypus, Mammal) -> Linked by 'is' -> Strong.
    # d(Platypus, Eggs) -> Linked by 'lays' -> Strong.
    # d(Platypus, Bear) -> No direct link. V4 might link them if in same sentence (not here).
    
    # Check "Swims" confusion
    # Salmon swims. Whale swims.
    # V5 should find (Salmon, swims, ?) -> 'swims' acts as verb? or Entity?
    # In our list, 'swims' is entity.
    # "Salmon swims" -> Entity Entity. No verb?
    # Parser needs to handle "Entity IS Entity". "Entity VERBS Entity".
    # "Salmon swims" has no object.
    
    # Theorizer: "This highlights the 'Intransitive Verb' issue. 
    # If using SVO, we miss 'Subject-Verb' predicates like 'Bird flies'.
    # Improvement: SV(O) parser."
    
if __name__ == "__main__":
    run_comparison()
