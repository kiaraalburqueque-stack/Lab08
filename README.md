# Laboratorio 08 API REST con Django

API funcional de cuestionarios para Desarrollo de Aplicaciones Empresariales. Expone exámenes, preguntas y opciones con Django REST Framework, serializadores de modelo, validación de respuestas y operaciones HTTP.

## Ejecutar en Windows

Requiere Python 3.12 o superior y Git. Desde PowerShell:

```powershell
git clone https://github.com/kiaraalburqueque-stack/Lab08.git
cd Lab08
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Abrir http://127.0.0.1:8000/api/ para recorrer la API navegable. `seed_demo` es opcional e idempotente: carga un examen y siete preguntas para ver dos páginas. No requiere activar PowerShell ni crear un usuario. Para usar el administrador: ` .\.venv\Scripts\python.exe manage.py createsuperuser`.

## Recursos y decisiones

- `/api/exams/`: exámenes, con título y descripción.
- `/api/questions/`: preguntas; `exam` es un identificador y `options` es una lista anidada de lectura y escritura.
- `/api/options/`: opciones individuales relacionadas mediante `question`.

Los tres usan `ModelViewSet` y `DefaultRouter`. Los identificadores y fechas son de solo lectura. La creación de una pregunta y sus opciones es atómica. Cada pregunta debe tener exactamente una opción correcta. Un PATCH sin `options` conserva las existentes; si incluye `options`, reemplaza toda la colección y genera nuevos identificadores. Un PUT requiere los campos obligatorios, incluida la colección de opciones.

El recurso individual de opciones permite agregar respuestas incorrectas, cambiar textos y eliminar respuestas incorrectas. Rechaza una segunda correcta, quitar la única correcta o mover una opción a otra pregunta. Para cambiar la respuesta correcta, enviar toda la lista en un PATCH de la pregunta. La base de datos agrega una restricción de unicidad para impedir dos opciones correctas por pregunta.

Eliminar un examen elimina sus preguntas y opciones; eliminar una pregunta elimina sus opciones.

## Filtro búsqueda y paginación

```text
/api/questions/?exam=1
/api/questions/?search=Django
/api/questions/?exam=1&search=Django&page=2
```

Se devuelven cinco registros por página, ordenados por ID, con `count`, `next`, `previous` y `results`. `exam` debe ser un entero positivo; un filtro inválido devuelve 400. Una página inexistente devuelve 404. La búsqueda usa el texto del enunciado.

## Verificación

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe scripts/verify_http.py
```

El cliente externo `requests` inicia un servidor real en un puerto libre y una base temporal, recorre las cinco operaciones de los tres recursos, provoca errores y comprueba filtros, búsqueda, paginación y respuestas HTML de la API navegable. Cierra el servidor y elimina su base temporal. No modifica `db.sqlite3`.

Resultados de la ejecución: **6 pruebas automatizadas correctas y 39 solicitudes HTTP correctas**. Las solicitudes y respuestas completas están en [docs/http-results.json](docs/http-results.json). Para repetir las operaciones en VS Code con REST Client se incluye [docs/api.http](docs/api.http).

## Documentación y entrega

- [Tabla completa de la API y ejemplos](docs/API.md).
- [Desarrollo y conclusiones del laboratorio](docs/INFORME.md).
- [Evidencia de las solicitudes HTTP ejecutadas](docs/http-results.json).

## Configuración

SQLite permite ejecutar el laboratorio sin servicios adicionales. `AllowAny` permite practicar las operaciones sin autenticación en el entorno local. `SessionAuthentication` conserva la protección CSRF para sesiones autenticadas. Esta configuración es académica; antes de publicar en internet deben definirse permisos y autenticación apropiados.

`DJANGO_DEBUG` vale `1` por defecto. Con `DJANGO_DEBUG=0`, es obligatorio definir `DJANGO_SECRET_KEY`. La clave local se genera durante el arranque y no se guarda en el repositorio. `DJANGO_ALLOWED_HOSTS` admite nombres separados por comas; por defecto acepta únicamente direcciones locales. `DJANGO_DB_PATH` permite cambiar la ubicación de SQLite. Estas variables se leen del entorno; un archivo `.env` no se carga automáticamente.

## Estructura

```text
config/                  Configuración, rutas y WSGI
quiz/
  migrations/            Esquema versionado
  management/commands/   Datos de demostración
  models.py              Exam, Question y Option
  serializers.py         Relaciones y validaciones
  views.py               ViewSets, filtros y búsqueda
  tests.py               Pruebas de regresión
scripts/verify_http.py    Cliente HTTP externo reproducible
docs/                    Tabla, informe y evidencia
manage.py
requirements.txt
```
