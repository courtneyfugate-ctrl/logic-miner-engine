from src.logic_miner.core.solver import ModularSolver

print("### DEBUG: Cubic Mod 17 ###")
solver17 = ModularSolver(17)

# 1. Verify solve_polynomial Degree 3
# Target: y = 2x^3 - x + 7 (mod 17)
# Points: (0, 7), (1, 8), (2, 2*8 - 2 + 7 = 16-2+7 = 21=4), (3, 2*27 - 3 + 7 = 54-3+7 = 58=7)
points = [(0, 7), (1, 8), (2, 4), (3, 7)]
print(f"Points: {points}")

coeffs = solver17.solve_polynomial(points, degree=3)
print(f"Coeffs: {coeffs}")
# Expected: (2, 0, -1, 7) or (2, 0, 16, 7)

# 2. Verify RANSAC on full dataset
X = list(range(100))
Y = [(2*x**3 - x + 7) % 17 for x in X]
data = list(zip(X, Y))

res = solver17.ransac(data, iterations=100, max_degree=3)
print(f"RANSAC Result: {res}")


print("\n### DEBUG: Parity Mod 2 ###")
solver2 = ModularSolver(2)

# 1. Verify Data
X2 = list(range(100))
Y2 = [x % 2 for x in X2]
data2 = list(zip(X2, Y2))

# 2. RANSAC Degree 1
res_d1 = solver2._ransac_poly(data2, 50, degree=1)
print(f"Degree 1 Result: {res_d1['ratio']} Params: {res_d1['model']}")

# 3. Full RANSAC with max_degree=3 (Match Production)
res2 = solver2.ransac(data2, iterations=50, max_degree=3)
print(f"Full RANSAC Result (MaxDeg=3): {res2}")
