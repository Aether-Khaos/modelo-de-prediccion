import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Tuple, List, Dict

class RegresionLinealMultiple:
    def entrenar(self, X_raw: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[float], float, float, float]:
        # 1. Matriz de datos X (agregando columna de 1s para β0)
        n_muestras = X_raw.shape[0]
        columna_unos = np.ones((n_muestras, 1))
        X = np.hstack((columna_unos, X_raw))

        # 2. Ecuación Normal: β = (XᵀX)⁻¹XᵀY
        X_T = X.T                        # Matriz transpuesta Xᵀ
        XTX = X_T @ X                    # Producto matricial XᵀX
        XTX_inv = np.linalg.pinv(XTX)    # Inversa (XᵀX)⁻¹
        XTY = X_T @ Y                    # Producto XᵀY
        beta = XTX_inv @ XTY             # Vector de coeficientes β

        # 3. Validación cruzada con Scikit-Learn (para demostrar equivalencia)
        sk_model = LinearRegression(fit_intercept=True)
        sk_model.fit(X_raw, Y)
        beta_sklearn = [round(float(sk_model.intercept_), 4)] + [round(float(c), 4) for c in sk_model.coef_]

        # 4. Predicciones (Ŷ = Xβ) y métricas
        Y_pred = X @ beta
        errores = Y - Y_pred
        mae = float(np.mean(np.abs(errores)))
        rmse = float(np.sqrt(np.mean(errores ** 2)))
        
        ss_res = np.sum(errores ** 2)
        ss_tot = np.sum((Y - np.mean(Y)) ** 2)
        r2 = float(1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0

        return beta, X, X_T, Y_pred, beta_sklearn, mae, rmse, r2

    def generar_interpretaciones(self, beta: np.ndarray) -> List[Dict[str, str]]:
        b = [round(float(x), 4) for x in beta]
        return [
            {
                'simbolo': 'β₀',
                'variable': 'Intercepto (Término independiente)',
                'valor': str(b[0]),
                'explicacion': f"Calificación base teórica ({b[0]} pts) cuando todas las variables X₁..X₄ valen cero."
            },
            {
                'simbolo': 'β₁',
                'variable': 'Horas de estudio semanal (X₁)',
                'valor': str(b[1]),
                'explicacion': f"Por cada hora adicional de estudio a la semana, la calificación final {'aumenta' if b[1] >= 0 else 'disminuye'} en {abs(b[1])} puntos (manteniendo X₂, X₃, X₄ constantes)."
            },
            {
                'simbolo': 'β₂',
                'variable': 'Porcentaje de asistencia (X₂)',
                'valor': str(b[2]),
                'explicacion': f"Por cada 1% adicional de asistencia a clases, la nota final {'aumenta' if b[2] >= 0 else 'disminuye'} en {abs(b[2])} puntos."
            },
            {
                'simbolo': 'β₃',
                'variable': 'Porcentaje de tareas completadas (X₃)',
                'valor': str(b[3]),
                'explicacion': f"Por cada 1% más de tareas entregadas, la calificación final {'aumenta' if b[3] >= 0 else 'disminuye'} en {abs(b[3])} puntos."
            },
            {
                'simbolo': 'β₄',
                'variable': 'Calificación previa Matemáticas (X₄)',
                'valor': str(b[4]),
                'explicacion': f"Por cada punto adicional en la nota previa de Matemáticas, la nota final {'aumenta' if b[4] >= 0 else 'disminuye'} en {abs(b[4])} puntos."
            }
        ]

    def predecir(self, beta: list, x1: float, x2: float, x3: float, x4: float) -> float:
        x_nuevo = np.array([1.0, x1, x2, x3, x4])
        prediccion = float(x_nuevo @ np.array(beta))
        return round(max(0.0, min(100.0, prediccion)), 2)