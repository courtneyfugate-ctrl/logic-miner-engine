
import spacy
from collections import defaultdict, Counter
import numpy as np
import re
from typing import List, Tuple, Dict, Optional

# Protocol V.60: Hensel-Voted P-adic Ontology Miner
# "We are not mining text. We are reconstructing the Galois geometry of a book."

class PrimeMapper:
    """
    Assigns a unique prime number to each relation type.
    This turns the text into a numerical field where divisibility implies hierarchy.
    """
    def __init__(self):
        # Pre-assign standard relations to low primes for stability
        self.registry = {
            'causes': 2,
            'implies': 2,
            'creates': 2,
            'is-a': 3,
            'type-of': 3,
            'has': 5,
            'contains': 5,
            'part-of': 5,
            'is': 7, # New entry
            'produces': 11, # Prime changed from 7
            'yields': 11, # Prime changed from 7
            'reacts': 13, # Prime changed from 11
            'bonds': 17,
            'has-property': 19,
            'in': 23,        # New: Containment
            'of': 29,        # New: Composition
            'from': 31,      # New: Origin
            'with': 37,      # New: Interaction
            'on': 41,        # New: Surface
            'to': 43         # New: Direction
        }
        self.next_prime = 47 
        self.primes = self._prime_generator()
        # Fast forward generator (2...43) -> 14 primes used
        for _ in range(14): next(self.primes) 
        
    def _prime_generator(self):
        D = {}
        q = 2
        while True:
            if q not in D:
                yield q
                D[q * q] = [q]
            else:
                for p in D[q]:
                    D.setdefault(p + q, []).append(p)
                del D[q]
            q += 1
            
    def get_prime(self, relation: str) -> int:
        rel_norm = relation.lower().strip()
        if rel_norm in self.registry:
            return self.registry[rel_norm]
        
        # Assign new prime
        p = next(self.primes)
        self.registry[rel_norm] = p
        return p

