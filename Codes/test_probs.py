import pickle
import numpy as np
import pandas as pd
from itertools import product

model = pickle.load(open('fraud_model.pkl', 'rb'))

amounts = [10.0, 100.0, 1000.0, 5000.0]
times = [2.0, 12.0, 23.0]
tx_types = ["Online", "POS"]
risks = ["Low", "Medium", "High"]

results = []
for amount, time_val, tx_type, risk in product(amounts, times, tx_types, risks):
    tx_type_mapped = 1 if tx_type == "Online" else 0
    risk_mapping = {"Low": 0, "Medium": 1, "High": 2}
    loc_risk_mapped = risk_mapping.get(risk, 0)
    
    input_data = np.array([[time_val, amount, tx_type_mapped, loc_risk_mapped, 0.0]])
    
    if hasattr(model, "predict_proba"):
        prob = model.predict_proba(input_data)[0][1] * 100
    else:
        prob = 0.0
        
    results.append({
        "Amount": amount,
        "Time": time_val,
        "Transaction_Type": tx_type,
        "Location_Risk": risk,
        "Probability": prob
    })

df = pd.DataFrame(results)
print("Low Risk:")
print(df[df['Probability'] <= 30].head(5))
print("\nMedium Risk:")
print(df[(df['Probability'] > 30) & (df['Probability'] <= 70)].head(5))
print("\nHigh Risk:")
print(df[df['Probability'] > 70].head(5))

# Let's also check boundaries if any probability is > 30 at all.
print("\nMax Probability:", df['Probability'].max())
print("Min Probability:", df['Probability'].min())

# Generate a CSV with some synthetic data that forces high probability by tweaking inputs directly if mapping doesn't work.
