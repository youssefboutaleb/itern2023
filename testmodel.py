import joblib
import numpy as np

# Load the trained model
model = joblib.load('model/logistic_regression_model.pkl')

# My train data is: costumer, GC, hourofday, minuteofhour, dayofweek, dayofmonth, monthofyear, year, Anomaly
# So to predict the anomaly, I use this dataEntry to test the model

dataEntry = np.array([[ 9, 5.071, 23, 30, 6, 30, 6, 2]])  # Reshape the input to a 2D array
prediction = model.predict(dataEntry)
print(prediction)
