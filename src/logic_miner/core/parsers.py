import re
from collections import defaultdict

class StructuralParser:
    """
    Measurement Device for Structural Incidence.
    Extracts (Subject, Relation, Object) triads without semantic interpretation.
    
    Modes:
    1. spaCy Dependency Parse (Preferred)
    2. Regex Fallback (Robust approximation)
    """
    def __init__(self):
        self.use_spacy = False
        try:
            import spacy
            # Attempt to load a small model
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.use_spacy = True
            except OSError:
                print("! spaCy model 'en_core_web_sm' not found. Using Regex Fallback.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"! spaCy library error (Import/Pydantic): {e}. Using Regex Fallback.")

    def extract_triads(self, text):
        """
        Returns a list of (Subject, Relation, Object) tuples.
        """
        if self.use_spacy:
            return self._extract_spacy(text)
        else:
            return self._extract_regex(text)

    def _extract_spacy(self, text):
        start_char_idx = 0
        triads = []
        doc = self.nlp(text)
        
        for sent in doc.sents:
            # Simple heuristic for SVO in dependency tree
            # root verb -> nsubj (Subject)
            # root verb -> dobj/attr (Object)
            for token in sent:
                if token.pos_ == "VERB" or token.dep_ == "ROOT":
                    subj = None
                    obj = None
                    # Find subject and object children
                    for child in token.children:
                        if child.dep_ in ("nsubj", "nsubjpass"):
                            subj = self._get_compound(child)
                        if child.dep_ in ("dobj", "attr", "acomp", "pobj"):
                            obj = self._get_compound(child)
                    
                    if subj and obj:
                        # Normalize relation
                        relation = token.lemma_
                        triads.append((subj, relation, obj))
                        
        return triads

    def _get_compound(self, token):
        # Helper to get full noun phrase "The Red Cat" instead of "Cat"
        parts = []
        for child in token.children:
            if child.dep_ == "compound" or child.dep_ == "amod":
                parts.append(child.text)
        parts.append(token.text)
        return " ".join(parts)

    def _extract_regex(self, text):
        # Fallback: Sliding window or Sentence split?
        # Let's split by sentence first
        sentences = re.split(r'[.!?]', text)
        triads = []
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            # 1. Try explicit SVO pattern
            match = self.triplet_pattern.search(sent)
            if match:
                s, v, o = match.groups()
                # Clean up
                s = s.strip()
                o = o.strip()
                if len(s) > 1 and len(o) > 1:
                     triads.append((s, v, o))
            else:
                 # 2. Flexible heuristic: Split by logic words
                 # "A implies B" -> (A, implies, B)
                 tokens = sent.split()
                 # Basic scan for known operators (from Featurizer list)
                 # We can't access Featurizer here comfortably, so dry run
                 ops = {'implies', 'yields', 'forms', 'creates', 'is', 'are'}
                 
                 found_op = None
                 op_idx = -1
                 for i, t in enumerate(tokens):
                     if t.lower() in ops:
                         found_op = t
                         op_idx = i
                         break
                
                 if found_op and op_idx > 0 and op_idx < len(tokens)-1:
                     subj = " ".join(tokens[:op_idx])
                     obj = " ".join(tokens[op_idx+1:])
                     triads.append((subj, found_op, obj))
                     
        return triads
