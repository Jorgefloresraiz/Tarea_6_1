# Evaluación crítica del flujo distribuido

La separación de roles aportó revisión independiente de la interpretación. El analista señaló que el baseline del 70 % no detecta bad; se incorporó recall junto a exactitud. El auditor encontró una omisión concreta en la primera tabla: foreign_worker no estaba incluido. Su revisión independiente mostró que la exactitud de 91.9 % del grupo coexistía con una detección de solo 1/4 positivos. Ese resultado se conservó con sus denominadores y la advertencia de muestra pequeña, en vez de declararlo evidencia de equidad.

Un segundo hallazgo fue que las pruebas heredadas seguían incompletas: la presencia de un paso prep tampoco demuestra por sí sola que el encoder no haya visto validación. Se transfirió esa observación al responsable de pruebas para probar aislamiento mediante una categoría exclusiva de validación y revisar pliegues, métricas y estabilidad.

El costo fue coordinar cuatro entregas y revisar cada transferencia. La ingeniería pudo preparar archivos mientras el analista trabajaba, pero no entrenó hasta recibir su resumen. La auditoría esperó los resultados y las pruebas esperaron la auditoría. Esa dependencia serial limita el ahorro de tiempo. No se midió una comparación controlada con un solo agente y no se atribuye una mejora cuantificada al reparto.

Repetiría el flujo cuando una revisión independiente pueda cuestionar una decisión importante. Para modificaciones cortas, el intercambio de contexto puede costar más que hacer y revisar el cambio directamente. Los roles no sustituyen la responsabilidad humana ni validan el prototipo para uso financiero real.
