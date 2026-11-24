import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, classification_report

# Load dataset and standard-scale features
d = load_breast_cancer()
Xs = StandardScaler().fit_transform(d.data)

# Perform KMeans clustering (k=2)
km = KMeans(n_clusters=2, random_state=42)
yk = km.fit_predict(Xs)
print("Confusion Matrix:\n", confusion_matrix(d.target, yk))
print("\nClassification Report:\n", classification_report(d.target, yk))

# Compute 2D PCA components for plotting
pca = PCA(n_components=2)
df = pd.DataFrame(pca.fit_transform(Xs), columns=['PC1', 'PC2'])
df['Cluster'], df['True Label'] = yk, d.target

# Plot predictions and true labels
for h, title in [('Cluster', 'K-Means Clustering of Breast Cancer Dataset'), ('True Label', 'True Labels of Breast Cancer Dataset')]:
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x='PC1', y='PC2', hue=h, palette='Set1' if h=='Cluster' else 'coolwarm', s=100, edgecolor='black', alpha=0.7)
    plt.title(title); plt.xlabel('Principal Component 1'); plt.ylabel('Principal Component 2'); plt.legend(title=h); plt.show()

# Plot clusters with centroids overlaid
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='PC1', y='PC2', hue='Cluster', palette='Set1', s=100, edgecolor='black', alpha=0.7)
ctr = pca.transform(km.cluster_centers_)
plt.scatter(ctr[:, 0], ctr[:, 1], s=200, c='red', marker='X', label='Centroids')
plt.title('K-Means Clustering with Centroids'); plt.xlabel('Principal Component 1'); plt.ylabel('Principal Component 2'); plt.legend(); plt.show()