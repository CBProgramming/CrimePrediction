import numpy as np
import pandas as pd
import sklearn

print(np.__version__)
print(pd.__version__)
print(sklearn.__version__)

df = pd.read_csv('finalised_data.csv')
print(df.describe())
