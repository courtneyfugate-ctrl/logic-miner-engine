import random
from src.logic_miner.engine import LogicMiner

class TheorizerGen2:
    def generate(self, logic_type, noise_level=0.0):
        n = 100
        X = list(range(n))
        Y = []
        name = f"{logic_type} (Noise {noise_level:.0%})"
        
        if logic_type == 'CUBIC_P17':
            Y = [(2*x**3 - x + 7) % 17 for x in X]
            
        elif logic_type == 'COMPOSITE_MOD12':
            Y = [(5*x + 3) % 12 for x in X]
            
        elif logic_type == 'REAL_STEP':
            # y = floor(x / 8)
            Y = [x // 8 for x in X]
            
        elif logic_type == 'PARITY_MAHLER':
            Y = [x % 2 for x in X]
            
        # Inject Noise
        num_noise = int(n * noise_level)
        indices = random.sample(range(n), num_noise)
        
        min_y, max_y = min(Y), max(Y)
        range_y = max(max_y - min_y, 10)
        
        for i in indices:
            Y[i] = random.randint(min_y, max_y + range_y)
            
        return {'name': name, 'X': X, 'Y': Y, 'type': logic_type}

class SkepticalProbe:
    def probe(self, dataset):
        miner = LogicMiner()
        print(f"\nProbing: {dataset['name']}...")
        try:
            # We relax min_consensus for noisy data
            result = miner.fit(dataset['X'], dataset['Y'], min_consensus=0.30)
            
            print(f"  > Mode: {result.get('mode')}")
            print(f"  > p: {result.get('p')}")
            print(f"  > Conf: {result.get('discovery_confidence'):.2f}")
            
            # Validation Logic
            success = False
            expected = dataset['type']
            mode = result.get('mode', '')
            p = result.get('p')
            
            if expected == 'CUBIC_P17':
                if p == 17 and 'POLYNOMIAL' in mode: success = True
            elif expected == 'COMPOSITE_MOD12':
                if 'ADELIC_COMPOSITE' in mode and p in [6, 12]: success = True
            elif expected == 'REAL_STEP':
                if 'REAL' in mode: success = True
            elif expected == 'PARITY_MAHLER':
                # Parity is Linear Mod 2. Accept Poly p=2 or Mahler p=2.
                if p == 2: success = True
                
            return {'success': success, 'result': result}
            
        except Exception as e:
            print(f"  > FAILED with Error: {e}")
            return {'success': False, 'error': str(e)}

def run_noisy_arena():
    theo = TheorizerGen2()
    skep = SkepticalProbe()
    
    logics = ['CUBIC_P17', 'COMPOSITE_MOD12', 'REAL_STEP', 'PARITY_MAHLER']
    noises = [0.0, 0.20, 0.40]
    
    score_card = {}
    
    for logic in logics:
        for noise in noises:
            loss_count = 0
            runs = 1 
            
            data = theo.generate(logic, noise)
            res = skep.probe(data)
            
            key = f"{logic} @ {noise:.0%}"
            score_card[key] = "PASS" if res['success'] else "FAIL"
            
    print("\n\n=== NOISY LIMIT PROBE REPORT ===")
    for k, v in score_card.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    run_noisy_arena()
