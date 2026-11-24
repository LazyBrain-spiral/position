# PRD-01: Product Overview, Architecture & Data Model — Amber Box Tracker

## Table of Contents
- §1.0 — Product Context & Core Parts
- §1.1 — Tech Stack & Licence Notes
- §1.2 — Target Folder Structure (`amber-box-tracker/`)
- §1.3 — Canonical Data Model (SQLModel / SQLite)
- §1.4 — QR Payload & Seed Data (`data/seed.json`)
- §1.5 — Master Acceptance Criteria

---

## §1.0 — Product Context & Core Parts

**Amber Box Tracker** joins what job-site cameras see with what Kaya's AI assistant **Amber** already knows (deliveries, PO lines, storage facilities). It runs on a normal laptop (**CPU only, no GPU required**) and works with 2–3 recorded videos plus a live webcam/phone.

### Three Core Capabilities
1. **CCTV Box Tracking**: Fixed cameras (simulated by video files / webcam / RTSP) read QR labels on cartons. Each camera knows its floor (`level`) and role (`kind`). Amber alerts on:
   - **WRONG FLOOR**: carton seen on floor $L$ where `carton.dest_level != L`.
   - **WRONG SHELF**: carton resting next to ArUco shelf marker $S$ where `S != carton.dest_shelf`.
   - **NOT ARRIVED**: carton received at gate but not seen on `dest_level` within $N$ minutes.
2. **Meta Glasses / Phone POV (`/m`)**:
   - **Where does this go?**: Live camera scan → reads QR → displays & speaks floor + shelf.
   - **Proof of delivery**: Record/upload a POV clip at the gate → reads all carton QRs → compares count against expected delivery → flags `short_delivery` + `DeliveryIssue` if short.
   - **Defect proof**: Capture frame + note → creates `DeliveryIssue.damaged_items` + `damaged` Alert.
   - **Ask Amber (voice)**: Web Speech API → `/api/amber/chat` → spoken reply.
3. **Find + Shelf Lights**:
   - Natural-language/fuzzy search ("where is box X / AHU-3 dampers?").
   - Physical LED strip on that shelf blinks (**ESP32-C3 + WS2812B**) + Virtual Shelf Grid in dashboard blinks as fallback.

---

## §1.1 — Tech Stack & Licence Notes

- **Backend**: Python 3.11, FastAPI, Uvicorn, SQLModel on SQLite (`data/app.db`), Pydantic v2.
- **Computer Vision**:
  - `ultralytics>=8.3` with **YOLO-World `yolov8s-worldv2.pt`** (`model.set_classes(["cardboard box", "person"])`, `model.track(..., persist=True, tracker="bytetrack.yaml", imgsz=960, conf=0.15)`).
  - Fallback detector: `yoloe-11s-seg.pt` (same text prompts) → last resort `detector: none` (full-frame QR only).
  - **QR Decoding**: `opencv-contrib-python-headless==4.10.0.84` → `cv2.wechat_qrcode_WeChatQRCode(detect.prototxt, detect.caffemodel, sr.prototxt, sr.caffemodel)` (downloaded from `WeChatCV/opencv_3rdparty/tree/wechat_qrcode` into `models/wechat/`). Fallback: no-arg `WeChatQRCode()` → `cv2.QRCodeDetectorAruco()`.
  - **Shelf Markers**: ArUco `cv2.aruco.DICT_4X4_50` via `cv2.aruco.ArucoDetector`. Marker ID $N$ = Shelf $N$.
