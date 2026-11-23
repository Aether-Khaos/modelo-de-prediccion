# Análisis Técnico del Proyecto `sistema-prediccion`

> Informe generado a partir de la revisión estática del código y de comprobaciones de ejecución
> (versiones instaladas, `manage.py check`, serialización de sesión y cálculo del modelo).
> No se modificó ningún archivo de código ni de configuración.

---

## 1. Resumen Ejecutivo y Stack Tecnológico

### 1.1 Propósito

El proyecto es un **dashboard académico** que implementa una **regresión lineal múltiple (OLS)**
para estimar la calificación final de un estudiante a partir de cuatro variables:

| Símbolo | Variable | Descripción |
|---|---|---|
| `X1` | `horas_estudio` | Horas de estudio por semana |
| `X2` | `asistencia` | Porcentaje de asistencia |
| `X3` | `tareas_completadas` | Porcentaje de tareas completadas |
| `X4` | `nota_previa` | Nota previa de Matemáticas |
| `Y`  | Calificación final | Variable objetivo |

El usuario carga un CSV (`X1,X2,X3,X4,Y`), el sistema calcula los coeficientes mediante la
ecuación normal `β = (XᵀX)⁻¹XᵀY` con NumPy, valida el resultado contra Scikit-Learn, muestra
métricas (`R²`, `MAE`, `RMSE`), gráficas de dispersión/residuales y permite predecir un caso.
La interfaz es una única plantilla HTML estilizada con Tailwind CSS (vía CDN).

### 1.2 Stack real detectado

No existe `requirements.txt`, `pyproject.toml`, `Pipfile` ni `setup.py`. Las versiones se
obtuvieron directamente del entorno virtual `venv/`.

| Componente | Versión / Valor | Observación |
|---|---|---|
| Python | **3.14.10** | Detectado en `venv` |
| Django | **6.1.3** | `config/settings.py` y paquete instalado |
| Base de datos | **SQLite 3** (`db.sqlite3`) | `DATABASES` en `config/settings.py:76-81` |
| NumPy | **2.5.5** | Álgebra matricial |
| pandas | **3.1.1** | Lectura/análisis del CSV |
| scikit-learn | **1.9.1** | Validación cruzada del modelo |
| matplotlib | **3.11.2** | Generación de gráficas |
| Pillow | **13.0.0** | Dependencia de matplotlib para PNG |
| Django REST Framework | **No instalado** | No hay APIs REST |
| Celery / Redis / colas | **No instalado** | Todo es síncrono |
| Gunicorn / WhiteNoise / whitenoise | **No instalado** | Sin despliegue configurado |
| python-dotenv / django-environ | **No instalado** | Sin gestión de entornos |
| Tailwind CSS | CDN (`cdn.tailwindcss.com`) | Dependencia externa en runtime |
| Google Fonts | CDN | Dependencia externa en runtime |

### 1.3 Configuración y entornos

- **No hay separación de settings** por entorno: todo vive en un único
  `config/settings.py`.
- **No hay variables de entorno**: no se leen `.env` ni `os.environ`.
- `SECRET_KEY` está **hardcodeada** en `config/settings.py:23`.
- `DEBUG = True` (`config/settings.py:26`) y `ALLOWED_HOSTS = []` (`:28`).
- `MAILERS` usa el backend de consola (`config/settings.py:124-128`).
- `LANGUAGE_CODE = 'en-us'` y `TIME_ZONE = 'UTC'` (`:106-112`) pese a que la app es en español.
- `db.sqlite3` (385 KB) está dentro del proyecto y contiene sesiones reales.
- Existe un archivo suelto `10` en la raíz con la salida de un `wc -l`, probablemente accidental.

**Conclusión del stack:** prototipo/demo funcional de una sola página, correcto para fines
didácticos, pero **no apto para producción** tal como está configurado.

---

## 2. Arquitectura y Mapa de Apps

### 2.1 Estructura general

```
sistema-prediccion/
├── manage.py
├── db.sqlite3
├── estudiantes.csv
├── 10                          # archivo residual (salida de wc)
├── config/                     # proyecto Django
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── academico/                  # única app de negocio
    ├── domain/
    │   ├── entities.py         # dataclasses del dominio
    │   └── repositories.py     # VACÍO (interfaz no implementada)
    ├── application/
    │   └── use_cases.py        # casos de uso
    ├── infrastructure/
    │   ├── csv_repository.py   # adaptador CSV/pandas
    │   ├── linear_regression.py# adaptador NumPy/sklearn
    │   └── chart_generator.py  # adaptador matplotlib
    └── presentation/
        ├── urls.py
        ├── views.py
        ├── forms.py            # VACÍO
        └── templates/academico/dashboard.html
```

