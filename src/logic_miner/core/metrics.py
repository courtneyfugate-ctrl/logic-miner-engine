import math
import random

def get_valuation(n, p):
    if n == 0:
        return float('inf')
    v = 0
    while n % p == 0:
        v += 1
        n //= p
    return v

def p_adic_norm(n, p):
    if n == 0:
        return 0.0
    v = get_valuation(n, p)
    return p ** (-v)

def calculate_lipschitz_violation(inputs, outputs, p, samples=100):
    """
    Checks if the function implied by inputs->outputs is 1-Lipschitz.
    Condition: |f(x) - f(y)|_p <= |x - y|_p
    Returns: violation_ratio (0.0 to 1.0)
    """
    if len(inputs) < 2:
        return 0.0
        
    n = len(inputs)
    violations = 0
    total_checks = 0
    
    # We sample pairs
    for _ in range(samples):
        idx1 = random.randint(0, n-1)
        idx2 = random.randint(0, n-1)
        
        if idx1 == idx2:
            continue
            
        x1, x2 = inputs[idx1], inputs[idx2]
        y1, y2 = outputs[idx1], outputs[idx2]
        
        dist_x = p_adic_norm(x1 - x2, p)
        dist_y = p_adic_norm(y1 - y2, p)
        
        # Check strict inequality: dist_y > dist_x implies expansion (violation)
        # We use a small epsilon for float comparison safety? N/A for p-adic powers usually.
        # But float precision might be an issue. 
        # dist_x and dist_y are powers of p.
        
        if dist_y > dist_x:
            violations += 1
        
        total_checks += 1
        
    return violations / total_checks if total_checks > 0 else 0.0