- **Labels**: `qrcode[pil]` + `reportlab` → 4×6 in (101.6 × 152.4 mm) and A4 (2-up) PDFs.
- **Frontend**: Plain HTML + vanilla JS + one CSS file served by FastAPI from `web/` (no build step). MJPEG live streams, SSE alerts, Web Speech API voice.
- **Amber AI**: `AmberProvider` interface with `GeminiProvider` (`google-genai`, `GEMINI_API_KEY`), `AnthropicProvider` (`anthropic`, `ANTHROPIC_API_KEY`), and automatic `OfflineAmberProvider` (regex intents, zero network dependency).
- **Firmware**: PlatformIO (Arduino) for `esp32-c3-devkitm-1`, `adafruit/Adafruit NeoPixel`, `bblanchon/ArduinoJson@^7`, plus Python simulator `sim.py`.
- **Licence Note (for README)**: Ultralytics YOLO models are **AGPL-3.0** (acceptable for hackathon prototype). Kaya's production stack uses **RF-DETR (Apache-2.0)** for permissive commercial licensing.

---

## §1.2 — Target Folder Structure (`amber-box-tracker/`)

```text
amber-box-tracker/
  README.md
  requirements.txt
  .env.example
  config/
    cameras.yaml
    settings.yaml
  data/
    seed.json
  models/                  # YOLO + WeChat weights (via scripts/setup.py)
  scripts/
    setup.py               # Downloads weights, creates DB, loads seed
    make_labels.py         # Carton label PDF + shelf marker PDF
    make_synthetic_video.py# Synthetic 3-scenario test videos
    run_on_video.py        # Offline harness: video -> annotated mp4 + events.jsonl
  app/
    main.py
    db.py
    models.py
    seed.py
    rules.py
    alerts.py
    devices.py
    vision/
      detector.py
      qr.py
      markers.py
      pipeline.py
      sources.py
      worker.py
      privacy.py
      annotate.py
    amber/
      provider.py
      gemini_provider.py
      anthropic_provider.py
      offline_provider.py
      tools.py
    routers/
      cartons.py
      deliveries.py
      find.py
      alerts.py
      cameras.py
      mobile.py
      devices.py
      amber.py
      labels.py
  web/
    index.html
    m.html
    app.js
    styles.css
  firmware/shelf-light/
    platformio.ini
    include/config.h
    src/main.cpp
    sim.py
  videos/
  output/
  tests/
```

---

## §1.3 — Canonical Data Model (SQLModel / SQLite)

Data shapes mirror Kaya's production tables (`delivery_details`, `purchase_order`, `storage_facility`, `delivery_issues`) for easy porting:

| Table | Key Fields |
| :--- | :--- |
| `Project` | `id`, `name` |
| `StorageFacility` | `id`, `project_id`, `name`, `level` (e.g., `"Floor 2 Store"`, `2`) |
| `Shelf` | `id`, `facility_id`, `level`, `code` (`"L2-B2"`), `marker_id`, `light_device_id` (nullable) |
| `PurchaseOrder` | `id`, `po_number`, `supplier`, `lines` (JSON: `[{line, part_number, description, qty}]`) |
| `Delivery` | `id`, `event_name`, `po_ids` (JSON), `gate`, `storage_facility_id`, `date`, `status`, `proof_video_path` (nullable) |
| `Carton` | `id`, `label_code` (UNIQUE), `delivery_id`, `po_number`, `po_line`, `part_number`, `item_name`, `qty_in_carton`, `dest_facility_id`, `dest_level`, `dest_shelf_id`, `status` (`received\|in_transit\|stored\|misplaced\|issued`), `received_at`, `last_seen_at`, `last_seen_level`, `last_seen_shelf_id`, `last_seen_camera_id`, `last_snapshot` |
| `Camera` | `id`, `name`, `kind` (`gate\|hoist\|floor_entrance\|aisle\|pov`), `level` (nullable), `facility_id` (nullable), `source`, `enabled` |
| `Sighting` | `id`, `carton_id`, `camera_id`, `source` (`cctv\|phone\|glasses`), `level`, `shelf_id`, `seen_at`, `snapshot_path`, `bbox` (JSON), `track_id` |
| `Alert` | `id`, `type` (`wrong_floor\|wrong_shelf\|not_arrived\|short_delivery\|damaged`), `carton_id` (nullable), `delivery_id` (nullable), `camera_id` (nullable), `message`, `snapshot_path`, `status` (`open\|resolved`), `created_at`, `resolved_note` |
| `DeliveryIssue` | `id`, `delivery_id`, `missing_items` (JSON), `wrong_items` (JSON), `damaged_items` (JSON), `evidence` (JSON), `created_at` |
| `ShelfLight` | `id`, `device_id`, `shelf_id`, `last_seen`, `battery`, `rssi` |

