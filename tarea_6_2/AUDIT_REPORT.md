# Auditoría de la Tarea 6.2

Fecha: 5 de noviembre de 2026. Skill del Módulo 4: copia conservada en `skill/auditoria-modelos/SKILL.md`, sin cambios. Auditoría realizada por el asistente principal; no se presenta como dictamen de un segundo agente. Se distingue revisión estática del código, ejecución del script numérico en copia temporal y pruebas pytest. Los hashes antes y después están en `evidencia/hashes_auditoria.json`.

## Inventario y alcance
Clasificación binaria; positiva bad=1. Datos: 1,000 filas, 300 bad. Se audita el procedimiento de búsqueda del árbol y sus predicciones externas, no el ajuste global sobre los 1,000 registros. Se excluyen age, personal_status, housing y foreign_worker; housing se conserva para la auditoría predefinida. El protocolo se fijó en PLAN.md antes de la comparación. Los costos monetarios no fueron suministrados; F2 expresa una prioridad de recall, no una función de pérdidas monetarias.

| Criterio | Veredicto | Evidencia |
|---|---|---|
| M1 métricas | PASA | `experimento.py:19–24,37–55`; recálculo con script original en `evidencia/auditoria_numerica.json`: TN449, FP251, FN83, TP217; accuracy0.666, precisión0.463675, recall0.723333, F1 0.565104. |
| M2 desbalance y costo | PASA para cobertura; NO SE PUEDE DETERMINAR costo real | `PLAN.md:5–10`; clase mayoritaria70%; se reportan métricas adicionales y se priorizan FN mediante F2. No se conoce una relación monetaria FN/FP ni un umbral operacional aceptable. |
| P1 partición | PASA para estratificación y comparación; NO SE PUEDE DETERMINAR temporalidad | `modelo.py:27–31`, `experimento.py:28–39`, `evidencia/particiones.json`: mismos cinco pliegues externos, 800/200, internos contenidos en entrenamiento externo. No hay fecha ni identificador de persona. |
| P2 transformaciones | PASA | `modelo.py:33–42`: encoder en Pipeline dentro de GridSearchCV; no se ejecuta fit_transform global. La detección de tipos de columna no estima parámetros de valores. Prueba de categoría exclusiva de validación en `tests/test_modelo.py`. |
| P3 selección | PASA para estimación anidada del árbol; reserva para elección entre familias | `experimento.py:35–46`: nueva búsqueda por fold y test externo aislado. Ajuste global posterior en líneas57–59 solo documenta ganador. La elección entre tres familias usa F2 externo (líneas60–61), por lo que su máximo no es una evaluación independiente de todo el proceso de selección. |
| F1 fuga temporal o semántica | NO SE PUEDE DETERMINAR | `modelo.py:20–25`: target y cuatro variables de auditoría excluidos. El CSV no acredita cuándo se observaron los predictores ni independencia entre personas. Variables restantes podrían funcionar como proxies. |
| S1 disparidad | PASA en vivienda bajo el criterio exploratorio | `experimento.py:82–84`, `evidencia/auditoria_numerica.json`: máximo desfase de recall2.67pp; todos los grupos tienen al menos20 filas y10 positivos. No certifica equidad general. |
| D1 duplicados | PASA para duplicados exactos; NO SE PUEDE DETERMINAR entidades | Inspección del CSV y control automatizado: sin filas duplicadas; falta identificador personal para excluir repetición de entidad. |
| R1, R2, S2 | NO APLICA | Es clasificación, no regresión. |

## Subgrupos
Recall global:217/300=0.723333. Diferencia absoluta respecto al global; umbral0.10 fijado por la Skill.

| Vivienda | n | bad | TP | Recall | Brecha | Estado |
|---|---:|---:|---:|---:|---:|---|
| for free |108|44|33|0.7500|0.0267|PASA|
| own |713|186|133|0.7151|0.0083|PASA|
| rent |179|70|51|0.7286|0.0052|PASA|

## Hallazgos y correcciones
La 6.1 conservaba variables sensibles entre los predictores. La consigna 6.2 exige reservarlas para auditoría; se retiraron cuatro columnas antes de entrenar y se agregó una prueba de exclusión. Se recalculó el árbol por defecto con las mismas16 variables, evitando atribuir al afinado una diferencia causada por el cambio de entradas.

La curva del árbol afinado termina en exactitud0.662, distinta de0.666 de la tabla. No es una contradicción: learning_curve baraja el entrenamiento antes de la CV interna, cambiando los pliegues internos y posibles desempates. Se declara esa diferencia y no se reemplaza el resultado externo principal por el de la curva.

La exactitud del árbol elegido es inferior a0.70. No se impuso un test de superar ese baseline porque se optimiza F2 y se reconoce explícitamente la pérdida de exactitud. El control pertinente es la consistencia del criterio y de la conclusión, no forzar una aprobación cosmética.

## Omisiones y posibles falsos positivos
No se auditaron todas las variables sensibles, intersecciones, calibración, deriva temporal, costos reales ni legalidad de uso. No hay referencia independiente para cuantificar falsos negativos de la auditoría ni afirmar ausencia de falsos positivos. Una brecha menor a10pp en housing no prueba ausencia de discriminación; omitir una variable tampoco elimina sus proxies.

Dos ejecuciones del script producen exactamente el mismo JSON y los archivos auditados conservaron sus hashes. Esto prueba estabilidad numérica, no estabilidad de juicios de distintos asistentes. La recomendación queda limitada a un candidato para piloto supervisado y requiere datos nuevos antes de decisiones reales.