### 2.2 Apps en `INSTALLED_APPS`

`config/settings.py:33-40` solo contiene apps de Django:

| App | Propósito |
|---|---|
| `django.contrib.admin` | Panel de administración (sin modelos propios registrados) |
| `django.contrib.auth` | Autenticación estándar (usada solo por el admin) |
| `django.contrib.contenttypes` | Marco de tipos de contenido requerido por auth/admin |
| `django.contrib.sessions` | **Persistencia del estado del modelo** (backend DB) |
| `django.contrib.messages` | Mensajes (no se usan en las vistas) |
| `django.contrib.staticfiles` | Gestión de estáticos (no hay carpeta `static/`) |

> **Hallazgo importante:** la app `academico` **no está en `INSTALLED_APPS`**.
> Funciona igualmente porque:
> 1. `config/urls.py:6` la importa directamente vía `include('academico.presentation.urls')`.
> 2. La carpeta de plantillas se registra manualmente en `TEMPLATES['DIRS']`
>    (`config/settings.py:57`), por lo que `APP_DIRS` no es necesario para encontrarla.
>
> Consecuencias: no hay `AppConfig`, no hay `models.py`, no hay migraciones propias y no se
> aprovecha el descubrimiento automático de plantillas/estáticos/templates tags.

### 2.3 Arquitectura interna (Clean/Hexagonal “manual”)

La app sigue una separación por capas, aunque sin inversión de dependencias real:

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Dominio | `academico/domain/entities.py` | `EstudianteInput`, `ResultadoEntrenamiento` (dataclasses) |
| Dominio | `academico/domain/repositories.py` | **Vacío**: no define interfaces/contratos |
| Aplicación | `academico/application/use_cases.py` | Orquesta entrenamiento y predicción |
| Infraestructura | `csv_repository.py` | Carga, valida y resume el CSV |
| Infraestructura | `linear_regression.py` | Ecuación normal, sklearn, métricas e interpretación |
| Infraestructura | `chart_generator.py` | Gráficas PNG en Base64 |
| Presentación | `presentation/views.py` | FBV `dashboard`: recibe fichero, sesión, render |
| Presentación | `presentation/urls.py` | Ruta raíz `''` |
| Presentación | `templates/.../dashboard.html` | UI completa (566 líneas) |

**Flujo de interacción:**

```
POST accion=entrenar
  dashboard (views.py)
    → EntrenarModeloUseCase.ejecutar(file)
        → CsvDatasetRepository.cargar_y_analizar()
        → RegresionLinealMultiple.entrenar() + generar_interpretaciones()
        → GraficadorResultados.generar_dispersion()/generar_residuales()
    → asdict(resultado) → request.session['resultado_modelo']
    → render(dashboard.html)

POST accion=predecir
  dashboard (views.py)
    → lee beta de la sesión
    → PredecirCalificacionUseCase.ejecutar(beta, EstudianteInput)
    → render con predicción
```

### 2.4 Problemas arquitectónicos observados

- Los casos de uso instancian **directamente** las clases de infraestructura
  (`academico/application/use_cases.py:8-10` y `:49`), violando la inversión de dependencias:
  el dominio/aplicación queda acoplado a pandas, NumPy, sklearn y matplotlib.
- `domain/repositories.py` está vacío: no existe el contrato que justificaría la capa.
- `presentation/forms.py` está vacío: la validación se hace a mano en la vista.
- No hay inyección de dependencias ni configuración centralizada.

---

## 3. Modelos de Datos y Relaciones

### 3.1 No existen modelos Django

No hay `models.py`, `migrations/`, `admin.py` ni `apps.py`. Por tanto:

- **No hay entidades ORM propias.**
- **No hay `ForeignKey`, `ManyToMany`, `OneToOne` ni relaciones de base de datos.**
- Las únicas tablas de `db.sqlite3` son las estándar de Django:
  `django_migrations`, `django_session`, `auth_*`, `django_admin_log`,
  `django_content_type`.