class TriadParser:
    """
    Phase I: Passive Measurement.
    Extracts (A, R, B) triads from text. 
    NO embeddings. NO semantic similarity. Pure structural extraction.
    """
    def __init__(self, model='en_core_web_sm'):
        try:
            from sandbox.v60.spacy_helper import load_spacy_safe
        except ImportError:
            from spacy_helper import load_spacy_safe # Fallback for local run
        
        try:
            from sandbox.v60.term_normalizer import TermNormalizer
        except ImportError:
            from term_normalizer import TermNormalizer
            
        self.nlp = load_spacy_safe(model)
        self.normalizer = TermNormalizer()

    def parse(self, text: str) -> List[Tuple[str, str, str]]:
        doc = self.nlp(text)
        triads = []
        
        for sent in doc.sents:
            # 1. Subject-Verb-Object/Attribute
            for token in sent:
                if token.pos_ == "VERB" or token.dep_ == "ROOT":
                    subj = None
                    objs = []
                    
                    for child in token.children:
                        if "subj" in child.dep_:
                            subj = " ".join([t.text for t in child.subtree])
                        if "obj" in child.dep_ or child.dep_ == "attr" or child.dep_ == "acomp":
                            objs.append(" ".join([t.text for t in child.subtree]))
                        if child.dep_ == "prep":
                            # Capture prepositional objects: "bonds WITH oxygen"
                            for grandchild in child.children:
                                if grandchild.dep_ == "pobj":
                                    # Append tuple (obj_text, prep_text)
                                    objs.append((" ".join([t.text for t in grandchild.subtree]), child.text))
                                    
                    if subj:
                        # Normalize and add
                        # Handle direct objects (no prep)
                        # We need to know which objs had preps.
                        # Retrofit 'objs' list to always be tuples?
                        # Or process mixed list.
                        # Let's fix the list above.
                        pass

            # Re-collect logic to be cleaner
            # 1. Subject-Verb-Object/Attribute
            for token in sent:
                if token.pos_ == "VERB" or token.dep_ == "ROOT":
                    subj = None
                    # List of (obj_text, prep_text or None)
                    collected_objs = []
                    
                    for child in token.children:
                        if "subj" in child.dep_:
                            subj = " ".join([t.text for t in child.subtree])
                        if "obj" in child.dep_ or child.dep_ == "attr" or child.dep_ == "acomp":
                            collected_objs.append((" ".join([t.text for t in child.subtree]), None))
                        if child.dep_ == "prep":
                            for grandchild in child.children:
                                if grandchild.dep_ == "pobj":
                                    obj_text = " ".join([t.text for t in grandchild.subtree])
                                    prep_text = child.text
                                    collected_objs.append((obj_text, prep_text))
                                    
                    if subj:
                        base_relation = token.lemma_
                        for obj_text, prep in collected_objs:
                            final_rel = base_relation
                            if prep:
                                final_rel = f"{base_relation} {prep}"
                            
                            s_n = self.normalizer.normalize(self._clean(subj))
                            o_n = self.normalizer.normalize(self._clean(obj_text))
                            r_n = self.normalizer.normalize(final_rel)
                            
                            if s_n and o_n and r_n:
                                triads.append((s_n, r_n, o_n))
            
            # 2. Adjective-Noun (Attributional Logic)
            # "The stable atom" -> (atom, has-property, stable)
            for token in sent:
                if token.dep_ == "amod" and token.head.pos_ in ["NOUN", "PROPN"]:
                    adj = token.text
                    noun = token.head.text
                    
                    s_n = self.normalizer.normalize(self._clean(noun))
                    o_n = self.normalizer.normalize(self._clean(adj))
                    r_n = "has-property"
                    if s_n and o_n:
                        triads.append((s_n, r_n, o_n))
                        
                        
        return triads

    def _get_phase(self, relation: str) -> complex:
        """
        Phase XXIX: Gaussian Logic Phases.
        Assigns geometric rotation based on logical operator.
        """
        r = relation.lower().strip()
        if r in ['cause', 'causes', 'lead', 'trigger', 'produce', 'yield']:
            return 1j # Rotation by 90 degrees (Causality)
        if r in ['is-not', 'differ', 'distinct', 'unlike']:
            return -1 # Rotation by 180 degrees (Negation)
        if r in ['correlate', 'associate', 'link']:
            return 1+1j # 45 degrees (Correlation/Entanglement)
        # Phase XXXV: Extended Causal Map
        if r in ['lead to', 'leads to', 'result in', 'results in']:
            return 1j 
        return 1 # Identity (Standard connection)

    def parse_with_phase(self, text: str):
        # Wrapper to return (s, r, o, phase)
        # Re-using parse logic but augmenting it
        simple_triads = self.parse(text)
        phased_triads = []
        for s, r, o in simple_triads:
            ph = self._get_phase(r)
            phased_triads.append((s, r, o, ph))
        return phased_triads

    def _clean(self, term: str) -> str:
        # Remove determiners and lower case
        term = re.sub(r'^(a|an|the)\s+', '', term.lower())
        return term.strip()

