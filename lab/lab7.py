import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

# Load dataset and split train/test 80/20
d = load_breast_cancer()
X_tr, X_te, y_tr, y_te = train_test_split(d.data, d.target, test_size=0.2, random_state=42)

# Train decision tree classifier
clf = DecisionTreeClassifier(random_state=42).fit(X_tr, y_tr)
print(f"\nPredicted Class for the new sample: {d.target_names[clf.predict([X_te[0]])[0]].capitalize()}")

# Visual plot of the decision tree model
plt.figure(figsize=(12, 8))
plot_tree(clf, filled=True, feature_names=d.feature_names, class_names=d.target_names)
plt.title("Decision Tree - Breast Cancer Dataset"); plt.show()