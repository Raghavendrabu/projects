import pandas as pd

# Load weather dataset and compute min-max normalized values
df = pd.read_csv(r'C:\Projects\lab\weather.csv')
print("--- Original Data ---\n", df)
print("\n--- Normalized Data ---\n", (df - df.min()) / (df.max() - df.min()))
