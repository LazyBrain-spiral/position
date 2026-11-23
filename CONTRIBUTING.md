# Contributing Guidelines

Welcome to the team! We follow top-tier SDE standards to ship fast without breaking things.

## Quickstart

1. **Clone the repository**:
   ```bash
   git clone https://github.com/priyamraj201-art/position.git
   cd position
   ```

2. **Run setup**:
   ```bash
   make setup
   # Or manually:
   npm install
   uv sync
   ```

3. **Copy environment variables**:
   ```bash
   cp .env.example .env
   ```

4. **Start local development**:
   ```bash
   make dev
   ```
   - API runs on: `http://localhost:8000` (Docs: `http://localhost:8000/docs`)
   - Web Client runs on: `http://localhost:3000`

5. **Run tests & quality checks before pushing**:
   ```bash
   make ci
   ```

## Development Commands

| Command | Action |
| :--- | :--- |
| `make dev` | Run backend and frontend concurrently |
| `make test` | Run pytest backend and vitest frontend test suites |
| `make lint` | Run Ruff and ESLint across the codebase |
| `make format` | Automatically format all Python, TS, and JSON files |
| `make typecheck` | Run Pyright and TypeScript type checking |
| `make ci` | Run the complete CI verification pipeline locally |
| `make docker-up` | Boot full platform in Docker containers |
| `make docker-down` | Stop and tear down local containers |
