# Tarea 6.2 Optimización y auditoría del modelo

Continuación de [Tarea 6.1](../README.md), en el mismo repositorio y con el mismo `datos/credit_g.csv`. Autor: Jorge Josué Flores González. Se conserva intacta la evidencia 6.1; el punto de entrada nuevo es `tarea_6_2/experimento.py`.

## Entrega
- [Informe Word APA](documentos/Informe_Tarea_6_2.docx): portada, tres páginas de contenido y referencias.
- [Bitácora Word](documentos/Bitacora_Tarea_6_2.docx).
- [Auditoría](AUDIT_REPORT.md), [Skill original del Módulo 4](skill/auditoria-modelos/SKILL.md) y [pruebas pytest](tests/test_modelo.py).
- Repositorio: https://github.com/Jorgefloresraiz/Tarea_6_1/tree/main/tarea_6_2

## Reproducir desde la raíz del repositorio
Entorno probado: Python3.14.4. No requiere API, clave, Matplotlib ni conexión externa durante el análisis. Instalación de dependencias desde PyPI:
```bash
python3 -m venv .venv62
source .venv62/bin/activate
python -m pip install -r tarea_6_2/requirements.txt
python tarea_6_2/experimento.py
python tarea_6_2/skill/auditoria-modelos/scripts/auditar_predicciones.py tarea_6_2/evidencia/predicciones_auditoria.csv --tipo clasificacion --positiva 1 > tarea_6_2/evidencia/auditoria_numerica.json
python -m pytest tarea_6_2/tests -v
python tarea_6_2/graficar.py
```
El último paso genera SVG. El PNG incluido es la misma figura rasterizada para el informe. Las salidas numéricas se regeneran; los tiempos dependen del equipo. La auditoría semántica escrita no se regenera automáticamente con el script numérico.

## Diseño y resultado
`PLAN.md` fija la rejilla y la métrica antes de ejecutar: 24 combinaciones de profundidad, hoja mínima y pesos de clases, seleccionadas por F2 de bad. Se excluyen age, personal_status, housing y foreign_worker de los predictores. Vivienda se usa solo para auditar.

Cinco pliegues externos estratificados compartidos; la búsqueda del árbol usa tres pliegues internos. El encoder está dentro del Pipeline. La configuración global (balanced, profundidad5, hoja10) no se usa para producir las predicciones externas. Su F2 aparente es0.6732; el F2 anidado medio es0.6490. No se interpreta la diferencia como estimación pura de optimismo ni se equipara la media de F2 por fold con F2 agregado.

| Modelo | Accuracy media | DE | Recall bad agregado | F2 medio | Ajuste medio s |
|---|---:|---:|---:|---:|---:|
| Árbol por defecto |0.697|0.0144|0.5167|0.5119|0.0052|
| Árbol afinado |0.666|0.0297|0.7233|0.6490|0.7899|
| Random Forest |0.740|0.0288|0.5800|0.5763|0.0828|
| HistGradientBoosting |0.761|0.0229|0.5200|0.5375|0.0670|

El tiempo del afinado incluye búsqueda y refit. El refit global con configuración fijada tomó0.0048s. Todos los modelos se midieron con un hilo. DE es dispersión descriptiva entre pliegues, no intervalo de confianza.

El árbol afinado mejora F2 y recall, **no exactitud**: pierde3.1pp frente al árbol por defecto con las mismas entradas. Su exactitud queda bajo el baseline siempre good (70%, recall0). Se recomienda como candidato para piloto supervisado por el objetivo de detección de bad, sujeto a confirmar costos. Frente a RF evita43FN y añade117FP; el costo total solo mejora si costo(FN)/costo(FP)>2.72, suponiendo costos constantes. F2 no certifica esa relación.

## Curvas y límites
La curva elegida repite GridSearchCV dentro de cada subconjunto. Su extremo puede diferir de la comparación principal debido al barajado de filas y a los pliegues internos. Brecha final0.0555 frente a0.302 en6.1. Se incorpora también un control sin afinar con16 variables (brecha0.303). No se promete que añadir datos mejorará el resultado.

La selección entre familias es exploratoria y no tiene una evaluación externa posterior. El CSV carece de fechas e identificadores de persona; no permite certificar independencia de entidades ni generalización temporal. Excluir cuatro columnas no elimina proxies ni garantiza equidad. Housing pasa el criterio descriptivo de la Skill, pero no representa todos los atributos o intersecciones. No usar este prototipo para aprobar o rechazar créditos reales sin validación nueva, costos acordados y supervisión.

## Evidencia y cobertura de la consigna
| Requisito | Evidencia |
|---|---|
| Rejilla, ganador y comparación por defecto | modelo.py; evidencia/grid_global.csv; resultados.json |
| Número honesto anidado | experimento.py; particiones.json; grid_fold_0.csv a grid_fold_4.csv |
| Tres modelos con mismo protocolo | metricas_folds.json; predicciones_oof.csv |
| Curvas comparadas con6.1 | figs/curvas.svg; evidencia/curvas.csv; ../evidencia/curva_arbol.csv |
| Skill y vivienda | AUDIT_REPORT.md; auditoria_numerica.json; hashes_auditoria.json |
| Al menos dos pruebas pytest | ocho pruebas; evidencia/pytest.txt |
| Recomendación e informe APA | documentos/Informe_Tarea_6_2.docx |
| Bitácora asistida | documentos/Bitacora_Tarea_6_2.docx |

La auditoría la realizó el asistente principal aplicando la Skill, no un segundo auditor independiente. Dos ejecuciones idénticas demuestran estabilidad numérica del script, no exhaustividad de la revisión. La evidencia de trabajo registra acciones realizadas, sin inventar sesiones en Claude Code.