### 3.2 Modelo de dominio (en memoria)

Definido en `academico/domain/entities.py`:

| Entidad | Campos | Tipo |
|---|---|---|
| `EstudianteInput` | `horas_estudio`, `asistencia`, `tareas_completadas`, `nota_previa` | `float` |
| `ResultadoEntrenamiento` | `beta` (5 coefs.), `beta_sklearn` (5 coefs.), `interpretaciones` | listas/dicts |
| | `matriz_x_muestra` (6×5), `matriz_xt_muestra` (5×6), `vector_y_muestra` (6) | matrices NumPy serializadas a listas |
| | `dimensiones_x`, `dimensiones_xt`, `mae`, `rmse`, `r2`, `calidad_modelo` | escalares/texto |
| | `registros_tabla`, `resumen_datos`, `total_registros` | listas/dicts |
| | `grafica_dispersion`, `grafica_residuales` | Base64 (strings) |

### 3.3 Esquema de entrada CSV

Definido en `academico/infrastructure/csv_repository.py:6`:

```python
COLUMNAS_REQUERIDAS = ['X1', 'X2', 'X3', 'X4', 'Y']
```

Reglas actuales:
- Deben existir las 5 columnas (si no, `ValueError` en `:11-13`).
- Las filas con `NaN` se descartan silenciosamente (`:15`).
- Se exige un mínimo de **5 registros** (`:16-17`), sin exigir más que el número de parámetros.
- Columnas extra se ignoran (`:15`).
- `registros_tabla` y `resumen_datos` se derivan con pandas (`:23-43`).

### 3.4 Persistencia real: la sesión

El “estado del modelo” se guarda en `request.session['resultado_modelo']`
(`academico/presentation/views.py:21`). Con el backend por defecto, esto se serializa en la tabla
`django_session`.

Comprobación real con `estudiantes.csv` (20 filas): el payload serializado ocupa
**≈182.869 bytes**, y la fila existente en `django_session` mide **173.839 caracteres**.
La mayor parte corresponde a las **dos imágenes PNG en Base64** y a `registros_tabla`.

> No hay modelo relacional, pero sí un “modelo de datos” implícito y volátil en la sesión.

---

## 4. Endpoints, Vistas y Lógica de Negocio

### 4.1 Rutas

`config/urls.py`:

| Ruta | Destino | Nombre |
|---|---|---|
| `/admin/` | `admin.site.urls` | — |
| `/` | `academico.presentation.urls` → `views.dashboard` | `dashboard` |

`academico/presentation/urls.py:4-6` define una única ruta.

### 4.2 Vistas

| Vista | Tipo | Métodos | Archivo |
|---|---|---|---|
| `dashboard` | **FBV** (Function-Based View) | GET, POST | `academico/presentation/views.py:6-44` |

No hay CBV, `ViewSet`, `APIView` ni routers de DRF.

### 4.3 Acciones POST

La vista multiplexa dos acciones mediante el campo `accion` (`views.py:14`):

1. **`entrenar`** (`views.py:16-24`)
   - Requiere `request.FILES['archivo_csv']`.
   - Ejecuta `EntrenarModeloUseCase`, convierte el resultado con `asdict` y lo guarda en sesión.
   - Cualquier excepción se captura con `except Exception` y se muestra como texto.

2. **`predecir`** (`views.py:26-42`)
   - Requiere un `resultado_modelo` previo en sesión.
   - Convierte `x1..x4` con `float(...)`.
   - Ejecuta `PredecirCalificacionUseCase`.
   - Captura solo `ValueError`.

### 4.4 Autenticación y permisos

- **La vista `dashboard` es totalmente pública**: no tiene `@login_required`, `LoginRequiredMixin`,
  decoradores de permiso ni comprobaciones de usuario.
- **Cualquier visitante puede subir un CSV** y ejecutar el entrenamiento (CPU/memoria).
- `/admin/` sí usa la autenticación estándar de Django, pero no hay modelos propios registrados.
- **CSRF está correctamente habilitado** (`CsrfMiddleware` en `settings.py:46` y
  `{% csrf_token %}` en `dashboard.html:175` y `:209`).
- No hay rate limiting, throttling ni cuotas.

### 4.5 Dónde reside la lógica de negocio

