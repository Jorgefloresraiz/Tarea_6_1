"""Controles independientes de Tarea 6.1; unittest, sin regenerar evidencia."""
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from datos import cargar_datos, RUTA
from modelos import crear_pipeline, tres_modelos
from validacion import validar, proporcion_malos_detectados, particion_unica


def conteos(y, pred):
    """Oráculo por conteo, independiente de sklearn.metrics."""
    pares = list(zip(y, pred))
    return tuple(sum(a == real and b == estimado for a, b in pares)
                 for real, estimado in [(0, 0), (0, 1), (1, 0), (1, 1)])


def resumen(y, pred):
    tn, fp, fn, tp = conteos(y, pred)
    return dict(n=tn+fp+fn+tp, bad=fn+tp, tn=tn, fp=fp, fn=fn, tp=tp,
                accuracy=(tn+tp)/(tn+fp+fn+tp),
                recall_bad=tp/(tp+fn) if tp+fn else None,
                fpr=fp/(fp+tn) if fp+tn else None)


class PruebasTarea61(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X, cls.y, cls.cats, cls.cv = cargar_datos()
        ev = ROOT / 'evidencia'
        cls.result = json.loads((ev/'resultados.json').read_text())
        cls.report = {r['modelo']: r for r in cls.result['modelos']}
        cls.splits = json.loads((ev/'pliegues.json').read_text())
        cls.oof = pd.read_csv(ev/'predicciones_oof.csv')
        cls.folds = pd.read_csv(ev/'pliegues_metricas.csv')
        cls.parts = pd.read_csv(ev/'particiones.csv')
        cls.groups = pd.read_csv(ev/'subgrupos.csv')
        cls.audit = json.loads((ev/'auditor.json').read_text())

    def pred(self, name):
        return self.oof[self.oof.modelo == name].sort_values('fila').y_pred.to_numpy()

    def test_01_integridad_y_target_fuera_de_X(self):
        raw = pd.read_csv(RUTA)
        self.assertEqual(raw.shape, (1000, 21))
        self.assertEqual(raw.clase.value_counts().to_dict(), {'good': 700, 'bad': 300})
        self.assertFalse(raw.isna().any().any())
        self.assertFalse(raw.duplicated().any())
        self.assertFalse(self.X.duplicated().any())
        self.assertNotIn('clase', self.X.columns)
        pd.testing.assert_frame_equal(self.X, raw.drop(columns='clase'))
        np.testing.assert_array_equal(self.y, [1 if c == 'bad' else 0 for c in raw.clase])
        self.assertEqual(hashlib.sha256(RUTA.read_bytes()).hexdigest(), self.result['sha256_dataset'])

    def test_02_disjuncion_estratificacion_cobertura(self):
        expected = list(StratifiedKFold(5, shuffle=True, random_state=42).split(self.X, self.y))
        actual = list(self.cv.split(self.X, self.y))
        self.assertEqual(len(self.splits), 5)
        coverage = []
        for i, fold in enumerate(self.splits):
            with self.subTest(pliegue=i):
                a, b = fold['entrenamiento'], fold['validacion']
                self.assertEqual((len(a), len(b), len(set(a)), len(set(b))), (800, 200, 800, 200))
                self.assertFalse(set(a) & set(b))
                self.assertEqual(set(a) | set(b), set(range(1000)))
                self.assertEqual((int(self.y.iloc[a].sum()), int(self.y.iloc[b].sum())), (240, 60))
                for saved, generated, reference in zip((a, b), actual[i], expected[i]):
                    np.testing.assert_array_equal(saved, reference)
                    np.testing.assert_array_equal(generated, reference)
                coverage.extend(b)
        self.assertEqual(sorted(coverage), list(range(1000)))

    def test_03_oof_alineacion_y_unicidad(self):
        self.assertEqual(set(self.oof.modelo), {'Árbol', 'Random Forest'})
        self.assertEqual(len(self.oof), 2000)
        self.assertFalse(self.oof.duplicated(['modelo', 'fila']).any())
        for name, g in self.oof.groupby('modelo'):
            with self.subTest(modelo=name):
                g = g.sort_values('fila')
                np.testing.assert_array_equal(g.fila, np.arange(1000))
                np.testing.assert_array_equal(g.y_true, self.y)
                self.assertTrue(g.y_pred.isin([0, 1]).all())
                for col in ['housing', 'personal_status']:
                    np.testing.assert_array_equal(g[col], self.X[col])

    def test_04_encoder_solo_entrenamiento_categoria_exclusiva(self):
        train = pd.DataFrame({'categoria': ['a', 'b', 'a', 'b'], 'numero': [1, 2, 3, 4]})
        validation = pd.DataFrame({'categoria': ['EXCLUSIVA_VALIDACION'], 'numero': [5]})
        for name in ['Árbol', 'Random Forest']:
            with self.subTest(modelo=name):
                pipe = crear_pipeline(tres_modelos()[name], ['categoria'])
                pipe.fit(train, [0, 1, 0, 1])
                prep = pipe.named_steps['prep']
                encoder = prep.named_transformers_['cat']
                self.assertEqual(encoder.categories_[0].tolist(), ['a', 'b'])
                before = encoder.categories_[0].copy()
                self.assertEqual(prep.transform(validation)[0, 0], -1)
                prediction = pipe.predict(validation)
                self.assertEqual(prediction.shape, (1,))
                self.assertIn(prediction[0], [0, 1])
                np.testing.assert_array_equal(before, encoder.categories_[0])

    def test_05_metricas_y_DE_recalculadas(self):
        self.assertEqual(len(self.folds), 10)
        self.assertFalse(self.folds.duplicated(['modelo', 'pliegue']).any())
        for name, r in self.report.items():
            with self.subTest(modelo=name):
                p = self.pred(name)
                tn, fp, fn, tp = conteos(self.y, p)
                self.assertEqual(r['matriz_confusion'], [[tn, fp], [fn, tp]])
                for key, value in {'accuracy_media': (tn+tp)/1000,
                                   'recall_bad_oof': tp/(tp+fn),
                                   'precision_bad_oof': tp/(tp+fp),
                                   'f1_bad_oof': 2*tp/(2*tp+fp+fn)}.items():
                    self.assertAlmostEqual(r[key], value, places=12)
                scores = []
                for i, f in enumerate(self.splits):
                    b = f['validacion']
                    score = sum(self.y.iloc[j] == p[j] for j in b)/len(b)
                    scores.append(score)
                    saved = self.folds[(self.folds.modelo == name) & (self.folds.pliegue == i)]
                    self.assertEqual(len(saved), 1)
                    self.assertAlmostEqual(saved.accuracy.iloc[0], score)
                mean = sum(scores)/5
                population_sd = math.sqrt(sum((v-mean)**2 for v in scores)/5)
                self.assertAlmostEqual(r['accuracy_std'], population_sd, places=12)
                self.assertNotAlmostEqual(population_sd, np.std(scores, ddof=1), places=6)

    def test_06_contraejemplo_accuracy_no_es_recall(self):
        baseline = resumen(self.y, np.zeros(1000, dtype=int))
        self.assertEqual((baseline['accuracy'], baseline['recall_bad']), (0.7, 0.0))
        self.assertEqual(self.result['configuracion']['baseline_accuracy'], baseline['accuracy'])
        self.assertEqual(self.result['configuracion']['baseline_recall_bad'], baseline['recall_bad'])
        tree, rf = (resumen(self.y, self.pred(n)) for n in ['Árbol', 'Random Forest'])
        self.assertLess(tree['accuracy'], baseline['accuracy'])
        self.assertGreater(rf['accuracy'], tree['accuracy'])
        self.assertLess(rf['recall_bad'], tree['recall_bad'])
        self.assertEqual((tree['fn'], rf['fn']), (141, 188))

    def test_07_reproduccion_RF_y_validacion(self):
        # Dos ajustes independientes de todos los pliegues, no solo resúmenes.
        scores = []
        for f in self.splits:
            a, b = f['entrenamiento'], f['validacion']
            replicas = []
            for _ in range(2):
                pipe = crear_pipeline(tres_modelos()['Random Forest'], self.cats)
                pipe.fit(self.X.iloc[a], self.y.iloc[a])
                replicas.append(pipe.predict(self.X.iloc[b]))
            np.testing.assert_array_equal(replicas[0], replicas[1])
            np.testing.assert_array_equal(replicas[0], self.pred('Random Forest')[b])
            scores.append(sum(replicas[0] == self.y.iloc[b])/len(b))
        pipe = crear_pipeline(tres_modelos()['Random Forest'], self.cats)
        mean, sd = validar(pipe, self.X, self.y, self.cv)
        expected_mean = sum(scores)/5
        expected_sd = math.sqrt(sum((s-expected_mean)**2 for s in scores)/5)
        self.assertAlmostEqual(mean, expected_mean, places=12)
        self.assertAlmostEqual(sd, expected_sd, places=12)
        self.assertAlmostEqual(proporcion_malos_detectados(pipe, self.X, self.y, self.cv), 112/300)
        for name in ['Árbol', 'Random Forest']:
            g = self.parts[self.parts.modelo == name].sort_values('semilla')
            self.assertEqual(g.semilla.tolist(), list(range(10)))
            rebuilt = particion_unica(crear_pipeline(tres_modelos()[name], self.cats), self.X, self.y)
            np.testing.assert_allclose(rebuilt, g.accuracy, rtol=0, atol=1e-12)
            r = self.report[name]
            self.assertAlmostEqual(r['particion_min'], min(rebuilt))
            self.assertAlmostEqual(r['particion_max'], max(rebuilt))
            self.assertAlmostEqual(r['particion_rango'], max(rebuilt)-min(rebuilt))

    def test_08_subgrupos_denominadores_y_hallazgos_auditor(self):
        self.assertEqual(len(self.groups), 14)
        self.assertFalse(self.groups.duplicated(['modelo', 'variable', 'grupo']).any())
        for name in ['Árbol', 'Random Forest']:
            for col in ['housing', 'personal_status']:
                rows = self.groups[(self.groups.modelo == name) & (self.groups.variable == col)]
                self.assertEqual(set(rows.grupo), set(self.X[col]))
                for row in rows.itertuples():
                    mask = self.X[col] == row.grupo
                    m = resumen(self.y[mask], self.pred(name)[mask])
                    self.assertEqual((row.n, row.bad_reales), (m['n'], m['bad']))
                    self.assertAlmostEqual(row.accuracy, m['accuracy'])
                    self.assertAlmostEqual(row.recall_bad, m['recall_bad'])
        for row in self.audit['subgrupos_recalculados']:
            mask = self.X[row['variable']] == row['grupo']
            m = resumen(self.y[mask], self.pred(row['modelo'])[mask])
            for key, val in m.items():
                self.assertAlmostEqual(row[key], val, msg=str((row['modelo'], row['grupo'], key)))
        mask = self.X.foreign_worker == 'no'
        m = resumen(self.y[mask], self.pred('Random Forest')[mask])
        self.assertEqual((m['n'], m['bad'], m['tp']), (37, 4, 1))
        self.assertAlmostEqual(m['accuracy'], 34/37)
        self.assertEqual(m['recall_bad'], 0.25)
        # Denominador ausente: indefinido, nunca inferir recall perfecto o cero.
        self.assertIsNone(resumen([0, 0], [0, 1])['recall_bad'])
        self.assertIsNone(resumen([1, 1], [0, 1])['fpr'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
