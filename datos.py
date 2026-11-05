"""Carga validada del CSV del curso; clase positiva = bad."""
from pathlib import Path
import pandas as pd
from sklearn.model_selection import StratifiedKFold
RUTA=Path(__file__).resolve().parent/'datos/credit_g.csv'
def cargar_datos(ruta=RUTA):
    df=pd.read_csv(ruta)
    if 'clase' not in df or df['clase'].isna().any() or not set(df['clase']).issubset({'good','bad'}):
        raise ValueError('La clase debe contener exclusivamente good/bad, sin nulos.')
    X=df.drop(columns='clase')
    y=df['clase'].eq('bad').astype(int)
    if X.isna().any().any():
        raise ValueError('Este experimento exige predictores sin nulos.')
    cols_cat=X.select_dtypes(exclude='number').columns.tolist()
    cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
    return X,y,cols_cat,cv
if __name__=='__main__':
    X,y,c,cv=cargar_datos(); print(X.shape,y.mean(),len(c))
