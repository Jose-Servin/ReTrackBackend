select * from public.shipments_shipment order by id


select * from public.locations_location



select 
s.id as shipment_id,
s.origin_id,
s.destination_id,
lo.id as location_origin_id,
ld.id as location_destination_id,
lo.city as origin_city,
ld.city as destination_city
from shipments_shipment s 
LEFT JOIN locations_location lo ON s.origin_id = lo.id
LEFT JOIN locations_location ld ON s.destination_id = ld.id
order by s.id


INSERT INTO public.locations_location (
    name, address_line1, address_line2, city, state, postal_code, country,
    latitude, longitude, created_at, updated_at
) VALUES
('Houston Terminal', '123 Main St', NULL, 'Houston', 'TX', '77001', 'US', NULL, NULL, NOW(), NOW()),
('Dallas Hub', '456 Elm St', NULL, 'Dallas', 'TX', '75201', 'US', NULL, NULL, NOW(), NOW()),
('Austin Depot', '789 Congress Ave', NULL, 'Austin', 'TX', '73301', 'US', NULL, NULL, NOW(), NOW()),
('Lubbock Yard', '101 Tech Dr', NULL, 'Lubbock', 'TX', '79401', 'US', NULL, NULL, NOW(), NOW()),
('El Paso Station', '202 Border Hwy', NULL, 'El Paso', 'TX', '79901', 'US', NULL, NULL, NOW(), NOW()),
('Wichita Falls Dock', '303 Falls St', NULL, 'Wichita Falls', 'TX', '76301', 'US', NULL, NULL, NOW(), NOW()),
('Beaumont Center', '404 Gulf Ave', NULL, 'Beaumont', 'TX', '77701', 'US', NULL, NULL, NOW(), NOW()),
('Bryan Logistics', '505 College Ave', NULL, 'Bryan', 'TX', '77801', 'US', NULL, NULL, NOW(), NOW()),
('McAllen Freight', '606 Border Rd', NULL, 'McAllen', 'TX', '78501', 'US', NULL, NULL, NOW(), NOW()),
('Plano Hub', '707 Legacy Dr', NULL, 'Plano', 'TX', '75023', 'US', NULL, NULL, NOW(), NOW()),
('Midland Depot', '808 Oilfield Rd', NULL, 'Midland', 'TX', '79701', 'US', NULL, NULL, NOW(), NOW()),
('Fort Worth Yard', '909 Stockyard Blvd', NULL, 'Fort Worth', 'TX', '76101', 'US', NULL, NULL, NOW(), NOW()),
('San Antonio Terminal', '1001 Alamo St', NULL, 'San Antonio', 'TX', '78201', 'US', NULL, NULL, NOW(), NOW()),
('Odessa Facility', '1111 E 42nd St', NULL, 'Odessa', 'TX', '79761', 'US', NULL, NULL, NOW(), NOW()),
('Temple Distribution', '1212 Rail Ave', NULL, 'Temple', 'TX', '76501', 'US', NULL, NULL, NOW(), NOW()),
('Longview Center', '1313 Pine Tree Rd', NULL, 'Longview', 'TX', '75601', 'US', NULL, NULL, NOW(), NOW()),
('Galveston Port', '1414 Seawall Blvd', NULL, 'Galveston', 'TX', '77550', 'US', NULL, NULL, NOW(), NOW()),
('Laredo Border Facility', '1515 International Blvd', NULL, 'Laredo', 'TX', '78040', 'US', NULL, NULL, NOW(), NOW()),
('Irving Logistics Park', '1616 MacArthur Blvd', NULL, 'Irving', 'TX', '75039', 'US', NULL, NULL, NOW(), NOW());


-- Update origin_location_id based on city name match
UPDATE public.shipments_shipment AS s
SET origin_location_id = l.id
FROM public.locations_location AS l
WHERE l.city = s.origin;

-- Update destination_location_id based on city name match
UPDATE public.shipments_shipment AS s
SET destination_location_id = l.id
FROM public.locations_location AS l
WHERE l.city = s.destination;


SELECT 
    s.id,
    s.origin,
    s.origin_location_id,
    lo.city AS resolved_origin_city,
    s.destination,
    s.destination_location_id,
    ld.city AS resolved_dest_city
FROM public.shipments_shipment s
LEFT JOIN public.locations_location lo ON s.origin_location_id = lo.id
LEFT JOIN public.locations_location ld ON s.destination_location_id = ld.id
ORDER BY s.id;



-- Shipment 1
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'Houston'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Midland'
) WHERE id = 1;

-- Shipment 2
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'Dallas'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Fort Worth'
) WHERE id = 2;

-- Shipment 3
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'Austin'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'San Antonio'
) WHERE id = 3;

-- Shipment 4
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'Lubbock'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Odessa'
) WHERE id = 4;

-- Shipment 5
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'El Paso'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Houston'
) WHERE id = 5;

-- Shipment 6
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'Wichita Falls'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Temple'
) WHERE id = 6;

-- Shipment 7
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'Beaumont'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Longview'
) WHERE id = 7;

-- Shipment 8
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'Bryan'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Galveston'
) WHERE id = 8;

-- Shipment 9
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'McAllen'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Laredo'
) WHERE id = 9;

-- Shipment 10
UPDATE shipments_shipment SET origin_id = (
  SELECT id FROM locations_location WHERE city = 'Plano'
), destination_id = (
  SELECT id FROM locations_location WHERE city = 'Irving'
) WHERE id = 10;


