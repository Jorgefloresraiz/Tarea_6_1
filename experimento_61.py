"""Genera evidencia de CV y particiones. No usa los valores de ejemplo de la guía."""
from pathlib import Path
import json,hashlib,platform,time
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import cross_validate,learning_curve
from sklearn.metrics import accuracy_score,recall_score,precision_score,f1_score,confusion_matrix
from datos import cargar_datos,RUTA
from modelos import crear_pipeline,tres_modelos
from validacion import particion_unica
ROOT=Path(__file__).resolve().parent

def ejecutar():
    out=ROOT/'evidencia';out.mkdir(exist_ok=True)
    X,y,cats,cv=cargar_datos();splits=list(cv.split(X,y))
    (out/'pliegues.json').write_text(json.dumps([{'entrenamiento':a.tolist(),'validacion':b.tolist()} for a,b in splits]))
    rows=[];folds=[];oof=[];parts=[]
    for name in ['Árbol','Random Forest']:
        pipe=crear_pipeline(tres_modelos()[name],cats)
        run=cross_validate(pipe,X,y,cv=splits,scoring='accuracy',return_train_score=True,return_estimator=True,n_jobs=1)
        pred=np.full(len(y),-1,dtype=int)
        for i,((train,test),model) in enumerate(zip(splits,run['estimator'])):
            pred[test]=model.predict(X.iloc[test])
            folds.append({'modelo':name,'pliegue':i,'accuracy':float(run['test_score'][i]),'accuracy_train':float(run['train_score'][i]),'segundos_fit':float(run['fit_time'][i])})
        assert (pred>=0).all()
        scores=particion_unica(pipe,X,y)
        for i,s in enumerate(scores):parts.append({'modelo':name,'semilla':i,'accuracy':float(s)})
        rows.append({'modelo':name,'accuracy_media':float(run['test_score'].mean()),'accuracy_std':float(run['test_score'].std()),'recall_bad_oof':float(recall_score(y,pred)),'precision_bad_oof':float(precision_score(y,pred,zero_division=0)),'f1_bad_oof':float(f1_score(y,pred)),'train_media':float(run['train_score'].mean()),'particion_min':float(scores.min()),'particion_max':float(scores.max()),'particion_rango':float(np.ptp(scores)),'fit_segundos_media':float(run['fit_time'].mean()),'matriz_confusion':confusion_matrix(y,pred,labels=[0,1]).tolist()})
        for i in range(len(y)):
            oof.append({'fila':i,'modelo':name,'y_true':int(y.iloc[i]),'y_pred':int(pred[i]),'housing':X.iloc[i]['housing'],'personal_status':X.iloc[i]['personal_status']})
        print(name,rows[-1],flush=True)
    # Diagnóstico inicial para enlazar 6.2, sin seleccionar modelos con estas curvas.
    pipe=crear_pipeline(tres_modelos()['Árbol'],cats)
    sizes,tr,va=learning_curve(pipe,X,y,cv=splits,train_sizes=np.linspace(.15,1,6),scoring='accuracy',shuffle=True,random_state=42,n_jobs=1)
    curve=[{'n':int(n),'train':float(t),'validacion':float(v)} for n,t,v in zip(sizes,tr.mean(1),va.mean(1))]
    result={'configuracion':{'n_splits':5,'semilla':42,'semillas_particiones':list(range(10)),'clase_positiva':'bad','std_ddof':0,'baseline_accuracy':float(1-y.mean()),'baseline_recall_bad':0.0},'modelos':rows,'curva_arbol':curve,'entorno':{'python':platform.python_version(),'sklearn':sklearn.__version__,'pandas':pd.__version__,'numpy':np.__version__},'sha256_dataset':hashlib.sha256(RUTA.read_bytes()).hexdigest()}
    (out/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    for name,content in [('pliegues_metricas',folds),('predicciones_oof',oof),('particiones',parts),('curva_arbol',curve)]:pd.DataFrame(content).to_csv(out/(name+'.csv'),index=False)
    tabla=pd.DataFrame(oof)
    groups=[]
    for model,df in tabla.groupby('modelo'):
        for col in ['housing','personal_status']:
            for grupo,g in df.groupby(col):
                groups.append({'modelo':model,'variable':col,'grupo':grupo,'n':len(g),'bad_reales':int(g.y_true.sum()),'accuracy':accuracy_score(g.y_true,g.y_pred),'recall_bad':recall_score(g.y_true,g.y_pred,zero_division=0)})
    pd.DataFrame(groups).to_csv(out/'subgrupos.csv',index=False)
    lines=['# Resultados del ingeniero de modelos','', '| Modelo | Accuracy media | DE | Recall bad OOF | Partición mín.–máx. |','|---|---:|---:|---:|---|']
    for r in rows:lines.append(f"| {r['modelo']} | {r['accuracy_media']:.3f} | {r['accuracy_std']:.3f} | {r['recall_bad_oof']:.3f} | {r['particion_min']:.3f}–{r['particion_max']:.3f} |")
    lines+=['','Mismos cinco pliegues estratificados, semilla 42. Positivo=bad. DE descriptiva entre pliegues (ddof=0), no intervalo de confianza. Recall calculado agrupando las predicciones fuera de pliegue.','', 'Diez particiones 75/25 con semillas 0–9; misma partición para ambos modelos en cada semilla. Rango y DE son medidas distintas, no una prueba de superioridad estadística de CV.','', 'Se conserva OrdinalEncoder del kit: asigna un orden artificial a categorías nominales. No se ajustó fuera del Pipeline. Incluye edad/personal_status/foreign_worker como predictores para reproducir el ejercicio; no se describe un modelo autorizado para decisiones reales.','', 'Accuracy del baseline siempre good: 0.700; recall bad: 0.000. Mejor accuracy no implica mejor detección de bad. No se hizo búsqueda ni recomendación de producción. El test independiente de 6.2 queda pendiente.','', 'Evidencia: evidencia/resultados.json, pliegues.json, predicciones_oof.csv, particiones.csv, subgrupos.csv.']
    (ROOT/'RESULTADOS.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':ejecutar()
