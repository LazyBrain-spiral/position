# Track 2 State — Computer Vision, Labels & Offline Harness

- **Owner**: Priyam (`@priyamraj201-art`) + Agent 2
- **Branch**: `feat/track-2-vision-labels`
- **Status**: READY_TO_START
- **Current Task**: Wave 1 — Build `scripts/make_labels.py` + `tests/test_labels.py` and `app/vision/` core detectors
- **Last Completed**: PRD & multi-track governance setup
- **Blockers**: None (can build against `PRD_01` / `PRD_03` contracts; sync after `[MERGE-POINT-1]`)
- **Next Sync**: Post `[TRACK-2 -> TRACK-1] [HANDOFF]` on GitHub when `VisionPipeline` & `sources.py` pass synthetic videos at >= 5 FPS.

### Checklist
- [ ] `scripts/make_labels.py` (4×6 + A4 carton PDFs + ArUco marker PDF) + `tests/test_labels.py`
- [ ] `app/vision/detector.py` (YOLO-World `yolov8s-worldv2.pt` + ByteTrack + fallbacks)
- [ ] `app/vision/qr.py` (WeChat QR + 15% pad + 2× upscale + full-frame sweep)
- [ ] `app/vision/markers.py` (ArUco `DICT_4X4_50` + shelf association)
- [ ] `app/vision/privacy.py` (top 35% person head blur) & `annotate.py`
- [ ] `app/vision/pipeline.py` & `sources.py`
- [ ] `scripts/make_synthetic_video.py` & `scripts/run_on_video.py` (verify all 3 scenarios + FPS >= 5)