class ValuationTensorBuilder:
    """
    Builds the valuation tensor X_{A,B}.
    For each pair (A,B), V_p(X_{A,B}) = exponent of prime p in the relation product.
    """
    def __init__(self, prime_mapper: PrimeMapper):
        self.mapper = prime_mapper
        try:
            from sandbox.frontend_experiment.v60_lib.gaussian import GaussianInt
        except ImportError:
            from gaussian import GaussianInt
            
        self.counts = defaultdict(lambda: defaultdict(GaussianInt)) # counts[pairs][relation] = GaussianInt
        self.GaussianInt = GaussianInt
        self.terms = set()
        
    def ingests(self, triads: List[Tuple]):
        for item in triads:
            # Handle both 3-tuple (legacy) and 4-tuple (complex)
            if len(item) == 4:
                s, r, o, phase = item
                # Ensure phase is GaussianInt (Robust Duck Typing)
                if isinstance(phase, self.GaussianInt):
                    pass
                elif isinstance(phase, complex):
                    phase = self.GaussianInt(int(phase.real), int(phase.imag))
                elif hasattr(phase, 'real') and hasattr(phase, 'imag'):
                    # Alien GaussianInt (from different import path)
                    phase = self.GaussianInt(phase.real, phase.imag)
                else:
                    phase = self.GaussianInt(int(phase), 0)
            else:
                s, r, o = item
                phase = self.GaussianInt(1, 0)
                
            self.terms.add(s)
            self.terms.add(o)
            
            p = self.mapper.get_prime(r)
            
            # Standard Direct Link (S, O)
            pair = tuple(sorted((s, o)))
            self.counts[pair][p] += phase
            
            # Generalized Reification (S -> R -> O)
            self.terms.add(r)
            pair_sr = tuple(sorted((s, r)))
            self.counts[pair_sr][p] += phase 
            
            pair_ro = tuple(sorted((r, o)))
            self.counts[pair_ro][p] += phase
            
    def ingest_seeds(self, integer_lists: List[List[int]]):
        """
        [Protocol V3.0] Direct P-adic Injection.
        Takes V2.3 recursive integer lists and seeds the valuation tensor.
        list = [Root, [Rel, Child], ...]
        v_p(Root-Child) is determined by depth.
        """
        def traverse(node, root_term, depth=1):
            if not isinstance(node, list): return
            if not node: return
            
            # Node structure: [Term, [Rel, Child]...] OR [Term]
            # Actually V2.3 structure is: [Head, [Rel, Child, [Rel, Grandchild...]]]
            # Wait, the integer list example is [24541, 56181] for "pure oxygen".
            # It's a flat interaction list in some debug output, but the encoder produces tree.
            # Let's assume standard recursive list: [Head, [Rel, Child]...]
            
            head_id = node[0]
            # We need to map integer ID back to string? 
            # Or does run_lattice pass strings?
            # run_lattice adapter handles the JSON which has STRINGS in structure,
            # but 'p_adic_integers' in JSON are INTEGERS.
            # The adapter should probably parse the 'structure' field which is easier,
            # OR we assume the input here is the 'p_adic_integers' list.
            # If input is integers, we need a map. 
            # BUT: The goal is to use the *structure* of the list.
            
            # Let's assume the adapter passes [HeadStr, [RelStr, ChildStr]] for ease,
            # OR we stick to the plan: "seeds with Integer Lists". 
            # If we use integers, we can't map to 'is' or 'atom' without a lookup.
            # The V2.3 dump has "structure" which is explicit.
            # Maybe we just use "structure" to derive the seeds, but use the logic of "Depth".
            
            # Actually, `ingest_seeds` implies we trust the list structure.
            # Let's define it to accept [Head, [Rel, Child], ...] where Head/Child are STRINGS.
            
            head = node[0]
            
            for i in range(1, len(node)):
                sub = node[i]
                if not sub or len(sub) < 2: continue
                
                rel = sub[0]
                child_node = sub[1]
                child = child_node[0] if isinstance(child_node, list) else child_node
                
                # Injection: Valuation = Depth
                # We want v_p(Head, Child) >= Depth.
                # In our tensor, counts[pair][p] ~ Strength.
                # Higher strength -> Closer -> Lower p-adic norm?
                # No, in V.60: v_p(X) is the EXPONENT. 
                # High Exponent = High Depth = Closer.
                # So we add 'Depth' to the count.
                
                # Phase XXIX: Gaussian Accumulation
                # For seeds, we assume a default phase of 1 (real, no rotation)
                # The 'depth' acts as the magnitude.
                
                p = self.mapper.get_prime(rel)
                
                # Symmetrize
                pair = tuple(sorted((head, child)))
                
                # Current value in the tensor
                current_val = self.counts[pair].get(p, self.GaussianInt(0, 0))
                
                # Add the depth as a real component to the GaussianInt
                # We assume seeds are "real" contributions unless specified otherwise
                to_add = self.GaussianInt(depth * 10, 0) # Strong seed
                
                self.counts[pair][p] = current_val + to_add
                
                # Recurse
                if isinstance(child_node, list):
                    traverse(child_node, root_term, depth + 1)
        
        for tree in integer_lists:
            traverse(tree, tree[0])
            
    def build_metric_space(self) -> Dict:
        return dict(self.counts)

