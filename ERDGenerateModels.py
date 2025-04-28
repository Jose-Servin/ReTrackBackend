from graphviz import Digraph
import os

dot = Digraph(comment="ReTrackLogistics ERD", format="png")

# Define entity shapes
entities = {
    "Carrier": ["id", "name", "mc_number", "created_at", "updated_at"],
    "CarrierContact": [
        "id",
        "carrier_id → Carrier",
        "first_name",
        "last_name",
        "email",
        "phone",
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
        "origin_id → Location",
        "destination_id → Location",
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
        "timestamp",
        "source",
        "notes",
    ],
}

# Create nodes
for entity, fields in entities.items():
    label = f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0'>"
    label += f"<TR><TD BGCOLOR='lightblue'><B>{entity}</B></TD></TR>"
    for field in fields:
        label += f"<TR><TD ALIGN='LEFT'>{field}</TD></TR>"
    label += "</TABLE>>"
    dot.node(entity, label=label, shape="plain")

# Define relationships
edges = [
    ("CarrierContact", "Carrier"),
    ("Driver", "Carrier"),
    ("Vehicle", "Carrier"),
    ("Shipment", "Carrier"),
    ("Shipment", "Driver"),
    ("Shipment", "Vehicle"),
    ("ShipmentStatusEvent", "Shipment"),
    ("Shipment", "Location"),  # For both origin and destination
]

# Add edges
for source, target in edges:
    dot.edge(source, target)

# Save or render
# dot.render("retrack_erd", view=True)

# Render diagram
os.makedirs("diagrams", exist_ok=True)
erd_image_path = "diagrams/Current_retrack_ERD"
dot.render(erd_image_path, format="png", cleanup=True)

erd_image_path
