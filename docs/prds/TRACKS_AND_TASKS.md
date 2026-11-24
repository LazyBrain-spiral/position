# 4-Track Parallel Execution Plan & Task Division — Amber Box Tracker

> **Golden Rule**: Each track owns distinct directories so all 4 agents + 4 engineers can code concurrently on separate branches (`feat/track-1-*` .. `feat/track-4-*`) with **zero merge conflicts**. Cross-track sync happens via **GitHub Issue / PR Comments** on the [Master Integration Tracking Issue (#1)](https://github.com/priyamraj201-art/position/issues/1) using `[HANDOFF]`, `[CONTRACT-REQ]`, `[BLOCKED @track-X]`, and `[MERGE-POINT]`.

---

## Track Ownership & File Boundaries

| Track | Owner | Branch Prefix | Exclusive File Ownership |
| :--- | :--- | :--- | :--- |
| **Track 1 — Platform, DB, Rules & Devices** *(Integration Owner)* | **Shivam** | `feat/track-1-*` | `amber-box-tracker/requirements.txt`, `.env.example`, `config/*`, `data/seed.json`, `scripts/setup.py`, `app/db.py`, `app/models.py`, `app/seed.py`, `app/rules.py`, `app/alerts.py`, `app/devices.py`, `app/main.py`, `app/routers/*`, `tests/test_rules.py`, `tests/test_devices.py` |
| **Track 2 — Computer Vision, Labels & Harness** | **Priyam** (`@priyamraj201-art`) | `feat/track-2-*` | `amber-box-tracker/app/vision/*` (`detector.py`, `qr.py`, `markers.py`, `pipeline.py`, `sources.py`, `privacy.py`, `annotate.py`), `scripts/make_labels.py`, `scripts/make_synthetic_video.py`, `scripts/run_on_video.py`, `tests/test_labels.py`, `tests/test_vision_pipeline.py` |
| **Track 3 — Dashboard UI, Mobile POV & Firmware** | **Yashwant** | `feat/track-3-*` | `amber-box-tracker/web/*` (`index.html`, `m.html`, `app.js`, `styles.css`), `amber-box-tracker/firmware/shelf-light/*` (`platformio.ini`, `include/config.h`, `src/main.cpp`, `sim.py`) |
| **Track 4 — Amber AI, Find/Mobile Logic & Demo Ops** | **Abhishek** | `feat/track-4-*` | `amber-box-tracker/app/amber/*` (`provider.py`, `gemini_provider.py`, `anthropic_provider.py`, `offline_provider.py`, `tools.py`), `tests/test_amber.py`, `tests/test_find.py`, `tests/test_e2e.py`, `amber-box-tracker/README.md` |

*(Note: `app/vision/worker.py` bridges Vision + FastAPI; Track 2 defines `VisionPipeline` & `sources.py` interfaces, Track 1 wires `worker.py` into `app/main.py`.)*

---

## Parallel Execution Waves & GitHub Sync Checkpoints

### Wave 1 — Foundation & Independent Building Blocks (Start Immediately in Parallel)
- **Track 1**: Scaffold `amber-box-tracker/`, `requirements.txt` (enforcing `opencv-contrib-python-headless==4.10.0.84`), `config/settings.yaml`, `config/cameras.yaml`, `data/seed.json`, `app/db.py`, `app/models.py`, `app/seed.py`, `scripts/setup.py`.
  - **GitHub Sync**: Open Tracking Issue `#1: [MERGE-POINT-1] Core DB, Models & Seed` and post `[HANDOFF]` once `models.py` + `seed.json` land on `main`.
- **Track 2**: Build `scripts/make_labels.py` (4×6 + A4 carton PDFs + ArUco marker PDFs) + `tests/test_labels.py` (WeChat QR + ArUco round-trip). Build `app/vision/detector.py`, `qr.py`, `markers.py`, `privacy.py`, `annotate.py`.
- **Track 3**: Build `web/styles.css`, `web/index.html` (5 tabs + Amber right panel + Virtual Shelf Grid), `web/m.html` (4 mobile POV modes), mocking API responses initially against `PRD_02` contracts. Build `firmware/shelf-light/` + `sim.py`.
- **Track 4**: Build `app/amber/provider.py`, `offline_provider.py` (regex intents), `gemini_provider.py`, `anthropic_provider.py`, `tools.py` (against `PRD_01` models) + `tests/test_amber.py`. Draft `amber-box-tracker/README.md` (Windows/macOS setup, licence note, glasses AUP note, recording guide, 3-min demo script).

### Wave 2 — Core Engines & Offline Verification
- **Track 1**: Implement `app/rules.py`, `app/alerts.py` (dedup + SSE), `app/devices.py` (long-poll command queue), and all FastAPI routers (`app/routers/*.py`) + `tests/test_rules.py` (including fake-clock `not_arrived`) + `tests/test_devices.py`.
- **Track 2**: Implement `app/vision/pipeline.py`, `sources.py`, `scripts/make_synthetic_video.py`, and `scripts/run_on_video.py`. Verify all 3 synthetic videos (`01_gate_pov`, `02_wrong_floor`, `03_shelf`) hit **>= 5 FPS CPU** and emit expected events.
  - **GitHub Sync**: Post `[TRACK-2 -> TRACK-1] [HANDOFF]` with `VisionPipeline` & `sources.py` signatures.
- **Track 3**: Wire `web/app.js` and `web/m.html` to live endpoints (`/api/cameras/{id}/mjpeg`, `/api/alerts/stream`, `/ws/pov`, `/api/mobile/pov-upload`, `/api/find`, `/api/amber/chat`). Test `sim.py` against Track 1's `/api/devices/{id}/commands`.
- **Track 4**: Write `tests/test_find.py` (fuzzy difflib >= 0.6) and `tests/test_e2e.py` covering all Acceptance Criteria in `PRD_01 §1.5`.

### Wave 3 — Integration, Synthetic & Real Video Acceptance
- **Track 1** merges Track 2/3/4 PRs into `main` after verifying `[MERGE-POINT-2]`.
- **All Tracks**: Run full acceptance suite:
  1. `python scripts/setup.py`
  2. `pytest` (all green)
  3. `python scripts/run_on_video.py` on all 3 synthetic videos
  4. `uvicorn app.main:app --host 0.0.0.0 --port 8000` (plus HTTPS test for `/m`)
  5. Verify >= 5 FPS per camera with 3 cameras on CPU.
