import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA

# Load Iris dataset
iris = load_iris()

# Reduce features to 2 components using PCA
X_r = PCA(n_components=2).fit_transform(iris.data)
colors = ['r', 'g', 'b']

# Scatter plot for each class
for i, name in enumerate(iris.target_names):
    plt.scatter(X_r[iris.target == i, 0], X_r[iris.target == i, 1], label=name, color=colors[i])
plt.title('PCA on Iris Dataset')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.grid(True)
plt.legend()
plt.show()