"""Configuraciones fijas; no se optimizan hiperparámetros en 6.1."""
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier,HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier

def crear_pipeline(modelo,cols_cat):
    encoder=OrdinalEncoder(handle_unknown='use_encoded_value',unknown_value=-1)
    prep=ColumnTransformer([('cat',encoder,cols_cat)],remainder='passthrough')
    return Pipeline([('prep',prep),('modelo',modelo)])

def tres_modelos():
    return {'Árbol':DecisionTreeClassifier(random_state=42),
            'Random Forest':RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=1),
            'Boosting':HistGradientBoostingClassifier(random_state=42)}
