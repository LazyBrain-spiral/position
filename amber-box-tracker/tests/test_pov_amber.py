"""Shared-state parity: POV upload sightings, deliveries API, Amber and /mcp agree.

After POST /api/mobile/pov-upload writes sightings, Amber's delivery_status (over /mcp and via
chat) must report the same seen and missing cartons as the upload response.

Limits: the clip is synthetic QR frames. In an environment where the WeChat QR decoder is not
available (for example a mixed opencv-python / opencv-contrib install) the pipeline uses its
ArUco-detector fallback, and this test passes on that path. It makes no claim about WeChat
decoding, real footage, YOLO or hardware.
"""
from __future__ import annotations

import json

import pytest
from app import devices
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    import app.db as db_module

    db_module._engine = None
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "pov.db")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    devices.reset()
    with TestClient(create_app()) as test_client:
        yield test_client
    devices.reset()


def _clip(path, codes):
    cv2 = pytest.importorskip("cv2")
    np = pytest.importorskip("numpy")
    qrcode = pytest.importorskip("qrcode")
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 10.0, (480, 480))
    if not writer.isOpened():
        pytest.skip("cv2 VideoWriter unavailable")
    for code in codes:
        qr = qrcode.make(f"KYC1:{code}").convert("RGB").resize((480, 480))
        frame = cv2.cvtColor(np.array(qr), cv2.COLOR_RGB2BGR)
        for _ in range(10):
            writer.write(frame)
    writer.release()


def _mcp(client, name, args):
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": args}}
    result = client.post("/mcp", json=body).json()["result"]
    return json.loads(result["content"][0]["text"])


def test_amber_sees_what_pov_upload_recorded(client, tmp_path):
    clip = tmp_path / "proof.mp4"
    _clip(clip, ["BV2401", "BV2402"])
    with open(clip, "rb") as fh:
        up = client.post("/api/mobile/pov-upload/DEL-2211",
                         files={"file": ("proof.mp4", fh, "video/mp4")}).json()
    assert sorted(up["answer"]["seen"]) == ["BV2401", "BV2402"]
    assert up["needs_human_review"] is True  # 4 cartons still missing

    env = _mcp(client, "delivery_status", {"delivery_id": "DEL-2211"})
    answer = env["answer"]
    assert answer["seen"] == 2
    assert "KYC1:BV2401" not in answer["missing_codes"]
    assert len(answer["missing_codes"]) == 4

    reply = client.post("/api/amber/chat", json={"message": "status of DEL-2211"}).json()
    assert "2 of 6" in reply["reply"]

    found = _mcp(client, "find_carton", {"query": "BV2401"})
    assert found["answer"]["matches"][0]["label_code"] == "KYC1:BV2401"
    alerts = _mcp(client, "list_open_alerts", {})
    assert alerts["answer"]["count"] >= 1
