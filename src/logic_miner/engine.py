from .core.discovery import PrimeSelector
from .core.lifter import HenselLifter
from .core.solver import ModularSolver
from .core.ultrametric import UltrametricBuilder
import zlib
import re
from collections import Counter

class StochasticChaosError(Exception):
    pass

class LogicMiner:
    def __init__(self):
        self.selector = PrimeSelector()
        self.lifter = None
        self.p = None
        
    def fit_corpus(self, texts, entities=None, validation='CRT'):
        """
        [Research V.4] Adelic Multi-Text Synthesis.
        Mines logic from multiple texts and synthesizes a global model (Mod M).
        """
        print(f"--- [Logic Miner] Adelic Synthesis on {len(texts)} texts ---")
        from .core.adelic import AdelicIntegrator
        
        models = []
        
        # 1. Mine Local Models
        for i, text in enumerate(texts):
            print(f"   > Mining Text {i+1}...")
            # We use the standard fit_text, but we need the raw model data
            # fit_text returns the Tree Visualization dict.
            # We need to bypass or extract.
            
            # Direct Solver Call for Access
            from .core.algebraic_text import AlgebraicTextSolver
            
            # Extract Local Entities if not provided
            local_ents = entities
            if not local_ents:
                 # Auto-extract per text?
                 # CRT requires Consistent Parameter Mapping (Coefficient i corresponds to same term).
                 # This implies we must model the SAME entities across texts.
                 # or we fit a generic polynomial f(x) where x is abstract?
                 # For now, we assume user provides the Unified Entity List.
                 print("   [Error] Adelic Synthesis requires a unified 'entities' list.")
                 return None
            
            # Force diversity? No, let Auto-Prime do it.
            solver = AlgebraicTextSolver() # Uses Auto-Prime
            res = solver.solve(text, local_ents)
            
            model = {
                'p': res['p'],
                'params': tuple(res['polynomial']),
                'degree': len(res['polynomial']) - 1
            }
            models.append(model)
            
        # 2. Synthesize Global Model
        integrator = AdelicIntegrator()
        global_logic = integrator.solve_crt(models)
        
        if global_logic:
            print("--- [Logic Miner] Adelic Consensus Reached ---")
            print(f"   > Type: {global_logic['type']}")
            print(f"   > Global Modulus: {global_logic['modulus']}")
            print(f"   > Params: {global_logic['params']}")
            return global_logic
        else:
            print("--- [Logic Miner] Adelic Consensus Failed (Incompatible Topologies) ---")
            return None

    def fit(self, inputs, outputs=None, min_consensus=0.30):
        """
        Universal Entry Point.
        Auto-detects:
        1. Natural Language (Input: String) -> Semantic Tree
        2. Ultrametric Tree (Input: Distance Matrix)
        3. Multivariate Logic (Input: Vectors)
        4. Scalar Logic (Input: Integers)
        """
        # 0. Check for NLP
        if isinstance(inputs, str):
            return self.fit_text(inputs)

        # Legacy Numeric Pipeline
        return self.fit_numeric(inputs, outputs, min_consensus)

    def fit_text(self, raw_text, use_adelic_shake=True, use_serial=True, reader=None):
        """
        Mines semantic logic tree from raw text.
        If use_serial=True and input is large, uses SerialManifoldSynthesizer (Splining).
        """
        # Threshold for serial: 100k chars or presence of reader
        if use_serial and (len(raw_text) > 100000 or reader):
            print("   > Large Corpus Detected: Switching to Serial Spline Synthesis (V.22)...")
            from .core.serial_synthesis import SerialManifoldSynthesizer
            synthesizer = SerialManifoldSynthesizer(chunk_size=50)
            result = synthesizer.fit_stream(text=raw_text, reader=reader)
            
            # Result synthesis for Serial
            coords = result['coordinates']
            labels = list(coords.keys())
            p = result['p']
            
            # Derive distance matrix from p-adic coordinates d_p(x,y) = p^-v_p(x-y)
            n = len(labels)
            dist_matrix = [[0.0]*n for _ in range(n)]
            for i in range(n):
                for j in range(i+1, n):
                    diff = abs(coords[labels[i]] - coords[labels[j]])
                    if diff == 0:
                        v = 100 # Infinity
                    else:
                        v = 0
                        while diff % p == 0:
                            diff //= p
                            v += 1
                    dist = p**(-v)
                    dist_matrix[i][j] = dist_matrix[j][i] = dist
            
            tree_result = self.fit_ultrametric(dist_matrix, labels=labels, source_type='SERIAL_SYNTHESIS')
            tree_result['spline_trace'] = result['spline_trace']
            tree_result['anchors'] = result['anchors']
            tree_result['p'] = result['p']
            tree_result['classification'] = result.get('classification', {})
            tree_result['entities'] = list(result['coordinates'].keys())
            tree_result['coordinates'] = result['coordinates']
            # For compatibility with audit script
            tree_result['polynomial'] = result['spline_trace'][-1]['polynomial'] if result['spline_trace'] else []
            return tree_result

        print("--- [Logic Miner] Detected Logic: Natural Language (Semantic Tree) ---")
        
        # ... (Monolithic path remains for small texts) ...
        from .core.algebraic_text import AlgebraicTextSolver
        solver = AlgebraicTextSolver(p=5, ransac_iterations=15) 
        
        # Process Matrix for purified set
        p_matrix, p_counts, _ = featurizer.build_association_matrix(raw_text, purified_candidates)
        
        result = solver.solve(p_matrix, purified_candidates, p_counts)
        
        # 4. Process Hyper-Edges (Reactions)
        from .core.process_graph import ProcessGraphExtractor
        pge = ProcessGraphExtractor()
        reactions = pge.extract_reactions(raw_text, purified_candidates)
        if reactions:
            print(f"   > Process Graph: Extracted {len(reactions)} Reaction Hyper-edges.")

        # 5. Result Synthesis
        tree_result = self.fit_ultrametric(result['matrix'], labels=purified_candidates, source_type='ALGEBRAIC_TEXT')
        tree_result['polynomial'] = result['polynomial']
        tree_result['coordinates'] = result['coordinates']
        tree_result['classification'] = classifications
        tree_result['reactions'] = reactions
        tree_result['energy'] = result['energy']
        tree_result['analytic_score'] = result['analytic_score']
        
        return tree_result


    def fit_ultrametric(self, matrix, labels=None, source_type='MATRIX', precomputed_tree=None):
        """
        Solves for the optimal p-adic tree topology given a distance matrix.
        Enforces Ultrametric Inequality: d(x,z) <= max(d(x,y), d(y,z))
        """
        print(f"--- [Logic Miner] Detected Structure: Ultrametric Tree ({source_type}) ---")
        builder = UltrametricBuilder()
        
        if labels is None:
            labels = [str(i) for i in range(len(matrix))]
            
        if precomputed_tree:
             tree = precomputed_tree
        else:
             tree = builder.build_tree(labels, matrix)
        
        mode = 'ULTRAMETRIC'
        if source_type == 'TEXT': mode = 'SEMANTIC_TREE'
        elif source_type == 'MATRIX': mode = 'ULTRAMETRIC'
        else: mode = source_type # Pass ALGEBRAIC_TEXT through
        
        return {
            'mode': mode,
            'tree': tree,
            'entities': labels,
            'note': f"Recovered p-adic topology from {source_type} noise."
        }


    def fit_numeric(self, inputs, outputs, min_consensus):
        # 1. Check for Distance Matrix (Ultrametric)
        # If inputs is NxN matrix and outputs is None/Labels
        if isinstance(inputs, list) and len(inputs) > 0 and isinstance(inputs[0], list) and (outputs is None or isinstance(outputs[0], str)):
             # Heuristic: square matrix of floats?
             is_matrix = len(inputs) == len(inputs[0])
             if is_matrix:
                 return self.fit_ultrametric(inputs, labels=outputs)

        # 2. Check for Multivariate (Vectors)
        is_multivariate = inputs and isinstance(inputs[0], (list, tuple))
        
        if is_multivariate:
             print("--- [Logic Miner] Detected Logic: Multivariate ---")
             
             scan_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 101]
             best_multivariate_res = None
             best_score = 0.0
             
             for p in scan_list:
                 solver = ModularSolver(p)
                 data = [(x, y % p) for x, y in zip(inputs, outputs)]
                 
                 layers = solver.ransac_iterative(data, min_ratio=0.4)
                 
                 if layers:
                     # Score = Ratio of Dominant Branch
                     score = layers[0]['ratio']
                     
                     if score > best_score:
                         best_score = score
                         
                         branches = []
                         for i, layer in enumerate(layers):
                             branch_res = {
                                 'p': p,
                                 'mode': 'MULTIVARIATE',
                                 'discovery_confidence': layer['ratio'],
                                 'params': layer['model'],
                                 'inliers_count': len(layer['inliers']),
                                 'layer_index': i
                             }
                             # Only attempt lifting if score is high enough to be worth it
                             if i == 0 and layer['ratio'] > 0.8:
                                 self.lifter = HenselLifter(p_base=p)
                                 lift_res = self.lifter.lift(inputs, outputs, max_depth=20, min_consensus=layer['ratio']*0.9)
                                 branch_res['logic_trace'] = lift_res
                                 
                             branches.append(branch_res)
                         
                         if len(branches) == 1:
                             best_multivariate_res = branches[0]
                         else:
                             best_multivariate_res = {
                                 'p': p,
                                 'mode': 'MULTIMODAL',
                                 'branches': branches,
                                 'note': f"Found {len(branches)} distinct logic rules via Peeling."
                             }

             if best_multivariate_res and best_score > 0.5:
                 # Update state to best found
                 self.p = best_multivariate_res['p']
                 print(f"   > Selected Logic Mod {self.p} (Score {best_score:.2f})")
                 return best_multivariate_res
                 
             return {'mode': 'NOISE', 'p': None}

        # 3. Standard Scalar Logic
        return self._fit_scalar_pipeline(inputs, outputs, min_consensus)

    def _fit_scalar_pipeline(self, inputs, outputs, min_consensus=0.30):
        """
        Black Box Mining Pipeline:
        0. Pre-Flight: Lipschitz Continuity Check.
        1. Discover: optimal p.
        2. Lift: Find logic rule F(x).
        """
        print("--- [Logic Miner] Stage 0: Pre-Flight Checks ---")
        from .core.metrics import calculate_lipschitz_violation
        
        print("--- [Logic Miner] Stage 1: Discovery ---")
        p, score, candidates = self.selector.select_detailed(inputs, outputs)
        print(f"   > Discovered p={p} (Conf: {score:.2f})")
        
        # --- PHASE A: Adelic Hasse Synthesis (Global Logic) ---
        valid_candidates = [c for c in candidates if c['score'] > 0.4]
        if len(valid_candidates) >= 2:
            print(f"   > Multiple strong signals detected: {[c['p'] for c in valid_candidates]}. Attempting Synthesis...")
            from .core.adelic import AdelicIntegrator
            integrator = AdelicIntegrator()
            
            subsets_to_try = []
            if len(valid_candidates) >= 2:
                subsets_to_try.append(valid_candidates[:2])
            if len(valid_candidates) >= 3:
                 subsets_to_try.append(valid_candidates[:3])
                 
            synth_res = None
            for subset in subsets_to_try:
                res = integrator.solve_crt(subset, inputs, outputs)
                
                if res:
                     # Verify Fidelity on GLOBAL Integers
                     M = res['modulus']
                     params = res['params']
                     hits = 0
                     for x, y in zip(inputs, outputs):
                         pred = 0
                         if res['degree'] == 1: pred = (params[0]*x + params[1]) % M
                         elif res['degree'] == 0: pred = params[0] % M
                         
                         if pred == y % M: hits += 1
                         
                     fid = hits / len(inputs)
                     print(f"   > Hasse Composite Fidelity (Mod {M}): {fid:.2f}")
                     
                     if fid > 0.95:
                         synth_res = res # Found it
                         synth_res['fidelity'] = fid # Hack
                         break
            
            if synth_res:
                 M = synth_res['modulus']
                 params = synth_res['params']
                 fid = synth_res.get('fidelity', 1.0)
                 
                 print(f"   > Hasse Success! Mod {M}")
                 
                 if fid > 0.95:
                     return {
                         'p': M,
                         'mode': 'ADELIC_' + synth_res['type'],
                         'discovery_confidence': fid,
                         'params': params,
                         'note': synth_res['note'] + " (Validated Modulo M)"
                     }

        # --- PHASE B: Single Prime / Fallback ---
        if score < min_consensus:
            print(f"   > Polynomial consensus {score:.2f} < {min_consensus}. Analyzing Adelic options...")
            
            # 2. Scanning Mahler Decay (p-adic Continuous)
            p_m, score_m = self.selector.scan_mahler(inputs, outputs)
            print(f"   > Mahler p={p_m} (Decay Score: {score_m:.2f})")
            
            # 3. Adelic Scan (Real / Archimedean)
            from .core.real import RealSolver
            real_res = RealSolver().solve(inputs, outputs)
            print(f"   > Adelic (Real) Scan: Type={real_res['type']} Fidelity={real_res['fidelity']:.2f}")
            
            # Global Selection (Adelic Unification)
            runs = [
                {'mode': 'POLYNOMIAL', 'score': score, 'p': p},
                {'mode': 'MAHLER', 'score': score_m, 'p': p_m},
                {'mode': f"REAL_{real_res['type']}", 'score': real_res['fidelity'], 'p': float('inf'), 'data': real_res}
            ]
            
            best = max(runs, key=lambda x: x['score'])
            
            if best['score'] < min_consensus:
                 raise StochasticChaosError(f"No logic rule found. Best: {best['mode']} ({best['score']:.2f})")
                 
            if 'REAL' in best['mode']:
                return {
                    'p': float('inf'),
                    'mode': best['mode'],
                    'discovery_confidence': best['score'],
                    'params': best['data']['params'],
                    'note': 'Modeled using Archimedean (Real) Logic'
                }
            elif best['mode'] == 'MAHLER':
                from .core.mahler import MahlerSolver
                ms = MahlerSolver(p_m)
                coeffs = ms.compute_coefficients(inputs, outputs, max_degree=20)
                return {
                   'p': p_m,
                   'mode': 'MAHLER',
                   'discovery_confidence': score_m,
                   'coefficients': coeffs,
                   'note': 'Modeled using Mahler Basis (Continuous Function)'
                }
            
            pass
            
        # Lipschitz Validator (Only for p-adic)
        violation = calculate_lipschitz_violation(inputs, outputs, p)
        print(f"   > Lipschitz Violation: {violation:.2%}")
        if violation > 0.05:
            # We warn but maybe don't abort strict? The prompt says "If high, abort".
            raise StochasticChaosError(f"Lipschitz violation {violation:.2%} too high. Logic is unstable/discontinuous.")
            
        self.p = p
        
        print(f"--- [Logic Miner] Stage 2: Lifting (p={p}) ---")
        
        # Adelic Verification (Ghost Term Check)
        from .core.real import RealSolver
        real_res = RealSolver().solve(inputs, outputs)
        adelic_note = " (Adelic Status: "
        if real_res['fidelity'] > 0.85:
             adelic_note += "Universal/Real-Consistent)"
        elif real_res['fidelity'] < 0.2:
             adelic_note += "Strictly Modular)"
        else:
             adelic_note += "Ambiguous)"
        print(f"   > Adelic Verification: Real Fidelity={real_res['fidelity']:.2f} -> {adelic_note}")

        self.lifter = HenselLifter(p_base=p)
        result = self.lifter.lift(inputs, outputs, min_consensus=min_consensus)
        
        return {
            'p': p,
            'discovery_confidence': score,
            'logic_trace': result,
            'lipschitz_violation': violation,
            'note': adelic_note
        }
