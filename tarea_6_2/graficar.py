"""Curvas SVG reproducibles con biblioteca estándar, sin dependencias gráficas."""
import csv
from pathlib import Path
P=Path(__file__).resolve().parent
old=list(csv.DictReader((P.parent/'evidencia/curva_arbol.csv').open()))
new=list(csv.DictReader((P/'evidencia/curvas.csv').open()))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="420" viewBox="0 0 1100 420">',
 '<rect width="1100" height="420" fill="white"/>',
 '<g font-family="Arial" font-size="15" fill="#222">']
def text(x,y,t,size=20):svg.append(f'<text x="{x}" y="{y}" font-size="{size}">{t}</text>')
def panel(left,title,series):
 x=lambda n:left+(n-120)/680*430
 y=lambda v:310-(v-.5)/.5*245
 text(left,25,title,22)
 for v in [.5,.6,.7,.8,.9,1.0]:
  svg.append(f'<line x1="{left}" y1="{y(v)}" x2="{left+430}" y2="{y(v)}" stroke="#ddd"/>');text(left-37,y(v)+5,f'{v:.1f}')
 for n in [120,255,392,528,664,800]:text(x(n)-12,334,str(n),20)
 for name,values,col,dash in series:
  points=' '.join(f'{x(n)},{y(v)}' for n,v in values)
  svg.append(f'<polyline points="{points}" fill="none" stroke="{col}" stroke-width="3" stroke-dasharray="{dash}"/>')
  for n,v in values:svg.append(f'<circle cx="{x(n)}" cy="{y(v)}" r="3" fill="{col}"/>')
 for i,(name,_,col,dash) in enumerate(series):
  yy=360+i*20;svg.append(f'<line x1="{left}" y1="{yy}" x2="{left+25}" y2="{yy}" stroke="{col}" stroke-width="3" stroke-dasharray="{dash}"/>');text(left+33,yy+5,name,20)

panel(60,'6.1 Árbol sin afinar con 20 variables',[
 ('Entrenamiento',[(int(r['n']),float(r['train'])) for r in old],'#222','0'),
 ('Validación',[(int(r['n']),float(r['validacion'])) for r in old],'#176b9b','0')])
r=[r for r in new if r['modelo']=='Arbol afinado'];b=[r for r in new if r['modelo']=='Arbol por defecto']
panel(625,'6.2 Árbol afinado con 16 variables',[
 ('Entrenamiento afinado',[(int(a['n_train']),float(a['train_media'])) for a in r],'#222','0'),
 ('Validación afinado',[(int(a['n_train']),float(a['validacion_media'])) for a in r],'#176b9b','0'),
 ('Validación sin afinar (16 variables)',[(int(a['n_train']),float(a['validacion_media'])) for a in b],'#9b5924','6,4')])
svg.append('</g></svg>');(P/'figs/curvas.svg').write_text('\n'.join(svg))
