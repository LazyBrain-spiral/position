# PRD-03: Computer Vision Pipeline, Labels & Video Harness

## Table of Contents
- §3.0 — Camera Sources & Worker Architecture (`config/cameras.yaml`, `sources.py`, `worker.py`)
- §3.1 — Exact 8-Step Vision Pipeline (`app/vision/pipeline.py`)
- §3.2 — Privacy & Annotation (`privacy.py`, `annotate.py`)
- §3.3 — PDF Labels & ArUco Shelf Markers (`scripts/make_labels.py`)
- §3.4 — Offline Video Harness & Synthetic Generator (`run_on_video.py`, `make_synthetic_video.py`)
- §3.5 — Setup & Weights Downloader (`scripts/setup.py`)

---

## §3.0 — Camera Sources & Worker Architecture

### `config/cameras.yaml`
Each camera defines: `id, name, kind, level, facility, source, loop, fps_process`.
Supported `source` formats:
- `file:videos/02_wrong_floor.mp4` — played at real-time FPS pacing, looped if `loop: true`.
- `rtsp://user:pass@ip/stream` — live RTSP stream.
- `webcam:0` — local USB/laptop webcam.
- `push` — frames pushed from `/m` over `WS /ws/pov`.

### Worker Thread Rules (`worker.py`)
- One dedicated thread per camera.
- **Drop-Oldest Frame Policy**: Always process the newest frame; drop stale frames rather than queuing.
- If a `file:` path does not exist yet, mark camera status `"no signal"` in the API/UI instead of crashing.
- Target CPU throughput: **>= 5 FPS per camera** across 3 active cameras.

### `config/settings.yaml` Defaults
```yaml
fps_process: 8
yolo_imgsz: 960
yolo_conf: 0.15
detector: yolo_world  # options: yolo_world | yoloe | none
rest_seconds: 3       # 3s for demo; 120s in production
not_arrived_minutes: 2 # 2m for demo; 240m in production
sighting_dedup_seconds: 10
track_bind_ttl: 10
```

---

## §3.1 — Exact 8-Step Vision Pipeline (`app/vision/pipeline.py`)

Per frame (at `fps_process`):
1. **Detect & Track (`detector.py`)**: Run `yolov8s-worldv2.pt` with `set_classes(["cardboard box", "person"])` and `model.track(..., persist=True, tracker="bytetrack.yaml", imgsz=960, conf=0.15)`. Fallback: `yoloe-11s-seg.pt` or `detector: none`.
2. **Box Track QR Binding (`qr.py`)**: For each `"cardboard box"` track:
   - a. If `track_id` is in the bound cache (TTL `track_bind_ttl = 10s` after track disappears), reuse `label_code` (*"read once, track forever"*).
   - b. Otherwise crop the box with **15% padding**. If short side `< 300 px`, upscale **2×** (`cv2.INTER_CUBIC`). Run `WeChatQRCode` on the crop. Accept **only** payloads matching `^KYC1:[A-Z0-9]{6}$`. Bind `track_id -> label_code`.
3. **Full-Frame QR Sweep**: Every **4th frame** (and **every frame** when `detector: none`), run `WeChatQRCode` on the full frame to catch missed boxes. Associate each decoded QR with the `"cardboard box"` bbox containing the QR centre; if none, create a pseudo-box from the QR polygon.
4. **ArUco Marker Detection (`markers.py`)**: Run `cv2.aruco.ArucoDetector(DICT_4X4_50)` on the full frame → list of `(marker_id, center_xy, side_px)`.
5. **Shelf Association (aisle cameras only)**: For each carton box, filter markers whose centre is within `3 × marker_side` vertically of the carton box's bottom edge, then pick the nearest marker horizontally. Map `marker_id -> Shelf`. If none qualifies, shelf is `None`.
6. **Motion State**: Carton is `"resting"` if its bbox centre moved `< 4%` of frame width over the last `rest_seconds` (3 s demo).
7. **Sighting Emission & Snapshot**: Emit a `Sighting` when first seen by a camera, when shelf changes, or every `10 s` while visible (dedup per `camera + carton`). Save privacy-blurred JPEG to `data/snapshots/`.
8. **Annotation & MJPEG Publish (`annotate.py`)**: Draw green outline (right place), red outline (wrong floor/shelf), or grey (unknown), label `"BV2401 -> L2-B2"`, ArUco IDs, and corner HUD (`camera.name`, `Floor N`, `FPS`). Publish to camera's MJPEG buffer.

---

## §3.2 — Privacy & Annotation (`privacy.py`, `annotate.py`)

- `privacy.py`: For every `"person"` bbox in a frame before saving to `data/snapshots/`, apply strong Gaussian blur to the **top 35%** of the bbox (head/face region).
- `annotate.py`: Clean high-contrast overlays readable on a projector.

---

## §3.3 — PDF Labels & ArUco Markers (`scripts/make_labels.py`)

- **Carton Labels (`4×6 in` / `101.6 × 152.4 mm`, 1/page + A4 2-up mode)**:
  - Top: QR code (`KYC1:<CODE>`, Error Correction **M**) at **90 mm × 90 mm**.
  - Below: Large bold `"FLOOR 2 · SHELF L2-B2"`, item name, `PO-line`, carton code, delivery ID.
- **Shelf Markers PDF**:
  - ArUco `DICT_4X4_50` markers at **100 mm** square with **20 mm** white quiet zone and shelf code (`L2-B2`) printed underneath.
- **Round-trip Test (`tests/test_labels.py`)**: Render PDF page to PNG (e.g., via `pymupdf` or `pdf2image` or reportlab/pillow verification) and assert `WeChatQRCode` decodes every carton QR and `ArucoDetector` decodes every shelf marker ID.

---

## §3.4 — Offline Harness & Synthetic Videos

- `scripts/make_synthetic_video.py`: Generates 3 realistic 1080p/720p test videos (moving box with real QR label image pasted on it, sliding past ArUco markers, with slight blur/noise/scale changes):
  1. `videos/01_gate_pov.mp4`: 5 of 6 `DEL-2211` cartons (omits `DM0402`).
  2. `videos/02_wrong_floor.mp4`: `BV2401` (dest Floor 2) + `CH0201` (dest Floor 3).
  3. `videos/03_shelf.mp4`: `DM0401` placed at ArUco marker `3` (`L2-B3`) for 5 s, then moved to marker `2` (`L2-B2`) for 5 s.
- `scripts/run_on_video.py --video <path> --camera <CAM-ID> [--reset] [--live-db]`:
  - Runs the exact `pipeline.py` + `rules.py` against a fresh copy of seed DB (unless `--live-db`).
  - Writes `output/<name>_annotated.mp4` and `output/<name>_events.jsonl`.
  - Prints summary: cartons read, read rate, FPS, alerts raised.

---

## §3.5 — Setup Script (`scripts/setup.py`)

1. Ensure `opencv-contrib-python-headless==4.10.0.84` (warn/fix if `opencv-python` conflicts).
2. Download `yolov8s-worldv2.pt` into `models/`.
3. Download WeChat QR 4 model files (`detect.prototxt`, `detect.caffemodel`, `sr.prototxt`, `sr.caffemodel`) from `WeChatCV/opencv_3rdparty` into `models/wechat/` (clear fallback message if offline).
4. Initialize `data/app.db` and load `data/seed.json`.