class GlobalAdelicIntegrator:
    """
    Glue Layer: Accumulates local charts into a global atlas.
    Uses Max-Accumulation (Sheaf property) to preserve hierarchical strength.
    """
    def __init__(self):
        self.global_tensor = defaultdict(dict)
        
    def integrate(self, local_tensor: Dict):
        for pair, p_vals in local_tensor.items():
            for p, v in p_vals.items():
                # Phase XXVIII: Complex accumulation
                # Summation allows phase cancellation (1 + -1 = 0)
                current = self.global_tensor[pair].get(p, 0)
                self.global_tensor[pair][p] = current + v

class HenselVoter:
    """
    Phase II: The Filter.
    Replaces RANSAC with p-adic model selection.
    Partitions the congruence graph A ~ B (mod p^k).
    """
    def __init__(self, min_support: int = 2):
        self.min_support = min_support
        
    def vote(self, metric_space: Dict) -> Dict:
        """
        Returns the dominant prime valuations for each pair.
        """
        # 1. Histogram of Primes
        # We look for primes that appear consistently across many pairs?
        # No, we look for primes that define a deep hierarchy.
        
        # Simple voting for prototype:
        # Keep valuations that have high magnitude (k >= 1)
        # and appear in structured patterns?
        
        # Actually, Hensel Voting means we accept a valuation v_p(A,B) = k
        # if it is supported by the neighborhood.
        # For prototype, we just trust the Sheaf-Stabilized Tensor.
        # The "Voting" happened via the Rigid Lock.
        return metric_space


class HenselLifterV60:
    """
    Phase IIb: Coordinate Reconstruction.
    Solves v_p(x_A - x_B) approx v_p(X_{A,B})
    """
    def __init__(self, p_base: int = 3):
        self.p = p_base
        
    def lift(self, metric_space: Dict) -> Dict:
        """
        Recursive lifting of coordinates (Phase XIII: Mahler & Lipschitz).
        Updated for Phase XXVIII: Component-Wise Complex Lifting.
        """
        try:
            from sandbox.v60.stability_filters import MahlerAuditor, LipschitzCutter
        except ImportError:
            # Fallback or local import if needed, but for now we assume they exist or we skip
            MahlerAuditor = None
            LipschitzCutter = None

        # 1. Split Metric Space into Real and Imaginary Components
        real_space = defaultdict(lambda: defaultdict(int))
        imag_space = defaultdict(lambda: defaultdict(int))
        
        entities = set()
        
        for pair, p_vals in metric_space.items():
            for e in pair: entities.add(e)
            
            for p, val in p_vals.items():
                if hasattr(val, 'real') and hasattr(val, 'imag'):
                    # Handle both complex and GaussianInt
                    # We lift the magnitude of the net weight
                    r = int(abs(val.real))
                    i = int(abs(val.imag))
                    
                    if r > 0: real_space[pair][p] = r
                    if i > 0: imag_space[pair][p] = i
                else:
                    # Legacy int handling
                    real_space[pair][p] = int(val)

        # 2. Define Lifting Logic (Inner Function)
        def run_lifting(sub_metric):
            coords = {e: 0 for e in entities}
            
            # Pre-calculate node degrees
            node_degrees = defaultdict(int)
            for (u, v), vals in sub_metric.items():
                node_degrees[u] += vals.get(self.p, 0)
                node_degrees[v] += vals.get(self.p, 0)

            # Max level
            max_p_val = 0
            for vals in sub_metric.values():
                max_p_val = max(max_p_val, vals.get(self.p, 0))
                
            # 2. Define Lifting Logic (Inner Function)
            def recurse_partition(nodes, level, base_coord):
                if not nodes or level > max_p_val + 1:
                    return

                # Build Adjacency for current level (Threshold Graph)
                adj = defaultdict(set)
                for (a, b), vals in sub_metric.items():
                    if a in nodes and b in nodes:
                        # Strong connection check
                        if vals.get(self.p, 0) >= level:
                            adj[a].add(b)
                            adj[b].add(a)

                # Connected Components (Cluster Detection)
                seen = set()
                cluster_index = 0
                
                # Sort nodes to ensure deterministic behavior
                sorted_nodes = sorted(list(nodes))
                
                for e in sorted_nodes:
                    if e not in seen:
                        # BFS for Component
                        q = [e]
                        seen.add(e)
                        comp = []
                        while q:
                            curr = q.pop(0)
                            comp.append(curr)
                            for n in adj[curr]:
                                if n not in seen:
                                    seen.add(n)
                                    q.append(n)
                        
                        # Assign Coordinate Digit
                        # Each component gets a distinct digit at this p-adic level
                        # coord = base + index * p^(level-1)
                        digit_val = cluster_index * (self.p ** (level - 1))
                        
                        for node in comp:
                            coords[node] += digit_val
                        
                        # Recurse if component has size > 1 (refined splitting)
                        if len(comp) > 1:
                            recurse_partition(comp, level + 1, base_coord + digit_val)
                            
                        cluster_index += 1
            
            recurse_partition(list(entities), 1, 0)
            return coords

        # 3. Component-Wise Execution
        print("   > Lifting Real Component...")
        real_coords = run_lifting(real_space)
        
        print("   > Lifting Imaginary Component...")
        imag_coords = run_lifting(imag_space)
        
        # 4. Combine into Gaussian Integers
        final_coords = {}
        for e in entities:
            # z = x + iy
            final_coords[e] = real_coords.get(e, 0) + 1j * imag_coords.get(e, 0)
            
        return final_coords

