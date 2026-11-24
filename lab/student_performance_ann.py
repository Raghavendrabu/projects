# ============================================================
# STUDENT PERFORMANCE PREDICTION USING DEEP LEARNING (ANN)
# Tanh + Sigmoid | BCE Loss | SGD Optimizer
# ============================================================

# ---------- 6.3.1 Import Libraries ----------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense

# ---------- 6.3.2 Create Dataset ----------
np.random.seed(42)
n = 500

data = pd.DataFrame({
    "Attendance":            np.random.randint(50, 101, n),
    "Internal_Marks":        np.random.randint(30, 101, n),
    "Assignment_Score":      np.random.randint(30, 101, n),
    "Study_Hours":           np.random.randint(1, 11, n),
    "Previous_Performance":  np.random.randint(30, 101, n)
})

# Create binary target: 1 = Pass, 0 = Fail
data["Pass_Fail"] = (
    (data["Attendance"] >= 75) &
    (data["Internal_Marks"] >= 40) &
    (data["Assignment_Score"] >= 40) &
    (data["Previous_Performance"] >= 40)
).astype(int)

print("Dataset shape:", data.shape)
print(data.head())
print("\nPass/Fail counts:\n", data["Pass_Fail"].value_counts())

# ---------- 6.3.3 Separate Features and Target ----------
X = data.drop("Pass_Fail", axis=1)
y = data["Pass_Fail"]

# ---------- 6.3.4 Split and Scale Data ----------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

print("\nTraining samples:", X_train.shape[0])
print("Testing samples :", X_test.shape[0])

# ---------- 6.3.5 Build ANN Model ----------
model = Sequential([
    Input(shape=(5,)),
    Dense(16, activation="tanh"),
    Dense(8,  activation="tanh"),
    Dense(1,  activation="sigmoid")
])

model.summary()

# ---------- 6.3.6 Compile and Train Model ----------
model.compile(
    optimizer=tf.keras.optimizers.SGD(learning_rate=0.01),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=16,
    validation_split=0.2,
    verbose=1
)

# ---------- 6.3.7 Evaluate Model ----------
test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
print("\nTest Loss:", test_loss)
print("Test Accuracy:", test_accuracy)

# ---------- 6.3.8 Generate Predictions ----------
y_pred_probability = model.predict(X_test)
y_pred = (y_pred_probability >= 0.5).astype(int).flatten()

# ---------- 6.3.9 Confusion Matrix and Classification Report ----------
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Fail", "Pass"]))

# ---------- 6.3.10 Save Model ----------
model.save("student_performance_model.keras")
print("\nModel saved as student_performance_model.keras")

# ============================================================
# VISUALIZATIONS (Section 7 & 8)
# ============================================================

# ---------- 7.1 Training Loss vs Epochs ----------
plt.figure(figsize=(7,4))
plt.plot(history.history["loss"])
plt.title("Training Loss vs Epochs")
plt.xlabel("Epochs")
plt.ylabel("Training Loss")
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------- 7.2 Validation Loss vs Epochs ----------
plt.figure(figsize=(7,4))
plt.plot(history.history["val_loss"], color="orange")
plt.title("Validation Loss vs Epochs")
plt.xlabel("Epochs")
plt.ylabel("Validation Loss")
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------- 7.3 Training Accuracy vs Epochs ----------
plt.figure(figsize=(7,4))
plt.plot(history.history["accuracy"], color="green")
plt.title("Training Accuracy vs Epochs")
plt.xlabel("Epochs")
plt.ylabel("Training Accuracy")
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------- 7.4 Validation Accuracy vs Epochs ----------
plt.figure(figsize=(7,4))
plt.plot(history.history["val_accuracy"], color="red")
plt.title("Validation Accuracy vs Epochs")
plt.xlabel("Epochs")
plt.ylabel("Validation Accuracy")
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------- 8.1 Confusion Matrix Heatmap ----------
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="rocket",
            xticklabels=["Fail", "Pass"],
            yticklabels=["Fail", "Pass"])
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()

# ---------- 8.2 Additional Metrics (Specificity) ----------
TN, FP, FN, TP = cm.ravel()
accuracy    = (TP + TN) / (TP + TN + FP + FN)
precision   = TP / (TP + FP) if (TP + FP) else 0
recall      = TP / (TP + FN) if (TP + FN) else 0
f1          = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
specificity = TN / (TN + FP) if (TN + FP) else 0

print("\n===== Performance Metrics =====")
print(f"Accuracy    : {accuracy*100:.2f}%")
print(f"Precision   : {precision*100:.2f}%")
print(f"Recall      : {recall*100:.2f}%")
print(f"F1-Score    : {f1*100:.2f}%")
print(f"Specificity : {specificity*100:.2f}%")
