# Roles y límites de la Tarea 6.1

| Rol | Responsabilidad | Puede escribir | No modifica | Entrega |
|---|---|---|---|---|
| Analista | Calidad y límites del dataset | Su resumen y evidencia | CSV, modelos, pruebas | datos/RESUMEN.md |
| Ingeniero | Implementar y evaluar configuraciones fijas | Código de datos/modelos/evaluación y resultados | CSV, informe del auditor, tests | RESULTADOS.md y evidencia/ |
| Auditor | Revisar metodología y resultados | Su informe | Código, datos y métricas | AUDIT_REPORT.md |
| Pruebas | Convertir hallazgos en verificaciones | tests/ y registro de ejecución | Modelos, datos y auditoría | evidencia/pruebas.txt |

Orden: analista → ingeniero → auditor → responsable de pruebas. El orquestador integra y documenta. Un propietario por archivo evita modificaciones simultáneas. Los permisos declarados son reglas de trabajo, no aislamiento del sistema operativo.

## Ejecución real
Se utilizó Codex: un subagente analista, el agente principal como ingeniero/orquestador y subagentes para auditoría y pruebas. No se afirma haber ejecutado Claude Code; los archivos .claude/agents/ permiten reutilizar los roles en ese cliente. La guía autoriza otro asistente.

El analista trabajó en paralelo con la preparación de archivos; su resumen se revisó antes del entrenamiento. La auditoría recibió código y resultados; las pruebas recibieron el informe del auditor. Las entregas y observaciones están en evidencia/flujo.json.
