import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_california_housing

# Load California Housing dataset
d = fetch_california_housing()
df = pd.DataFrame(d.data, columns=d.feature_names)
df["Target"] = d.target

# Print statistical summary of numerical features
print("\nStatistical Summary of the Dataset:\n", df.describe())

# Plot Histograms of Numerical Features
df.hist(figsize=(15, 10), color='skyblue', edgecolor='black')
plt.suptitle('Histograms of Numerical Features', fontsize=16)
plt.tight_layout(); plt.show()

# Box Plots for outlier visualization
plt.figure(figsize=(15, 8))
sns.boxplot(data=df,orient="h")
plt.title('Box Plots for Numerical Features')
plt.tight_layout()
plt.show()

# Detect outliers using Interquartile Range (IQR) method
out = {}
for c in df.columns:
    q1, q3 = df[c].quantile([0.25, 0.75])
    # Keep values outside [Q1 - 1.5 * IQR, Q3 + 1.5 * IQR]
    v = df[(df[c] < q1 - 1.5 * (q3 - q1)) | (df[c] > q3 + 1.5 * (q3 - q1))][c].values
    if len(v) > 0: out[c] = v
print(out)