| Lógica | Ubicación |
|---|---|
| Carga/validación/resumen del CSV | `infrastructure/csv_repository.py:8-45` |
| Cálculo OLS y métricas | `infrastructure/linear_regression.py:6-34` |
| Interpretación de coeficientes | `infrastructure/linear_regression.py:36-69` |
| Predicción y clipping 0–100 | `infrastructure/linear_regression.py:71-74` |
| Orquestación y clasificación de calidad | `application/use_cases.py:12-45` |
| Gestión de estado HTTP/sesión | `presentation/views.py` |

La vista es relativamente delgada (44 líneas), lo cual es positivo, pero toda la lógica
depende de infraestructura concreta y no hay capa de validación formal.

### 4.6 Interfaz

`dashboard.html` (566 líneas) incluye:
- Formulario de carga CSV y formulario de inferencia.
- Estado vacío vs. panel de resultados.
- Tres pestañas: diagnóstico, matricial y registros.
- Gráficas embebidas como `data:image/png;base64,...`.
- Tailwind y Google Fonts cargados desde CDN.

Referencia a un campo inexistente: `dashboard.html:178` usa
`{% if resultado.nombre_archivo %}`, pero `ResultadoEntrenamiento` **no define**
`nombre_archivo`; el bloque nunca se muestra (código muerto).

---

## 5. Auditoría Técnica (Bugs, Seguridad y Rendimiento)

### 5.1 Consultas ORM y N+1

- **No aplica N+1 clásico**: no hay modelos Django ni `QuerySet` de negocio.
- Sí hay acceso implícito a base de datos en **cada petición**: el `SessionMiddleware`
  consulta `django_session` para cargar (y al final guardar) el resultado.
- **Sesión sobredimensionada:** se guardan en sesión las dos gráficas Base64, la tabla completa
  de registros, la matriz de muestra y el resumen. Medido: **~174–183 KB por sesión** para solo
  20 filas. Con CSV grandes crece de forma aproximadamente lineal.
- Consecuencias:
  - Lectura/escritura de un `TEXT` grande en SQLite en cada request.
  - Envío repetido de Base64 al navegador en cada render.
  - Si en el futuro se cambia a `signed_cookies`, **la cookie superará el límite de ~4 KB**
    y el modelo no se podrá persistir (fallo latente de diseño).

### 5.2 Bugs y robustez

| # | Severidad | Hallazgo | Ubicación |
|---|---|---|---|
| B1 | Alta | `float(request.POST.get('x1'))`: si el campo falta, `float(None)` lanza **`TypeError`**, que **no** es capturado por `except ValueError` → **HTTP 500**. | `presentation/views.py:32-42` |
| B2 | Alta | Solo se valida la extensión/nombre en el cliente (`accept=".csv"`). El servidor pasa el archivo directamente a `pd.read_csv` sin comprobar tipo, tamaño ni número de filas. | `views.py:16-19`, `dashboard.html:187` |
| B3 | Media | `except Exception as e` muestra `str(e)` al usuario y **no registra logs**. Puede filtrar detalles internos y ocultar errores de programación. | `views.py:23-24` |
| B4 | Media | `ResultadoEntrenamiento` no tiene `nombre_archivo`, pero la plantilla lo referencia. | `domain/entities.py:11-38`, `dashboard.html:178` |
| B5 | Media | matplotlib con estado global (`plt.savefig`, `plt.close(fig)`) **no es thread-safe**. Dos entrenamientos concurrentes pueden intercambiar gráficas o corromper la salida. | `infrastructure/chart_generator.py:11` |
| B6 | Media | Solo se exige `n >= 5`; con 5 filas y 5 parámetros (incluido intercepto) el sistema es cuadrado/singular y el ajuste es trivial/degenerado. Debería exigirse `n > p + 1` (margen estadístico). | `csv_repository.py:16-17` |
| B7 | Media | El cálculo con `np.linalg.pinv(XTX)` sobre la ecuación normal puede ser numéricamente inestable con variables mal escaladas o colineales. `np.linalg.lstsq` sobre `X` es preferible. | `linear_regression.py:14-17` |
| B8 | Baja | `df.dropna()` elimina filas inválidas sin avisar ni informar cuántas se descartaron. | `csv_repository.py:15` |
| B9 | Baja | No hay validación de rangos en servidor (`x1` 0–80, `x2..x4` 0–100 solo en HTML). | `dashboard.html:217-250`, `views.py:32-37` |
| B10 | Baja | La predicción se recorta silenciosamente a `[0, 100]`; puede ocultar un modelo mal ajustado. | `linear_regression.py:74` |
| B11 | Baja | `plt.savefig(...)` guarda la figura “actual” en lugar de `fig.savefig(...)`; funciona por accidente y es frágil. | `chart_generator.py:11` |
| B12 | Baja | Archivo residual `10` en la raíz y archivos vacíos (`repositories.py`, `forms.py`). | raíz / `domain/` / `presentation/` |
| B13 | Baja | Cada recarga del panel reenvía las dos imágenes Base64 completas; no hay caché ni endpoint separado. | `views.py:6-44`, plantilla |

