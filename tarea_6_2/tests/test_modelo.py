"""Pruebas pytest del protocolo y de sus resultados, sin exigir mejoras inventadas."""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import GridSearchCV, ParameterGrid
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from modelo import EXCLUIDAS, GRID, cargar, busqueda, modelos, pipeline

@pytest.fixture(scope='module')
def evidencia():
    return json.loads((ROOT/'evidencia/resultados.json').read_text())

def test_variables_sensibles_y_objetivo_excluidos():
    X,y,g=cargar()
    assert X.shape==(1000,16)
    assert set(X.columns).isdisjoint([*EXCLUIDAS,'clase'])
    assert set(g.columns)==set(EXCLUIDAS)
    assert y.sum()==300
    assert not X.join(g).assign(clase=y).duplicated().any()

def test_particiones_internas_no_tocan_test_externo():
    folds=json.loads((ROOT/'evidencia/particiones.json').read_text())
    todos=[]
    for f in folds:
        tr,te=set(f['train']),set(f['test'])
        assert not tr & te
        assert len(tr)==800 and len(te)==200
        interno=[]
        for i in f['inner']:
            a,b=set(i['train']),set(i['validacion'])
            assert not a & b and a|b==tr
            assert not (a|b)&te
            interno.extend(b)
        assert sorted(interno)==sorted(tr)
        todos.extend(te)
    assert sorted(todos)==list(range(1000))

def test_busqueda_dentro_del_procedimiento_y_24_candidatos():
    X,_,_=cargar(); m=modelos(X)['Arbol afinado']
    assert isinstance(m,GridSearchCV)
    assert m.refit=='f2'
    assert len(list(ParameterGrid(GRID)))==24
    assert 'prep' in m.estimator.named_steps
    assert m.cv.n_splits==3

def test_encoder_no_aprende_categoria_exclusiva_de_validacion():
    X=pd.DataFrame({'cat':['a','b','a','b'],'numero':[1,2,3,4]})
    m=pipeline(DecisionTreeClassifier(random_state=42),X).fit(X,[0,1,0,1])
    encoder=m.named_steps['prep'].named_transformers_['cat']
    antes=[c.copy() for c in encoder.categories_]
    nueva=pd.DataFrame({'cat':['solo_test'],'numero':[5]})
    assert m.named_steps['prep'].transform(nueva)[0,0]==-1
    for a,b in zip(antes,encoder.categories_): np.testing.assert_array_equal(a,b)

def test_metricas_externas_recalculadas_por_conteos(evidencia):
    p=pd.read_csv(ROOT/'evidencia/predicciones_oof.csv')
    folds=json.loads((ROOT/'evidencia/metricas_folds.json').read_text())
    for r in evidencia['resultados']:
        g=p[p.modelo==r['modelo']].sort_values('fila')
        assert len(g)==1000 and g.fila.nunique()==1000
        tp=int(((g.y_true==1)&(g.y_pred==1)).sum())
        fn=int(((g.y_true==1)&(g.y_pred==0)).sum())
        fp=int(((g.y_true==0)&(g.y_pred==1)).sum())
        tn=len(g)-tp-fn-fp
        assert r['matriz_0_good_1_bad']==[[tn,fp],[fn,tp]]
        assert r['accuracy']==pytest.approx((tp+tn)/1000)
        assert r['recall_bad']==pytest.approx(tp/(tp+fn))
        assert r['f2_bad']==pytest.approx(5*tp/(5*tp+4*fn+fp))
        valores=[f['accuracy'] for f in folds if f['modelo']==r['modelo']]
        assert r['accuracy_media']==pytest.approx(np.mean(valores))
        assert r['accuracy_de']==pytest.approx(np.std(valores,ddof=0))

def test_evidencia_de_busquedas_independientes(evidencia):
    folds=json.loads((ROOT/'evidencia/metricas_folds.json').read_text())
    afinado=[f for f in folds if f['modelo']=='Arbol afinado']
    assert len(afinado)==5
    for f in afinado:
        tabla=pd.read_csv(ROOT/f"evidencia/grid_fold_{f['fold']}.csv")
        assert len(tabla)==24
        assert f['mejor_f2_interno']==pytest.approx(tabla.mean_test_f2.max())
        assert f['n_train']==800 and f['n_test']==200
        assert f['refit_configuracion_s']>0
    # Reentrenamiento independiente del primer fold, sin usar el ganador global.
    X,y,_=cargar()
    part=json.loads((ROOT/'evidencia/particiones.json').read_text())[0]
    m=busqueda(X).fit(X.iloc[part['train']],y.iloc[part['train']])
    assert m.best_params_==afinado[0]['ganador']
    p=pd.read_csv(ROOT/'evidencia/predicciones_oof.csv')
    p=p[p.modelo=='Arbol afinado'].set_index('fila')
    np.testing.assert_array_equal(m.predict(X.iloc[part['test']]),p.loc[part['test'],'y_pred'])

def test_subgrupos_con_soporte_y_alertas_sin_ocultar():
    d=json.loads((ROOT/'evidencia/auditoria_numerica.json').read_text())
    global_recall=d['global']['recall']
    assert d['global']['n']==1000
    assert sum(g['metricas']['n'] for g in d['subgrupos'])==1000
    for g in d['subgrupos']:
        m=g['metricas']; soporte=m['n']>=20 and m['TP']+m['FN']>=10
        assert g['brecha']==pytest.approx(abs(m['recall']-global_recall))
        esperado=('FALLA' if g['brecha']>.10 else 'PASA') if soporte else 'NO SE PUEDE DETERMINAR'
        assert g['resultado']==esperado

def test_seleccion_respeta_f2_y_declara_costo_en_accuracy(evidencia):
    r={m['modelo']:m for m in evidencia['resultados']}
    ganador=max((m for m in evidencia['resultados'] if m['modelo']!='Arbol por defecto'),key=lambda m:m['f2_media'])
    assert evidencia['modelo_elegido']==ganador['modelo']
    # Controles de la conclusión en este conjunto fijo: no son garantía para datos futuros.
    assert r['Arbol afinado']['recall_bad']>r['Arbol por defecto']['recall_bad']
    assert r['Arbol afinado']['accuracy_media']<.70
