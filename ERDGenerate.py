from graphviz import Digraph
import os

dot = Digraph(comment="ReTrackLogistics ERD", format="png")
dot.attr(rankdir="TB")  # Top to Bottom layout

# Define entities with fields
entities = {
    "Organization": [
        "id: int",
        "name: str",
        "industry: str",
        "settings: json",
        "created_at: datetime",
    ],
    "User": [
        "id: int",
        "username: str",
        "role: str",
        "organization_id: FK → Organization.id",
    ],
    "Carrier": [
        "id: int",
        "name: str",
        "mc_number: str",
        "organization_id: FK → Organization.id",
    ],
    "Driver": [
        "id: int",
        "name: str",
        "phone: str",
        "email: str",
        "carrier_id: FK → Carrier.id",
    ],
    "Vehicle": [
        "id: int",
        "plate_number: str",
        "vehicle_type: str",
        "carrier_id: FK → Carrier.id",
    ],
    "Location": [
        "id: int",
        "name: str",
        "address: str",
        "latitude: float",
        "longitude: float",
        "organization_id: FK → Organization.id",
    ],
    "Shipment": [
        "id: int",
        "shipment_id: str",
        "origin_id: FK → Location.id",
        "destination_id: FK → Location.id",
        "driver_id: FK → Driver.id",
        "vehicle_id: FK → Vehicle.id",
        "carrier_id: FK → Carrier.id",
        "scheduled_pickup: datetime",
        "scheduled_delivery: datetime",
        "actual_pickup: datetime",
        "actual_delivery: datetime",
        "status: str",
    ],
    "GPSPing": [
        "id: int",
        "driver_id: FK → Driver.id",
        "vehicle_id: FK → Vehicle.id",
        "shipment_id: FK → Shipment.id",
        "timestamp: datetime",
        "latitude: float",
        "longitude: float",
        "speed: float",
        "heading: float",
    ],
    "TrackingEvent": [
        "id: int",
        "shipment_id: FK → Shipment.id",
        "event_type: str",
        "timestamp: datetime",
        "location_id: FK → Location.id",
        "description: str",
        "created_by_id: FK → User.id",
    ],
    "ETAEstimate": [
        "id: int",
        "shipment_id: FK → Shipment.id",
        "calculated_at: datetime",
        "eta: datetime",
        "confidence_score: float",
    ],
}

# Add nodes
for entity, fields in entities.items():
    label = "{{{}|{}}}".format(entity, "\\l".join(fields) + "\\l")
    dot.node(entity, label, shape="record")

# Relationships with direction pointing FROM Organization downward
relationships = [
    ("Organization", "User"),
    ("Organization", "Carrier"),
    ("Organization", "Location"),
    ("Carrier", "Driver"),
    ("Carrier", "Vehicle"),
    ("Carrier", "Shipment"),
    ("Driver", "Shipment"),
    ("Vehicle", "Shipment"),
    ("Location", "Shipment"),  # Both origin and destination
    ("Driver", "GPSPing"),
    ("Vehicle", "GPSPing"),
    ("Shipment", "GPSPing"),
    ("Shipment", "TrackingEvent"),
    ("Location", "TrackingEvent"),
    ("User", "TrackingEvent"),
    ("Shipment", "ETAEstimate"),
]

# Draw edges
for src, tgt in relationships:
    dot.edge(src, tgt)

# Force Organization at the top by giving it the "min" rank
dot.body.append("{ rank=min; Organization; }")

# Render diagram
os.makedirs("diagrams", exist_ok=True)
erd_image_path = "diagrams/retrack_ERD"
dot.render(erd_image_path, format="png", cleanup=True)

erd_image_path
