# PRD-02: Backend API, Rules Engine, Alerts, Devices & Amber AI

## Table of Contents
- §2.0 — FastAPI Lifecycle & Routers
- §2.1 — Rules Engine & Background Tasks (`app/rules.py`, `app/alerts.py`)
- §2.2 — REST, MJPEG, SSE & WebSocket Contracts
- §2.3 — Shelf Light Device Channel (`app/devices.py`)
- §2.4 — Amber AI Provider & Tools (`app/amber/`)

---

## §2.0 — FastAPI Lifecycle & Routers

- **Entrypoint**: `amber-box-tracker/app/main.py`
- **Startup**:
  1. Initialize SQLite DB (`data/app.db`) & ensure seed is loaded if empty.
  2. Load `config/settings.yaml` and `config/cameras.yaml`.
  3. Start one `CameraWorker` thread per enabled camera (`file`, `rtsp`, `webcam`, `push`).
  4. Start background asyncio task for `not_arrived` check (runs every **30 s**).
- **Static Serving**: Mount `web/` so `/` serves `index.html`, `/m` serves `m.html`, and `/snapshots/` serves `data/snapshots/` JPEGs.

---

## §2.1 — Rules Engine & Alert Deduplication (`app/rules.py`, `app/alerts.py`)

### Sighting Evaluation Rules
1. **`wrong_floor`**:
   - Trigger: `camera.kind in {"hoist", "floor_entrance", "aisle"}` AND `camera.level is not None` AND `camera.level != carton.dest_level`.
   - Action: Create alert `"Box {code} ({item_name}, {po_number}) is on Floor {camera.level} — it belongs on Floor {dest_level}, shelf {dest_shelf_code}."` Set `carton.status = "misplaced"`.
2. **`wrong_shelf`**:
   - Trigger: `camera.kind == "aisle"` AND `is_resting == True` AND `current_shelf_id is not None` AND `current_shelf_id != carton.dest_shelf_id`.
   - Action: Create alert `"Box {code} is on {current_shelf_code} — it should be on {dest_shelf_code}."`
   - Device Commands: Queue `blink_red` (20 s) to `current_shelf.light_device_id` and `blink` (20 s, blue) to `dest_shelf.light_device_id`.
3. **`confirmed put-away`**:
   - Trigger: `camera.kind == "aisle"` AND `is_resting == True` AND `current_shelf_id == carton.dest_shelf_id`.
   - Action: Set `carton.status = "stored"`. Auto-resolve any open `wrong_floor` or `wrong_shelf` alerts for that carton with `resolved_note = "auto-resolved"`. Queue `ack` (green 2 s) to `dest_shelf.light_device_id`.
4. **`not_arrived`** (Background task every 30 s):
   - Trigger: `carton.status == "received"` AND no sighting on `dest_level` within `not_arrived_minutes` (default `2` for demo, `240` in prod; injectable fake clock for `pytest`).
   - Action: Create `not_arrived` alert.

### Deduplication & SSE Broadcast
- **Dedup**: At most **one `open` alert** per `(carton_id, type)`.
- **SSE**: Every new alert broadcasts immediately over `GET /api/alerts/stream` with JSON payload `{id, type, message, carton_id, snapshot_path, created_at, shelf_light_events}`.

---

## §2.2 — API Contracts

