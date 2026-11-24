import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# Generate synthetic train/test data points
np.random.seed(42)
data = np.random.rand(100)
tr_x, te_x = data[:50], data[50:]
tr_y = ["Class 1" if x < 0.5 else "Class 2" for x in tr_x]

# KNN scratch classifier function
def knn(point, k):
    # Sort neighbors by absolute distance
    dists = sorted([(abs(point - tr_x[i]), tr_y[i]) for i in range(50)])
    # Return majority class of k nearest neighbors
    return Counter([lbl for _, lbl in dists[:k]]).most_common(1)[0][0]

print("---KNN Classification Results---\ntraining dataset:first 50 data points based on rule x<0.5 is class 1 and x>=0.5 is class 2\ntest dataset: last 50 data points")

k_vals, res = [1, 2, 3, 4, 5, 20, 30], {}
for k in k_vals:
    print(f"results for k={k}:")
    preds = [knn(p, k) for p in te_x]
    res[k] = preds
    for i, lbl in enumerate(preds, start=51):
        print(f"Point x{i}(value:{te_x[i-51]:.4f}) classified as: {lbl}\n\nclassifications completed:")

# Plot KNN test classifications compared to training data
for k in k_vals:
    preds = res[k]
    c1 = [te_x[i] for i in range(50) if preds[i] == "Class 1"]
    c2 = [te_x[i] for i in range(50) if preds[i] == "Class 2"]
    plt.figure(figsize=(10, 6))
    plt.scatter(tr_x, [0]*50, c=["blue" if l == "Class 1" else "red" for l in tr_y], label="Training Data")
    plt.scatter(c1, [1]*len(c1), c="blue", marker="x", label="Class 1 (Test)")
    plt.scatter(c2, [1]*len(c2), c="red", marker="x", label="Class 2 (Test)")
    plt.title(f"KNN Classification (k={k})")
    plt.xlabel("Data Points"); plt.ylabel("classification levels")
    plt.legend(); plt.grid(True); plt.show()