# Engineering Rules & Vibe-Coding Anti-Patterns — Amber Box Tracker

> **Purpose**: Keep 4 parallel AI agents shipping fast, clean, CPU-friendly code without breaking OpenCV, duplicating logic, or colliding on git.

## 1. Hard Technical Guardrails (Non-Negotiable)

### 1.1 OpenCV Dependency Rule (CRITICAL)
- **MUST** use `opencv-contrib-python-headless==4.10.0.84` (needed for `cv2.wechat_qrcode_WeChatQRCode` and `cv2.aruco.ArucoDetector`).
- **NEVER** install `opencv-python` alongside `opencv-contrib-python-headless`.
- If `ultralytics` pulls in `opencv-python`, immediately run:
  ```bash
  pip uninstall -y opencv-python opencv-python-headless
  pip install --force-reinstall opencv-contrib-python-headless==4.10.0.84
  ```

### 1.2 CPU-Only & Latency Budget
- Target hardware: **normal laptop, CPU only, no GPU required**.
- Minimum throughput: **>= 5 FPS per camera** with 3 simultaneous cameras.
- Camera workers (`app/vision/worker.py`) **MUST** keep only the newest frame (`maxlen=1` or overwrite slot). **Drop old frames, NEVER build a queue.**
- If CPU FPS drops below 5 FPS, use `imgsz=640` for non-aisle cameras and `fps_process: 5` in `config/settings.yaml`.

### 1.3 Privacy & Security
- **Head Blur**: `app/vision/privacy.py` MUST blur the top 35% of every `"person"` bounding box in all saved snapshots (`data/snapshots/`).
- **No Hard-Coded Secrets**: Read `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, Wi-Fi credentials, etc., from `.env` (provide `.env.example`).
- **Glasses AUP Note**: In production, QR decoding of Meta glasses frames happens on-device; document this in `README.md`.

### 1.4 Offline Resilience (Demo Insurance)
- Every external dependency MUST have a working offline fallback:
  - **WeChat QR weights download fails** -> Construct `cv2.wechat_qrcode_WeChatQRCode()` with no args; fallback to `cv2.QRCodeDetectorAruco()`.
  - **YOLO-World detects boxes poorly** -> Try `yoloe-11s-seg.pt`; last resort `detector: none` (full-frame QR only).
  - **No LLM API key** -> `AmberProvider` automatically selects `OfflineAmberProvider` (regex intents).
  - **No ESP32 hardware** -> `firmware/shelf-light/sim.py` + Dashboard Virtual Shelf Grid blink identically.
  - **Missing video file** -> Camera worker marks camera `"no signal"` in UI instead of crashing.

---

## 2. Code Quality & Vibe-Coding Anti-Patterns

| Anti-Pattern (DO NOT DO) | Pro Vibe-Coder Standard (DO THIS) |
| :--- | :--- |
| One-file 900-line monoliths | Keep each module focused (< 250 lines where practical), single-responsibility, type hints everywhere. |
| Editing another track's files "just to be helpful" | Respect track boundaries. If you need a change in another track's file, post a `[CONTRACT-REQ]` GitHub comment. |
| Mocking everything in tests & skipping real video runs | Write unit tests with `pytest` AND run `scripts/run_on_video.py` on synthetic/real videos to verify end-to-end alerts. |
| Putting destination floor/shelf inside the QR code | QR payload is **ONLY** `KYC1:<6-char code>` (error correction M). Destination lives in SQLite (`Carton`). |
| Storing camera frames in memory queues | Single-slot latest-frame buffer per camera thread; drop stale frames immediately. |
| Inventing locations in Amber LLM responses | Amber MUST always use tool outputs; never hallucinate floors or shelves. |
| Blocking `uvicorn` event loop with YOLO inference | Run camera inference in dedicated worker threads; push annotated JPEGs & events safely. |
| Adding Node/React build steps to `web/` | `web/` is plain HTML + vanilla JS + 1 CSS file served directly by FastAPI. Zero build step. |
| Coding blind without checking GitHub comments | Always run `gh issue view 1 --comments --repo priyamraj201-art/position` at session start and adapt your code to any `[HANDOFF]`, `[CONTRACT-REQ]`, or `[MERGE-POINT]` comments. |

---

## 3. Definition of Done (DoD) per PR

Before opening a PR to `main`:
1. All unit/integration tests in `tests/` pass (`pytest`).
2. Type hints and clean imports (no unused imports, plain-language logging).
3. Your track's state file (`docs/state/track-<N>.md`) is updated.
4. PR description includes the `[TRACK-N]` tag, test output, and any `[HANDOFF]` notes for other tracks.
