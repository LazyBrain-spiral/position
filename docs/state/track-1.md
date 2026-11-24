# Track 1 State — Platform, DB, Rules, Alerts & Devices (Integration Owner)

- **Owner**: Shivam + Agent 1
- **Branch**: `feat/track-1-core-platform`
- **Status**: READY_TO_START
- **Current Task**: Wave 1 — Scaffold `amber-box-tracker/`, `requirements.txt`, `config/`, `data/seed.json`, `app/models.py`, `app/db.py`, `scripts/setup.py`
- **Last Completed**: PRD & multi-track governance setup
- **Blockers**: None
- **Next Sync**: Post `[MERGE-POINT-1]` on GitHub Tracking Issue once `models.py` + `seed.json` are merged to `main`.

### Checklist
- [ ] `amber-box-tracker/requirements.txt` (with `opencv-contrib-python-headless==4.10.0.84` guard) + `.env.example`
- [ ] `config/settings.yaml` & `config/cameras.yaml`
- [ ] `data/seed.json` & `app/models.py` & `app/db.py` & `app/seed.py`
- [ ] `scripts/setup.py`
- [ ] `app/rules.py` & `app/alerts.py` + `tests/test_rules.py`
- [ ] `app/devices.py` + `tests/test_devices.py`
- [ ] `app/main.py` & `app/routers/*` & `app/vision/worker.py` wiring
