# PDFintoWord

Professional SaaS platform for converting PDF documents into editable Word (DOCX) files with layout preservation.

## Architecture

- **API**: FastAPI (`:8000`)
- **Worker**: Celery + Redis
- **Database**: PostgreSQL
- **Storage**: Local filesystem (dev) or Oracle Object Storage (prod)

## Conversion quality — visual reconstruction

PDF pages are treated as a **visual canvas**, not plain text. **Accurate** mode runs:

```
PDF → layout analysis → visual blocks → reading flow → typography
    → invisible layout grid → DOCX rendering → mirror-like Word output
```

- **Grid engine** — maps PDF coordinates to an invisible Word table (no borders); cells merged to match block width/height.
- **Typography** — font size, bold/italic/underline, colors, alignment, line spacing per block.
- **Tables** — nested editable tables inside grid cells; cell colors when available.
- **Images** — sized to PDF dimensions within grid cells.
- **OCR** — scanned PDFs use the same visual pipeline after PaddleOCR/Tesseract.
- **Fast mode** — lighter flow (paragraph-based layout, still keeps colors).

For invoices, statements, forms, and multi-column PDFs, use **Accurate** mode.

## Requirements

- **Docker Compose V2** only — use `docker compose` (with a space), not legacy `docker-compose` V1.

## Quick start

From the **project root**:

```bash
cp infrastructure/.env.example infrastructure/.env
docker compose up --build
```

Or from `infrastructure/`:

```bash
cd infrastructure
cp .env.example .env
docker compose up --build
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

Host ports (if you need to connect from outside Docker): Postgres **5433**, Redis **6380** — internal services still use `postgres:5432` and `redis:6379`.

Run migrations (if needed):

```bash
docker compose exec backend alembic upgrade head
```

## API usage (curl)

### Create conversion job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -F "file=@/path/to/document.pdf" \
  -F "mode=fast"
```

Modes: `fast` | `accurate`

### Check status

```bash
curl "http://localhost:8000/api/v1/jobs/{job_id}"
```

### Download DOCX

```bash
curl -o output.docx "http://localhost:8000/api/v1/jobs/{job_id}/download"
```

### Health check

```bash
curl "http://localhost:8000/health"
```

## Environment variables

See [`infrastructure/.env.example`](infrastructure/.env.example).

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis for Celery |
| `STORAGE_BACKEND` | `local` or `oracle` |
| `LOCAL_STORAGE_PATH` | Path for local storage |
| `MAX_UPLOAD_MB` | Max upload size |
| `MAX_PDF_PAGES` | Max pages per PDF |
| `JOB_TTL_HOURS` | Job expiry time |

## Conversion pipeline

1. PDF type detection (digital / scanned / mixed)
2. Layout extraction (PyMuPDF, pdfplumber)
3. OCR (PaddleOCR, Tesseract fallback) for scanned PDFs
4. Structure reconstruction (headings, lists, paragraphs)
5. Table extraction (Camelot)
6. Image extraction
7. DOCX generation (python-docx)

## Docker troubleshooting (Ubuntu)

This project uses **Compose V2** (`docker compose`), same as a typical server.

If you see daemon/socket errors or apt conflicts between `docker-compose-v2` and `docker-compose-plugin`:

```bash
# Default: Ubuntu docker-compose-v2 package (matches many Ubuntu servers)
bash infrastructure/scripts/fix-docker.sh

# Or: Docker Compose plugin (matches Docker CE / get.docker.com installs)
COMPOSE_PROVIDER=plugin bash infrastructure/scripts/fix-docker.sh
```

Then open a **new terminal** and verify:

```bash
hash -r
docker context use default
docker info
docker compose version   # must show 2.x
docker compose up --build
```

Only one V2 provider can be installed at a time — not both `docker-compose-v2` and `docker-compose-plugin`.

**Build error `docker-credential-desktop: executable file not found`** — leftover Docker Desktop config. Fix:

```bash
# Remove Desktop credential helper
python3 -c "import json,pathlib; p=pathlib.Path.home()/'.docker/config.json'; c=json.loads(p.read_text()); c.pop('credsStore',None); c.pop('credHelpers',None); p.write_text(json.dumps(c,indent=2)+'\n')"
docker compose up --build
```

Or re-run `bash infrastructure/scripts/fix-docker.sh` (it applies this fix automatically).

**Port already in use** (e.g. `5432/tcp: address already in use`) — another Postgres/Redis is running on your machine. Compose maps DB to host port **5433** and Redis to **6380** to avoid that. Run `docker compose up` again.

## Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Project structure

```
apps/frontend/          # Next.js UI
backend/app/            # FastAPI + pipeline
infrastructure/         # Docker Compose, nginx
```
