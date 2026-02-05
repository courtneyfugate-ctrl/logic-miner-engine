from src.logic_miner.engine import LogicMiner
from src.logic_miner.core.visualizer import LatexVisualizer

def test_vis():
    miner = LogicMiner()
    viz = LatexVisualizer()
    
    # 1. Numeric Test (Lifting)
    print("Generating Numeric Logic...")
    X = [0, 1, 2, 3, 4, 5]
    y = [5, 13, 21, 29, 37, 45] # y = 8x + 5
    res = miner.fit(X, y) # Should find p=2 or p=3 etc
    
    tex_src = viz.to_reledmac(res, title="P-adic Lifting Visualization")
    
    with open("sandbox/lift_viz.tex", "w") as f:
        f.write(tex_src)
        
    print("Saved sandbox/lift_viz.tex")

if __name__ == "__main__":
    test_vis()
