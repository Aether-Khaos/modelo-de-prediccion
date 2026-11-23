from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class EstudianteInput:
    horas_estudio: float      # X1
    asistencia: float         # X2
    tareas_completadas: float # X3
    nota_previa: float        # X4

@dataclass
class ResultadoEntrenamiento:
    # Ecuación normal: β = (XᵀX)⁻¹XᵀY
    beta: List[float]                     # [β0, β1, β2, β3, β4]
    beta_sklearn: List[float]             # Validación cruzada con Scikit-Learn
    interpretaciones: List[Dict[str, str]]
    
    # Matrices para exposición de Álgebra Lineal
    matriz_x_muestra: List[List[float]]   # Primeras filas de X (n x 5)
    matriz_xt_muestra: List[List[float]]  # Matriz transpuesta Xᵀ (5 x n)
    vector_y_muestra: List[float]         # Vector de resultados Y
    dimensiones_x: str                    # Ej: "20 x 5"
    dimensiones_xt: str                   # Ej: "5 x 20"
    
    # Métricas de evaluación
    mae: float
    rmse: float
    r2: float
    calidad_modelo: str                   # Ej: "Excelente ajuste"
    
    # Datos registrados y análisis
    registros_tabla: List[Dict[str, float]]
    resumen_datos: List[Dict[str, Any]]
    total_registros: int
    
    # Gráficas en Base64
    grafica_dispersion: str
    grafica_residuales: str