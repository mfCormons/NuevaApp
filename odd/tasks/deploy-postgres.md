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

## Server (relevamiento 2026-09-24)
- Hostinger VPS `srv857300` (69.62.95.88), Ubuntu 22.04.5 LTS, 7.8GB RAM, 97GB disco, Python 3.10.12.
- Acceso: root por SSH; **el usuario administra el server**.
- Ya corriendo: nginx (80/443), MySQL (127.0.0.1:3306, bases cormons/cormons_app), 8 gunicorn en 127.0.0.1:8000-8007 para las apps Django (`*.cormons.app`).
- **NO hay PostgreSQL** → se instala en el server (decidido 2026-09-24, junto a MySQL, conviven).
- Patrón de deploy existente a replicar: clone como `www-data` en /home/cormons/ → venv → gunicorn_<name>.service en puerto local libre → server block nginx con subdominio *.cormons.app → certbot.
- Hallazgo de seguridad: `mysql -u root` entra sin contraseña (aviso al administrador, no arreglar en este feature).
- Progreso deploy:
  - [x] Repo PGDG agregado (`jammy-pgdg`) + `apt update` OK (warnings de `ubuntu-mirrors.list` duplicado = preexistente, inofensivo)
  - [x] `postgresql-18` instalado — 18.6 (Ubuntu 18.6-1.pgdg22.04+2), servicio `active`
  - [x] Post-reinicio needrestart (OK accidental): 22 servicios reiniciados, 0 failed; mysql/nginx/postgresql `active`
  - [x] Crear rol+base `nuevaapp` en el server (usuario dedicado, menor privilegio)
  - [x] Verificar conexión TCP `-h 127.0.0.1` (misma que usará la app) — `current_user=nuevaapp | current_database=nuevaapp`
- Reboot del kernel (5.15.0-164 → 5.15.0-191) queda PENDIENTE: se elige ventana de mantenimiento al final del deploy.

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