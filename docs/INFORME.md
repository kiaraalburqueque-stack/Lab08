# Desarrollo del laboratorio 08

## Implementación de servicios web con Django

Este proyecto expone los modelos de cuestionarios mediante Django REST Framework. El objetivo es crear, consultar, actualizar y eliminar recursos por HTTP, validar los datos de entrada y documentar las respuestas observadas.

## Desarrollo

Se implementaron los modelos `Exam`, `Question` y `Option`, sus migraciones y serializadores derivados de `ModelSerializer`. El examen se referencia por identificador y las opciones viajan anidadas dentro de cada pregunta. La escritura anidada se realiza mediante operaciones atómicas para guardar la pregunta y sus opciones juntas.

La validación exige exactamente una opción correcta por pregunta. También se revisan las modificaciones desde el recurso individual de opciones para mantener esa regla. Los identificadores y las fechas de creación son de solo lectura. Las relaciones usan eliminación en cascada.

Los tres `ModelViewSet` se registraron en un `DefaultRouter`, incluido desde `config/urls.py`. Se configuró paginación de cinco registros y permisos de acceso para la práctica local. Las preguntas admiten filtro por examen y búsqueda por texto.

## Casos de prueba y resultado

Se ejecutaron seis pruebas automatizadas para comprobar escritura anidada, actualización parcial, rechazo de colecciones inválidas, integridad al modificar opciones, relaciones, campos de solo lectura, filtros, búsqueda, paginación y eliminación en cascada. Todas finalizaron correctamente.

Además, `scripts/verify_http.py` levantó un servidor real y utilizó el cliente externo `requests` sobre una base temporal. Las 39 solicitudes cumplieron los estados esperados: 200 para consultas y modificaciones, 201 para creación, 204 para eliminación, 400 para entradas inválidas y 404 para recursos eliminados. El archivo `docs/http-results.json` contiene el método, ruta, cuerpo enviado, estado esperado, estado obtenido y respuesta de cada solicitud.

Se provocaron los tres errores solicitados: campo obligatorio ausente, identificador de examen con tipo incorrecto y pregunta sin opción correcta. Todos devolvieron 400. También se comprobó el rechazo de eliminar la respuesta correcta y reemplazar las opciones con una lista vacía.

Las pruebas HTTP verificaron que las tres colecciones entregan la API navegable en HTML. El recorrido interactivo mediante formularios y las capturas para el campus deben completarse durante la demostración del estudiante; las verificaciones HTML no sustituyen esas capturas.

## Evidencias para completar la entrega académica

1. Registrar el nombre del alumno y el reparto real de trabajo si participa un equipo.
2. Capturar la estructura del proyecto en el editor.
3. Ejecutar los comandos de prueba del README y capturar sus resultados.
4. Abrir `/api/` y recorrer listar, detalle, crear, modificar parcialmente y eliminar desde los formularios del navegador; capturar los resultados y sus estados.
5. Adjuntar la tabla `docs/API.md` y las respuestas del cliente externo.
6. Presentar el enlace del repositorio y subir el entregable al campus virtual.

## Conclusiones

Los serializadores de modelo permiten validar los datos antes de guardarlos. La escritura anidada reúne la pregunta y sus respuestas en una sola operación, mientras que la validación en el recurso de opciones evita cambios que contradigan la regla del cuestionario.

Los conjuntos de vistas y el enrutador ofrecen rutas consistentes para los tres recursos. La comprobación con un cliente HTTP externo confirma los códigos y respuestas reales. La búsqueda, el filtro por examen y la paginación permiten consultar el cuestionario sin devolver todos sus registros en cada solicitud.
