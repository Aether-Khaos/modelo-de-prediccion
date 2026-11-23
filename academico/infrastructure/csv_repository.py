import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any

class CsvDatasetRepository:
    COLUMNAS_REQUERIDAS = ['X1', 'X2', 'X3', 'X4', 'Y']

    def cargar_y_analizar(self, archivo_csv) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, float]], List[Dict[str, Any]], int]:
        df = pd.read_csv(archivo_csv)
        
        for col in self.COLUMNAS_REQUERIDAS:
            if col not in df.columns:
                raise ValueError(f"El CSV debe contener la columna '{col}'. Columnas encontradas: {list(df.columns)}")

        df = df[self.COLUMNAS_REQUERIDAS].dropna()
        if len(df) < 5:
            raise ValueError("El archivo CSV debe tener al menos 5 registros válidos para entrenar el modelo.")
        
        X_raw = df[['X1', 'X2', 'X3', 'X4']].to_numpy(dtype=float)
        Y = df['Y'].to_numpy(dtype=float)

        # Registros individuales para mostrar en la tabla
        registros_tabla = df.round(2).to_dict(orient='records')

        # Estadísticas descriptivas
        desc = df.describe().round(2).to_dict()
        resumen = []
        nombres = {
            'X1': 'Horas estudio / semana (X1)',
            'X2': 'Porcentaje asistencia (X2)',
            'X3': 'Porcentaje tareas (X3)',
            'X4': 'Nota previa Matemáticas (X4)',
            'Y': 'Calificación Final (Y)'
        }
        for col in self.COLUMNAS_REQUERIDAS:
            resumen.append({
                'codigo': col,
                'variable': nombres[col],
                'promedio': desc[col]['mean'],
                'minimo': desc[col]['min'],
                'maximo': desc[col]['max'],
                'desviacion': desc[col]['std'],
            })

        return X_raw, Y, registros_tabla, resumen, len(df)