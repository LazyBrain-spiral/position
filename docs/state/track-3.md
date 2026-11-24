# Track 3 State — Dashboard UI, Mobile POV (/m) & ESP32 Firmware

- **Owner**: Yashwant + Agent 3
- **Branch**: `feat/track-3-ui-mobile-firmware`
- **Status**: WAVE_1_COMPLETE
- **Current Task**: Completed Wave 1 deliverables (5-tab web dashboard, Amber assistant panel, Virtual Shelf Grid, mobile `/m.html`, ESP32 firmware & simulator). Ready for Wave 2 backend endpoint integration.
- **Last Completed**: Built `web/styles.css`, `web/index.html`, `web/app.js`, `web/m.html`, `firmware/shelf-light/` (`platformio.ini`, `include/config.h`, `src/main.cpp`), and `firmware/shelf-light/sim.py` (verified via `--demo`).
- **Blockers**: None (UI supports built-in fallback/mock data conforming to `PRD_01` / `PRD_02` contracts and seamlessly consumes live `/api` endpoints and SSE streams).
- **Next Sync**: Ready for Track 1 & Track 2 integration (`[TRACK-3] [READY]`).

### Checklist
- [x] `web/styles.css` (dark projector-ready theme + Virtual Shelf Grid pulse animations)
- [x] `web/index.html` + `web/app.js` (Live MJPEG, Alerts SSE + toast + speech, Cartons timeline, Receive, Find + Virtual Grid, Amber panel)
- [x] `web/m.html` (HTTPS `getUserMedia` + `WS /ws/pov` 4 fps, POV video upload, Damage report, Hold-to-talk Amber voice)
- [x] `firmware/shelf-light/` (`platformio.ini`, `include/config.h`, `src/main.cpp` for ESP32-C3 + WS2812B + buzzer)
- [x] `firmware/shelf-light/sim.py` (terminal shelf-light simulator)
