import pandas as pd
import numpy as np
import seaborn as sns
import datetime as dt
import time
import matplotlib.pyplot as plt
import matplotlib as mpl
import pybaseball
from pybaseball import lahman
from pybaseball import retrosheet
import mlbgame
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from scipy import stats

start_time = time.time()

path = "/Users/ryangerda/PycharmProjects/DFS_Baseball/DFS_Baseball/Salary_Database_2014_2020.xlsx"
salary = pd.read_excel(path, nrows=100)

d2 = salary[['Player','Points','Salary']]
d2 = d2.set_index('Player')
d2 = d2.fillna(d2.mean())
train_set, test_set = train_test_split(d2, test_size=0.2, random_state=42)
player = train_set.drop('Points',axis=1)
player_labels = train_set['Points'].copy()
player_num = player
player_cat = [['']]
num_pipeline = Pipeline([('imputer',SimpleImputer(strategy='median')),('std_scaler',StandardScaler()),])
player_num_tr = num_pipeline.fit_transform(player_num)
num_attribs = list(player_num)
full_pipeline = ColumnTransformer([
    ('num',num_pipeline,num_attribs)])
player_prepared = full_pipeline.fit_transform(player)


lin_reg = LinearRegression()
lin_reg.fit(player_prepared,player_labels)

some_data = player.iloc[:5]
some_labels = player_labels.iloc[:5]
some_data_prepared = full_pipeline.transform(some_data)
print('predictions:',lin_reg.predict(some_data_prepared))
print('labels:',list(some_labels))

player_predictions = lin_reg.predict(player_prepared)
lin_mse = mean_squared_error(player_labels,player_predictions)
lin_rmse = np.sqrt(lin_mse)
print(lin_rmse)

tree_reg = DecisionTreeRegressor()
tree_reg.fit(player_prepared,player_labels)
tree_reg_predictions = tree_reg.predict(player_prepared)
tree_mse = mean_squared_error(player_labels,tree_reg_predictions)
tree_rmse = np.sqrt(tree_mse)
print(tree_rmse)

scores = cross_val_score(tree_reg,player_prepared,player_labels,scoring='neg_mean_squared_error',cv=5)
tree_rmse_scores = np.sqrt(-scores)

def display_scores(scores):
    print('Scores:',scores)
    print('Mean:',scores.mean())
    print('Standard Deviation:',scores.std())
print(display_scores(tree_rmse_scores))

lin_scores = cross_val_score(lin_reg,player_prepared,player_labels,scoring='neg_mean_squared_error',cv=5)
lin_rmse_scores = np.sqrt(-lin_scores)
print(display_scores(lin_rmse_scores))

forest_reg = RandomForestRegressor()
forest_reg.fit(player_prepared,player_labels)

forest_scores = cross_val_score(forest_reg,player_prepared,player_labels,scoring='neg_mean_squared_error',cv=5)
forest_rmse_scores = np.sqrt(-forest_scores)
print(display_scores(forest_rmse_scores))

param_grid = [{'n_estimators':[3,10,30,50,75],'max_features':[2,4,6,8,10,12]},
              {'bootstrap':[False],'n_estimators':[3,10,30,50,75],'max_features':[2,3,4,6,8]},]
grid_search = GridSearchCV(forest_reg,param_grid,cv=5,scoring='neg_mean_squared_error',return_train_score=True)
grid_search.fit(player_prepared,player_labels)
grid_search.best_params_

cvres = grid_search.cv_results_
for mean_score, params in zip(cvres['mean_test_score'],cvres['params']):
    print(np.sqrt(-mean_score),params)

feature_importances = grid_search.best_estimator_.feature_importances_
print(feature_importances)

attributes = num_attribs# + cat_attribs
print(sorted(zip(feature_importances,attributes),reverse=True))

#forst = Mean: 5.002738927741765
# lin reg = Mean: 4.454555242949654
# tree Mean: 7.041815695862683

final_model = grid_search.best_estimator_
X_test = test_set.drop('Points',axis=1)
y_test = test_set['Points'].copy()
X_test_prepared = full_pipeline.transform(X_test)
final_predictions = final_model.predict((X_test_prepared))
final_mse = mean_squared_error(y_test,final_predictions)
final_rmse = np.sqrt(final_mse)

confidence = 0.95
squared_errors = (final_predictions - y_test) ** 2
interval = np.sqrt(stats.t.interval(confidence,len(squared_errors) - 1, loc=squared_errors.mean(),scale=stats.sem(squared_errors)))
print(interval)



print("--- %s minutes ---" % ((time.time() - start_time)/60))