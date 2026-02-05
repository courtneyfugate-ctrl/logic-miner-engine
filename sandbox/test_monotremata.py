from src.logic_miner.engine import LogicMiner
import time

def run_monotremata_test():
    """
    Test V.3 Pure P-adic Pipeline on User's High-Density Taxonomic Text.
    Focus: Platypus (Monotremata) separation from Eutheria (Elephant, Bat, Whale).
    """
    miner = LogicMiner()
    
    # Input Text (Raw from User)
    text = """
    The Biological Architecture of the Class Mammalia
    The biological world is organized through a series of nested innovations, where each level of the hierarchy incorporates the structural logic of its predecessors while adding specific constraints. At the foundation of our study is the Phylum Chordata, defined by the presence of a dorsal nerve cord. Within this phylum lies the Subphylum Vertebrata, where the nerve cord is encased in a protective spinal column. Every creature discussed hereafter is, fundamentally, a vertebrate chordate.
    
    The Class Mammalia represents a major branching point in the vertebrate tree, defined by three "Parent" traits: the possession of mammary glands for nourishing young, the growth of hair or fur for thermoregulation, and the presence of three middle ear bones. These traits constitute the "Mammalian Signature," the root logic from which all diverse mammalian lineages diverge.
    
    The Divergent Branches of Eutheria
    The majority of modern mammals belong to the Infraclass Eutheria, or placental mammals. This branch is characterized by the innovation of the placenta, allowing for extended internal development.
    The Proboscidea Branch: Represented by the Elephant, this lineage specializes in massive skeletal support and the development of the trunk, a fusion of the nose and upper lip.
    The Chiroptera Branch: Represented by the Bat, this lineage demonstrates the extreme adaptation of mammalian limbs into wings, proving that the mammalian blueprint can achieve true flight while maintaining mammary glands and fur.
    The Cetacea Branch: Represented by the Whale, this lineage shows the return to an aquatic environment. Despite their fish-like appearance, whales retain the core mammalian requirements of warm-bloodedness and nursing their young with milk.
    
    The Taxonomic Exception: Monotremata
    The hierarchy faces its most rigorous test with the Order Monotremata, specifically the Platypus. The platypus is a "Bridge Taxon" that sits at the earliest divergence of the mammalian tree. It serves as an exceptional case for a logic miner because it possesses the core "Parent" traits of Mammalia—it has fur and it produces milk—yet it retains the ancestral "Outlier" trait of laying leathery eggs, a characteristic typically reserved for reptiles and birds.
    """
    
    print("\n--- [Input] High-Density Taxonomic Text ---")
    print(f"Length: {len(text)} chars")
    
    target_entities = ["Elephant", "Bat", "Whale", "Platypus", "Mammalia", "Eutheria"]
    
    print(f"\n--- Running V.3 Miner with Forced Candidates: {target_entities} ---")
    
    # We pass candidates directly to fit() if supported, or we mock the entity extraction?
    # engine.py's fit() takes optional candidates? No, fit(inputs) checks if list or str.
    # If str, it calls fit_text. fit_text() calls nlp_extract.
    # We need to bypass auto-extraction to guarantee targets are in the graph.
    # We can instantiate AlgebraicTextSolver directly.
    
    from src.logic_miner.core.algebraic_text import AlgebraicTextSolver
    solver = AlgebraicTextSolver(p=5)
    
    # Run Solver directly
    res = solver.solve(text, target_entities)
    
    # Extract Coordinates
    coords = res['coordinates']



    # Calculate Pairwise Distances (p=5)
    p = 5
    def pd(e1, e2):
        if e1 not in coords or e2 not in coords: return -1
        diff = coords[e1] - coords[e2]
        return p ** (-_valuation(diff, p))

    def _valuation(n, p):
        if n == 0: return float('inf')
        v = 0
        while n % p == 0:
            n //= p
            v += 1
        return v
    
    print("\n--- Derived Algebraic Distances (v_p) ---")
    
    # Eutherian Internal Distances
    d_bat_whale = pd("Bat", "Whale")
    d_bat_eleph = pd("Bat", "Elephant")
    d_whale_eleph = pd("Whale", "Elephant")
    
    # Monotreme vs Eutherian
    d_plat_bat = pd("Platypus", "Bat")
    d_plat_whale = pd("Platypus", "Whale")
    
    print(f"Bat <-> Whale:    {d_bat_whale}")
    print(f"Bat <-> Elephant: {d_bat_eleph}")
    print(f"Platypus <-> Bat: {d_plat_bat}")
    
    # Hypothesis: Platypus should be further from Bat/Whale than they are to each other
    # because Platypus context ("eggs", "monotremata") is more distinct than Eutherian context ("placenta").
    
    if d_plat_bat > d_bat_whale:
        print("\n>>> [PASS] Platypus correctly identified as deeper divergence (Outlier).")
    elif d_plat_bat == d_bat_whale:
        print("\n>>> [WARN] Platypus equidistant to Eutherians (Star Topology).")
    else:
        print("\n>>> [FAIL] Platypus clustered tighter than Eutherians??")

if __name__ == "__main__":
    run_monotremata_test()
