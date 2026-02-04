from src.logic_miner.engine import LogicMiner

def test_universal():
    miner = LogicMiner()
    
    print("### TEST 1: NLP MINING ###")
    text = "Dogs are canine. Wolves are canine. Cats are feline. Lions are feline."
    # Should group (Dogs, Wolves) and (Cats, Lions)
    res_nlp = miner.fit(text)
    print(f"Result Check: Mode={res_nlp.get('mode')}")
    print(f"Tree: {res_nlp.get('tree')}")
    
    if res_nlp.get('mode') == 'SEMANTIC_TREE':
        print("[PASS] NLP detected.")
    else:
        print("[FAIL] NLP not detected.")

    print("\n### TEST 2: NUMERIC MINING ###")
    X = [0, 1, 2, 3, 4]
    y = [1, 3, 5, 7, 9] # 2x+1
    res_num = miner.fit(X, y)
    print(f"Result Check: p={res_num.get('p')}, conf={res_num.get('discovery_confidence')}")
    
    if res_num.get('p') is not None and res_num.get('discovery_confidence') == 1.0:
        print("[PASS] Numeric detected.")
    else:
         print("[FAIL] Numeric failed.")

if __name__ == "__main__":
    test_universal()
