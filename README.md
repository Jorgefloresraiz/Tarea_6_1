# Tarea 6.1 — Evaluación con agentes especializados

Jorge Josué Flores González · MAI 540 · Atlantis University

Proyecto académico basado en el kit German Credit del profesor. No aprueba ni rechaza solicitudes reales. La optimización y la recomendación de producción corresponden a 6.2 y no se presentan como terminadas.

## Reproducir
Entorno verificado: Python 3.14, versiones en requirements.txt.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -v
python graficar_61.py
```
No se necesita una API de pago ni Matplotlib. `main.py` ejecuta solo 6.1. `main_modulo6_original.py`, `busqueda.py`, `curvas.py` y `auditoria.py` conservan pasos de la guía pendientes para 6.2; no son el punto de entrada de esta entrega. El diagnóstico por subgrupos de 6.1 se calcula con las predicciones OOF en experimento_61.py.

## Flujo y evidencia
1. Analista: `datos/RESUMEN.md`, `evidencia/analista.json`.
2. Ingeniero: `RESULTADOS.md`, `evidencia/resultados.json` y CSV por pliegue/partición.
3. Auditor: `AUDIT_REPORT.md`, `evidencia/auditor.json`.
4. Responsable de pruebas: `tests/`, `evidencia/pruebas.txt`.

`ROLES.md` define responsabilidades y límites. `evidencia/flujo.json` registra agentes y entregas. Se utilizó Codex con subagentes reales y el agente principal como ingeniero/orquestador. Las definiciones `.claude/agents/` se incluyen para reutilización; no se afirma una ejecución en Claude Code.

## Diseño
- Objetivo positivo: `bad`; baseline siempre `good`: accuracy 0.700, recall bad 0.
- Árbol y Random Forest con configuraciones fijas; semilla 42.
- Cinco pliegues estratificados compartidos; OrdinalEncoder ajustado dentro de cada Pipeline.
- Media y DE de accuracy; recall/precisión/F1 agregados de predicciones fuera de pliegue.
- Diez particiones estratificadas 75/25 (semillas 0–9), emparejadas entre modelos.
- Curva inicial del árbol como diagnóstico para enlazar 6.2; sin selección por sus resultados.

El rango de diez particiones y la DE entre cinco pliegues son estadísticas distintas; no constituyen una prueba formal de superioridad de un método. La CV tampoco garantiza generalización temporal ni ausencia de fuga semántica. El conjunto completo se usa exploratoriamente: no se declara un test externo intacto para 6.1.

Se conserva la codificación ordinal del kit, que introduce un orden artificial en categorías nominales. Incluye variables sensibles entre los predictores para reproducir el ejercicio; no se afirma que su uso esté autorizado en producción. La auditoría por grupos es descriptiva y no certifica equidad.

## Procedencia
CSV proporcionado en el curso, idéntico al archivo adjunto por el estudiante. SHA-256: 82b9757965557e2318d267100d13283da961497a36938d1a384dea716a68f6f2. La referencia de la familia del dataset es Statlog German Credit (Hofmann, 1994), https://doi.org/10.24432/C5NC77. No se comprobó la equivalencia fila a fila del CSV del curso con la descarga original de UCI.

Las métricas se calcularon mediante ejecución; no se copiaron del instructivo. Los tiempos son observaciones del equipo utilizado, no benchmarks universales. Las pruebas son controles del prototipo, no validación de una herramienta financiera.

## Entrega
- [Informe APA en Word](documentos/Informe_Tarea_6_1.docx)
- [Informe en PDF](documentos/Informe_Tarea_6_1.pdf): portada, tres páginas de contenido y referencias.
- [Bitácora](BITACORA.md) y [cierre de auditoría](CIERRE_AUDITORIA.md).
- Verificación: ocho pruebas unittest aprobadas, cero fallos y errores.
- Repositorio: https://github.com/Jorgefloresraiz/Tarea_6_1

## Continuación Tarea 6.2
La optimización y auditoría posterior están en [tarea_6_2](tarea_6_2/README.md), con informe, bitácora, búsqueda anidada y pytest. La evidencia de la 6.1 se conserva.
