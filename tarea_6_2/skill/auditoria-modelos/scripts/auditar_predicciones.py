"""Verificación numérica reproducible; no sustituye la revisión semántica de la Skill."""
import argparse,csv,json,math
from pathlib import Path

def regresion(rows):
    if not rows: raise ValueError('Sin observaciones')
    y=[float(r['y_true']) for r in rows]; pred=[float(r['y_pred']) for r in rows]
    if not all(math.isfinite(v) for v in y+pred): raise ValueError('Valores no finitos')
    mse=sum((a-b)**2 for a,b in zip(y,pred))/len(y)
    media=sum(y)/len(y); sst=sum((a-media)**2 for a in y)
    return {'n':len(y),'MSE':mse,'RMSE':math.sqrt(mse),'R2':1-mse*len(y)/sst if sst else None,
            'sesgo':sum(a-b for a,b in zip(y,pred))/len(y),'predicciones_negativas':sum(v<0 for v in pred)}

def clasificacion(rows,positiva='0'):
    if not rows: raise ValueError('Sin observaciones')
    def pos(x): return str(x)==str(positiva)
    tp=sum(pos(r['y_true']) and pos(r['y_pred']) for r in rows)
    fn=sum(pos(r['y_true']) and not pos(r['y_pred']) for r in rows)
    fp=sum(not pos(r['y_true']) and pos(r['y_pred']) for r in rows)
    tn=len(rows)-tp-fn-fp
    div=lambda a,b:a/b if b else None
    return {'n':len(rows),'TP':tp,'FN':fn,'FP':fp,'TN':tn,'accuracy':div(tp+tn,len(rows)),
            'precision':div(tp,tp+fp),'recall':div(tp,tp+fn),'F1':div(2*tp,2*tp+fp+fn)}

def auditar(rows,tipo,positiva='0'):
    calc=regresion if tipo=='regresion' else lambda r:clasificacion(r,positiva)
    global_=calc(rows); grupos=[]
    for grupo in sorted(set(r.get('subgrupo','') for r in rows)):
        g=[r for r in rows if r.get('subgrupo','')==grupo]; m=calc(g)
        if tipo=='regresion':
            base=global_['RMSE']; v=m['RMSE']; dif=abs(v-base)/base if base else (0 if v==0 else None)
            soporte=len(g)>=20; umbral=.20
        else:
            base=global_['recall']; v=m['recall']; dif=abs(v-base) if base is not None and v is not None else None
            soporte=len(g)>=20 and m['TP']+m['FN']>=10; umbral=.10
        estado='NO SE PUEDE DETERMINAR' if not grupo or not soporte or dif is None else ('FALLA' if dif>umbral else 'PASA')
        grupos.append({'grupo':grupo,'metricas':m,'brecha':dif,'resultado':estado})
    return {'tipo':tipo,'global':global_,'subgrupos':grupos,'alcance':'Solo consistencia numérica y disparidad; partición y fuga requieren revisión de código.'}

if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('csv'); a.add_argument('--tipo',choices=['regresion','clasificacion'],required=True); a.add_argument('--positiva',default='0'); args=a.parse_args()
    with Path(args.csv).open(newline='') as f: rows=list(csv.DictReader(f))
    print(json.dumps(auditar(rows,args.tipo,args.positiva),indent=2,ensure_ascii=False,allow_nan=False))
