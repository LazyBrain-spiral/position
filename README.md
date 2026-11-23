# Enterprise Platform Monorepo

> Production-grade, modular monorepo architecture engineered for a high-velocity 4-SDE team.

[![CI Pipeline](https://github.com/priyamraj201-art/position/actions/workflows/ci.yml/badge.svg)](https://github.com/priyamraj201-art/position/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Node.js 24 LTS](https://img.shields.io/badge/node-24%20LTS-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/frontend-React%2019-61dafb.svg)](https://react.dev/)
[![uv](https://img.shields.io/badge/package%20manager-uv-blueviolet.svg)](https://github.com/astral-sh/uv)

---

## 🏛 Architecture Overview

```
├── .github/                  # CI/CD Workflows, CODEOWNERS, PR & Issue Templates
│   ├── workflows/ci.yml      # Automated lint, typecheck, test, and build matrix
│   ├── CODEOWNERS            # 4-track ownership mapping
│   └── PULL_REQUEST_TEMPLATE.md
├── apps/
│   ├── api/                  # High-performance FastAPI modular service
│   │   ├── src/api/          # Routers, endpoints, dependencies, services
│   │   ├── tests/            # Integration & endpoint test suites
│   │   └── pyproject.toml
│   └── web/                  # Modern React 19 + TypeScript + Vite frontend
│       ├── src/              # UI components, state, API client
│       ├── tsconfig.json
│       └── package.json
├── packages/
│   ├── contracts/            # Single source of truth for DTOs and API contracts
│   │   └── src/contracts/    # Canonical Pydantic & TS schemas
│   └── common/               # Shared cross-cutting modules
│       └── src/common/       # Structured logging, config, domain exceptions
├── infra/
│   ├── docker/               # Multi-stage production Dockerfiles (API & Web)
│   └── docker-compose.yml    # Local dev orchestration (API, Web, Postgres, Redis)
├── docs/
│   ├── team/                 # Team protocols, track ownership, branching rules
│   │   ├── TRACKS.md         # Detailed 4-SDE responsibilities and contracts
│   │   └── COLLABORATION.md  # Git hygiene and PR review guidelines
│   └── state/                # Individual track state files (prevents collisions)
│       ├── track-1.md        # Platform & Infra (SDE 1)
│       ├── track-2.md        # Backend Core (SDE 2)
│       ├── track-3.md        # Frontend Web (SDE 3)
│       └── track-4.md        # Quality & Systems (SDE 4)
├── .editorconfig             # Cross-IDE code consistency
├── .pre-commit-config.yaml   # Pre-commit quality gates (Ruff, formatting, hooks)
├── Makefile                  # Developer workflow automation (1-command commands)
├── package.json              # Monorepo workspace orchestration
└── pyproject.toml            # Python UV workspace configuration
```

---

## 👥 4-Track Ownership Matrix

| Track | SDE Role | Responsibilities | State File |
| :--- | :--- | :--- | :--- |
| **Track 1** | **Platform & Infra** | Docker, CI/CD, DB migrations, deployment, observability | [`docs/state/track-1.md`](file:///d:/code/kayareal/docs/state/track-1.md) |
| **Track 2** | **Backend Core** | FastAPI endpoints, services, domain algorithms, DB logic | [`docs/state/track-2.md`](file:///d:/code/kayareal/docs/state/track-2.md) |
| **Track 3** | **Frontend Web** | React 19 UI, component design, client API integration | [`docs/state/track-3.md`](file:///d:/code/kayareal/docs/state/track-3.md) |
| **Track 4** | **Quality & Contracts**| Shared schemas, integration tests, contract freeze | [`docs/state/track-4.md`](file:///d:/code/kayareal/docs/state/track-4.md) |

---

## 🚀 Quickstart (One Command Setup)

### Prerequisites:
- Python 3.11+ & [`uv`](https://docs.astral.sh/uv/)
- Node.js 24 LTS & `npm`
- [Docker](https://www.docker.com/) (optional, for full containerized stack)

```bash
# 1. Clone the repository
git clone https://github.com/priyamraj201-art/position.git
cd position

# 2. Boot dependencies
make setup

# 3. Initialize environment
cp .env.example .env

# 4. Start concurrent development server
make dev
```

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Swagger Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Specification**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🛡 Quality Gates & CI

Run local verification before creating a Pull Request:

```bash
make ci
```
This executes:
1. `uv run ruff check .` (Python linting)
2. `uv run pyright` (Python static type checking)
3. `npm run --workspace=@repo/web typecheck` (TypeScript static analysis)
4. `uv run pytest` (Backend & contracts test suite)
