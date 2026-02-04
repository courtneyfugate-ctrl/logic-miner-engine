# Implementation Plan: Phase VIII - Valuation Discovery (Hierarchy Reconstruction)

## Goal
To resolve the "Flat Logic" issue where disparate levels of taxonomy (Phylum, Class, Species) currently share the same $p$-adic valuation. We must "unfold" the coordinate space to restore vertical depth.

## Technical Objectives

### 1. Coordinate Unfolding (Hensel-Basis Mapping)
Currently, the solver uses a Dense Integer Basis ($0, 1, 2, 3...$). This causes "Coordinate Congestion."
*   **Action**: Modify the Mapping Strategy in `AlgebraicTextSolver`.
*   **Mechanism**: Allow the RANSAC loop to explore mappings where related entities share $p$-adic prefixes (e.g., multiples of $5, 25, 125$).
*   **Logic**: If $A$ and $B$ are siblings, $|x_A - x_B|_p$ should be large. If $A$ is a parent of $B$, $|x_A - x_B|_p$ should be small (valuation $\geq 1$).

### 2. Hierarchical Energy Function (Energy Refinement)
The current Mahler score is indifferent to topological rooting for small graphs.
*   **Action**: Penalize "Valuation Inversion" in `_optimize_mapping`.
*   **Constraint**: If Node $A$ has higher centrality (frequency/degree) than Node $B$, but $v_p(A) > v_p(B)$, the configuration is penalized.
*   **Goal**: Force generalities (Phylum/Class) to the $p$-adic roots (lowest valuations).

### 3. Restoration of Analytic Audits
*   **Action**: Fix the `analytic_score` and `lipschitz_violation` reporting to ensure every solved model has a verifiable "Proof of Truth."

## Proposed Changes

### [MODIFY] [algebraic_text.py](file:///d:/Dropbox/logic-miner-engine/src/logic_miner/core/algebraic_text.py)
*   Update `_optimize_mapping` to use a **Hierarchical RANSAC** pattern.
*   Implement a "Clustering Mutation" in the RANSAC loop rather than just random swaps.

### [MODIFY] [engine.py](file:///d:/Dropbox/logic-miner-engine/src/logic_miner/engine.py)
*   Ensure all audit metrics (Mahler, Lipschitz) are forwarded correctly to the result artifacts.

## Verification Plan
### Automated Tests
*   Run `sandbox/test_deep_mammalia.py`.
*   **Check**: Mammalia must have valuation $\infty$ (coordinate 0) or share a prefix with all other mammals.
*   **Check**: Platypus must share a $p$-adic prefix with mammals at a lower resolution than Eutherians share among themselves.
