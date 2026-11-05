"""Experimento 6.2: configuración reproducible y sin predictores sensibles."""
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import fbeta_score, make_scorer
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parent
DATOS = ROOT.parent / 'datos' / 'credit_g.csv'
EXCLUIDAS = ['age', 'personal_status', 'housing', 'foreign_worker']
GRID = {'modelo__max_depth': [3, 5, 8, None],
        'modelo__min_samples_leaf': [1, 5, 10],
        'modelo__class_weight': [None, 'balanced']}
F2 = make_scorer(fbeta_score, beta=2, zero_division=0)

def cargar():
    df = pd.read_csv(DATOS)
    if df.isna().any().any() or set(df.clase) != {'good', 'bad'}:
        raise ValueError('Datos incompletos o etiquetas no esperadas')
    X = df.drop(columns=['clase', *EXCLUIDAS])
    return X, df.clase.eq('bad').astype(int), df[EXCLUIDAS].copy()

def cv_externa():
    return StratifiedKFold(5, shuffle=True, random_state=42)

def cv_interna():
    return StratifiedKFold(3, shuffle=True, random_state=17)

def pipeline(estimador, X):
    cat = X.select_dtypes(exclude='number').columns.tolist()
    prep = ColumnTransformer([('cat', OrdinalEncoder(
        handle_unknown='use_encoded_value', unknown_value=-1), cat)], remainder='passthrough')
    return Pipeline([('prep', prep), ('modelo', estimador)])

def busqueda(X):
    return GridSearchCV(pipeline(DecisionTreeClassifier(random_state=42), X), GRID,
                        scoring={'f2': F2, 'accuracy': 'accuracy'}, refit='f2',
                        cv=cv_interna(), n_jobs=1, error_score='raise', return_train_score=True)

def modelos(X):
    return {'Arbol por defecto': pipeline(DecisionTreeClassifier(random_state=42), X),
            'Arbol afinado': busqueda(X),
            'Random Forest': pipeline(RandomForestClassifier(n_estimators=100,
                class_weight='balanced', random_state=42, n_jobs=1), X),
            'Boosting': pipeline(HistGradientBoostingClassifier(
                random_state=42, early_stopping=False), X)}
