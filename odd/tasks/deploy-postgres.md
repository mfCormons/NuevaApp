# Feature: Migrate NuevaApp to PostgreSQL for production

## Objective
Levantar NuevaApp como web app de producción estándar con PostgreSQL como motor de base de datos, en el VPS Hostinger. Primera etapa: adaptar la app localmente a PostgreSQL y probarla en local contra Postgres.

## Problem / Why
- El jefe pidió levantar la app sin limitarse a VFP: estándar de producción.
- SQLite es un archivo local sin protocolo de red; no es el estándar para producción web.
- PostgreSQL es el motor client/server estándar en el ecosistema Python web.
- Paridad dev/prod: mismo motor en local y en el server.

## Scope
- [x] Decidir motor: PostgreSQL (estándar producción, refuerza el camino VFP vía ODBC si luego se pide)
- [x] Instalar PostgreSQL local (Windows, winget) — PostgreSQL 18.6-4, servicio postgresql-x64-18 running
- [x] Crear base/rol local (`nuevaapp`, usuario dedicado `nuevaapp`/`nuevaapp_dev`, DB dueña del rol)
- [x] Adaptar `app.py`: `sqlite3` → `psycopg` y conexión vía `DATABASE_URL` (commit 72493af)
- [x] Adaptar `seed_db.py` a PostgreSQL (commit 72493af)
- [x] Actualizar `requirements.txt` con psycopg (psycopg[binary]==3.3.6, commit 72493af)
- [x] Probar local: seed + `/api/consultar` + `/health` (test_client: 200/ok, n1=Valor 1, 404) — commit 72493af
- [x] Commit por work-unit: `72493af feat: migrate app from SQLite to PostgreSQL` (branch feature/postgres-local, sin push)
- [ ] (Siguiente feature/stage) Deploy en VPS: PostgreSQL, gunicorn, systemd, nginx, certbot, ufw

## Constraints
- Proyecto de aprendizaje: cambios explicados, sin capa de abstracciones innecesaria.
- Otros desarrollos en producción en el VPS: cuidado con nginx/ufw/ports.
- Commits: Conventional Commits, sin atribución AI.

## Decisiones de arquitectura
- **Doble vía de carga de datos (DUAL)**: ODBC (VFP → psqlODBC → PostgreSQL) + API (VFP/otros → HTTP/JSON → Flask → PostgreSQL). Ambas escriben la misma tabla; Postgres tolera escrituras concurrentes de múltiples fuentes. Advertencia: por ODBC los datos entran sin validación de la app; por API la app valida/loguea.
- **PENDIENTE — mapeo de tipos VFP ↔ PostgreSQL**: revisar compatibilidad (p.ej. "C" Caracter de VFP vs TEXT/VARCHAR de Postgres; Numeric vs NUMERIC; Date/DateTime vs DATE/TIMESTAMP; Logical vs BOOLEAN; Memo vs TEXT; tipos sin equivalente como General/OLE). Verificar con el dev de VFP y con pruebas ODBC reales.

## Acceptance criteria
- Local: `DATABASE_URL` apunta a Postgres local; `/health` ok; `/api/consultar?numero=1` devuelve `{"valor": "Valor 1"}`.
- seed_db.py crea la tabla `valores` y la alimenta.
- Todo el código corre contra Postgres: ninguna referencia activa a SQLite.

## Checks (modo TDD: OFF — sin framework de tests configurado; checks funcionales ordinarios)
- `python seed_db.py` (crea + seed)
- `flask` local o gunicorn: GET /health
- GET /api/consultar?numero=1 y ?numero=999 (404)

## Delivery strategy
- ask-on-risk (default). Forecast: < 400 líneas por task — sin split.

## Progress
- [x] 2026-09-24: decisión PostgreSQL, sesión preflight. Documento creado.