from .serial_synthesis_v54 import SerialSynthesizerV54
from .algebraic_text import AlgebraicTextSolver
from .mahler import MahlerSolver
from collections import defaultdict, Counter
import math
import numpy as np

class SerialSynthesizerV55(SerialSynthesizerV54):
    """
    Protocol V.56-Standard: Mahler-Locked Sheaf Integration.
    Implements rigid verification over logical polynomials (Mahler Coefficients).
    Transitions windows into a global ontology via identity locking.
    """
    def __init__(self, chunk_size=50, momentum=0.0):
        super().__init__(chunk_size=chunk_size, momentum=momentum)
        # Window-based storage
        self.window_logic = {}  # window_id -> {term: {p: coord}}
        self.window_overlaps = []  # (win_A_id, win_B_id, overlap_pages)
        self.locked_terms = set()  # Terms that passed sheaf lock
        self.rejected_links = []  # (term, reason)
        self.global_valuations = defaultdict(list) # term -> [vals]
        self.global_counts = Counter()
        
        self.STOPWORDS_SEMANTIC = {
            "Figure", "Table", "Example", "Exercise", "Problem", "Solution", 
            "Chapter", "Section", "Two", "Number", "Given", "Find", "Using", 
            "Calculate", "Determine", "Assume", "Suppose", "Consider", "Note",
            "Values", "Recall", "Review", "Answers", "Questions", "Summary",
            "Key Terms", "Objectives", "Introduction", "Chemistry", "Science",
            "you", "your", "than", "this", "that", "these", "those", "with",
            "from", "will", "and", "the", "for", "are", "but", "have", "can",
            "which", "also", "all", "its", "their", "when", "into", "between"
        }
        self.final_valuations = {}
        
    def fit_stream(self, text=None, reader=None, max_pages=1200):
        """
        Override to use overlapping windows with sheaf verification.
        Window size: 50 pages, Step: 25 pages (50% overlap)
        """
        if not reader:
            # For text input, fall back to V.54 logic
            return super().fit_stream(text=text, reader=None, max_pages=max_pages)
        
        if max_pages is None:
            max_pages = len(reader.pages)
            
        self.reader = reader # Store for sheaf verification
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
        
        return {
            'coordinates': self.final_vectors,
            'tree': self.tree_structure,
            'locked_terms': list(self.locked_terms),
            'valuations': self.final_valuations
        }

    def _process_window(self, window_text, window_id):
        """
        [Protocol V.56] Processes a text window into a Field of Potentials.
        Returns discovered logic (coordinates and Mahler polynomial).
        """
        # 1. Atomize (Bag of Atoms)
        atom_counts = self.featurizer.extract_entities(window_text, limit=400)
        entities = list(atom_counts.keys())
        
        if len(entities) < 5:
            return {}
            
        # 2. Field Generation (Valuation Map + Interaction Tensor)
        valuations = self.featurizer.compute_valuation_map(atom_counts)
        implication_matrix = self.featurizer.compute_interaction_tensor(window_text, entities)
        
        # 3. Solver: Field -> Hensel Lift -> Coordinates
        solver = AlgebraicTextSolver(p=self.p)
        try:
            local_manifold = solver.solve(valuations, implication_matrix, atom_counts)
            
            if local_manifold['analytic_score'] > 0.4:
                return {
                    'coordinates': local_manifold['coordinates'],
                    'depths': local_manifold['depths'],
                    'atom_counts': atom_counts,
                    'valuations': valuations,
                    'implication_matrix': implication_matrix,
                    'entities': entities,
                    'polynomial': local_manifold['polynomial'],
                    'analytic_score': local_manifold['analytic_score'],
                    'p': local_manifold['p']
                }
        except Exception as e:
            print(f"     ! Window {window_id} Solver Error: {e}")
            
        return {}

    def _sheaf_lock_check(self, win_A_id, win_B_id, overlap_pages):
        """
        [Protocol V.56.6] Intersection Sheaf Logic.
        Rigid verification through subtractive field intersection.
        """
        logic_A = self.window_logic.get(win_A_id, {})
        logic_B = self.window_logic.get(win_B_id, {})
        
        if not logic_A or not logic_B:
            return
            
        common_terms = list(set(logic_A['entities']) & set(logic_B['entities']))
        if len(common_terms) < 5:
            return
            
        # 1. Compute Intersection Field: min(P_A, P_B)
        mA = logic_A['implication_matrix']
        mB = logic_B['implication_matrix']
        
        intersection_matrix = defaultdict(dict)
        for t1 in common_terms:
            for t2 in common_terms:
                pA = mA.get(t1, {}).get(t2, 0.0)
                pB = mB.get(t1, {}).get(t2, 0.0)
                p_int = min(pA, pB)
                if p_int > 0.1:
                    intersection_matrix[t1][t2] = p_int
                
        # 2. Valuation Supremum: max(vA, vB)
        vA = logic_A['valuations']
        vB = logic_B['valuations']
        intersection_valuations = {t: max(vA[t], vB[t]) for t in common_terms}
        
        # 3. Analytic Intersection Test: Solve the residual structure
        solver = AlgebraicTextSolver(p=self.p)
        try:
            # We need counts for Mahler regression. min counts?
            cA = logic_A['atom_counts']
            cB = logic_B['atom_counts']
            intersection_counts = {t: min(cA[t], cB[t]) for t in common_terms}
            
            res = solver.solve(intersection_valuations, intersection_matrix, intersection_counts)
            
            # If the intersection is structurally sound (Energy -> 0)
            if res['analytic_score'] > 0.5:
                # RIGID LOCK
                for t in common_terms:
                    self.locked_terms.add(t)
                    p = logic_A['p']
                    self.adelic_coords[t][p].append(logic_A['coordinates'].get(t, 0))
                    self.adelic_coords[t][p].append(logic_B['coordinates'].get(t, 0))
                
                print(f"     > Windows {win_A_id}-{win_B_id}: RIGID LOCK ACQUIRED (Intersection Score: {res['analytic_score']:.2f})")
            else:
                print(f"     ! Windows {win_A_id}-{win_B_id}: REJECTED (Intersection Energy too high: {1 - res['analytic_score']:.2f})")
                self.rejected_links.append((win_A_id, win_B_id))
                
        except Exception as e:
            print(f"     ! Windows {win_A_id}-{win_B_id}: Intersection Test Error: {e}")

    def _compute_restricted_relative_poly(self, window_logic, common_terms, local_counts):
        """
        Helper: Computes a Mahler polynomial for a subset of terms with relative depth normalization.
        """
        depths = window_logic.get('depths', {})
        p = window_logic.get('p', self.p)
        
        # Filter intersection data
        subset_depths = {t: depths[t] for t in common_terms if t in depths}
        if not subset_depths: return None
        
        # Re-index: Relative Depth = Absolute Depth - Local Root Depth
        min_d = min(subset_depths.values())
        layers = defaultdict(list)
        for term, abs_d in subset_depths.items():
            rel_d = abs_d - min_d
            # Use local_counts for pure overlap identity
            layers[rel_d].append(math.log(local_counts.get(term, 0) + 1))
            
        depth_keys = sorted(layers.keys())
        xs = depth_keys
        ys = [sum(layers[d]) / len(layers[d]) for d in depth_keys]
        
        if len(xs) < 2: return None 
        
        from .mahler import MahlerSolver
        ms = MahlerSolver(p)
        coeffs = ms.compute_coefficients(xs, ys)
        # Round for identity match stability
        return [round(float(c), 3) for c in coeffs]

    def _consolidate_sheaf_lattice(self):
        """
        [Protocol V.56.8] Dense Global Consolidation.
        Unions all verified window fields to build a connected ontology.
        """
        if not self.locked_terms:
            self.final_vectors = {}
            self.tree_structure = {'tree': {}, 'roots': []}
            return

        print(f"       - Consolidating Global Sheaf for {len(self.locked_terms)} locked terms...")
        
        # 1. Aggregate Global Field (Union of Window Knowlege)
        global_field = defaultdict(dict)
        global_vals = defaultdict(list)
        global_counts = Counter()
        
        for win_id, logic in self.window_logic.items():
            if not logic: continue
            
            # Use all terms in the window that were eventually locked and NOT stopwords
            valid_window_terms = [t for t in logic['entities'] if t in self.locked_terms and t.title() not in self.STOPWORDS_SEMANTIC and t.lower() not in self.STOPWORDS_SEMANTIC]
            
            # Valuations and Counts
            for t in valid_window_terms:
                global_vals[t].append(logic['valuations'][t])
                global_counts[t] += logic['atom_counts'].get(t, 0)
                
            # Field: P(X|Y)
            m = logic['implication_matrix']
            for t1 in valid_window_terms:
                for t2 in valid_window_terms:
                    p = m.get(t1, {}).get(t2, 0)
                    if p > 0.1:
                        # Max-pooling: If any window sees a strong connection, it's global logic
                        global_field[t1][t2] = max(global_field[t1].get(t2, 0), p)

        # 2. Average Valuations
        self.final_valuations = {t: sum(v_list)/len(v_list) for t, v_list in global_vals.items()}
        
        # 3. Build Final Tree via Global Solver (Aggressive Lower Threshold)
        solver = AlgebraicTextSolver(p=self.p, lift_threshold=0.2)
        try:
            res = solver.solve(self.final_valuations, global_field, global_counts)
            
            self.final_vectors = res['coordinates']
            self.tree_structure = {
                'tree': res['tree'],
                'analytic_score': res['analytic_score'],
                'energy': res['energy']
            }
            # Add roots
            all_children = set()
            for children in res['tree'].values():
                all_children.update(children)
            self.tree_structure['roots'] = [n for n in self.final_vectors if n not in all_children]
            
            print(f"       - Global Consolidation Success (Score: {res['analytic_score']:.2f})")
            print(f"       - Global Roots: {len(self.tree_structure['roots'])}")
            
            # DEBUG: Sample some implications
            print("       - [DEBUG] Top Global Implications:")
            impls = []
            for t1, targets in global_field.items():
                for t2, p in targets.items():
                    impls.append((p, t1, t2))
            impls.sort(reverse=True)
            for p, t1, t2 in impls[:15]:
                print(f"         {t1} -> {t2} (P = {p:.2f})")
            
        except Exception as e:
            print(f"       ! Global Consolidation Error: {e}")
            self.final_vectors = {}
            self.tree_structure = {'tree': {}, 'roots': []}
