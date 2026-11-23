from academico.domain.entities import EstudianteInput, ResultadoEntrenamiento
from academico.infrastructure.csv_repository import CsvDatasetRepository
from academico.infrastructure.linear_regression import RegresionLinealMultiple
from academico.infrastructure.chart_generator import GraficadorResultados

class EntrenarModeloUseCase:
    def __init__(self):
        self.repo = CsvDatasetRepository()
        self.modelo = RegresionLinealMultiple()
        self.graficador = GraficadorResultados()

    def ejecutar(self, archivo_csv) -> ResultadoEntrenamiento:
        X_raw, Y, registros_tabla, resumen, total = self.repo.cargar_y_analizar(archivo_csv)
        beta, X, X_T, Y_pred, beta_sklearn, mae, rmse, r2 = self.modelo.entrenar(X_raw, Y)
        interpretaciones = self.modelo.generar_interpretaciones(beta)
        
        graf_disp = self.graficador.generar_dispersion(Y, Y_pred)
        graf_res = self.graficador.generar_residuales(Y_pred, Y)

        if r2 >= 0.85:
            calidad = "Excelente ajuste"
        elif r2 >= 0.65:
            calidad = "Buen ajuste"
        else:
            calidad = "Ajuste moderado/bajo"

        return ResultadoEntrenamiento(
            beta=[round(float(b), 4) for b in beta],
            beta_sklearn=beta_sklearn,
            interpretaciones=interpretaciones,
            matriz_x_muestra=X[:6].round(2).tolist(),
            matriz_xt_muestra=X_T[:, :6].round(2).tolist(),
            vector_y_muestra=Y[:6].round(2).tolist(),
            dimensiones_x=f"{X.shape[0]} filas × {X.shape[1]} columnas",
            dimensiones_xt=f"{X_T.shape[0]} filas × {X_T.shape[1]} columnas",
            mae=round(mae, 4),
            rmse=round(rmse, 4),
            r2=round(r2, 4),
            calidad_modelo=calidad,
            registros_tabla=registros_tabla,
            resumen_datos=resumen,
            total_registros=total,
            grafica_dispersion=graf_disp,
            grafica_residuales=graf_res
        )

class PredecirCalificacionUseCase:
    def __init__(self):
        self.modelo = RegresionLinealMultiple()

    def ejecutar(self, beta: list, estudiante: EstudianteInput) -> float:
        return self.modelo.predecir(
            beta,
            estudiante.horas_estudio,
            estudiante.asistencia,
            estudiante.tareas_completadas,
            estudiante.nota_previa
        )