from .serial_synthesis_v54 import SerialSynthesizerV54
from .discovery import PrimeSelector
from .lifter import HenselLifter
from .adelic import AdelicIntegrator
from .real import RealSolver
from collections import defaultdict, Counter
import math

class SerialSynthesizerV55(SerialSynthesizerV54):
    """
    Protocol V.55: Sheaf Splining.
    Implements rigid overlap verification (Sheaf Property) for text windows.
    
    Key Corrections from External Agent:
    - BANNED: Spline Momentum (continuous averaging)
    - PERMITTED: Sheaf Splining (rigid lock verification)
    
    Sheaf Property: If two p-adic functions agree on overlap → LOCK into global law.
    If they disagree even slightly → REJECT (no averaging).
    """
    def __init__(self, chunk_size=50, momentum=0.0):
        super().__init__(chunk_size=chunk_size, momentum=momentum)
        # Window-based storage
        self.window_logic = {}  # window_id -> {term: {p: coord}}
        self.window_overlaps = []  # (win_A_id, win_B_id, overlap_pages)
        self.locked_terms = set()  # Terms that passed sheaf lock
        self.rejected_links = []  # (term, reason)
        
    def fit_stream(self, text=None, reader=None, max_pages=1200):
        """
        Override to use overlapping windows with sheaf verification.
        Window size: 50 pages, Step: 25 pages (50% overlap)
        """
        if not reader:
            # For text input, fall back to V.54 logic
            return super().fit_stream(text=text, reader=None, max_pages=max_pages)
        
        print("--- [Serial Sheaf Synthesis V.55] ---")
        window_size = 50
        step_size = 25  # 50% overlap
        total_windows = (max_pages - window_size) // step_size + 1
        
        curr_win_id = 0
        for start_page in range(0, max_pages - window_size + 1, step_size):
            end_page = min(start_page + window_size, max_pages)
            
            print(f"\n   > Processing Window {curr_win_id}: Pages [{start_page}-{end_page})")
            
            # Extract window text
            window_text = ""
            for page_num in range(start_page, end_page):
                if page_num < len(reader.pages):
                    window_text += reader.pages[page_num].extract_text()
            
            if not window_text.strip():
                curr_win_id += 1
                continue
                
            # Process window independently (V.54 logic)
            window_terms = self._process_window(window_text, curr_win_id)
            
            # Store window logic
            self.window_logic[curr_win_id] = window_terms
            
            # If not first window, check sheaf lock with previous
            if curr_win_id > 0:
                overlap_start = start_page
                overlap_end = start_page + step_size  # Overlap region
                self._sheaf_lock_check(curr_win_id - 1, curr_win_id, (overlap_start, overlap_end))
            
            curr_win_id += 1
        
        # Consolidate only locked terms
        print(f"\n   > Phase V.55: Sheaf Consolidation...")
        print(f"       - {len(self.locked_terms)} terms passed sheaf lock verification.")
        print(f"       - {len(self.rejected_links)} inconsistent links rejected.")
        
        self._consolidate_sheaf_lattice()
        
        return {}  # Dummy return for compatibility

    def _process_window(self, window_text, window_id):
        """
        Process a text window using V.54 logic, return discovered terms.
        """
        candidates = self.featurizer.extract_entities(window_text, limit=500)
        if not candidates:
            return {}
        
        matrix_raw, counts, _ = self.featurizer.build_association_matrix(window_text, candidates)
        hilbert_map = self.hilbert_mapper.compute_mappings(matrix_raw, candidates)
        
        # Filter valid terms
        valid_terms = [c for c in candidates if hilbert_map.get(c, 0) > 0]
        if len(valid_terms) < 5:
            return {}
        
        # RANSAC Discovery
        inputs = [hilbert_map[term] for term in valid_terms]
        outputs = [counts.get(term.replace(" ", "_"), 0) for term in valid_terms]
        
        try:
            best_p, score, _ = self.prime_selector.select_detailed(inputs, outputs)
            
            if score > 0.3:
                # Hensel Lifting with Ghost Detection
                from .solver import ModularSolver
                solver = ModularSolver(best_p)
                data_mod_p = [(x, y % best_p) for x, y in zip(inputs, outputs)]
                layers = solver.ransac_iterative(data_mod_p, min_ratio=0.3, min_size=3)
                
                window_terms = {}
                for layer in layers[:3]:
                    lifter = HenselLifter(best_p)
                    inlier_inputs = [d[0] for d in layer['inliers']]
                    inlier_outputs = [d[1] for d in layer['inliers']]
                    
                    lift_res = lifter.lift(inlier_inputs, inlier_outputs, max_depth=10, min_consensus=0.4)
                    
                    if lift_res['status'] == 'CONVERGED':
                        # Store lifted coordinates
                        for d in layer['inliers']:
                            h_coord = d[0]
                            for term in valid_terms:
                                if hilbert_map[term] == h_coord:
                                    if term not in window_terms:
                                        window_terms[term] = {}
                                    window_terms[term][best_p] = h_coord
                                    break
                
                return window_terms
        except Exception as e:
            print(f"     ! Window {window_id} Error: {e}")
        
        return {}

    def _sheaf_lock_check(self, win_A_id, win_B_id, overlap_pages):
        """
        Sheaf Property: Check if logic from two windows LOCKS on overlap.
        If coords agree exactly → LOCK (merge)
        If coords disagree → REJECT (no averaging)
        """
        logic_A = self.window_logic.get(win_A_id, {})
        logic_B = self.window_logic.get(win_B_id, {})
        
        if not logic_A or not logic_B:
            return
        
        # Find common terms (overlap)
        common_terms = set(logic_A.keys()) & set(logic_B.keys())
        
        if len(common_terms) < 3:
            print(f"     ! Windows {win_A_id}-{win_B_id}: Insufficient overlap ({len(common_terms)} terms)")
            return
        
        # Check RIGID LOCK: coords must match EXACTLY
        locked = 0
        rejected = 0
        
        for term in common_terms:
            coords_A = logic_A[term]
            coords_B = logic_B[term]
            
            # Check all primes
            common_primes = set(coords_A.keys()) & set(coords_B.keys())
            if not common_primes:
                rejected += 1
                self.rejected_links.append((term, f"No common primes between win{win_A_id}-{win_B_id}"))
                continue
            
            # EXACT match required (no tolerance)
            matches = all(coords_A[p] == coords_B[p] for p in common_primes)
            
            if matches:
                locked += 1
                self.locked_terms.add(term)
                # Merge coordinates
                for p in coords_A.keys():
                    self.adelic_coords[term][p].append(coords_A[p])
                for p in coords_B.keys():
                    if p not in coords_A:
                        self.adelic_coords[term][p].append(coords_B[p])
            else:
                rejected += 1
                self.rejected_links.append((term, f"Coord mismatch between win{win_A_id}-{win_B_id}"))
        
        print(f"     > Windows {win_A_id}-{win_B_id}: {locked} locked, {rejected} rejected (Sheaf Property)")

    def _consolidate_sheaf_lattice(self):
        """
        Consolidate only terms that passed sheaf lock.
        Use trajectory mode (discrete majority) for stability.
        """
        # Only keep locked terms
        self.final_vectors = {}
        for term in self.locked_terms:
            if term in self.STOPWORDS_SEMANTIC:
                continue
            
            vec = {}
            for p, coords in self.adelic_coords[term].items():
                if coords:
                    # DISCRETE MAJORITY VOTING (not averaging)
                    from collections import Counter
                    mode_coord = Counter(coords).most_common(1)[0][0]
                    vec[p] = mode_coord
            
            if vec:
                self.final_vectors[term] = vec
        
        print(f"       - Final Yield (Sheaf-Verified): {len(self.final_vectors)} terms")
        
        # Build tree using V.54's p-adic logic
        self.tree_structure = self._build_padic_tree(list(self.final_vectors.keys()))
