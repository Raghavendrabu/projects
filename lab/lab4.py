import pandas as pd

# Load Find-S training CSV data
df = pd.read_csv(r'C:\Projects\lab\training_data.csv')
attrs, tgt, hyp, steps = df.columns[:-1], df.columns[-1], None, []

# Train hypothesis step-by-step
for index, r in df.iterrows():
    v = list(r[attrs])
    if str(r[tgt]).strip().lower() == 'yes': # generalize only from positive samples
        hyp = v.copy() if hyp is None else [hyp[i] if hyp[i] == v[i] else '?' for i in range(len(hyp))]
    steps.append(v + [r[tgt], hyp.copy() if hyp else None])

# Print progression table and final hypothesis
print("\nStep-by-step table:\n\n", pd.DataFrame(steps, columns=list(attrs) + ["play", "Hypothesis"]).to_string(index=False))
print("\nFinal hypothesis:", hyp)