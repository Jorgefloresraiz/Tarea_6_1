# Protocolo fijado antes de ejecutar la comparación

5 de noviembre de 2026. Se continúa Tarea_6_1 en el mismo repositorio y CSV.

- Positiva: bad=1. Un falso negativo significa clasificar un crédito malo como bueno. Se prioriza su detección, sin asignar un costo monetario no suministrado.
- Se excluyen age, personal_status, housing y foreign_worker de los predictores. Se conservan únicamente para auditoría; housing es el subgrupo predefinido. Esto cambia el espacio de variables frente a 6.1, por lo que se recalcula un árbol por defecto comparable.
- Cinco pliegues externos estratificados, shuffle=True, random_state=42, idénticos a 6.1. Dentro de cada entrenamiento externo: tres pliegues estratificados, semilla 17.
- Árbol: GridSearchCV sobre max_depth=[3,5,8,None], min_samples_leaf=[1,5,10], class_weight=[None,'balanced']: 24 combinaciones. Se maximiza F2 de bad (peso mayor al recall), con umbral predictivo estándar. No se cambia la métrica ni la rejilla después de ver resultados.
- Comparadores fijos: RandomForestClassifier(n_estimators=100,class_weight='balanced',random_state=42,n_jobs=1) y HistGradientBoostingClassifier(random_state=42,early_stopping=False). Se evalúa también el árbol por defecto con los mismos 16 predictores.
- Toda codificación se ajusta dentro del Pipeline de cada partición. Media y desviación poblacional de accuracy y F2; recall agregado de predicciones externas. Se reportan también precisión, F1, matriz y tiempos. El tiempo del árbol afinado incluye búsqueda y refit; se separa tiempo de entrenamiento de una configuración ya fijada.
- La rejilla en todos los datos produce una configuración para ajuste posterior y un resultado aparente. La estimación honesta de la búsqueda procede exclusivamente de los pliegues externos. Las diferencias entre ambos números incluyen diferencias de partición y tamaño, no son una medida pura del optimismo.
- Candidato recomendado: mayor F2 externo entre los tres modelos; en empate, menor costo de ajuste. La selección entre familias sigue siendo exploratoria; no se presenta su máximo como evaluación independiente de toda la selección. La producción real requiere nueva validación temporal y revisión de gobernanza.
- Curva: misma CV externa y fracciones de entrenamiento que 6.1; si se elige el árbol afinado, la búsqueda se repite dentro de cada subconjunto. Se compara además el árbol sin afinar con los 16 predictores para separar el cambio de variables del ajuste.
- Auditoría housing: recall y soporte por grupo; alerta exploratoria de 0.10 absoluta, mínimo n=20 y 10 positivos según la Skill del Módulo 4. Sin ajuste de umbral después de los resultados.
- Pruebas: exclusión de variables, separación externa/interna, aislamiento del encoder, recálculo de métricas y búsqueda anidada. Los resultados no se alterarán para conseguir un test favorable.
