import numpy as np
import pandas as pd

import seaborn as sns
import sklearn
from sklearn import svm
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
import pickle

with open('svm_f_regression','rb') as f:
    model = pickle.load(f)

x_test = pd.read_csv('x_test_f_regression.csv').values
y_test = pd.read_csv('y_test.csv')

y_test_predict = model.predict(x_test)
mse = mean_squared_error(y_test,y_test_predict)
mae = mean_absolute_error(y_test,y_test_predict)
r2 = r2_score(y_test,y_test_predict)
print('\nPrediction scores for SVM using f-regression:')
print('Mean Squared error:',mse)
print('Mean Absolute error:',mae)
print('R^2:',r2)
print(y_test_predict)
