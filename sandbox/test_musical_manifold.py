
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logic_miner.engine import LogicMiner

def test_musical_manifold():
    text = """
The Morphological Architecture of the Musical Manifold: A Discrete Structural Audit

The history of organized sound is not a linear progression of aesthetic choices, but a nested hierarchy of formal constraints. To audit this manifold, one must identify the foundational algebraic states upon which all subsequent rhythmic and harmonic "lifts" are constructed. At the base of our stratigraphy is the Phylum Acoustica, the most general informational state, defined by the presence of intentional frequency organization (pitch) and temporal subdivision (meter). Every entity discussed in this audit, from the minimalist cell to the Wagnerian opera, is bound to this acoustic root.

Within this foundational field lies the Subphylum Instrumentalis. This represents the first significant "lift" in the p-adic resolution of the manifold. Here, the abstract pitch is encased within a specific physical medium—the vibrating string, the column of air, or the struck surface. This skeletal framework—the Orchestral Skeleton—serves as the Algebraic Anchor for the entire system. Whether a work is a solo sonata or a massive symphony, it is algebraically locked to this instrumental prefix.

I. The Common Practice Signature: The Shared Prefix
As we move into the Class Organon (The Common Practice Era), the informational density increases. The "Classical Signature" is defined by a trifecta of invariant coefficients that must be satisfied by any root within this field. First is the possession of Tonal Gravity, a specialized system for the transfer of harmonic tension and resolution. Second is the Formal Barrier provided by structured repetition (Binary, Ternary, or Sonata form), allowing for stable internal computation regardless of thematic noise. Third is the Acoustic Logic of the middle-voice architecture, an exaptation where three distinct layers—the melody, the bass line, and the inner harmonic filler—function in a high-fidelity information-processing chain.

These three traits constitute the Primary Classical Polynomial. In a pure algebraic solver, these traits act as the "Parental Class" because they are the informational prerequisites for every subsequent branch. Whether a piece is played in a chamber hall or a cathedral, if it possesses tonal gravity, structured repetition, and three-voice architecture, it is algebraically locked to this prefix. The hierarchy is mathematical necessity.

II. The Symphonic Consensus: The Logic of the Sonata
The majority of the Classical manifold is occupied by the Infraclass Symphonia, or the orchestral absolute. This branch represents a major "lift" in the p-adic resolution of the musical tree, characterized by the innovation of the Sonata-Allegro Form, allowing for extended internal developmental logic within a protected thematic environment.

The Concerto Branch (The Virtuosic Lift): Represented by the Piano Concerto, this lineage specializes in the support of a single soloist against the massive skeletal support of the orchestra. In our algebraic audit, the concerto serves as a high-density node, where the orchestral mammary glands—the string sections—are retained but the physical focus is pushed to an extreme solo scale.

The String Quartet Branch (The Chamber Lift): Represented by the Quartet, this lineage demonstrates the extreme adaptation of orchestral limbs into a four-voice wingspan. This branch proves that the classical blueprint can achieve true flight—powered by a high-metabolism harmonic engine—while strictly maintaining its core identity. A quartet is not a symphony; it is a musical state that has solved the problem of complexity using a different set of coefficients.

III. The Taxonomic Exception: The 9th Symphony Root
The hierarchy faces its most rigorous "Audit" with the Beethovenian Divergence, specifically the Ninth Symphony (Op. 125). The Ninth is a "Ghost Term" in the musical manifold. It satisfies the Symphonic Signature—it uses the orchestral skeleton, it follows the four-movement structural lift, and its ear architecture is distinctly symphonic—yet it retains the Ancestral/External Coefficient of human vocalization (The Chorus).

In a p-adic solver, the Ninth shares the prefix of the symphonic expansion but fails to merge with the Absolute Instrumental Lift. While a Haydn or Mozart symphony can be simplified into the "Pure Instrumental" branch, the Ninth forces the solver to recognize a deeper, more primitive divergence where the "Vocal" and "Instrumental" roots overlap. It stands as a distinct root in the field Q_p, proving that while the symphonic logic is absolute, the methods of expression within that class are subject to deep, branching divergence. The Ninth is the Platypus of the Symphony: it is an orchestral work that "lays the eggs" of choral drama, challenging any solver that relies on simple, non-branching chains of logic.

IV. The Operatic Divergence: The Dramatic Outlier
Above the Symphonic Root, the manifold undergoes a major Adelic Synthesis known as the Subclass Drama. This branch represents the transition to stage-based birth and is further divided into distinct logical infraclasses: Opera Seria and Singspiel.

The Opera represents a specialized solution to the constraint of total internal development. Operas utilize a "Dual-Phase" developmental logic. The music is born in an extremely formal state but must complete its growth within a specialized external manifold known as the libretto (the text).

The Wagnerian Music Drama provides an exceptional example of Convergent Logic. Despite its "Theater-like" appearance, its p-adic coordinates are locked to the Organon branch. It possesses the leitmotif epipubic structures and the characteristic tonal logic, proving that physical morphology (the "staged" shape) is a secondary coefficient that can emerge in different p-adic lineages to solve similar environmental/narrative constraints.
"""
    
    print("--- [Verification] Musical Manifold Logic Mining ---")
    miner = LogicMiner() # Auto-detects p or uses internal defaults
    # In fit_text, it calls AlgebraicTextSolver(p=5).
    
    print(f"   > Loaded Text ({len(text)} chars).")
    print("   > Running Universal Blackbox...")
    
    # Phase XV is now automated inside
    result = miner.fit_text(text)
    
    print(f"--- [Logic Miner] Detected Structure: {result['mode']} ---")
    # print(miner.audit_result(result)) # Method does not exist
    
    print("\n--- [Audit Results] ---")
    print(f"   > Mahler Score (Convergence): {result['analytic_score']}")
    
    # Polynomial degree
    print(f"   > Polynomial Degree: {len(result['polynomial']) - 1}")

    print("\n   > Discovered p-adic Coordinates:")
    
    # Check specific keys
    check_keys = ["Phylum Acoustica", "Subphylum Instrumentalis", "Class Organon", 
                  "Infraclass Symphonia", "Ninth Symphony", "String Quartet", "Wagnerian Music Drama"]
    
    coords = result['coordinates']
    for k in check_keys:
        found = False
        for ent, coord in coords.items():
            if k in ent:
                print(f"     {ent}: {coord}")
                found = True
                # break # Show all variants
        if not found:
             print(f"     {k}: [Not Found/Filtered]")

    # Dump to file
    with open("sandbox/musical_manifold_dump.txt", "w") as f:
        f.write(str(result))
    
    print("\n   > Verification Complete.")
    print("   > Artifacts Dumped to: sandbox/musical_manifold_dump.txt")

if __name__ == "__main__":
    test_musical_manifold()
