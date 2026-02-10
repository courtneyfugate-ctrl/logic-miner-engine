# Architecture Directive: The Algebraic Standard

**Status**: HARD ENFORCEMENT
**Last Updated**: V.53

## Core Mandates
Any deviation from these pillars is a **Violation of Protocol**.

## **NON-ARCHIMEDEAN MANIFESTO (THE "ZERO-G" PRINCIPLE)**
**ERROR SOURCE**: The most common failure mode is drifting into Archimedean (Euclidean/Real) thinking.
**THE REALITY**: This engine operates in a **Non-Archimedean (Ultrametric) Universe**.
1.  **NO GRADIENTS**: "Probability", "Cosine Similarity", "Fisher Information", "Manifold Curvature" (Riemannian) are **FORBIDDEN**. These concepts rely on the Triangle Inequality ($a+b \ge c$), which defines a "fuzzy" world of mixtures.
2.  **STRICT HIERARCHY**: We rely on the **Strong Triangle Inequality** ($\max(a,b) \ge c$). This forces the world into a strict Tree Structure (P-adic).
3.  **DISCRETE TRUTH**: Logic is not continuous. A subset relationship is binary. Do not try to smooth or average logic.
4.  **ALGEBRAIC INCIDENCE**: Encode structure via **Incidence** (who touches whom), **Galois Orbit** (symmetry), or **Simplicial Complexes** (triangles). NEVER use continuous fields or gradients.

## **ARITHMETIC OBSERVABLE MANDATE**
**CRITICAL CORRECTION**: The engine requires **Arithmetic** inputs (Divisibility, Modular Congruence), not just Topological ones (Connectivity).
*   **DO NOT USE**: Distance Metrics, Simplicial Homology (Holes), Graph Centrality. These are "Flat" topological features.
*   **MUST USE**: 
    1.  **Inclusion Ratios**: $P(A|B) \approx 1 \implies A | B$. (Divisibility)
    2.  **Frequency Valuations**: High Frequency = Low Valuation (Units). Low Frequency = High Valuation (Deep Logic).
    3.  **Commutator Magnitude**: Integer degree of non-commutativity = Ramification Index.
*   **REASON**: The Solver extracts **P-adic Integers**, not manifold shapes. We must feed it "Numbers", not "Shapes".

### **STRUCTURAL PARSER AS MEASUREMENT DEVICE**
**PIPELINE**: `Raw Text` $\to$ `Structural Parser (spaCy/OpenIE)` $\to$ `Relation Atoms` $\to$ `Arithmetic Featurizer` $\to$ `P-adic Solver`.
*   **The Parser's Job**: Measure **Incidence** and **Order**. It is a **Detector**, not a Solver. It produces inputs like `(Carbon, forms, Bond)`.
*   **The Featurizer's Job**: Convert these atoms into **Arithmetic Invariants** (Divisibility via Inclusion, Valuation via Frequency, Ramification via Commutator).
*   **Result**: We feed **Arithmetized Relations** to the solver, not raw words.

To violate this is to destroy the engine's core purpose.

## Core Mandates

1.  **Discovery via RANSAC** (`discovery.py`)
    -   Logic **MUST** be discovered by filtering noise, not by averaging it.
    -   *Implementation*: `PrimeSelector.select_detailed()` must be called per data block.

2.  **Refinement via Hensel Lifting** (`lifter.py`)
    -   Modular structure ($mod p$) **MUST** be lifted to p-adic precision ($mod p^k$).
    -   *Implementation*: `HenselLifter.lift()` must be applied to all RANSAC inliers.

3.  **Adelic Integration**
    -   Truth is the intersection of all valid prime fields (`adelic_coords`).
    -   *Implementation*: The final Ontology Tree must be built *exclusively* from terms that survived Discovery and Refinement.

## Restricted Methods (Do Not Use)
-   **Pure Spectral/Graph Methods**: Adjacency lists without algebraic verification are "Forest Generators". Forbidden.
-   **Euclidean Metrics**: Cosine similarity, Jaccard index, etc., are forbidden on the logic lattice. Only p-adic valuations allowed.
-   **Arbitrary Bases**: No hardcoded $M=30030$ unless derived from data.
-   **Continuous Averaging**: Spline momentum, EMA, weighted blends (e.g., `α*x + (1-α)*y`). Use discrete verification instead.

## Permitted Methods (Rigorous)
-   **P-adic Sheaf Splining**: Overlapping windows where logic must lock perfectly. If $L_A$ and $L_B$ disagree on overlap → reject link (no averaging).
-   **Adelic Verification**: CRT-based consistency checking (`AdelicIntegrator.solve_crt`)
-   **Trajectory Mode**: Discrete majority voting from coordinate history

## Enforced Component
-   **Active Kernel**: `SerialSynthesizerV54` (Ultrametric Corrected).
