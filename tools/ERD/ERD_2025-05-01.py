"""
ERD generated on 2025-05-01

This diagram corresponds to the initial seed data defined in `seed_shipments_v1.sql`.
It represents the simplified version of the data model we're starting with and is
intended for early development and learning purposes. This is not the final schema —
models and relationships will evolve over time.
"""

from graphviz import Digraph
import os

dot = Digraph(comment="ReTrackLogistics ERD", format="png")
dot.attr(rankdir="RL")
dot.attr(size="12,6")
dot.attr(dpi="200")

entities = {
    "Carrier": [
        "id",
        "name",
        "mc_number",
        "created_at",
        "updated_at",
    ],
    "CarrierContact": [
        "id",
        "carrier_id → Carrier",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "role",
        "is_primary",
        "created_at",
        "updated_at",
    ],
    "Driver": [
        "id",
        "carrier_id → Carrier",
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "created_at",
        "updated_at",
    ],
    "Vehicle": [
        "id",
        "carrier_id → Carrier",
        "plate_number",
        "device_id",
        "created_at",
        "updated_at",
    ],
    "Shipment": [
        "id",
        "origin",
        "destination",
        "scheduled_pickup",
        "scheduled_delivery",
        "actual_pickup",
        "actual_delivery",
        "current_status",
        "carrier_id → Carrier",
        "driver_id → Driver",
        "vehicle_id → Vehicle",
        "created_at",
        "updated_at",
    ],
    "ShipmentStatusEvent": [
        "id",
        "shipment_id → Shipment",
        "status",
        "event_timestamp",
        "source",
        "notes",
        "created_at",
        "updated_at",
    ],
}

for entity, fields in entities.items():
    label = f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>"
    label += f"<TR><TD BGCOLOR='lightblue'><B>{entity}</B></TD></TR>"
    for field in fields:
        label += f"<TR><TD ALIGN='LEFT'>{field}</TD></TR>"
    label += "</TABLE>>"
    dot.node(entity, label=label, shape="plain")

edges = [
    ("CarrierContact", "Carrier"),
    ("Driver", "Carrier"),
    ("Vehicle", "Carrier"),
    ("Shipment", "Carrier"),
    ("Shipment", "Driver"),
    ("Shipment", "Vehicle"),
    ("ShipmentStatusEvent", "Shipment"),
]

for source, target in edges:
    dot.edge(source, target)

erd_path = "ERD_2025-05-01"
dot.render(erd_path, format="png", cleanup=True)

print(f"ERD generated at {erd_path}.png")
