"""Canonical data model for Amber Box Tracker (PRD-01 section 1.3).

SQLModel tables mirror Kaya's production shapes (delivery_details,
purchase_order, storage_facility, delivery_issues) for easy porting.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import NaiveDatetime
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

# All timestamps are naive UTC by convention: annotate with pydantic's
# NaiveDatetime so sqlmodel >= 0.0.49 maps them to naive DateTime columns
# (its default datetime mapping enforces timezone-aware values, which
# SQLite round-trips inconsistently).


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class StorageFacility(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    name: str
    level: int


class Shelf(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    facility_id: int = Field(foreign_key="storagefacility.id")
    level: int
    code: str = Field(unique=True, index=True)
    marker_id: int = Field(unique=True)
    light_device_id: Optional[str] = None


class PurchaseOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    po_number: str = Field(unique=True, index=True)
    supplier: str
    lines: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))


class Delivery(SQLModel, table=True):
    id: str = Field(primary_key=True)  # e.g. "DEL-2211"
    event_name: str
    po_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    gate: str
    storage_facility_id: int = Field(foreign_key="storagefacility.id")
    date: str
    status: str = "expected"  # expected | receiving | received | confirmed
    proof_video_path: Optional[str] = None


class Carton(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    label_code: str = Field(unique=True, index=True)  # 6-char code from KYC1:<code>
    delivery_id: str = Field(foreign_key="delivery.id")
    po_number: str
    po_line: int
    part_number: str
    item_name: str
    qty_in_carton: int
    dest_facility_id: int = Field(foreign_key="storagefacility.id")
    dest_level: int
    dest_shelf_id: int = Field(foreign_key="shelf.id")
    status: str = "received"  # received | in_transit | stored | misplaced | issued
    received_at: Optional[NaiveDatetime] = None
    last_seen_at: Optional[NaiveDatetime] = None
    last_seen_level: Optional[int] = None
    last_seen_shelf_id: Optional[int] = Field(default=None, foreign_key="shelf.id")
    last_seen_camera_id: Optional[str] = Field(default=None, foreign_key="camera.id")
    last_snapshot: Optional[str] = None


class Camera(SQLModel, table=True):
    id: str = Field(primary_key=True)  # e.g. "CAM-GATE"
    name: str
    kind: str  # gate | hoist | floor_entrance | aisle | pov
    level: Optional[int] = None
    facility_id: Optional[int] = Field(default=None, foreign_key="storagefacility.id")
    source: str = "file"
    enabled: bool = True


class Sighting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    carton_id: int = Field(foreign_key="carton.id")
    camera_id: str = Field(foreign_key="camera.id")
    source: str = "cctv"  # cctv | phone | glasses
    level: Optional[int] = None
    shelf_id: Optional[int] = Field(default=None, foreign_key="shelf.id")
    seen_at: NaiveDatetime = Field(default_factory=datetime.utcnow)
    snapshot_path: Optional[str] = None
    bbox: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    track_id: Optional[int] = None


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str  # wrong_floor | wrong_shelf | not_arrived | short_delivery | damaged
    carton_id: Optional[int] = Field(default=None, foreign_key="carton.id")
    delivery_id: Optional[str] = Field(default=None, foreign_key="delivery.id")
    camera_id: Optional[str] = Field(default=None, foreign_key="camera.id")
    message: str
    snapshot_path: Optional[str] = None
    status: str = "open"  # open | resolved
    created_at: NaiveDatetime = Field(default_factory=datetime.utcnow)
    resolved_note: Optional[str] = None


class DeliveryIssue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_id: str = Field(foreign_key="delivery.id")
    missing_items: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    wrong_items: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    damaged_items: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    evidence: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: NaiveDatetime = Field(default_factory=datetime.utcnow)


class ShelfLight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str = Field(unique=True, index=True)  # e.g. "shelf-light-01"
    shelf_id: int = Field(foreign_key="shelf.id")
    last_seen: Optional[NaiveDatetime] = None
    battery: Optional[float] = None
    rssi: Optional[int] = None
