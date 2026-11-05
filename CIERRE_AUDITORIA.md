# Cierre de auditoría — Tarea 6.1

Se conserva sin modificaciones el informe independiente AUDIT_REPORT.md. Sus recomendaciones sobre controles automatizados se atendieron con ocho pruebas unittest, todas aprobadas (exitcode 0), documentadas en evidencia/pruebas.txt y evidencia/pruebas.json.

Se verifican integridad y separación del objetivo, disjunción de pliegues, cobertura y alineación OOF, codificador ajustado solo al entrenamiento, recálculo independiente de métricas y desviaciones, reproducibilidad de Random Forest y denominadores de subgrupos. Un contraejemplo prueba que exactitud alta no implica recall alto.

La omisión de foreign_worker se incorporó al informe académico mediante el análisis independiente del auditor: n=37, cuatro casos bad y uno detectado. La muestra pequeña impide conclusiones firmes. No se subsanan mediante estos controles las limitaciones temporales, de procedencia ni de equidad; tampoco se certifica uso crediticio real.
