"""CV estratificada y sensibilidad a diez particiones 75/25."""
import numpy as np
from sklearn.base import clone
from sklearn.metrics import recall_score
from sklearn.model_selection import cross_val_score,cross_val_predict,train_test_split

def validar(pipeline,X,y,cv):
    s=cross_val_score(pipeline,X,y,cv=cv,scoring='accuracy',n_jobs=1)
    return s.mean(),s.std(ddof=0)

def proporcion_malos_detectados(pipeline,X,y,cv):
    pred=cross_val_predict(pipeline,X,y,cv=cv,n_jobs=1)
    return recall_score(y,pred,zero_division=0)

def particion_unica(pipeline,X,y,semillas=range(10)):
    scores=[]
    for seed in semillas:
        a,b=train_test_split(np.arange(len(y)),test_size=.25,stratify=y,random_state=seed)
        m=clone(pipeline).fit(X.iloc[a],y.iloc[a])
        scores.append(m.score(X.iloc[b],y.iloc[b]))
    return np.array(scores)
