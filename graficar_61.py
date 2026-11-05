"""Gráfica reproducible del diagnóstico del árbol, sin paquetes adicionales."""
from pathlib import Path
import json
p=Path(__file__).resolve().parent
r=json.loads((p/'evidencia/resultados.json').read_text())
c=r['curva_arbol'];out=p/'figs';out.mkdir(exist_ok=True)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600"><rect width="1200" height="600" fill="white"/><g font-family="Arial,sans-serif" font-size="22" fill="#222">','<text x="100" y="40">Curva de aprendizaje del árbol sin límite de profundidad</text>']
x=lambda n:100+(n-c[0]['n'])/(c[-1]['n']-c[0]['n'])*1000
y=lambda a:490-(a-.4)/.65*380
for i in range(7):
 a=.4+i*.1;s.append(f'<path d="M100 {y(a)}H1100" stroke="#ddd"/><text x="35" y="{y(a)+7}">{a:.1f}</text>')
for key,color,label in [('train','#205b8f','Entrenamiento'),('validacion','#b24d16','Validación')]:
 pts=' '.join(f'{x(v["n"])},{y(v[key])}' for v in c);s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="4"/>')
 for v in c:s.append(f'<circle cx="{x(v["n"])}" cy="{y(v[key])}" r="6" fill="{color}"/>')
for v in c:s.append(f'<text x="{x(v["n"])-20}" y="525">{v["n"]}</text>')
s+=['<text x="400" y="565">Casos de entrenamiento por pliegue</text>','<text x="100" y="85" fill="#205b8f">Entrenamiento</text><text x="400" y="85" fill="#b24d16">Validación</text><text x="680" y="85">Accuracy media de 5 pliegues</text>','</g></svg>']
(out/'curva_arbol.svg').write_text('\n'.join(s))
