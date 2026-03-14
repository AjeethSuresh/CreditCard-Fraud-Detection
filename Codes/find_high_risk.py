import pickle
import numpy as np

model = pickle.load(open('fraud_model.pkl', 'rb'))

def get_prob(amount, time_val, tx, loc, v12=0.0):
    input_data = np.array([[time_val, amount, tx, loc, v12]])
    return model.predict_proba(input_data)[0][1] * 100

best_prob = 0
best_params = None

# Grid search for amounts up to 10000000
for amount in [0, 10, 100, 1000, 10000, 100000, 1000000]:
    for time_val in [0, 12, 23]:
        for tx in [0, 1]:
            for loc in [0, 1, 2]:
                prob = get_prob(amount, time_val, tx, loc)
                if prob > best_prob:
                    best_prob = prob
                    best_params = (amount, time_val, tx, loc)

print("Best Probability with v12=0.0:", best_prob)
print("Params:", best_params)

# If best_prob < 30, it's impossible to get medium/high risk with just amount/time.
