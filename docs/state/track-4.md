# Track 4 State — Amber AI, Fuzzy Find, E2E Tests & Demo Docs

- **Owner**: Abhishek + Agent 4
- **Branch**: `feat/track-4-amber-qa-docs`
- **Status**: READY_TO_START
- **Current Task**: Wave 1 — Build `app/amber/` (`AmberProvider`, Gemini, Anthropic, Offline regex provider, tools) + `tests/test_amber.py`
- **Last Completed**: PRD & multi-track governance setup
- **Blockers**: None (uses `PRD_01` / `PRD_02` contracts; will run full E2E suite after Wave 2 merge)
- **Next Sync**: Post `[TRACK-4 -> TRACK-1] [HANDOFF]` on GitHub when `app/amber/` + `tests/test_amber.py` are green.

### Checklist
- [ ] `app/amber/provider.py` + `tools.py` (`find_carton`, `where_does_this_go`, `delivery_status`, `report_damage`, `list_open_alerts`)
- [ ] `app/amber/offline_provider.py` (regex intents, zero network dependency)
- [ ] `app/amber/gemini_provider.py` & `anthropic_provider.py`
- [ ] `tests/test_amber.py` & `tests/test_find.py` & `tests/test_e2e.py`
- [ ] `amber-box-tracker/README.md` (Windows/macOS setup, HTTPS cert guide, recording guide, 3-min demo script, AGPL/RF-DETR & Meta AUP notes, troubleshooting, deviations)
