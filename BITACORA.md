# Bitácora verificable de la Tarea 6.1

Fecha de trabajo: 4 de noviembre de 2026. Herramienta: Codex. Se conservó el kit original en su carpeta; el desarrollo se hizo en una copia versionada.

| Instrucción o decisión | Ejecución observada | Verificación o ajuste |
|---|---|---|
| Iniciar 6.1 antes de 6.2 | Se completaron datos, pipelines y validación de modelos fijos | Búsqueda y optimización excluidas del punto de entrada main.py |
| Analista: revisar únicamente el CSV | Subagente produjo resumen y JSON | 1,000 filas, 700/300, sin nulos; baseline70% con recall0 |
| Ingeniero: misma CV y diez particiones | Agente principal entrenó árbol y RF | Predicciones OOF guardadas; métricas reales difieren ligeramente del ejemplo del profesor |
| Auditor: revisar sin editar el código | Subagente realizó 46 comprobaciones | Extendió análisis a foreign_worker y encontró una omisión; no declaró equidad |
| Pruebas: convertir hallazgos en controles | Subagente recibió AUDIT_REPORT.md | Salida real y resultado en evidencia/pruebas.txt |
| Evitar dependencias adicionales de gráficos | SVG con biblioteca estándar | No se instaló Matplotlib; PNG solo para insertar en el documento |
| Referencias e informe | Consulta de UCI, documentación oficial y artículo JMLR | Referencias verificadas y documento renderizado para revisar páginas |

No se atribuyen a Claude Code las ejecuciones realizadas por Codex. Los agentes y sus entregas están registrados en evidencia/flujo.json. No se inventaron errores de IA ni se copiaron los resultados numéricos del instructivo.
