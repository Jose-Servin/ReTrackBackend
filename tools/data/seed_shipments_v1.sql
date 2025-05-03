-- Carriers
select * from public.shipments_carrier;

INSERT INTO public.shipments_carrier (name, mc_number, created_at, updated_at)
VALUES 
('Swift Logistics', 'MC456789', NOW(), NOW()),        -- id = 1
('FastLane Freight', 'MC888888', NOW(), NOW()),       -- id = 2
('BlueRoute Express', 'MC999999', NOW(), NOW()),      -- id = 3
('Midwest Movers', 'MC777777', NOW(), NOW());         -- id = 4

-- Drivers
select * from public.shipments_driver;

INSERT INTO public.shipments_driver (first_name, last_name, phone_number, email, carrier_id, created_at, updated_at)
VALUES
('Eric', 'Tran', '555-1000', 'eric.tran@swift.com', 1, NOW(), NOW()),       -- id = 1
('Alice', 'Nguyen', '555-1001', 'alice.nguyen@fastlane.com', 2, NOW(), NOW()), -- id = 2
('Carlos', 'Ramirez', '555-1002', 'carlos@blueroute.com', 3, NOW(), NOW()),   -- id = 3
('Nina', 'Patel', '555-1003', 'nina@midwest.com', 4, NOW(), NOW()),          -- id = 4
('Leo', 'Wang', '555-1004', 'leo@fastlane.com', 2, NOW(), NOW()),            -- id = 5
('Julia', 'Kim', '555-1005', 'julia@swift.com', 1, NOW(), NOW());            -- id = 6



-- Vehicles
select * from public.shipments_vehicle;

INSERT INTO public.shipments_vehicle (carrier_id, plate_number, device_id, created_at, updated_at)
VALUES
(1, 'XYZ111', 'DEV001', NOW(), NOW()),  -- id = 1
(1, 'XYZ222', 'DEV002', NOW(), NOW()),  -- id = 2
(2, 'FAST123', 'DEV003', NOW(), NOW()), -- id = 3
(2, 'FAST456', 'DEV004', NOW(), NOW()), -- id = 4
(3, 'BLUE789', 'DEV005', NOW(), NOW()), -- id = 5
(3, 'BLUE456', 'DEV006', NOW(), NOW()), -- id = 6
(4, 'MWM321', 'DEV007', NOW(), NOW()),  -- id = 7
(4, 'MWM654', 'DEV008', NOW(), NOW());  -- id = 8


-- Shipments
select * from public.shipments_shipment;

INSERT INTO public.shipments_shipment (
    origin, destination, scheduled_pickup, scheduled_delivery,
    actual_pickup, actual_delivery, current_status, carrier_id,
    driver_id, vehicle_id, created_at, updated_at
)
VALUES
-- pending → in_transit → delivered
('Chicago', 'Dallas', NOW(), NOW() + INTERVAL '2 days', NOW(), NOW() + INTERVAL '2 days', 'delivered', 1, 1, 1, NOW(), NOW()),
('New York', 'Atlanta', NOW(), NOW() + INTERVAL '1 day', NOW(), NOW() + INTERVAL '1 day', 'delivered', 2, 2, 3, NOW(), NOW()),
('LA', 'Seattle', NOW(), NOW() + INTERVAL '3 days', NOW(), NOW() + INTERVAL '3 days', 'delivered', 3, 3, 5, NOW(), NOW()),
-- pending → in_transit → delayed
('Houston', 'Miami', NOW(), NOW() + INTERVAL '4 days', NOW(), NULL, 'delayed', 4, 4, 7, NOW(), NOW()),
('Denver', 'Phoenix', NOW(), NOW() + INTERVAL '2 days', NOW(), NULL, 'delayed', 2, 5, 4, NOW(), NOW()),
-- pending → in_transit → cancelled
('Detroit', 'Boston', NOW(), NOW() + INTERVAL '2 days', NOW(), NULL, 'cancelled', 3, 6, 6, NOW(), NOW()),
('Orlando', 'Nashville', NOW(), NOW() + INTERVAL '3 days', NOW(), NULL, 'cancelled', 1, 1, 2, NOW(), NOW()),
-- delivered mix
('San Diego', 'San Jose', NOW(), NOW() + INTERVAL '1 day', NOW(), NOW() + INTERVAL '1 day', 'delivered', 4, 4, 8, NOW(), NOW()),
('Cleveland', 'Indianapolis', NOW(), NOW() + INTERVAL '2 days', NOW(), NULL, 'delayed', 2, 5, 3, NOW(), NOW()),
('Baltimore', 'Philadelphia', NOW(), NOW() + INTERVAL '1 day', NOW(), NOW() + INTERVAL '1 day', 'delivered', 3, 6, 5, NOW(), NOW());

