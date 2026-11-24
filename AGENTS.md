# AGENTS.md — Amber Box Tracker (4-Track Multi-Agent Build)

> **STOP & READ THIS FIRST.** Every AI coding agent (Claude Code, Antigravity, Cursor, Copilot) and every human engineer MUST follow this routing file.

## 1. Your Track Assignment

The human operator will tell you your track at session start (e.g., `"You are Track 2"`). If they did not specify a track, **ask once** and wait. Never guess or edit files outside your track's ownership.

| Track | Role & Focus | Owner | State File |
| :--- | :--- | :--- | :--- |
| **Track 1** | **Platform, DB, Rules, Alerts & Devices** *(Integration Owner)* | Shivam + Agent 1 | [`docs/state/track-1.md`](docs/state/track-1.md) |
| **Track 2** | **Computer Vision, Labels & Video Harness** | Priyam (`@priyamraj201-art`) + Agent 2 | [`docs/state/track-2.md`](docs/state/track-2.md) |
| **Track 3** | **Dashboard UI, Mobile POV (`/m`) & ESP32 Firmware** | Yashwant + Agent 3 | [`docs/state/track-3.md`](docs/state/track-3.md) |
| **Track 4** | **Amber AI (Providers/Tools), E2E Tests & Demo Ops** | Abhishek + Agent 4 | [`docs/state/track-4.md`](docs/state/track-4.md) |

- **Integration Owner (Track 1)** is the only track allowed to edit `AGENTS.md`, `docs/prds/*`, `app/models.py`, `app/db.py`, `requirements.txt`, and merge PRs into `main`.
- Cross-track questions, contract changes, or blockers MUST be communicated via **GitHub Issue / PR Comments** (see §3).

---

## 2. Context-Efficient Load Order (Do NOT Load All Docs!)

Every PRD has a Table of Contents. Read only what your track needs:

1. **Always read**: `AGENTS.md` (this file) + `docs/prds/RULES_AND_ANTIPATTERNS.md`
2. **Read your state**: `docs/state/track-<N>.md`
3. **Read your Track section**: `docs/prds/TRACKS_AND_TASKS.md` (only your track's section)
4. **Read relevant PRD sections**:
   - **Track 1**: `PRD_01_PRODUCT_AND_DATA.md`, `PRD_02_API_RULES_AND_AMBER.md`
   - **Track 2**: `PRD_01_PRODUCT_AND_DATA.md` (§4–§5), `PRD_03_VISION_LABELS_HARNESS.md`
   - **Track 3**: `PRD_02_API_RULES_AND_AMBER.md` (API/WS/SSE contracts only), `PRD_04_UI_MOBILE_FIRMWARE.md`
   - **Track 4**: `PRD_02_API_RULES_AND_AMBER.md` (Amber section), `PRD_01_PRODUCT_AND_DATA.md` (Acceptance Criteria)

---

## 3. GitHub Comment Communication Protocol

Because 4 agents work in parallel on separate branches (`feat/track-1-*`, `feat/track-2-*`, `feat/track-3-*`, `feat/track-4-*`), **GitHub Comments are the single source of truth for cross-track coordination**.

### 3.1 When to Post a GitHub Comment (via `gh` CLI or GitHub UI)
1. **Contract / Schema Request**: Need a new field in `models.py` or a new endpoint in `routers/`? Comment on the active **Integration Tracking Issue** or PR using the structured tag `[CONTRACT-REQ]`.
2. **Handoff Ready**: Finished a module another track depends on (e.g., Track 2 finished `VisionPipeline` interface for Track 1's `worker.py`)? Post `[HANDOFF]` on the tracking issue with exact import path, signature, and commit SHA.
3. **Blocker / Dependency**: Waiting on another track? Post `[BLOCKED @track-X]` and switch to your next independent task or build against the mock/contract interface.
4. **Merge Point Sync**: Track 1 announces `[MERGE-POINT]` on GitHub when contracts/core land on `main`; all tracks `git pull origin main` (or rebase) before continuing.

### 3.2 Structured Comment Format
```markdown
**[TRACK-2 -> TRACK-1] [HANDOFF]**
- **Module**: `amber-box-tracker/app/vision/pipeline.py`
- **Interface**: `VisionPipeline.process_frame(frame, camera) -> FrameResult`
- **Verified**: Passes `scripts/run_on_video.py` on synthetic video 02 at 8.4 FPS CPU.
- **Action Needed**: Track 1 can now wire `VisionPipeline` into `app/vision/worker.py`.
```

---

## 4. Session Lifecycle Rules

1. **Branch**: Work ONLY on `feat/track-<N>-<short-topic>`. Never commit directly to `main`.
2. **State File**: Update `docs/state/track-<N>.md` before finishing every task (`STATUS`, `CURRENT_TASK`, `LAST_COMPLETED`, `BLOCKERS`, `NEXT_SYNC`).
3. **Verify Before Handing Off**: Run `pytest` and your track's acceptance check before opening a PR.
4. **No Unapproved Pushes**: Always verify locally; push only to your feature branch when ready for PR review (or per human operator instruction).
