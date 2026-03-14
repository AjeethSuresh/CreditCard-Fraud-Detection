import pandas as pd
df = pd.read_csv('creditcard.csv')
fraud = df[df['Class'] == 1]
print("Fraud summary for Time, Amount, V14, V17, V12:")
print(fraud[['Time', 'Amount', 'V14', 'V17', 'V12']].describe())
