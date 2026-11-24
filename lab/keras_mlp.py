import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense

# 1. Load Dataset (Iris dataset: 4 features, 3 classes)
iris = load_iris()
X = iris.data
y = iris.target

# 2. Split into Train & Test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Standardize features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 4. Define Keras MLP Model
model = Sequential([
    Input(shape=(4,)),
    Dense(16, activation='relu'),
    Dense(8, activation='relu'),
    Dense(3, activation='softmax')
])

# 5. Compile Model
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("\n--- Model Summary ---")
model.summary()

# 6. Train Model
print("\n--- Training Model ---")
history = model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.1, verbose=1)

# 7. Evaluate on Test Set
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"\n--- Evaluation Results ---")
print(f"Test Loss:     {loss:.4f}")
print(f"Test Accuracy: {accuracy * 100:.2f}%")
print("Features:", iris.feature_names)

