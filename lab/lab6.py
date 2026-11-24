import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

print("Demonstrating Linear Regression using California Housing Dataset...\n")

# Prepare single feature (AveRooms) and split 80/20
h = fetch_california_housing(as_frame=True)
X_tr, X_te, y_tr, y_te = train_test_split(h.data[["AveRooms"]], h.target, test_size=0.2, random_state=42)

# Fit linear regression model and predict test set
pred = LinearRegression().fit(X_tr, y_tr).predict(X_te)

# Plot actual targets vs predicted line
plt.figure(figsize=(10, 6))
plt.scatter(X_te, y_te, color="blue", alpha=0.5, label="Actual Data")
plt.plot(X_te, pred, color="red", linewidth=2, label="Regression Line")
plt.xlim(0, 15); plt.xlabel("Average Number of Rooms (AveRooms)"); plt.ylabel("Median House Value ($100,000s)")
plt.title("Linear Regression - California Housing Dataset"); plt.legend();  plt.show()

# Print regression performance metrics
print(f"--- Model Evaluation ---\nMean Squared Error (MSE): {mean_squared_error(y_te, pred):.4f}\nR^2 Score (Coefficient of Determination): {r2_score(y_te, pred):.4f}")