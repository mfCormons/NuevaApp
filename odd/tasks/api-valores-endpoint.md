# Feature: API de carga de datos — POST /api/valores

## Objetivo
Exponer un endpoint HTTP que acepte carga de registros en `valores` (uno o lote),
primera pata de la estrategia DUAL de alimentación (API + ODBC).

## Por qué
- Decisión DUAL registrada: ODBC (VFP directo) + API (VFP/otros vía HTTP/JSON).
- La API es el camino estándar: valida, centraliza lógica y no expone la base.

## Alcance
- `app.py`: nueva ruta `POST /api/valores` que acepta un objeto JSON o una lista
  de objetos `{numero, valor}`; upsert sobre `ON CONFLICT (numero)` para que
  re-alimentar sea idempotente.
- No incluye: autenticación (pendiente futuro), mapeo de tipos VFP (pendiente
  definido con el dev de VFP), vía ODBC (tarea del lado del cliente VFP).

## Restricciones
- Estilo del proyecto existente: mensajes de error en español, sin capas extra.
- TDD OFF (no hay framework de tests en el repo); verificación funcional con
  `app.app.test_client()`.
- Convenciones: commit Conventional, sin atribución AI.

## Tareas
- [ ] Implementar `POST /api/valores` en `app.py` (single + lote, validación, upsert)
- [ ] Verificar: POST single 201, POST lote 201, GET refleja datos, 400s (sin body, numero no int, valor vacío), upsert re-ejecución
- [ ] Commit work-unit en `feature/postgres-local`

## Criterios de aceptación
- `curl -X POST .../api/valores -d '{"numero":10,"valor":"Valor 10"}'` → 201
- Lote de N filas → 201 con N insertados
- Reenviar el mismo numero → actualiza, no duplica ni error
- Consulta desde SQLTools muestra los registros nuevos

## Progreso
- 2026-09-24: doc creado; tareas pendientes.
