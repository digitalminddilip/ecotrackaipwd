# EcoTrack AI — PageKite Deployment

## Recommended setup

Expose the FastAPI application directly through PageKite. The FastAPI app serves
both the API and the frontend, so you do not need a separate `python -m http.server`
on port 5500 for the PageKite deployment.

### 1. Start FastAPI

From the project root:

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

If your installed environment does not have `uvicorn` on PATH:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. Test locally

Open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/health

The health endpoint should return an OK response.

### 3. Start PageKite

Point PageKite to local port 8000:

```powershell
pagekite.py 8000 ecotrackaipwd.pagekite.me
```

Use your PageKite account/authentication options as required by your installation.

### Why this fixes HTTP 405

Previously, the PageKite hostname could be serving the frontend server while
browser API requests were sent to the same public origin. Those requests then
did not reach the FastAPI routes.

This version recognizes `*.pagekite.me` and uses same-origin API URLs, while
FastAPI serves the frontend and API from the same process/port.

## Local development

You can still run the frontend separately on port 5500 if desired. In that
case, the browser will use:

```text
http://localhost:8000
```

for API requests.

## Important

Do not commit API keys or other secrets to the ZIP/repository. Use environment
variables for production credentials.
