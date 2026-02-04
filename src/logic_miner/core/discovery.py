from .solver import ModularSolver
from .sparse import SparseSolver
import math
from collections import Counter

class PrimeSelector:
    """
    Hunts for the optimal p-adic base by checking RANSAC consensus.
    """
    def __init__(self):
        self.scan_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]

    def select(self, inputs, outputs):
        p, score, _ = self.select_detailed(inputs, outputs)
        return p, score
        
    def scan_gcd_collisions(self, inputs, outputs):
        """
        [Proposal 4] Discovery via Collisions.
        If y_i = y_j, then a(x_i - x_j) = k*m.
        We find m via GCD of collision intervals (x_i - x_j).
        This works well if dataset size N > p.
        """
        # Group indices by Y value to find collisions
        y_map = {}
        for i, y in enumerate(outputs):
            if y not in y_map: y_map[y] = []
            y_map[y].append(inputs[i])
            
        intervals = []
        for y, indices in y_map.items():
            if len(indices) < 2: continue
            for i in range(len(indices)):
                for j in range(i+1, len(indices)):
                    intervals.append(abs(indices[i] - indices[j]))
        
        if not intervals: return None
        
        # Calculate GCD of all collision intervals
        def gcd_list(nums):
            if not nums: return 0
            res = nums[0]
            for n in nums[1:]:
                res = math.gcd(res, n)
            return res
            
        g = gcd_list(intervals)
        if g > 1:
             print(f"[PrimeHunter] GCD Collision Scan found candidate: {g}")
             return g
        return None

    def scan_lll_determinants(self, inputs, outputs):
        """
        [Proposal B] Discovery via Lattice Reduction (Determinant GCD).
        Finds p even if no collisions exist (N < p).
        Uses cross-product invariant of linear recurrence.
        """
        if len(inputs) < 4: return None
        
        # dX, dY
        dx = [inputs[i+1] - inputs[i] for i in range(len(inputs)-1)]
        dy = [outputs[i+1] - outputs[i] for i in range(len(outputs)-1)]
        
        determinants = []
        for i in range(len(dx) - 1):
             # Pair i, i+1
             # Det = dy_i * dx_j - dy_j * dx_i
             dxi, dyi = dx[i], dy[i]
             dxj, dyj = dx[i+1], dy[i+1]
             
             det = dyi * dxj - dyj * dxi
             if det != 0:
                 determinants.append(abs(det))
                 
        if not determinants: return None
        
        def gcd_list(nums):
            if not nums: return 0
            res = nums[0]
            for n in nums[1:]:
                res = math.gcd(res, n)
            return res
            
        g = gcd_list(determinants)
        if g > 1:
             print(f"[PrimeHunter] LLL Determinant Scan found candidate: {g}")
             return g
        return None

    def select_detailed(self, inputs, outputs):
        """
        Returns (best_p, best_score, candidates)
        candidates: list of {'p':, 'score':, 'params':, 'degree':}
        """
        if not outputs: return 2, 0.0, []
        
        candidates_list = []
        best_p = 2
        best_score = -1.0
        
        # 1. Add "Smart" Candidates
        # A. Collisions (N > p)
        gcd_p = self.scan_gcd_collisions(inputs, outputs)
        
        # B. LLL / Determinants (N < p)
        lll_p = self.scan_lll_determinants(inputs, outputs)
        
        active_scan_list = self.scan_list.copy()
        
        # Prioritize discovered moduli
        if lll_p and lll_p not in active_scan_list:
             active_scan_list.insert(0, lll_p)
        if gcd_p and gcd_p not in active_scan_list:
             if gcd_p != lll_p:
                 active_scan_list.insert(0, gcd_p)
        
        print(f"[PrimeHunter] Scanning Primes: {active_scan_list[:5]}...")
        
        for p in active_scan_list:
            solver = ModularSolver(p)
            data_mod_p = [(x, y % p) for x, y in zip(inputs, outputs)]
            
            # Use degree optimization (PolyMorph will try 0, 1, 2, 3)
            # Increased max_degree to 3 to support Cubic Logic.
            result = solver.ransac(data_mod_p, iterations=150, max_degree=3)
            
            if p == 2:
                 # Clean debug spam
                 pass
            
            l0_score = result['ratio']
            final_score = l0_score
            
            # --- [Proposal 1] Sparse Solver Fallback ---
            # If dense RANSAC fails to find high consistency, check Sparse.
            if l0_score < 0.8:
                sparse = SparseSolver(p)
                sparse_res = sparse.solve(data_mod_p)
                if sparse_res:
                     print(f"  > Testing p={p}: Found Sparse Logic! ({sparse_res['note']}) Ratio={sparse_res['ratio']:.2f}")
                     # If Sparse is better, use it.
                     if sparse_res['ratio'] > l0_score:
                         result = sparse_res # Swap result structure
                         l0_score = sparse_res['ratio']
                         final_score = l0_score
                         # Sparse is usually exact if found.
            
            # --- Depth Probe (Stability Check) ---
            if l0_score > 0.4:
                from .lifter import HenselLifter
                probe = HenselLifter(p).lift(inputs, outputs, max_depth=2, min_consensus=0.3)
                
                if probe['status'] == 'CONVERGED':
                    l1_score = probe.get('final_consensus', 0)
                    if l1_score < l0_score * 0.8 and l0_score > 0.85:
                         # Model degraded significantly at L1 -> Likely Strictly Modular (e.g. Parity)
                         final_score = l0_score * 0.95
                         print(f"  > Testing p={p}: L0={l0_score:.2f} -> L1={l1_score:.2f} (Weak Lift) -> Strict | Stability={final_score:.2f}")
                    else:
                        final_score = (l0_score + l1_score) / 2
                else:
                    # Lift failed.
                    if l0_score > 0.85:
                        # Strong Modular Logic (e.g. Parity). Don't crush it.
                        final_score = l0_score * 0.95
                        print(f"  > Testing p={p}: L0={l0_score:.2f} -> Strictly Modular (Lift Failed) | Stability={final_score:.2f}")
                    else:
                        final_score = l0_score * 0.5
                        print(f"  > Testing p={p}: L0={l0_score:.2f} -> Probe Failed | Stability={final_score:.2f}")
            
            # Adjusted Score
            adj_score = 0.0
            if p > 1:
                chance = 1.0 / p
                adj_score = (final_score - chance) / (1.0 - chance)
                
            print(f"  > Testing p={p}: Raw={final_score:.2f} -> Adj={adj_score:.2f}")
            
            # Store Candidate
            # Check if result has model (works for Dense and Sparse)
            # Sparse 'params' is (c,e,d), Dense 'model' is tuple.
            # Normalize key names? 
            # Dense result: {'model':, 'degree':}
            # Sparse result: {'params':, 'degree':, 'type':}
            
            params = result.get('model') or result.get('params')
            
            if params:
                candidates_list.append({
                    'p': p,
                    'score': adj_score,
                    'degree': result.get('degree'),
                    'params': params,
                    'type': result.get('type', 'POLYNOMIAL') 
                })

            # Track Best
            if best_score == -1.0 or adj_score > best_score + 0.02:
                best_score = adj_score
                best_p = p
            elif adj_score > best_score - 0.02 and p < best_p:
                best_p = p
                
        # Sort candidates
        candidates_list.sort(key=lambda x: x['score'], reverse=True)
        return best_p, best_score, candidates_list

    def _generate_primes(self, start, count=10):
        primes = []
        num = start
        while len(primes) < count:
            if self._is_prime(num):
                primes.append(num)
            num += 1
        return primes
        
    def _is_prime(self, n):
        if n < 2: return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0: return False
        return True

    def scan_mahler(self, inputs, outputs):
        """
        Scans primes using Mahler Decay Metric.
        Useful for non-polynomial logic (e.g. Parity).
        """
        from .mahler import MahlerSolver
        
        candidates = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        best_p = 2
        best_score = -1.0
        
        print("[MahlerHunter] Scanning Decay Metrics...")
        
        for p in candidates:
            solver = MahlerSolver(p)
            coeffs = solver.compute_coefficients(inputs, outputs, max_degree=15)
            # We need to verify if these coeffs model the data well?
            # Mahler coefficients match data EXACTLY for 0..N by definition.
            # The question is: do they DECAY?
            model_score = solver.validation_metric(coeffs)
            
            print(f"  > Testing p={p}: DecayScore={model_score:.2f}")
            
            if model_score > best_score:
                best_score = model_score
                best_p = p
                
        return best_p, best_score
