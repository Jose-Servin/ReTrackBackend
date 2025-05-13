
select * from public.shipments_shipment;

CREATE TABLE public.shipments_shipment_backup AS
SELECT * FROM public.shipments_shipment;

select * from public.shipments_shipment_backup


select * from public.shipments_shipmentstatusevent;

CREATE TABLE public.shipments_shipmentstatusevent_backup AS
SELECT * FROM public.shipments_shipmentstatusevent;

select * from public.shipments_shipmentstatusevent_backup;

TRUNCATE TABLE shipments_shipmentstatusevent, shipments_shipment RESTART IDENTITY;


select * from public.shipments_shipment;

select * from public.shipments_shipment_backup

-- Carrier 2: Shipment 1 (Pending) — Within capacity (2 max, 0 currently active)
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'Houston', 'Midland', NOW() + INTERVAL '2 days', 
    NOW() + INTERVAL '4 days', 
    NULL, 
    NULL, 
    'pending', 2, 4, 6, NOW(), NOW()
);

-- Carrier 4: Shipment 1 (Pending) — Within capacity (1 max, 0 currently active)
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'Dallas', 'Fort Worth', NOW() + INTERVAL '1 days', 
    NOW() + INTERVAL '3 days', 
    NULL, 
    NULL, 
    'pending', 4, 3, 8, NOW(), NOW()
);

-- Carrier 2: Shipment 2 (Delivered) — Does not count against capacity
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'Austin', 'San Antonio', NOW() + INTERVAL '-1 days', 
    NOW() + INTERVAL '0 days', 
    NOW() + INTERVAL '-1 days', 
    NOW() + INTERVAL '0 days', 
    'delivered', 2, 4, 3, NOW(), NOW()
);

-- Carrier 4: Shipment 2 (Cancelled) — Does not count against capacity
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'Lubbock', 'Odessa', NOW() + INTERVAL '0 days', 
    NOW() + INTERVAL '1 days', 
    NULL, 
    NULL, 
    'cancelled', 4, 2, 4, NOW(), NOW()
);

select * from public.shipments_shipment;

-- Carrier 1: Shipment 1 (Pending) — Within capacity (1 of 2 slots in use)
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'El Paso', 'Houston', NOW() + INTERVAL '2 days', 
    NOW() + INTERVAL '4 days', 
    NULL, 
    NULL, 
    'pending', 1, 1, 6, NOW(), NOW()
);

-- Carrier 1: Shipment 2 (Delayed) — Active, counts toward capacity (2 of 2 now in use)
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'Wichita Falls', 'Temple', NOW() + INTERVAL '-3 days', 
    NOW() + INTERVAL '0 days', 
    NOW() + INTERVAL '-3 days', 
    NULL, 
    'delayed', 1, 1, 1, NOW(), NOW()
);

select * from public.shipments_shipment;

-- Carrier 2: Shipment 3 (Delivered) — Does not count against capacity
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'Beaumont', 'Longview', NOW() + INTERVAL '-2 days', 
    NOW() + INTERVAL '0 days', 
    NOW() + INTERVAL '-2 days', 
    NOW() + INTERVAL '0 days', 
    'delivered', 2, 4, 7, NOW(), NOW()
);

-- Carrier 4: Shipment 3 (Delivered) — Does not count against capacity
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'Bryan', 'Galveston', NOW() + INTERVAL '-1 days', 
    NOW() + INTERVAL '0 days', 
    NOW() + INTERVAL '-1 days', 
    NOW() + INTERVAL '0 days', 
    'delivered', 4, 6, 4, NOW(), NOW()
);

-- Carrier 3: Shipment 1 (In Transit) — Occupies capacity (1 of 1 in use)
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'McAllen', 'Laredo', NOW() + INTERVAL '-1 days', 
    NOW() + INTERVAL '1 days', 
    NOW() + INTERVAL '-1 days', 
    NULL, 
    'in_transit', 3, 5, 8, NOW(), NOW()
);