class V60Engine:
    def __init__(self):
        self.mapper = PrimeMapper()
        self.parser = TriadParser()
        self.builder = ValuationTensorBuilder(self.mapper)
        
        try:
            from sandbox.v60.stabilizer import SlidingWindowGenerator, SheafGluer
        except ImportError:
            from stabilizer import SlidingWindowGenerator, SheafGluer
            
        self.slider = SlidingWindowGenerator(window_size=5000, overlap=2500)
        self.gluer = GlobalAdelicIntegrator() # Simplified gluer for now
        self.lifter = HenselLifterV60()
        self.pmi_scale = 10
        self.raw_cooc = defaultdict(int)
        
        try:
            from sandbox.v60.adelic_integrator import AdelicIntegrator
        except ImportError:
            from adelic_integrator import AdelicIntegrator
        self.adelic_synthesis = AdelicIntegrator(primes=[])

    def process(self, text: str):
        print(f"--- V.60 Execution: {len(text)} chars ---")
        
        # 1. Sliding Window & Accumulation
        term_counts = Counter()
        total_triads = 0
        
        for idx, window_text in self.slider.generate(text):
            print(f"   > Processing Window {idx}...")
        for idx, window_text in self.slider.generate(text):
            print(f"   > Processing Window {idx}...")
            # Phase XXIX: Use Phased Parser
            triads = self.parser.parse_with_phase(window_text)
            total_triads += len(triads)
            
            for (s, r, o, phase) in triads:
                term_counts[s] += 1
                term_counts[o] += 1
                term_counts[r] += 1
                pair = tuple(sorted((s, o)))
                self.raw_cooc[pair] += 1
                
            # Accumulate into global tensor
            local_builder = ValuationTensorBuilder(self.mapper)
            local_builder.ingests(triads)
            self.gluer.integrate(local_builder.build_metric_space())
            
        print(f"--- Global Atlas Built: {len(self.gluer.global_tensor)} relationships ---")
        
        # Phase X: Algebraic PMI Valuation
        from sandbox.frontend_experiment.v60_lib.pmi_metric import PMIMetric
            
        pmi_solver = PMIMetric(scale=self.pmi_scale)
        self.gluer.global_tensor = pmi_solver.apply_pmi(
            self.gluer.global_tensor, 
            term_counts, 
            total_triads
        )
        
        # 2.5 Phase V: Geometric Blow-up (Singularity Resolution)
        from sandbox.frontend_experiment.v60_lib.singularity_resolver import SingularityResolver
            
        resolver = SingularityResolver()
        
        # Construct Adjacency Valuation Map from Global Tensor
        # Tensor keys are (A, B) -> {p: val}
        # We need (A, B) -> 1 if ANY p-val >= 1
        adj_valuation = {}
        nodes = set()
        neighbors_map = defaultdict(set)
        
        for (A, B), p_vals in self.gluer.global_tensor.items():
            nodes.add(A)
            nodes.add(B)
            # Check if any prime shows connection
            is_connected = False
            for p, v in p_vals.items():
                if v >= 1:
                    is_connected = True
                    break
            
            if is_connected:
                neighbors_map[A].add(B)
                neighbors_map[B].add(A)
                adj_valuation[tuple(sorted((A, B)))] = 1

        # Identify Singularities
        replacements = {}
        for node in nodes:
            # We pass the full global tensor for spectral weight analysis
            if resolver.detect_singularity(node, neighbors_map[node], adj_valuation):
                split_map = resolver.resolve(node, neighbors_map[node], self.gluer.global_tensor)
                if split_map:
                    replacements[node] = split_map
                    # Debug: Print sample of split
                    if node in ['has', 'is', 'temperature']:
                        safe_node = str(node).encode('ascii', 'replace').decode('ascii')
                        print(f"   > [Debug] Split map for '{safe_node}': {len(split_map)} neighbors mapped.")
                        sample_keys = list(split_map.keys())[:5]
                        sample_map = {k: split_map[k] for k in sample_keys}
                        print(f"     Sample mapping: {sample_map}")

        # Apply Blow-up (Renaming in Tensor)
        if replacements:
            print(f"   > [Blow-up] Applying {len(replacements)} singularity resolutions...")
            new_tensor = defaultdict(dict) # (A, B) -> {p: v}
            
            for (A, B), p_vals in self.gluer.global_tensor.items():
                # A and B were sorted by the gluer/builder usually, but let's be sure
                # Re-indexing might change the order (e.g. 'is' -> 'is_1' vs 'atom')
                
                # Default: Keep original names
                candidates_A = [A]
                candidates_B = [B]
                
                # Apply replacements
                if A in replacements:
                    if B in replacements[A]:
                        candidates_A = [replacements[A][B]]
                    else:
                        # B not in Ego Graph of A. PRUNE link to A.
                        candidates_A = []
                        
                if B in replacements:
                    if A in replacements[B]:
                        candidates_B = [replacements[B][A]]
                    else:
                        # A not in Ego Graph of B. PRUNE link to B.
                        candidates_B = []
                
                # Reconstruct links
                for na in candidates_A:
                    for nb in candidates_B:
                        if na == nb: continue # Self-loops usually noise
                        
                        # Canonicalize Key
                        key = tuple(sorted((na, nb)))
                        
                        # Merge p-vals (if multiple original edges map here)
                        for p, v in p_vals.items():
                            new_tensor[key][p] = new_tensor[key].get(p, 0) + v
                            
            self.gluer.global_tensor = new_tensor
            print(f"   > [Blow-up] Tensor Re-indexed. New Size: {len(new_tensor)}")
        
        # 3. Hensel Voting
        # The HenselVoter is removed, its logic is now implicitly handled or replaced.
        # For now, final_metric is just the global_tensor after blow-up.
        final_metric = self.gluer.global_tensor
        
        # 4. Hensel Lifting
        # Try primary logic primes AND promoted manifolds
        final_coords = {}
        polynomials = {}
        
        from sandbox.frontend_experiment.v60_lib.polynomial import OntologyPolynomialSynthesizer
             
        synth = OntologyPolynomialSynthesizer()
        
        # Phase VII: Topological Promotion (Dust Cloud Fix)
        # We need to lift not just the base primes (causes, has, is-a)
        # But also any SPLIT manifolds (is_1, is_2, has_1, has_2).
        # These must be promoted to DISTINCT PRIMES to force orthogonality.
        
        # Iterate over the RE-INDEXED tensor keys to find split manifolds
        # The tensor keys are (A, B). The relation R is implicit? 
        # Wait, the tensor is R-specific? 
        # No, the Global Tensor maps (A, B) -> {p1: v1, p2: v2}.
        # The split happened on the NODES (A, B), not the relation R?
        # NO. The Singularity Resolution splits the RELATION NODE R if R is reified.
        # BUT V.60 Engine treats relations as PRIMES in the valuation map.
        # "has" is a prime (5).
        # If "has" is split into "has_1", "has_2", does it mean we use Prime 5_1 and Prime 5_2?
        # NO. We must assign NEW Primes.
        
        # We check the 'replacements' map produced by the SingularityResolver.
        # If 'is' was split into 'is_1', 'is_2', we need to:
        # 1. Assign new primes to 'is_1', 'is_2'.
        # 2. Re-calculate valuations for these new primes?
        #    The tensor update (lines 340-370) supposedly re-indexed the graph.
        #    BUT the tensor values are {p=5: 1}. 
        #    If we replaced node A with A_1, the tensor keys changed to (A_1, B).
        #    But the VALUES inside are still {p=5: 1}.
        #    This means 'has_1' still acts as Prime 5.
        #    This is the "Dust Cloud": they are different nodes but same Prime dimension.
        
        # TO FIX: We must PROMOTE the prime dimension itself.
        # We need to know which NODE acts as the relation?
        # In V.60, R is a node in the graph, but also a Prime in the metric?
        # Yes, "Reification".
        
        # Strategy:
        # If a prime-relation P (e.g. 'is') was split into P1, P2...
        # We must iterate the tensor. For every edge that involves P1, 
        # we must change the valuation key from p(P) to p(P1).
        
        # Since we don't have a direct "Edge involves P1" check (P1 is a node),
        # we assume that if P1 is the *relation* node, it doesn't appear in the tensor keys (A, B) usually.
        # Wait, Triad is (A, R, B).
        # The Engine creates cliques: (A, B), (A, R), (B, R).
        # If R became R1, we have cliques (A, B), (A, R1), (B, R1).
        # The valuations are derived from these cliques.
        
        # If we want 'is_1' to be a distinct dimension, we must assign it a prime.
        # self.mapper.get_prime('is_1') will return a NEW prime (e.g. 17).
        # But the tensor currently stores {p(is)=3: 1}.
        # We need a pass to UPDATE the tensor values:
        # For every pair (u, v):
        #   If (u, v) is connected to R1 (via triangle inequality or direct link), switch p(R) to p(R1).
        
        # Simplified Approach for Prototype:
        # We just iterate the registry.
        # If we find 'is_1', 'is_2' in the node list (from replacements), we add them to registry.
        
        # Let's find all "Prime-Like" nodes that exist in the graph.
        all_nodes = set()
        for (u, v) in self.gluer.global_tensor.keys():
            all_nodes.add(u)
            all_nodes.add(v)
            
        active_primes = []
        bases = ['causes', 'has', 'is', 'produces', 'temperature', 'has-property', 'bonds']
        for p_name in bases: 
            # Check for base
            if p_name in all_nodes:
                active_primes.append(p_name)
            
            # Check for splits (is_1, is_2, etc.)
            for node in all_nodes:
                if node.startswith(p_name + "_") and node[len(p_name)+1:len(p_name)+2].isdigit():
                     if node not in active_primes:
                        active_primes.append(node)
        
        # Phase XI.2: Valuation Migration & Primary Injection
        # Ensure split manifolds (is_1) inherit valuations from base primes (is).
        # This is critical for Deep Lifting.
        new_tensor = self.gluer.global_tensor.copy()
        for (u, v), vals in self.gluer.global_tensor.items():
            for node in [u, v]:
                # If node is a prime relation (e.g., 'is' or 'is_1')
                p_current = self.mapper.get_prime(node)
                
                # Check for base relation (if split)
                base_name = node
                if "_" in node:
                    parts = node.split("_")
                    if parts[0] in bases and parts[1].isdigit():
                        base_name = parts[0]
                
                p_base = self.mapper.get_prime(base_name)
                
                # Migrate valuation: val(p_current) = max(val(p_current), val(p_base))
                weight = vals.get(p_base, 1) # Default to 1 if not in PMI
                new_tensor[(u, v)][p_current] = max(new_tensor[(u, v)].get(p_current, 0), weight)
                      
        self.gluer.global_tensor = new_tensor
        
        # Now we lift
        for p_name in active_primes:
             # Lift
             p_val = self.mapper.get_prime(p_name)
             if not p_val: continue
             
             print(f"   > Lifting Geometry for '{p_name}' (p={p_val})...")
             self.lifter.p = p_val
             coords = self.lifter.lift(self.gluer.global_tensor)
             final_coords[p_name] = coords
             
              # Synthesize
             poly = synth.synthesize(coords, p_name)
             polynomials[p_name] = poly
        
        # Phase XXVI: Adelic Ball Collapse (Berkovich Tree)
        print("\n--- Phase XXVI: Adelic Ball Collapse ---")
        
        try:
            from sandbox.frontend_experiment.v60_lib.berkovich_tree import AdelicBallTree
        except ImportError:
            try:
                from sandbox.v60.berkovich_tree import AdelicBallTree
            except ImportError:
                from berkovich_tree import AdelicBallTree
                
        tree_builder = AdelicBallTree(max_depth=20)
        
        # Prepare Primes Map
        primes_map = {}
        for p_name in active_primes:
            p_val = self.mapper.get_prime(p_name)
            if p_val:
                primes_map[p_name] = p_val

        # Build Tree
        # final_coords is {p_name: {entity: coord}}
        idelic_tree = tree_builder.build(final_coords, primes_map, active_primes)
        
        print(f"   > Berkovich Tree built. Root has {len(idelic_tree.get('children', []))} primary branches.")
        
        # We can still run the old integrator for "Fact" verification if needed, 
        # but the Tree is the primary output now.
        master_ontology = {"tree": idelic_tree}
        
        # Return all artifacts
        return {
            'metric': final_metric,
            'coords': final_coords,
            'polynomials': polynomials,
            'master_ontology': master_ontology
        }

if __name__ == "__main__":
    # Load larger text
    try:
        with open("sandbox/data/custom.txt", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("[Error] Data file not found. Using fallback text.")
        text = "Carbon causes pollution. Pollution is bad. Carbon is an element. Hydrogen is an element. Hydrogen bonds with Carbon."
        
    engine = V60Engine()
    metric, coords, polys = engine.process(text)
    
    import json
    import os
    
    # Ensure directory
    os.makedirs("sandbox/v60/frontend", exist_ok=True)
    
    output_path = "sandbox/v60/frontend/data.json"
    with open(output_path, "w") as f:
        # Convert sets/tuples to lists/strings for JSON
        def convert(o):
            if isinstance(o, set): return list(o)
            if isinstance(o, tuple): return str(o)
            return o
            
        json.dump(polys, f, default=convert, indent=2)
        
    print(f"\n[Success] Logic Graph written to {output_path}")
    
    print("\nMEANING EXTRACTED:")
    for p_name, poly in polys.items():
        print(f"\n[Prime: {p_name}]")
        for factor in poly['factors']:
            if factor['multiplicity'] > 0:
                print(f"  Root {factor['root']} (Mass {factor['multiplicity']}): {factor['entities']}")
