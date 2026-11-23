import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class GraficadorResultados:
    def _to_base64(self, fig) -> str:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=160, bbox_inches='tight', transparent=True)
        plt.close(fig)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')

    def _estilizar_ejes(self, ax, titulo, xlabel, ylabel):
        ax.set_facecolor('none')
        ax.set_title(titulo, fontsize=11, fontweight='bold', color='#F8FAFC', loc='left', pad=14)
        ax.set_xlabel(xlabel, fontsize=9, color='#94A3B8', labelpad=8)
        ax.set_ylabel(ylabel, fontsize=9, color='#94A3B8', labelpad=8)
        ax.tick_params(labelsize=8.5, colors='#64748B')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#1E293B')
        ax.spines['bottom'].set_color('#1E293B')
        ax.grid(True, linestyle='--', alpha=0.25, color='#475569')

    def generar_dispersion(self, Y_real: np.ndarray, Y_pred: np.ndarray) -> str:
        fig, ax = plt.subplots(figsize=(6.8, 4.0))
        
        ax.scatter(
            Y_real, Y_pred,
            color='#818CF8', s=68, alpha=0.9,
            edgecolors='#0B0F17', linewidth=1.2,
            zorder=3, label='Estudiantes (Real vs Estimado)'
        )
        
        min_val = min(Y_real.min(), Y_pred.min()) - 2
        max_val = max(Y_real.max(), Y_pred.max()) + 2
        ax.plot(
            [min_val, max_val], [min_val, max_val],
            color='#10B981', linestyle='--', lw=1.6,
            zorder=2, label='Predicción Ideal (Y = Ŷ)'
        )
        
        self._estilizar_ejes(ax, 'Precisión del Modelo: Calificación Real vs. Predicha', 'Calificación Real (Y)', 'Calificación Estimada (Ŷ)')
        legend = ax.legend(frameon=True, facecolor='#161E2E', edgecolor='#1E293B', fontsize=8.5)
        for text in legend.get_texts():
            text.set_color('#CBD5E1')
        return self._to_base64(fig)

    def generar_residuales(self, Y_pred: np.ndarray, Y_real: np.ndarray) -> str:
        residuales = Y_real - Y_pred
        fig, ax = plt.subplots(figsize=(6.8, 4.0))
        
        ax.scatter(
            Y_pred, residuales,
            color='#38BDF8', s=68, alpha=0.9,
            edgecolors='#0B0F17', linewidth=1.2,
            zorder=3, label='Error Residual (Yᵢ - Ŷᵢ)'
        )
        ax.axhline(0, color='#F43F5E', linestyle='--', lw=1.6, zorder=2, label='Línea de Error Cero')
        
        self._estilizar_ejes(ax, 'Distribución de Errores Residuales', 'Calificación Estimada (Ŷ)', 'Error Residual (puntos)')
        legend = ax.legend(frameon=True, facecolor='#161E2E', edgecolor='#1E293B', fontsize=8.5)
        for text in legend.get_texts():
            text.set_color('#CBD5E1')
        return self._to_base64(fig)