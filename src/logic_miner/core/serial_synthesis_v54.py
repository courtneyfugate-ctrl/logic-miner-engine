from .serial_synthesis_v50 import SerialSynthesizerV50, HilbertMapper
from .discovery import PrimeSelector
from .lifter import HenselLifter
from .solver import ModularSolver
from collections import defaultdict, Counter
import math

class SerialSynthesizerV54(SerialSynthesizerV50):
    """
    Protocol V.54: Ultrametric Correction.
    Fixes V.53's frequency-based hierarchy violation.
    
    Key Corrections:
    1. Hilbert coordinates are PRIMARY signal (encode containment)
    2. Iterative RANSAC peeling for multi-modal logic
    3. Hensel lifting to depth=10 (higher precision)
    4. Tree hierarchy from p-adic valuations, NOT frequency
    """
    def __init__(self, chunk_size=50, momentum=0.3):
        super().__init__(chunk_size=chunk_size, momentum=momentum)
        # Protocol V.54 Restored: Primorial Projection (2*3*5*7*11=2310)
        self.hilbert_mapper = HilbertMapper(dimensions=6, base=2310)
        self.prime_selector = PrimeSelector()
        self.lifter = None  # Compliant Interface
        # adelic_coords structure: term -> {p: [lifted_hilbert_coord1, lifted_hilbert_coord2...]}
        self.adelic_coords = defaultdict(lambda: defaultdict(list))
        self.global_freqs = defaultdict(int)
        self.hilbert_coords = {}  # term -> raw Hilbert coordinate
        self.global_coordinates = {} # Protocol RESTORED
        self.global_energy = 0.0
        self.global_polynomial = []
        
    def _process_block(self, text_block, block_idx):
        """
        V.54 Corrected Block Processing.
        Uses Hilbert coordinates as the PRIMARY algebraic signal.
        """
        # 1. Featurize
        candidates = self.featurizer.extract_entities(text_block, limit=500)
        if not candidates: return
        
        matrix_raw, counts, _ = self.featurizer.build_association_matrix(text_block, candidates)
        
        # 2. Hilbert Mapping (THE TRUTH)
        hilbert_map = self.hilbert_mapper.compute_mappings(matrix_raw, candidates)
        
        # Store raw Hilbert coordinates
        for c in candidates:
            h_val = hilbert_map.get(c, 0)
            if h_val > 0:  # Valid coordinate
                self.hilbert_coords[c] = h_val
                self.global_freqs[c] += counts.get(c.replace(" ", "_"), 0)
        
        # 3. CORRECTED: Hilbert IS the signal, frequency is metadata
        # We're looking for logic governing the Hilbert space itself
        # inputs = Hilbert coordinates, outputs = term indices (for multi-modal detection)
        
        # Filter to terms with valid Hilbert coords
        valid_terms = [c for c in candidates if hilbert_map.get(c, 0) > 0]
        if len(valid_terms) < 5:
            print(f"   > [Block {block_idx}] Insufficient valid Hilbert coords ({len(valid_terms)}). Skipping.")
            return
            
        # Create signal: Hilbert coordinate is the X-axis
        inputs = [hilbert_map[term] for term in valid_terms]
        # Y-axis: We can use term index as a proxy, or frequency
        # For multi-modal detection, let's use a derived metric
        outputs = [counts.get(term.replace(" ", "_"), 0) for term in valid_terms]
        
        print(f"   > [Block {block_idx}] Ultrametric RANSAC on {len(inputs)} Hilbert coordinates...")
        
        # 4. Discovery with Iterative Peeling
        try:
            best_p, score, candidates_list = self.prime_selector.select_detailed(inputs, outputs)
            
            if score > 0.3:  # Lower threshold than V.53 due to noisier signal
                print(f"     ! Discovered p={best_p} (Score={score:.2f})")
                
                # 5. Multi-Modal Detection (Iterative Peeling)
                solver = ModularSolver(best_p)
                data_mod_p = [(x, y % best_p) for x, y in zip(inputs, outputs)]
                
                # Use iterative peeling to find multiple logic layers
                layers = solver.ransac_iterative(data_mod_p, min_ratio=0.3, min_size=3)
                
                if layers:
                    print(f"     ! Found {len(layers)} logic layers via peeling")
                    
                    # Process each layer
                    for layer_idx, layer in enumerate(layers[:3]):  # Top 3 layers
                        slope = layer.get('valuation_slope', 0.0)
                        print(f"     > Layer {layer_idx}: Newton Slope {slope:.2f}")
                        # 6. Hensel Lifting (INCREASED DEPTH)
                        try:
                            lifter = HenselLifter(best_p)
                            
                            # Extract inlier coordinates
                            inlier_inputs = [d[0] for d in layer['inliers']]
                            inlier_outputs = [d[1] for d in layer['inliers']]
                            
                            # Lift with DEEPER precision and RAMIFICATION
                            branches = lifter.lift(inlier_inputs, inlier_outputs, 
                                                 max_depth=10, 
                                                 min_consensus=0.4)
                            
                            for branch_idx, branch_res in enumerate(branches):
                                depth_achieved = branch_res['depth']
                                print(f"     + Layer {layer_idx} (Branch {branch_idx}): Lifted to depth={depth_achieved}")
                                
                                # Store lifted Hilbert coordinates for this branch
                                for original_idx in branch_res['active_indices']:
                                    # original_idx is within inlier_inputs/outputs
                                    # but we need to map back to valid_terms
                                    # For now, we trust the ordering or use the value-match
                                    h_coord = inlier_inputs[original_idx]
                                    for term in valid_terms:
                                        if hilbert_map[term] == h_coord:
                                            self.adelic_coords[term][best_p].append(h_coord)
                                            break
                                            
                        except Exception as e:
                            print(f"     ! Lifting Layer {layer_idx} Error: {e}")
                            
        except Exception as e:
            print(f"     ! Discovery Error: {e}")

    def _consolidate_global_lattice(self):
        """
        V.54: Build Tree from P-adic Valuations of Hilbert Coordinates.
        NOT from frequency.
        """
        print(f"     > Phase V.54: Ultrametric Consolidation...")
        
        # 1. Filter: Only terms with Hilbert coordinates that passed RANSAC
        valid_terms = [t for t in self.adelic_coords if t not in self.STOPWORDS_SEMANTIC]
        
        # 2. Create final vectors: term -> {p: lifted_hilbert_coord}
        self.final_vectors = {}
        for term in valid_terms:
            vec = {}
            for p, coords in self.adelic_coords[term].items():
                if coords:
                    # Use the Hilbert coordinate (average if multiple)
                    vec[p] = int(sum(coords) // len(coords))
            
            if vec:
                self.final_vectors[term] = vec
                
        print(f"       - Consolidated {len(self.final_vectors)} Ultrametric-Verified Terms.")
        
        # 3. Build Tree (P-ADIC HIERARCHY)
        print(f"       - Constructing P-adic Tree from Hilbert Valuations...")
        self.tree_structure = self._build_padic_tree(list(self.final_vectors.keys()))

        # 4. Map back to Global Coordinates & Calculate Energy (Protocol RESTORED)
        for term, vec in self.final_vectors.items():
            # Use the most common prime's Hilbert coordinate as the global scalar
            if vec:
                p_domin = max(vec.keys(), key=lambda k: k) # Pick largest for resolution
                self.global_coordinates[term] = vec[p_domin]

        if self.global_coordinates:
            from .algebraic_text import AlgebraicTextSolver
            solver = AlgebraicTextSolver(p=17) # Generic prime for audit
            coords = list(self.global_coordinates.values())
            self.global_polynomial = solver._compute_polynomial_from_coords(coords[:50]) # Sample
            from .mahler import MahlerSolver
            msolver = MahlerSolver(17)
            score = msolver.validation_metric(self.global_polynomial)
            self.global_energy = 1.0 - score
            print(f"       - Global Energy Calculated: {self.global_energy:.4f}")

    def _build_padic_tree(self, entities):
        """
        V.54 CORRECTED: Build hierarchy from p-adic distances of Hilbert coordinates.
        
        Logic: Terms with CLOSER Hilbert coordinates (higher p-adic valuation of difference)
        are semantically related. Parent-child determined by containment metric, not frequency.
        """
        tree = defaultdict(list)
        roots = []
        
        # For each term, find its closest "parent" in p-adic space
        for i, child in enumerate(entities):
            best_parent = None
            max_valuation = -1
            
            child_vec = self.final_vectors[child]
            
            # Consider all previous terms as potential parents
            potential_parents = entities[:i]
            
            for parent in potential_parents:
                parent_vec = self.final_vectors[parent]
                
                # Calculate p-adic strength (ultrametric distance)
                # Higher valuation = closer = stronger relationship
                valuation = self._calculate_padic_valuation(child_vec, parent_vec)
                
                if valuation > max_valuation:
                    max_valuation = valuation
                    best_parent = parent
            
            # Threshold: valuation >= 2 means they share structure at depth 2+
            if best_parent and max_valuation >= 2:
                tree[best_parent].append(child)
            else:
                roots.append(child)
                
        # Sort roots by Hilbert coordinate (lower = more fundamental)
        roots.sort(key=lambda r: min(self.final_vectors[r].values()) if self.final_vectors[r] else 0)
        
        return {'tree': tree, 'roots': roots}

    def _calculate_padic_valuation(self, vec_a, vec_b):
        """
        Calculate maximum p-adic valuation across all common primes.
        v_p(a - b) = number of times p divides (a - b).
        Higher valuation = closer in p-adic metric.
        """
        max_val = -1
        common_primes = set(vec_a.keys()) & set(vec_b.keys())
        
        for p in common_primes:
            diff = abs(vec_a[p] - vec_b[p])
            if diff == 0:
                val = 100  # Identical
            else:
                val = 0
                temp = diff
                while temp % p == 0:
                    val += 1
                    temp //= p
            
            if val > max_val:
                max_val = val
                
        return max_val
