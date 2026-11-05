"""Ejecutar: python tarea_6_2/experimento.py. No modifica la evidencia 6.1."""
import hashlib
import json
import platform
import time
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score, fbeta_score
from sklearn.model_selection import learning_curve
from threadpoolctl import threadpool_limits
from modelo import ROOT, DATOS, EXCLUIDAS, GRID, cargar, cv_externa, cv_interna, modelos, busqueda

EV = ROOT / 'evidencia'
def guardar(nombre, dato):
    (EV/nombre).write_text(json.dumps(dato, ensure_ascii=False, indent=2, allow_nan=False)+'\n')

def metricas(y, pred):
    return {'accuracy': accuracy_score(y,pred), 'recall_bad': recall_score(y,pred),
            'precision_bad': precision_score(y,pred,zero_division=0),
            'f1_bad': f1_score(y,pred,zero_division=0),
            'f2_bad': fbeta_score(y,pred,beta=2,zero_division=0),
            'matriz_0_good_1_bad': confusion_matrix(y,pred,labels=[0,1]).tolist()}

def ejecutar():
    EV.mkdir(exist_ok=True)
    X,y,grupos = cargar(); splits=list(cv_externa().split(X,y))
    protocolos=[]; filas=[]; resultados=[]; predicciones=[]
    for fold,(tr,te) in enumerate(splits):
        protocolos.append({'fold':fold,'train':tr.tolist(),'test':te.tolist(),
          'inner':[{'train':tr[a].tolist(),'validacion':tr[b].tolist()}
                   for a,b in cv_interna().split(X.iloc[tr],y.iloc[tr])]})
    guardar('particiones.json',protocolos)
    for nombre,est in modelos(X).items():
        oof=np.full(len(y),-1); tiempos=[]; exactitudes=[]; f2s=[]; train_acc=[]
        for fold,(tr,te) in enumerate(splits):
            m=clone(est); start=time.perf_counter(); m.fit(X.iloc[tr],y.iloc[tr]); dt=time.perf_counter()-start
            pred=m.predict(X.iloc[te]); oof[te]=pred
            met=metricas(y.iloc[te],pred); tiempos.append(dt); exactitudes.append(met['accuracy']);f2s.append(met['f2_bad'])
            ta=accuracy_score(y.iloc[tr],m.predict(X.iloc[tr])); train_acc.append(ta)
            registro={'modelo':nombre,'fold':fold,'n_train':len(tr),'n_test':len(te),'ajuste_s':dt,'accuracy_train':ta,**met}
            if nombre=='Arbol afinado':
                registro.update({'ganador':m.best_params_,'mejor_f2_interno':m.best_score_,
                                 'refit_configuracion_s':m.refit_time_})
                pd.DataFrame(m.cv_results_).to_csv(EV/f'grid_fold_{fold}.csv',index=False)
            filas.append(registro)
        res={'modelo':nombre,'accuracy_media':float(np.mean(exactitudes)),
             'accuracy_de':float(np.std(exactitudes)), 'f2_media':float(np.mean(f2s)),
             'f2_de':float(np.std(f2s)), 'ajuste_s_media':float(np.mean(tiempos)),
             'accuracy_train_media':float(np.mean(train_acc)), **metricas(y,oof)}
        resultados.append(res)
        for i in range(len(y)):
            predicciones.append({'modelo':nombre,'fila':i,'y_true':int(y.iloc[i]),'y_pred':int(oof[i]),
                                 **grupos.iloc[i].to_dict()})
        print(nombre, res, flush=True)
    # Ajuste global solo para documentar ganador; nunca se usa para calcular OOF.
    grid=busqueda(X);t=time.perf_counter();grid.fit(X,y);tiempo=time.perf_counter()-t
    pd.DataFrame(grid.cv_results_).to_csv(EV/'grid_global.csv',index=False)
    candidatos=[r for r in resultados if r['modelo']!='Arbol por defecto']
    elegido=sorted(candidatos,key=lambda r:(-r['f2_media'],r['ajuste_s_media']))[0]['modelo']
    resumen={'fecha':'2026-11-05','python':platform.python_version(),'sklearn':sklearn.__version__,
        'numpy':np.__version__,'pandas':pd.__version__,'sha256_dataset':hashlib.sha256(DATOS.read_bytes()).hexdigest(),
        'sha256_plan':hashlib.sha256((ROOT/'PLAN.md').read_bytes()).hexdigest(),
        'excluidas':EXCLUIDAS,'predictores':X.columns.tolist(),'grid':GRID,'metrica_busqueda':'F2 bad',
        'ganador_global':grid.best_params_,'f2_aparente_global':grid.best_score_,
        'accuracy_aparente_global':float(grid.cv_results_['mean_test_accuracy'][grid.best_index_]),
        'busqueda_global_s':tiempo,'refit_global_s':grid.refit_time_,
        'modelo_elegido':elegido,'resultados':resultados}
    guardar('resultados.json',resumen);guardar('metricas_folds.json',filas)
    pd.DataFrame(predicciones).to_csv(EV/'predicciones_oof.csv',index=False)
    print('Modelo elegido por F2 externo:',elegido,flush=True)
    # Curva del procedimiento elegido: si es búsqueda, se repite dentro de cada subconjunto.
    curvas=[]
    for nombre in dict.fromkeys([elegido,'Arbol por defecto']):
        n,train,val=learning_curve(modelos(X)[nombre],X,y,cv=splits,
            train_sizes=np.linspace(.15,1,6),scoring='accuracy',shuffle=True,random_state=42,n_jobs=1,error_score='raise')
        for i,size in enumerate(n):
            curvas.append({'modelo':nombre,'n_train':int(size),'train_media':float(train[i].mean()),
              'train_de':float(train[i].std()),'validacion_media':float(val[i].mean()),'validacion_de':float(val[i].std())})
    pd.DataFrame(curvas).to_csv(EV/'curvas.csv',index=False)
    seleccion=pd.DataFrame(predicciones);seleccion=seleccion[seleccion.modelo==elegido].copy()
    seleccion['subgrupo']=seleccion.housing
    seleccion.to_csv(EV/'predicciones_auditoria.csv',index=False)

if __name__=='__main__':
    with threadpool_limits(limits=1): ejecutar()
