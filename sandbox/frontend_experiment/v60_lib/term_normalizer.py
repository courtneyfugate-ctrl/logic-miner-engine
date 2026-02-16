
import re

class TermNormalizer:
    """
    Protocol V.60 Phase VII: Term Normalization.
    Merges plurals and singulars to reduce graph redundancy.
    """
    def __init__(self):
        # Basic English plural rules (heuristic but fast)
        self.rules = [
            (r'ies$', 'y'),
            (r's$', ''),
        ]
        # Exceptions that should NOT be stemmed
        self.exceptions = {
            'gas', 'mass', 'process', 'analysis', 'hypothesis', 'basis', 'radius',
            'this', 'is', 'was', 'has', 'does', 'yes', 'us', 'bus', 'glass',
            'class', 'grass', 'less', 'loss', 'pass', 'press', 'access',
            'address', 'ass', 'boss', 'brass', 'chess', 'cross', 'dress',
            'guess', 'kiss', 'mess', 'miss', 'moss', 'toss',
            'series', 'species'
        }
        
        # Pronouns to purge (Request: Phase IX)
        self.blocklist = {
            'it', 'that', 'this', 'which', 'there', 'he', 'she', 'they', 'them', 'his', 'her', 'their'
        }

    def normalize(self, term):
        """
        Normalize a term:
        1. Lowercase
        2. Strip punctuation
        3. Check blocklist
        4. Singularize
        """
        term = term.lower().strip()
        
        # Remove simple trailing punctuation
        term = re.sub(r'[.,;:)\]?!]+$', '', term)
        term = re.sub(r'^[(\[]+', '', term)
        
        if not term:
            return ""
            
        # Check blocklist
        if term in self.blocklist:
            return ""
            
        # Singularize
        if term in self.exceptions:
            return term
            
        # Apply rules
        # Only apply if length > 3 to avoid stemming short words like "is", "as"
        if len(term) > 3:
            for pattern, replacement in self.rules:
                if re.search(pattern, term):
                    # Check exceptions again after potential strip? 
                    # No, check before.
                    # Heuristic: If it ends in 'ss', it's likely an exception or non-plural
                    if term.endswith('ss'):
                        return term
                        
                    return re.sub(pattern, replacement, term)
        
        return term
