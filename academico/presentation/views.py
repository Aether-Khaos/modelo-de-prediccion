from dataclasses import asdict
from django.shortcuts import render
from academico.domain.entities import EstudianteInput
from academico.application.use_cases import EntrenarModeloUseCase, PredecirCalificacionUseCase

def dashboard(request):
    contexto = {
        'resultado': request.session.get('resultado_modelo'),
        'prediccion': None,
        'error': None,
    }

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'entrenar' and request.FILES.get('archivo_csv'):
            try:
                use_case = EntrenarModeloUseCase()
                resultado = use_case.ejecutar(request.FILES['archivo_csv'])
                resultado_dict = asdict(resultado)
                request.session['resultado_modelo'] = resultado_dict
                contexto['resultado'] = resultado_dict
            except Exception as e:
                contexto['error'] = f"Error al procesar el CSV: {str(e)}"

        elif accion == 'predecir':
            resultado_guardado = request.session.get('resultado_modelo')
            if not resultado_guardado:
                contexto['error'] = "Primero debes cargar un CSV y entrenar el modelo."
            else:
                try:
                    estudiante = EstudianteInput(
                        horas_estudio=float(request.POST.get('x1')),
                        asistencia=float(request.POST.get('x2')),
                        tareas_completadas=float(request.POST.get('x3')),
                        nota_previa=float(request.POST.get('x4')),
                    )
                    pred_use_case = PredecirCalificacionUseCase()
                    nota = pred_use_case.ejecutar(resultado_guardado['beta'], estudiante)
                    contexto['prediccion'] = {'nota': nota, 'datos': asdict(estudiante)}
                except ValueError:
                    contexto['error'] = "Por favor ingresa valores numéricos válidos."

    return render(request, 'academico/dashboard.html', contexto)