| Router | Endpoint | Purpose |
| :--- | :--- | :--- |
| `cameras.py` | `GET /api/cameras` | List cameras, status (`live\|no_signal`), fps |
| `cameras.py` | `GET /api/cameras/{id}/mjpeg` | `multipart/x-mixed-replace` annotated stream |
| `alerts.py` | `GET /api/alerts` | List alerts (filter by `type`, `status`) |
| `alerts.py` | `GET /api/alerts/stream` | SSE stream of new/resolved alerts |
| `alerts.py` | `POST /api/alerts/{id}/resolve` | Resolve alert with `note` (and optional `new_dest_shelf_id`) |
| `cartons.py` | `GET /api/cartons` | List cartons + current status/location |
| `cartons.py` | `GET /api/cartons/{code}/timeline` | Ordered `Sighting` history + snapshot thumbnails |
| `cartons.py` | `POST /api/cartons/{code}/locate` | Queue `blink` (30s, blue) on current/dest shelf light + return shelf grid target |
| `deliveries.py` | `GET /api/deliveries` | List deliveries & expected cartons |
| `deliveries.py` | `POST /api/deliveries/{id}/receive` | Mark cartons `received` (`received_at = now`) |
| `deliveries.py` | `POST /api/deliveries/{id}/confirm` | Confirm receipt or confirm with exceptions |
| `find.py` | `GET /api/find?q=` | Case-insensitive + fuzzy (`difflib.SequenceMatcher >= 0.6`) search across `label_code`, `part_number`, `item_name`, `po_number` |
| `mobile.py` | `WS /ws/pov` | Receive JPEG frames at 4 fps → `CAM-POV` pipeline → return decoded carton + destination |
| `mobile.py` | `POST /api/mobile/pov-upload/{delivery_id}` | Upload `.mp4` POV clip → run video pipeline → store `data/proof/{id}_{ts}.mp4` → compare seen vs expected → create `short_delivery` Alert + `DeliveryIssue` if short |
| `mobile.py` | `POST /api/mobile/damage` | Multipart image + `carton_code` + `note` → create `DeliveryIssue.damaged_items` + `damaged` Alert |
| `labels.py` | `GET /api/labels/cartons.pdf` | Generate 4×6 or A4 carton label PDF (optional `?delivery_id=`) |
| `labels.py` | `GET /api/labels/shelves.pdf` | Generate ArUco shelf marker PDF |
| `amber.py` | `POST /api/amber/chat` | `{message, confirm?}` → `{reply, tool_calls, needs_confirmation?}` |

---

## §2.3 — Shelf Light Device Channel (`app/devices.py`, `routers/devices.py`)

- `GET /api/devices/{device_id}/commands?wait=20&battery=..&rssi=..`:
  - Updates `ShelfLight` (`last_seen`, `battery`, `rssi`).
  - Long-polls up to `min(wait, 25)` seconds on an `asyncio.Event` queue.
  - Returns `{"commands": [{"cmd": "blink"|"blink_red"|"ack"|"off", "color": "blue"|"red"|"green", "seconds": 30}]}`.
- `POST /api/devices/{device_id}/heartbeat`: Updates telemetry.
- Also exposes virtual shelf grid state via `GET /api/devices/grid-state` or SSE so the dashboard virtual grid pulses in sync with physical ESP32s.

---

## §2.4 — Amber AI Provider & Tools (`app/amber/`)

### System Prompt
> *"You are Amber, Kaya's site assistant. Answer in 1–2 short spoken sentences. Always use tools; never invent locations. Floors are 'Floor N', shelves are codes like L2-B2."*

### Tool Functions (`app/amber/tools.py`)
1. `find_carton(query: str, auto_locate: bool = False)` → returns matching cartons; if `auto_locate=True` (user said "show/light/blink"), also calls locate.
2. `where_does_this_go(carton_code: str)` → returns destination floor & shelf.
3. `delivery_status(delivery_id: str)` → returns expected count, seen/received count, missing codes.
4. `report_damage(carton_code: str, note: str, confirm: bool = False)` → if `not confirm`, returns `{"needs_confirmation": True, "prompt": "Confirm marking ... as damaged?"}`. When `confirm=True`, creates `DeliveryIssue` + `damaged` Alert.
5. `list_open_alerts()` → returns open alerts summary.

### Providers (`app/amber/provider.py`)
- `GeminiProvider` (`google-genai`, `GEMINI_API_KEY`)
- `AnthropicProvider` (`anthropic`, `ANTHROPIC_API_KEY`)
- `OfflineAmberProvider` (auto-selected when no API key is set): regex intent router handling:
  - `"where is <x>"` / `"find <x>"`
  - `"light up <x>"` / `"blink <x>"` / `"show <x>"`
  - `"where does <code> go"`
  - `"status of <delivery>"`
  - `"<code> is damaged"`
  - `"open alerts"`
