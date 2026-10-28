# Tabla de la API

Base local: `http://127.0.0.1:8000`. Enviar `Content-Type: application/json` y `Accept: application/json`. Los ID de ejemplo dependen de los datos creados. Las listas usan paginación de cinco registros.

| Recurso | Dirección | Método | Cuerpo de ejemplo | Respuesta esperada |
|---|---|---|---|---|
| Examen | `/api/exams/` | GET | Sin cuerpo | 200, página de exámenes |
| Examen | `/api/exams/{id}/` | GET | Sin cuerpo | 200, examen; 404 si no existe |
| Examen | `/api/exams/` | POST | `{"title":"Python","description":"Prueba"}` | 201, examen creado con `id` y `created_at` |
| Examen | `/api/exams/{id}/` | PATCH | `{"description":"Actualizado"}` | 200, examen actualizado |
| Examen | `/api/exams/{id}/` | PUT | `{"title":"Python","description":"Completo"}` | 200, examen actualizado |
| Examen | `/api/exams/{id}/` | DELETE | Sin cuerpo | 204, sin cuerpo; eliminación en cascada |
| Pregunta | `/api/questions/` | GET | Sin cuerpo | 200, página de preguntas con opciones anidadas |
| Pregunta | `/api/questions/{id}/` | GET | Sin cuerpo | 200, pregunta; 404 si no existe |
| Pregunta | `/api/questions/` | POST | `{"exam":1,"text":"¿Qué es Django?","options":[{"text":"Framework","is_correct":true},{"text":"Base de datos","is_correct":false}]}` | 201, pregunta y opciones con sus ID |
| Pregunta | `/api/questions/{id}/` | PATCH | `{"text":"Enunciado actualizado"}` | 200, conserva opciones existentes |
| Pregunta | `/api/questions/{id}/` | PATCH | `{"options":[{"text":"Nueva respuesta","is_correct":true}]}` | 200, reemplaza todas las opciones |
| Pregunta | `/api/questions/{id}/` | PUT | `{"exam":1,"text":"Enunciado completo","options":[{"text":"Respuesta","is_correct":true}]}` | 200, pregunta actualizada |
| Pregunta | `/api/questions/{id}/` | DELETE | Sin cuerpo | 204, sin cuerpo; elimina opciones |
| Opción | `/api/options/` | GET | Sin cuerpo | 200, página de opciones |
| Opción | `/api/options/{id}/` | GET | Sin cuerpo | 200, opción; 404 si no existe |
| Opción | `/api/options/` | POST | `{"question":1,"text":"Distractor","is_correct":false}` | 201, opción creada; la pregunta debe conservar una correcta |
| Opción | `/api/options/{id}/` | PATCH | `{"text":"Otro distractor"}` | 200, opción actualizada |
| Opción | `/api/options/{id}/` | PUT | `{"question":1,"text":"Texto completo","is_correct":false}` | 200 si conserva la regla de respuesta correcta |
| Opción | `/api/options/{id}/` | DELETE | Sin cuerpo | 204 si es incorrecta; 400 si es la correcta |

Las respuestas de detalle de examen incluyen `id`, `title`, `description`, `created_at`. Las de pregunta incluyen `id`, `exam`, `text`, `options`, `created_at`. Cada opción anidada incluye `id`, `text`, `is_correct`; la opción individual también incluye `question`.

Ejemplo de lista:

```json
{"count":1,"next":null,"previous":null,"results":[{"id":1,"title":"Python","description":"Prueba","created_at":"2026-10-28T10:00:00-05:00"}]}
```

La fecha anterior es ilustrativa. Las respuestas reales están en [http-results.json](http-results.json).

## Errores previstos

| Caso | Solicitud | Resultado |
|---|---|---|
| Campo obligatorio ausente | POST `/api/exams/` con `{}` | 400, error en `title` |
| Tipo incorrecto | POST `/api/questions/` con `exam: "bad"` y demás campos válidos | 400, error en `exam` |
| Ninguna correcta | POST `/api/questions/` con todas las opciones falsas | 400, `options: ["Exactly one option must be correct."]` |
| Dos correctas | POST o PATCH de pregunta con dos opciones verdaderas | 400, mismo error de `options` |
| Eliminar la única correcta | DELETE de una opción correcta | 400, error en `is_correct` |
| Cambiar de pregunta | PATCH de opción con otro `question` | 400, error en `question` |
| Filtro inválido | GET `/api/questions/?exam=bad` | 400, error en `exam` |
| Recurso inexistente | GET `/api/exams/99999/` en una base sin ese ID | 404 |

DRF localiza sus mensajes estándar según el idioma configurado. Los mensajes de validación propios están en inglés, como el código del proyecto.

## Operaciones adicionales

GET `/api/` devuelve enlaces a los tres recursos. Las colecciones y detalles admiten OPTIONS y HEAD. En un navegador, DRF entrega formularios HTML para operar sobre la misma API. Se puede filtrar por examen y buscar texto con `/api/questions/?exam=1&search=Django`. El parámetro `page=2` solicita la segunda página.

Referencia técnica: [serializadores anidados de Django REST Framework](https://www.django-rest-framework.org/api-guide/serializers/#writing-create-methods-for-nested-representations).
