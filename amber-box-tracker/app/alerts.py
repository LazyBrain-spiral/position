"""Alert creation, dedup, resolution and SSE broadcast (PRD-02 section 2.1).

Dedup rule: at most one OPEN alert per (carton_id, type). Every new or
resolved alert is published to the broadcaster for the SSE stream.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Optional

from sqlmodel import Session, select

from app.models import Alert, Carton, Shelf

ALERT_TYPES = {"wrong_floor", "wrong_shelf", "not_arrived", "short_delivery", "damaged"}


class AlertBroadcaster:
    """Fan-out of alert events to SSE subscribers (asyncio queues)."""

    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def publish(self, payload: dict[str, Any]) -> None:
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass  # slow consumer drops events, never blocks the app


broadcaster = AlertBroadcaster()


def alert_payload(alert: Alert, shelf_light_events: Optional[list[dict]] = None) -> dict:
    return {
        "id": alert.id,
        "type": alert.type,
        "message": alert.message,
        "carton_id": alert.carton_id,
        "snapshot_path": alert.snapshot_path,
        "created_at": alert.created_at.isoformat(),
        "shelf_light_events": shelf_light_events or [],
    }


def open_alert_for(session: Session, carton_id: int, alert_type: str) -> Optional[Alert]:
    return session.exec(
        select(Alert).where(
            Alert.carton_id == carton_id,
            Alert.type == alert_type,
            Alert.status == "open",
        )
    ).first()


def create_alert(
    session: Session,
    alert_type: str,
    message: str,
    carton_id: Optional[int] = None,
    delivery_id: Optional[str] = None,
    camera_id: Optional[str] = None,
    snapshot_path: Optional[str] = None,
    shelf_light_events: Optional[list[dict]] = None,
    publish: bool = True,
) -> tuple[Alert, bool]:
    """Create an alert with dedup. Returns (alert, created)."""
    if alert_type not in ALERT_TYPES:
        raise ValueError(f"unknown alert type: {alert_type}")
    if carton_id is not None:
        existing = open_alert_for(session, carton_id, alert_type)
        if existing is not None:
            return existing, False
    alert = Alert(
        type=alert_type,
        message=message,
        carton_id=carton_id,
        delivery_id=delivery_id,
        camera_id=camera_id,
        snapshot_path=snapshot_path,
    )
    session.add(alert)
    session.commit()
    session.refresh(alert)
    if publish:
        broadcaster.publish(alert_payload(alert, shelf_light_events))
    return alert, True


def resolve_alert(
    session: Session,
    alert_id: int,
    note: str,
    new_dest_shelf_id: Optional[int] = None,
    publish: bool = True,
) -> Optional[Alert]:
    """Resolve an alert; optionally repoint the carton's destination shelf."""
    alert = session.get(Alert, alert_id)
    if alert is None:
        return None
    alert.status = "resolved"
    alert.resolved_note = note
    if new_dest_shelf_id is not None and alert.carton_id is not None:
        carton = session.get(Carton, alert.carton_id)
        shelf = session.get(Shelf, new_dest_shelf_id)
        if carton is not None and shelf is not None:
            carton.dest_shelf_id = shelf.id
            carton.dest_level = shelf.level
            carton.dest_facility_id = shelf.facility_id
            session.add(carton)
    session.add(alert)
    session.commit()
    session.refresh(alert)
    if publish:
        payload = alert_payload(alert)
        payload["status"] = "resolved"
        payload["resolved_note"] = note
        broadcaster.publish(payload)
    return alert


def auto_resolve_for_carton(
    session: Session,
    carton_id: int,
    types: tuple[str, ...] = ("wrong_floor", "wrong_shelf"),
    note: str = "auto-resolved",
) -> int:
    """Resolve open alerts of the given types for a carton. Returns count."""
    count = 0
    for alert_type in types:
        alert = open_alert_for(session, carton_id, alert_type)
        if alert is not None:
            resolve_alert(session, alert.id, note)
            count += 1
    return count


def list_alerts(
    session: Session,
    alert_type: Optional[str] = None,
    status: Optional[str] = None,
) -> list[Alert]:
    query = select(Alert).order_by(Alert.created_at.desc())
    if alert_type:
        query = query.where(Alert.type == alert_type)
    if status:
        query = query.where(Alert.status == status)
    return list(session.exec(query).all())