### 5.3 Seguridad

Resultado real de `python manage.py check --deploy`:

```
ERRORS:
?: (mail.E001) MAILERS usa backend de desarrollo (console.EmailBackend)
WARNINGS:
?: (security.W004) SECURE_HSTS_SECONDS no configurado
?: (security.W008) SECURE_SSL_REDIRECT no es True
?: (security.W009) SECRET_KEY insegura (prefijo django-insecure-)
?: (security.W012) SESSION_COOKIE_SECURE no es True
?: (security.W016) CSRF_COOKIE_SECURE no es True
?: (security.W018) DEBUG = True
?: (security.W020) ALLOWED_HOSTS vacío
```

Hallazgos adicionales:

| # | Severidad | Hallazgo | Ubicación |
|---|---|---|---|
| S1 | **Crítica** | `SECRET_KEY` hardcodeada en el repositorio. | `config/settings.py:23` |
| S2 | **Crítica** | `DEBUG = True` (páginas de error detalladas, fuga de configuración). | `config/settings.py:26` |
| S3 | **Alta** | `ALLOWED_HOSTS = []`; en producción rompe o, mal configurado, facilita Host header attacks. | `config/settings.py:28` |
| S4 | **Alta** | Endpoint público de subida y cómputo pesado sin autenticación ni límites → **DoS** por CPU/memoria (pandas + sklearn + matplotlib en el hilo de la petición). | `presentation/views.py:6-24` |
| S5 | Media | Sin cabeceras de endurecimiento: HSTS, `SECURE_SSL_REDIRECT`, cookies `Secure`/`HttpOnly`/`SameSite`, `X_FRAME_OPTIONS`. | `config/settings.py` |
| S6 | Media | Dependencias frontend por CDN sin SRI ni CSP (`cdn.tailwindcss.com`, Google Fonts): riesgo de supply chain y de privacidad. | `dashboard.html:7-8` |
| S7 | Media | Email backend de consola; `check --deploy` lo marca como error. | `config/settings.py:124-128` |
| S8 | Media | Sin gestión de secretos por entorno ni `.gitignore`; `db.sqlite3` con sesiones se distribuye con el proyecto. | raíz |
| S9 | Baja | No hay logging de seguridad/errores; los fallos de entrenamiento no dejan traza. | `views.py:23-24` |

**Aspectos positivos de seguridad:**
- CSRF activo y usado en ambos formularios.
- El motor de plantillas de Django **autoescapa** por defecto; `{{ error }}` no genera XSS
  directo (aunque sí puede revelar mensajes internos).
- No hay SQL crudo ni concatenación de SQL → sin inyección SQL.
- No se deserializan datos no confiables (no `pickle`/`eval`).
- pandas solo lee columnas numéricas y no ejecuta fórmulas del CSV.

### 5.4 Rendimiento

| # | Hallazgo | Impacto | Ubicación |
|---|---|---|---|
| P1 | Base64 de gráficas + dataset completo en sesión (~174 KB–183 KB con 20 filas) | I/O de sesión y HTML inflados en cada request | `views.py:20-22` |
| P2 | Entrenamiento, sklearn y matplotlib **dentro del ciclo petición/respuesta** | Respuestas lentas; bloqueo de worker; vulnerable a DoS | `views.py:18-19` |
| P3 | `new_df` completo se renderiza sin paginación (`max-h` solo visual) | HTML grande con datasets grandes | `dashboard.html:518-549` |
| P4 | Sin límite de filas del CSV | Memoria/CPU no acotadas | `csv_repository.py:8-20` |
| P5 | matplotlib se inicializa y grafica en cada entrenamiento; sin caché | Coste evitable | `chart_generator.py` |
| P6 | SQLite con sesiones y posible concurrencia de escritura | Bloqueos bajo carga | `settings.py:76-81` |
| P7 | `resumen_datos` y `registros_tabla` se serializan/deserializan completos en cada request | Coste redundante | `use_cases.py:40-42` |

