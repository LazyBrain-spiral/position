# Track 3 State — Dashboard UI, Mobile POV (/m) & ESP32 Firmware

- **Owner**: Yashwant + Agent 3
- **Branch**: `feat/track-3-ui-mobile-firmware`
- **Status**: READY_TO_START
- **Current Task**: Wave 1 — Build `web/` (5-tab dark dashboard + Virtual Shelf Grid + Amber panel) & `web/m.html` + `firmware/shelf-light/`
- **Last Completed**: PRD & multi-track governance setup
- **Blockers**: None (UI mocks against `PRD_02` API contracts until Track 1 routers merge)
- **Next Sync**: Post `[TRACK-3] [READY]` on GitHub once UI & `sim.py` are wired to live endpoints.

### Checklist
- [ ] `web/styles.css` (dark projector-ready theme + Virtual Shelf Grid pulse animations)
- [ ] `web/index.html` + `web/app.js` (Live MJPEG, Alerts SSE + toast + speech, Cartons timeline, Receive, Find + Virtual Grid, Amber panel)
- [ ] `web/m.html` (HTTPS `getUserMedia` + `WS /ws/pov` 4 fps, POV video upload, Damage report, Hold-to-talk Amber voice)
- [ ] `firmware/shelf-light/` (`platformio.ini`, `include/config.h`, `src/main.cpp` for ESP32-C3 + WS2812B + buzzer)
- [ ] `firmware/shelf-light/sim.py` (terminal shelf-light simulator)
