# Auditoría de modelos
Invocación en Claude Code: `/auditoria-modelos ruta/al/proyecto`. También puede leerse SKILL.md en otro asistente, declarando cuál se utilizó. Indique objetivo, clase positiva si corresponde, subgrupo, costo del error y ubicación de predicciones. La Skill no cambia el código auditado.

Clasificación: métricas y matriz, partición estratificada, aislamiento del preprocesamiento y de selección, temporalidad y brechas por subgrupo. Regresión: MSE/RMSE/R², referencia y residuos; R² negativo es válido. Umbrales exploratorios: diferencia absoluta0.10 en recall; diferencia relativa0.20 en RMSE. Mínimo20 casos por grupo y10 positivos para recall. Ver SKILL.md para denominadores y excepciones.

Salida: AUDIT_REPORT.md con PASA, FALLA o NO SE PUEDE DETERMINAR y evidencia de celda/línea. NO SE PUEDE DETERMINAR nunca se convierte en PASA por falta de información. No certifica equidad causal ni seguridad clínica.

Comprobación numérica (Python estándar, sin dependencias):
`python .claude/skills/auditoria-modelos/scripts/auditar_predicciones.py predicciones_insurance.csv --tipo regresion`
CSV: y_true, y_pred y subgrupo; para clasificación binaria agregar `--tipo clasificacion --positiva 0`. El script no detecta fugas por sí solo. El soporte de clasificación es binario, no usarlo para colapsar Iris multiclase.

Pruebas: `python -B pruebas/test_auditoria.py`. Historial: v1 criterios de clasificación; v2 selección de hiperparámetros; v3 extensión a regresión y verificación numérica. Las revisiones fueron realizadas con Codex; no se afirma que se haya ejecutado Claude Code.
