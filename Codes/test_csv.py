import pandas as pd
from app import predict_fraud

df = pd.read_csv('sample_transactions.csv')
results = []
for index, row in df.iterrows():
    pred, prob = predict_fraud(row['Amount'], row['Time'], row['Transaction_Type'], row['Location_Risk'])
    
    risk_level = "Low Risk"
    if prob > 70:
        risk_level = "High Risk"
    elif prob > 30:
        risk_level = "Medium Risk"
        
    results.append({
        "Amount": row['Amount'],
        "Location_Risk": row['Location_Risk'],
        "Prob": f"{prob:.2f}%",
        "Risk": risk_level
    })
    
print(pd.DataFrame(results))
