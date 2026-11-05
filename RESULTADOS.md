# Resultados del ingeniero de modelos

| Modelo | Accuracy media | DE | Recall bad OOF | Partición mín.–máx. |
|---|---:|---:|---:|---|
| Árbol | 0.698 | 0.017 | 0.530 | 0.608–0.720 |
| Random Forest | 0.757 | 0.007 | 0.373 | 0.716–0.792 |

Mismos cinco pliegues estratificados, semilla 42. Positivo=bad. DE descriptiva entre pliegues (ddof=0), no intervalo de confianza. Recall calculado agrupando las predicciones fuera de pliegue.

Diez particiones 75/25 con semillas 0–9; misma partición para ambos modelos en cada semilla. Rango y DE son medidas distintas, no una prueba de superioridad estadística de CV.

Se conserva OrdinalEncoder del kit: asigna un orden artificial a categorías nominales. No se ajustó fuera del Pipeline. Incluye edad/personal_status/foreign_worker como predictores para reproducir el ejercicio; no se describe un modelo autorizado para decisiones reales.

Accuracy del baseline siempre good: 0.700; recall bad: 0.000. Mejor accuracy no implica mejor detección de bad. No se hizo búsqueda ni recomendación de producción. El test independiente de 6.2 queda pendiente.

Evidencia: evidencia/resultados.json, pliegues.json, predicciones_oof.csv, particiones.csv, subgrupos.csv.