-- ShipmentStatusEvents (3 per shipment)
-- Shipment 1 to 10

select * from public.shipments_shipmentstatusevent;

INSERT INTO public.shipments_shipmentstatusevent (shipment_id, status, event_timestamp, source, notes, created_at, updated_at)
VALUES
-- Shipment 1
(1, 'pending', NOW() - INTERVAL '3 days', 'system', 'Created', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
(1, 'in_transit', NOW() - INTERVAL '2 days', 'system', 'Picked up', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(1, 'delivered', NOW(), 'system', 'Delivered on time', NOW(), NOW()),

-- Shipment 2
(2, 'pending', NOW() - INTERVAL '2 days', 'system', 'Created', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(2, 'in_transit', NOW() - INTERVAL '1 day', 'system', 'En route', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(2, 'delivered', NOW(), 'system', 'Delivered early', NOW(), NOW()),

-- Shipment 3
(3, 'pending', NOW() - INTERVAL '4 days', 'system', 'Created', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
(3, 'in_transit', NOW() - INTERVAL '2 days', 'system', 'Left depot', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(3, 'delivered', NOW(), 'system', 'Delivered', NOW(), NOW()),

-- Shipment 4
(4, 'pending', NOW() - INTERVAL '2 days', 'system', 'Created', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(4, 'in_transit', NOW() - INTERVAL '1 day', 'system', 'In transit', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(4, 'delayed', NOW(), 'system', 'Stuck in traffic', NOW(), NOW()),

-- Shipment 5
(5, 'pending', NOW() - INTERVAL '1 day', 'system', 'Created', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(5, 'in_transit', NOW() - INTERVAL '12 hours', 'system', 'In transit', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours'),
(5, 'delayed', NOW(), 'system', 'Weather delay', NOW(), NOW()),

-- Shipment 6
(6, 'pending', NOW() - INTERVAL '2 days', 'system', 'Created', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(6, 'in_transit', NOW() - INTERVAL '1 day', 'system', 'Dispatched', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(6, 'cancelled', NOW(), 'system', 'Customer cancelled', NOW(), NOW()),

-- Shipment 7
(7, 'pending', NOW() - INTERVAL '1 day', 'system', 'Created', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(7, 'in_transit', NOW() - INTERVAL '10 hours', 'system', 'En route', NOW() - INTERVAL '10 hours', NOW() - INTERVAL '10 hours'),
(7, 'cancelled', NOW(), 'system', 'Vehicle issue', NOW(), NOW()),

-- Shipment 8
(8, 'pending', NOW() - INTERVAL '1 day', 'system', 'Created', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(8, 'in_transit', NOW() - INTERVAL '12 hours', 'system', 'In transit', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours'),
(8, 'delivered', NOW(), 'system', 'Delivered early', NOW(), NOW()),

-- Shipment 9
(9, 'pending', NOW() - INTERVAL '1 day', 'system', 'Created', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(9, 'in_transit', NOW() - INTERVAL '5 hours', 'system', 'En route', NOW() - INTERVAL '5 hours', NOW() - INTERVAL '5 hours'),
(9, 'delayed', NOW(), 'system', 'Road closure', NOW(), NOW()),

-- Shipment 10
(10, 'pending', NOW() - INTERVAL '2 days', 'system', 'Created', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(10, 'in_transit', NOW() - INTERVAL '1 day', 'system', 'In transit', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
(10, 'delivered', NOW(), 'system', 'Delivered', NOW(), NOW());