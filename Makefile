.PHONY: all setup test lint format build dev-backend dev-frontend clean

all: test lint build

setup:
	@echo "Setting up backend..."
	cd backend && mise exec -- uv venv .venv --python 3.12 && . .venv/bin/activate && uv pip install -e ".[dev]"
	@echo "Setting up frontend..."
	cd frontend && npm install

test: test-backend test-frontend

test-backend:
	cd backend && .venv/bin/pytest tests/

test-frontend:
	cd frontend && npm run test

lint: lint-backend lint-frontend

lint-backend:
	cd backend && .venv/bin/ruff check .

lint-frontend:
	cd frontend && npm run lint

format:
	cd backend && .venv/bin/ruff format .

build:
	cd frontend && npm run build

dev:
	@echo "Starting backend and frontend concurrently..."
	@make -j 2 dev-backend dev-frontend

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

clean:
	rm -rf backend/.venv frontend/node_modules frontend/dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
