_default: just --list

dev-server: uv run granian api.main:app --interface asgi --reload --host 0.0.0.0

dev-server-uvicorn: uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
