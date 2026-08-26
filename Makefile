.PHONY: help install dev backend frontend test lint build docker-up docker-down clean

help:
	@echo "Startup Canvas — make targets"
	@echo "  make install      install backend + frontend deps"
	@echo "  make dev          start postgres + backend + frontend via docker compose"
	@echo "  make backend      run backend locally (http://localhost:8000)"
	@echo "  make frontend     run frontend locally (http://localhost:5173)"
	@echo "  make test         run all tests (backend + frontend)"
	@echo "  make lint         run linters"
	@echo "  make build        build frontend for production"
	@echo "  make docker-up    docker compose up --build"
	@echo "  make docker-down  docker compose down -v"
	@echo "  make clean        remove caches and build artifacts"

install:
	cd backend && pip install -r requirements.txt -r requirements-dev.txt
	cd frontend && npm install

dev:
	docker compose up --build

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest -q
	cd frontend && npm run test -- --run

lint:
	cd backend && ruff check app
	cd frontend && npm run lint

build:
	cd frontend && npm run build

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v

clean:
	rm -rf backend/.pytest_cache backend/.ruff_cache backend/__pycache__
	rm -rf frontend/node_modules frontend/dist frontend/.vite
	rm -rf .puku