-- Carrier 3: Shipment 2 (Delivered) — Does not count against capacity
INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
) VALUES (
    'Plano', 'Irving', NOW() + INTERVAL '-2 days', 
    NOW() + INTERVAL '0 days', 
    NOW() + INTERVAL '-2 days', 
    NOW() + INTERVAL '0 days', 
    'delivered', 3, 1, 7, NOW(), NOW()
);

select * from public.shipments_shipment where ID = 10;
-- "2025-05-11 07:26:34.588368-05"
-- "2025-05-13 07:26:34.588368-05"

select * from public.shipments_shipmentstatusevent where shipment_id = 10;

-- Shipment 1: Carrier 2, Status = pending
-- Not yet picked up (scheduled in 2 days), only one event
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(1, 'pending', NOW() - INTERVAL '1 day', 'system_seed', NOW(), NOW());

-- Shipment 2: Carrier 4, Status = pending
-- Also not yet picked up, scheduled pickup tomorrow
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(2, 'pending', NOW() - INTERVAL '1 day', 'system_seed', NOW(), NOW());

-- Shipment 3: Carrier 2, Status = delivered
-- Delivered today, simulate full lifecycle
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(3, 'pending', NOW() - INTERVAL '3 days', 'api', NOW(), NOW()),
(3, 'in_transit', NOW() - INTERVAL '2 days', 'tracking_api', NOW(), NOW()),
(3, 'delivered', NOW() - INTERVAL '0.5 days', 'tracking_api', NOW(), NOW());

-- Shipment 4: Carrier 4, Status = cancelled
-- Scheduled for today, was cancelled recently
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(4, 'pending', NOW() - INTERVAL '2 days', 'api', NOW(), NOW()),
(4, 'cancelled', NOW() - INTERVAL '1 day', 'user_action', NOW(), NOW());

-- Shipment 5: Carrier 1, Status = pending
-- Scheduled pickup is still in the future
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(5, 'pending', NOW() - INTERVAL '1 day', 'system_seed', NOW(), NOW());

-- Shipment 6: Carrier 1, Status = delayed
-- Was picked up 3 days ago but not delivered; simulate delay
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(6, 'pending', NOW() - INTERVAL '4 days', 'api', NOW(), NOW()),
(6, 'in_transit', NOW() - INTERVAL '3 days', 'tracking_api', NOW(), NOW()),
(6, 'delayed', NOW() - INTERVAL '1 day', 'tracking_api', NOW(), NOW());

-- Shipment 7: Carrier 2, Status = delivered
-- Full successful cycle
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(7, 'pending', NOW() - INTERVAL '3 days', 'system_import', NOW(), NOW()),
(7, 'in_transit', NOW() - INTERVAL '2 days', 'tracking_api', NOW(), NOW()),
(7, 'delivered', NOW() - INTERVAL '1 day', 'tracking_api', NOW(), NOW());

-- Shipment 8: Carrier 4, Status = delivered
-- Short trip, delivered recently
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(8, 'pending', NOW() - INTERVAL '2 days', 'api', NOW(), NOW()),
(8, 'in_transit', NOW() - INTERVAL '1 day', 'tracking_api', NOW(), NOW()),
(8, 'delivered', NOW(), 'tracking_api', NOW(), NOW());

-- Shipment 9: Carrier 3, Status = in_transit
-- Picked up but not yet delivered
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(9, 'pending', NOW() - INTERVAL '2 days', 'user_upload', NOW(), NOW()),
(9, 'in_transit', NOW() - INTERVAL '1 day', 'tracking_api', NOW(), NOW());

-- Shipment 10: Carrier 3, Status = delivered
-- Fully completed
INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, created_at, updated_at)
VALUES 
(10, 'pending', NOW() - INTERVAL '3 days', 'user_upload', NOW(), NOW()),
(10, 'in_transit', NOW() - INTERVAL '2 days', 'tracking_api', NOW(), NOW()),
(10, 'delivered', NOW() - INTERVAL '1 day', 'tracking_api', NOW(), NOW());
