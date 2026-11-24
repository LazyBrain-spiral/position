# PRD-04: Dashboard UI, Mobile POV (`/m`) & ESP32 Shelf-Light Firmware

## Table of Contents
- §4.0 — Web Dashboard (`web/index.html`, `app.js`, `styles.css`)
- §4.1 — Mobile / Meta Glasses POV Page (`web/m.html`)
- §4.2 — ESP32-C3 Shelf Light Firmware & Python Simulator (`firmware/shelf-light/`)
- §4.3 — HTTPS Local Certs & Recording Guide Requirements

---

## §4.0 — Web Dashboard (`web/`)

- **Zero Build Step**: Plain HTML + vanilla JS + one CSS file (`styles.css`), served directly by FastAPI.
- **Visual Style**: Dark, clean, high-contrast, large readable typography (projector-ready), green/amber/red status badges.
- **Global Right-Side Panel**: Persistent **Amber** chat panel on every tab:
  - Text input + Send button.
  - Hold/click Mic button (`SpeechRecognition` Web Speech API).
  - Speak Replies toggle (`speechSynthesis`).
  - Confirmation prompt support when Amber asks to confirm damage reporting.

### 5 Dashboard Tabs
1. **Live**:
   - Grid of camera tiles (`<img src="/api/cameras/{id}/mjpeg">`) showing camera name, floor level, FPS, and `live` / `no signal` badge.
   - Real-time SSE listener (`/api/alerts/stream`) sliding in **toast notifications** at top-right with alert snapshot thumbnail + optional spoken alert via `speechSynthesis`.
2. **Alerts**:
   - Live SSE-updated list of alerts, filterable by `type` (`wrong_floor`, `wrong_shelf`, `not_arrived`, `short_delivery`, `damaged`) and `status`.
   - `"Resolve"` action with note input.
   - `"Destination was wrong -> set new destination"` quick-fix action.
3. **Cartons**:
   - Searchable table: `label_code`, `item_name`, `po_number`, `destination (Floor + Shelf)`, `status`, `last_seen`.
   - Clicking any row opens a **Sighting Timeline** drawer/modal with ordered snapshot thumbnails (`gate -> hoist -> floor -> shelf`).
4. **Receive**:
   - Select delivery (`DEL-2211`, `DEL-2190`) → view expected cartons.
   - `"Print Labels"` button (opens `/api/labels/cartons.pdf?delivery_id=...`).
   - `"Mark Received"` button (`POST /api/deliveries/{id}/receive`).
5. **Find**:
   - Search input + Mic button (`GET /api/find?q=`).
   - Result cards showing destination, current status, last-seen camera/level/shelf/time-ago, snapshot thumbnail, and `"Light it up"` button (`POST /api/cartons/{code}/locate`).
   - **Virtual Shelf Grid** (`Floor 2: L2-B1, L2-B2, L2-B3` | `Floor 3: L3-A1, L3-A2`):
     - Target shelf pulses **blue** on locate / wrong-shelf target.
     - Wrong shelf pulses **red** on `wrong_shelf` alert.
     - Confirmed put-away flashes **green** (`ack`).

---

## §4.1 — Mobile / Meta Glasses POV Page (`web/m.html`)

- Designed for Chrome on Android over LAN IP via HTTPS (`--ssl-keyfile` / `--ssl-certfile` so `getUserMedia` works in a secure context).
- **4 Modes**:
  1. **Where does this go?**: Opens rear camera (`facingMode: "environment"`), sends JPEG frames at **4 fps** over `WS /ws/pov`. On decoded carton, displays huge high-contrast card (`"BV2401 · 2in ball valve · FLOOR 2 · SHELF L2-B2"`) and speaks it via `speechSynthesis`.
  2. **Receive Delivery (Proof of Delivery)**:
     - Pick delivery (`DEL-2211`).
     - Either live-scan OR **upload POV `.mp4` clip** (from Meta Ray-Ban glasses / phone) to `POST /api/mobile/pov-upload/{delivery_id}`.
     - Displays summary: `Expected: 6 | Seen: 5 | Missing: DM0402`.
     - Buttons: `"Confirm receipt"` or `"Confirm with exceptions"`.
  3. **Report Damage**: Captures current video frame (or file upload), selects visible/manual carton code, adds damage note → `POST /api/mobile/damage`.
  4. **Ask Amber (Voice)**: Hold-to-talk button (`SpeechRecognition`) → `POST /api/amber/chat` → speaks reply.

---

## §4.2 — ESP32-C3 Shelf Light Firmware & Simulator (`firmware/shelf-light/`)

### PlatformIO Project (`env: esp32-c3-devkitm-1`)
- Libraries: `adafruit/Adafruit NeoPixel`, `bblanchon/ArduinoJson@^7`.
- `include/config.h`: `WIFI_SSID`, `WIFI_PASS`, `SERVER` (e.g. `http://192.168.1.50:8000`), `DEVICE_ID` (`shelf-light-01`), `LED_PIN 4`, `LED_COUNT 12`, `BUZZER_PIN 5`.
- **Behavior**:
  - Connects to Wi-Fi with retry; onboard LED indicates Wi-Fi state.
  - FreeRTOS task long-polls `GET /api/devices/{DEVICE_ID}/commands?wait=20` (`HTTPClient`, 25 s timeout) and parses JSON commands.
  - `loop()` renders non-blocking LED animations + passive buzzer chirp every 3 s while blinking:
    - `blink` (color blue): 250 ms on/off for `seconds`.
    - `blink_red`: fast red blink.
    - `ack`: solid green for 2 s.
    - `off`: clear strip.
- **Wiring Table (for README)**:
  - `ESP32-C3 GPIO4` → `330 Ω` resistor → `WS2812B DIN`
  - `5V / GND` to LED strip with `1000 µF` capacitor across `5V` & `GND`
  - `ESP32-C3 GPIO5` → passive buzzer (`+`), common `GND`

### Python Simulator (`firmware/shelf-light/sim.py`)
- CLI script: `python firmware/shelf-light/sim.py --device shelf-light-01 --server http://localhost:8000`
- Long-polls the exact same endpoint and prints colored terminal flashes (`[BLINK BLUE 30s]`, `[BLINK RED 20s]`, `[ACK GREEN 2s]`) so the demo works reliably without physical hardware.