---

## §1.4 — QR Payload & Seed Data (`data/seed.json`)

- **QR Payload Format**: `KYC1:<6-char code>` (uppercase base32/alphanumeric matching `^KYC1:[A-Z0-9]{6}$`, Error Correction Level **M**). Keep payload short so CCTV reads low-version QR codes from 1.5–3 m away. Destination never lives in the QR.
- **Project**: `"Harbor Point Medical Office (sample)"`
- **Facilities**: `"Gate / Laydown"` (level 0), `"Floor 2 Store"` (level 2), `"Floor 3 Store"` (level 3)
- **Shelves**:
  - `L2-B1` (marker 1)
  - `L2-B2` (marker 2, `light_device_id="shelf-light-01"`)
  - `L2-B3` (marker 3, `light_device_id="shelf-light-02"`)
  - `L3-A1` (marker 11)
  - `L3-A2` (marker 12)
- **POs**:
  - `PO-1077` (Ferguson): `BV-200-SS` 2in ball valve ×24; `BF-300-LUG` 3in butterfly valve ×12; `YS-250` Y strainer ×6; `AHU3-DMP` AHU-3 damper kit ×4.
  - `PO-1042` (Trane): `CVHF-0500` chiller parts kit CH-2 ×2.
- **Deliveries & Pre-Created Cartons**:
  - `DEL-2211` (`PO-1077`, today, expected 6 cartons, Floor 2 Store):
    - `KYC1:BV2401` → `L2-B2` (2in ball valve)
    - `KYC1:BV2402` → `L2-B2` (2in ball valve)
    - `KYC1:BF1201` → `L2-B1` (3in butterfly valve)
    - `KYC1:YS0601` → `L2-B1` (Y strainer)
    - `KYC1:DM0401` → `L2-B2` (`"AHU-3 damper kit"`)
    - `KYC1:DM0402` → `L2-B3` (`"AHU-3 damper kit"`)
  - `DEL-2190` (`PO-1042`, Floor 3 Store):
    - `KYC1:CH0201` → `L3-A1`
    - `KYC1:CH0202` → `L3-A1`
- **Cameras (`config/cameras.yaml`)**: `CAM-GATE` (`gate`, level 0), `CAM-HOIST-3` (`hoist`, level 3), `CAM-AISLE-2` (`aisle`, level 2, Floor 2 Store), `CAM-POV` (`pov`).

---

## §1.5 — Master Acceptance Criteria

1. `python scripts/setup.py` then `uvicorn app.main:app --host 0.0.0.0 --port 8000` starts cleanly on CPU.
2. `pytest` passes (rules, labels round-trip, offline Amber intents, find, device queue).
3. Synthetic videos via `run_on_video.py`: `01` → `short_delivery` listing missing `DM0402`; `02` → exactly 1 `wrong_floor` (`BV2401`); `03` → `wrong_shelf` then auto-resolved + `stored`.
4. Dashboard Live shows annotated MJPEG tiles; alerts appear as toasts within 2 s of video event.
5. Find `"AHU-3 dampers"` returns carton + shelf; `"Light it up"` blinks virtual grid + simulator prints `BLINK` for `shelf-light-01`.
6. `/m` over HTTPS on phone reads printed label and speaks destination.
7. Amber offline provider answers `"where is BV2401"` and `"status of DEL-2211"` accurately.
8. CPU throughput >= **5 FPS per camera** across 3 simultaneous cameras.