### 5.5 Deuda técnica

- **Sin tests**: no existe `tests.py`, carpeta `tests/` ni `pytest.ini`/`tox.ini`.
- **Sin `requirements.txt`/`pyproject.toml`**: imposible reproducir el entorno.
- **Sin README ni documentación**.
- **Sin `.gitignore`**; el proyecto ni siquiera es un repositorio Git.
- **Sin logging** estructurado ni manejo centralizado de errores.
- **`academico` fuera de `INSTALLED_APPS`**: funciona, pero dificulta el descubrimiento
  automático y el uso futuro de modelos/migraciones/admin.
- **Capa de dominio vacía** (`repositories.py`) y casos de uso acoplados a infraestructura.
- **Sin tipado en la vista** ni validación con forms (archivo `forms.py` vacío).
- **Configuración monolítica** sin separación dev/prod.
- **Idioma/zonas**: `LANGUAGE_CODE='en-us'`, `TIME_ZONE='UTC'` en una app en español.
- **Archivos residuales** (`10`) y plantilla muy extensa con lógica/estilos inline.

---

## 6. Plan de Acción Priorizado

### 6.1 Prioridad ALTA (seguridad y corrección inmediata)

| # | Tarea | Archivo / línea aproximada |
|---|---|---|
| A1 | Mover `SECRET_KEY` a variable de entorno, rotarla y no versionarla. | `config/settings.py:23` |
| A2 | `DEBUG = False` por defecto y activarlo solo vía entorno de desarrollo. | `config/settings.py:26` |
| A3 | Configurar `ALLOWED_HOSTS` desde entorno. | `config/settings.py:28` |
| A4 | Corregir el parseo de `x1..x4`: comprobar `None`, capturar `(ValueError, TypeError)` y validar rangos en servidor. | `academico/presentation/views.py:32-42` |
| A5 | Limitar/proteger el endpoint: autenticación (o `@login_required` + permisos), tamaño máximo de archivo, extensión y número máximo de filas. | `views.py:6-24`, `settings.py` |
| A6 | Sustituir `except Exception` por excepciones específicas y registrar con `logging` (sin exponer detalles internos al cliente). | `views.py:23-24` |
| A7 | Reducir el estado en sesión: guardar solo `beta` y métricas; **no** guardar Base64 ni el dataset completo. Regenerar gráficas o servirlas por endpoint/caché. | `views.py:20-22`, `use_cases.py:27-45` |
| A8 | Crear `requirements.txt` (o `pyproject.toml`) con las versiones verificadas. | raíz |
| A9 | Endurecer cookies y HTTPS: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SECURE_PROXY_SSL_HEADER`. | `config/settings.py` |
| A10 | Mover el cómputo pesado a una tarea asíncrona (Celery/RQ/hilo) o como mínimo imponer límites de recursos y timeout. | `application/use_cases.py`, `views.py` |

### 6.2 Prioridad MEDIA (robustez, arquitectura y rendimiento)

| # | Tarea | Archivo / línea aproximada |
|---|---|---|
| M1 | Añadir `AppConfig` (`apps.py`) y registrar `academico` en `INSTALLED_APPS`. | `academico/`, `settings.py:33-40` |
| M2 | Hacer thread-safe la generación de gráficas: usar `Figure` locales o un `threading.Lock`. | `infrastructure/chart_generator.py:11,29,54` |
| M3 | Usar `np.linalg.lstsq(X, Y)` en lugar de invertir `XᵀX`, o al menos comprobar el condicionamiento. | `infrastructure/linear_regression.py:14-17` |
| M4 | Exigir `n > p + 1` (más de 5 filas, idealmente un mínimo configurable) e informar filas descartadas. | `infrastructure/csv_repository.py:15-17` |
| M5 | Definir el contrato en `repositories.py` e inyectar dependencias en los casos de uso (DIP). | `domain/repositories.py`, `application/use_cases.py:7-10,48-49` |
| M6 | Eliminar o implementar `nombre_archivo` en el resultado. | `domain/entities.py`, `dashboard.html:178` |
| M7 | Añadir tests unitarios de `csv_repository`, `linear_regression` y de la vista (casos válidos, CSV inválido, campos faltantes). | nuevo `academico/tests/` |
| M8 | Añadir validación de formularios con `forms.py` (CSV + inferencia) y mensajes de error claros. | `presentation/forms.py`, `views.py` |
| M9 | Auto-hospedar Tailwind/fuentes o añadir `integrity` (SRI) y una CSP básica. | `dashboard.html:7-8`, `settings.py` |
| M10 | Configurar `MAILERS`/SMTP por entorno para eliminar el error de `check --deploy`. | `config/settings.py:124-128` |
| M11 | Paginar o limitar la tabla de registros y evitar serializar todo el dataset. | `dashboard.html:518-549`, `use_cases.py:40` |
| M12 | Añadir logging de aplicación y manejo de errores centralizado. | `config/settings.py`, `views.py` |
| M13 | Separar settings por entorno (`base/dev/prod`) y leerlos de variables de entorno. | `config/settings.py` |

### 6.3 Prioridad BAJA (calidad y mantenimiento)

| # | Tarea | Archivo / línea aproximada |
|---|---|---|
| L1 | Ajustar `LANGUAGE_CODE = 'es'` y `TIME_ZONE` acorde al despliegue. | `config/settings.py:106-112` |
| L2 | Eliminar el archivo residual `10` y los archivos vacíos no usados. | raíz, `domain/repositories.py`, `presentation/forms.py` |
| L3 | Usar `fig.savefig(...)` en lugar de `plt.savefig(...)`. | `infrastructure/chart_generator.py:11` |
| L4 | Añadir `.gitignore` (`venv/`, `db.sqlite3`, `__pycache__/`, `*.pyc`, `.env`) e inicializar Git. | raíz |
| L5 | Añadir `README.md` con instalación, variables de entorno y ejecución. | raíz |
| L6 | Advertir cuando el modelo tenga mal condicionamiento o baja calidad; no recortar predicciones en silencio. | `linear_regression.py:32,74` |
| L7 | Extraer estilos/JS de la plantilla y dividirla en parciales. | `dashboard.html` |
| L8 | Evaluar migrar de SQLite a PostgreSQL si se espera concurrencia o más usuarios. | `config/settings.py:76-81` |
| L9 | Añadir tipado (`type hints`) y docstrings en vistas y casos de uso. | `presentation/views.py`, `application/use_cases.py` |

---

## Anexo A. Comandos y comprobaciones realizadas

```bash
# Versiones reales del entorno
venv/bin/python -c "import sys, django; print(sys.version); print(django.get_version())"
# Python 3.14.10 / Django 6.1.3

