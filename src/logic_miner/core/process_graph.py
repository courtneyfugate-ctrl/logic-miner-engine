
import re
from collections import defaultdict

class ProcessGraphExtractor:
    """
    Identifies Hyper-Edges (Reactions) in clinical/chemical text.
    Patterns: A + B -> C, A reacts with B to produce C.
    """
    def __init__(self):
        self.reaction_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:\+|and|plus)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:yields|produces|to\s+form|reacts\s+to\s+form|->)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:reacts\s+with)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:yields|produces|to\s+form|reacts\s+to\s+form|->)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]

    def extract_reactions(self, text, entities):
        """
        Parses text for reaction hyper-edges.
        Returns: list of (reactant1, reactant2, product)
        """
        reactions = []
        ent_set = set(e.lower() for e in entities)
        
        for p in self.reaction_patterns:
            matches = re.finditer(p, text, re.IGNORECASE)
            for m in matches:
                r1, r2, prod = m.groups()
                # Verify they are in our entity set
                if r1.lower() in ent_set and r2.lower() in ent_set and prod.lower() in ent_set:
                    # Normalize casing to the canonical entity names
                    r1_canon = entities[[e.lower() for e in entities].index(r1.lower())]
                    r2_canon = entities[[e.lower() for e in entities].index(r2.lower())]
                    prod_canon = entities[[e.lower() for e in entities].index(prod.lower())]
                    reactions.append((r1_canon, r2_canon, prod_canon))
        
        # Deduplicate
        return list(set(reactions))

    def build_reaction_network(self, reactions):
        """
        Builds a bipartite-like graph or hyper-graph representation.
        """
        network = defaultdict(list)
        for r1, r2, prod in reactions:
            network[(r1, r2)].append(prod)
        return network
