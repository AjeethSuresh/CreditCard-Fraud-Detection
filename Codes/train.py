import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Load dataset
file_path = 'creditcard.csv'
df = pd.read_csv(file_path)

# Data preprocessing
# Remove duplicates and missing values
df = df.drop_duplicates()
df = df.dropna()

# Use only selected important features
# Based on updated credit_card_new.ipynb
selected_features = ['Time', 'Amount', 'V14', 'V17', 'V12']

X = df[selected_features]
y = df['Class']

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model with hyperparameters from notebook
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)

model.fit(X_train, y_train)

# Save model as specified in notebook
with open('fraud_model.pkl', 'wb') as file:
    pickle.dump(model, file)

print("Model saved successfully as fraud_model.pkl")
