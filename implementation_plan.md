# Implementation Plan: Protocol V.13 - Sheaf Manifold & Adelic Verification

## Goal
Implement **Protocol V.13 Sheaf Manifold** to enforce rigorous logic verification across sliding windows. This replaces "averaging" with **Sheaf Splining**, where local logical structures (defined on open sets/windows) must agree *exactly* on their intersections (overlaps) to be glued into a global section (Global Truth).

## User Review Required
> [!IMPORTANT]
> **Rigid Lock Enforcement**: This change introduces a strict "Reject" policy. If logic derived from Window A and Window B disagrees on the overlapping text, the link is **discarded**, not averaged. This may reduce the quantity of output but drastically increases quality/rigour.

## Technical Objectives

### 1. Adelic Embedding (Multi-Prime)
Currently, the solver typically focuses on a single prime or a sequential check.
*   **Action**: Enable simultaneous extraction of $p$-adic valuations for $p=\{2, 3, 5, 7, \dots\}$ (or a subset based on data).
*   **Reason**: "Truth" is the intersection of all relevant prime fields (Adelic).

### 2. Sheaf Splining (Windowed Rigid Locking)
*   **Action**: Implement a `SheafScanner` or modify `SerialSynthesizer` to process text in overlapping windows (e.g., 50% overlap).
*   **Mechanism**:
    1.  Compute Manifold $M_1$ for Window 1.
    2.  Compute Manifold $M_2$ for Window 2.
    3.  **Intersection Check**: For all terms $t$ present in the overlap region, verify $Valuation_{M_1}(t) == Valuation_{M_2}(t)$.
    4.  **Gluing**: If compliant, merge $M_1$ and $M_2$ using CRT (Chinese Remainder Theorem) or direct extension. If not, break the chain (Logic Cut).

### 3. Spline Curvature Filter
*   **Action**: Filter out trivial linear dependencies.
*   **Mechanism**: Ensure that the accepted logic exhibits non-trivial $p$-adic curvature (Mahler decay), rejecting "flat" or "noise" fits that happen to align by chance.

## Proposed Changes

### [NEW] [sheaf_core.py](file:///d:/Dropbox/logic-miner-engine/src/logic_miner/core/sheaf_core.py)
*   Create `SheafScanner` class.
*   Implement `verify_overlap(manifold_a, manifold_b, overlap_terms)`.
*   Implement `glue_manifolds(manifold_a, manifold_b)`.

### [MODIFY] [algebraic_text.py](file:///d:/Dropbox/logic-miner-engine/src/logic_miner/core/algebraic_text.py)
*   Expose `solve_block` method to return a local manifold object (valuations + basis) rather than just updating global state immediately.
*   Allow `AlgebraicTextSolver` to operate in "Local Section" mode.

### [MODIFY] [adelic_integrator.py](file:///d:/Dropbox/logic-miner-engine/src/logic_miner/core/adelic_integrator.py)
*   Ensure `solve_crt` is ready for rigid merging of verified sections.

## Verification Plan

### Automated Tests
*   **New Test**: `tests/test_sheaf_locking.py`
    *   **Case 1 (Success)**: Two windows with consistent logic for "Socrates is Man". Expect: Merged Manifold.
    *   **Case 2 (Failure)**: Window 1 says "Bat is Bird", Window 2 says "Bat is Mammal" (contradiction on overlap). Expect: Rejection/Split.
    *   **Case 3 (Adelic)**: Verify consistency across $p=3$ and $p=5$.

### Audits
*   Run the Chemistry Textbook audit again with Sheaf Splining enabled to see if it correctly segments topics without blurring them together.
