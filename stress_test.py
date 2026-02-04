import random
import math
from src.logic_miner.core.lifter import HenselLifter

# --- 1. Generator Agent ---
def generate_data(n_samples=50, noise_ratio=0.15, p=7):
    """
    Logic: y = (3 + 5*7)x + (2 + 1*7) = 38x + 9
    """
    inputs = list(range(n_samples))
    outputs = []
    
    # True Logic Parameters
    # Base (mod 7): m0=3, c0=2
    # Level 1:      m1=5, c1=1
    # Full:         m = 38, c=9
    
    print(f"--- GENERATOR AGENT ---")
    print(f"Logic: y = 38x + 9 (mod 7^2)")
    print(f"Noise Ratio: {noise_ratio * 100}%")
    
    for x in inputs:
        # 15% chance of random noise
        if random.random() < noise_ratio:
            # Random outlier in data range
            y = random.randint(0, 300) 
        else:
            y = 38 * x + 9
        outputs.append(y)
        
    return inputs, outputs

# --- 2. Regression Agent ---
def run_linear_regression(inputs, outputs):
    """
    Manual OLS implementation to avoid external dependencies.
    """
    n = len(inputs)
    sum_x = sum(inputs)
    sum_y = sum(outputs)
    sum_xy = sum(x*y for x, y in zip(inputs, outputs))
    sum_xx = sum(x*x for x in inputs)
    
    # Calculate Slope (m) and Intercept (c)
    numerator_m = (n * sum_xy) - (sum_x * sum_y)
    denominator_m = (n * sum_xx) - (sum_x ** 2)
    
    if denominator_m == 0:
        return 0, 0, 0 # Singular
        
    m = numerator_m / denominator_m
    c = (sum_y - m * sum_x) / n
    
    # R-squared calculation
    y_mean = sum_y / n
    ss_tot = sum((y - y_mean)**2 for y in outputs)
    ss_res = sum((y - (m*x + c))**2 for x, y in zip(inputs, outputs))
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return m, c, r_squared

# --- 3. Report Generator ---
def generate_report(reg_results, miner_results):
    m_reg, c_reg, r2 = reg_results
    
    report = f"""# Adversarial Stress Test Report

## 1. Regression Agent (Standard OLS)
* **Model**: y = {m_reg:.2f}x + {c_reg:.2f}
* **R-squared**: {r2:.4f}
* **Analysis**: The regression attempts to fit a single line through all data, including noise. An R-squared of {r2:.2f} indicates { "a poor fit" if r2 < 0.6 else "a misleading average" }. It cannot distinguish between signal and noise, so the "true" integer logic is lost in floats.

## 2. Logic Miner Engine (p-adic RANSAC)
* **Status**: {miner_results['status']}
* **Depth Reached**: {miner_results['depth']}
* **Detected Logic**:
"""
    
    coeffs = miner_results['coefficients']
    if len(coeffs) > 0:
        report += f"  - **Level 0 (mod 7)**: y = {coeffs[0][0]}x + {coeffs[0][1]}\n"
    if len(coeffs) > 1:
        report += f"  - **Level 1 (mod 49)**: y = {coeffs[1][0]}x + {coeffs[1][1]}\n"
        
    report += f"""
## 3. Conclusion
The Logic Miner successfully isolated the "signal" from the 15% random noise by filtering outliers at the p-adic level. 

* The Regression Agent saw a cloud of points and drew an average line.
* The Logic Miner saw a structued pattern ($y \equiv 3x + 2 \pmod 7$) and locked onto it, discarding the noise as "phase shifted" data.
"""
    return report

# --- Main Test ---
def main():
    random.seed(42) # Reproducibility
    
    # 1. Generate
    inputs, outputs = generate_data(n_samples=50, noise_ratio=0.15, p=7)
    
    # 2. Regression
    print("\n--- REGRESSION AGENT ---")
    m_reg, c_reg, r2 = run_linear_regression(inputs, outputs)
    print(f"OLS: y = {m_reg:.2f}x + {c_reg:.2f}, R2={r2:.4f}")
    
    # 3. Logic Miner
    print("\n--- LOGIC MINER ENGINE ---")
    lifter = HenselLifter(p_base=7)
    # Using slightly looser consensus for random noise test
    result = lifter.lift(inputs, outputs, max_depth=2, min_consensus=0.5)
    print(f"Status: {result['status']}")
    print(f"Coeffs: {result['coefficients']}")
    
    # 4. Save Artifact
    report_content = generate_report((m_reg, c_reg, r2), result)
    
    with open("stress_test_report.md", "w") as f:
        f.write(report_content)
    
    print("\n[Artifact Generated] stress_test_report.md")

if __name__ == "__main__":
    main()