# Comprobación estándar
venv/bin/python manage.py check
# System check identified no issues (0 silenced).

# Comprobación de despliegue
venv/bin/python manage.py check --deploy
# 1 error (mail.E001) + 7 warnings de seguridad

# Serialización del resultado del modelo en sesión
# -> OK, ~182.869 bytes para estudiantes.csv (20 filas)

# Contenido de django_session
# -> 1 fila, session_data de 173.839 caracteres
```

## Anexo B. Matriz de riesgos resumida

| Riesgo | Probabilidad | Impacto | Prioridad |
|---|---|---|---|
| Exposición por `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS` | Alta | Crítico | Alta |
| DoS por subida/cómputo sin límites | Media | Alto | Alta |
| Error 500 por `TypeError` en inferencia | Media | Medio | Alta |
| Sesión gigante / degradación progresiva | Alta | Medio | Alta |
| Gráficas cruzadas por concurrencia matplotlib | Media | Medio | Media |
| Inestabilidad numérica del modelo | Baja/Media | Medio | Media |
| Regresiones por ausencia de tests | Alta | Medio | Media |
| Falta de reproducibilidad (sin requirements) | Alta | Medio | Alta |

---

**Dictamen:** proyecto didáctico bien organizado en capas y funcional, con una UI cuidada y
cálculos correctos para el caso de uso. Antes de cualquier despliegue real debe resolverse la
configuración de seguridad, la validación/limitación de la subida, el manejo del estado en
sesión y la ausencia de tests y dependencias declaradas.
