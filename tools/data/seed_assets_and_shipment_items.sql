select * from public.shipments_shipment

select * from public.shipments_asset

-- INSERT INTO asset
INSERT INTO .shipments_asset (name, description, slug, weight_lb, length_in, width_in, height_in, is_fragile, is_hazardous, created_at, updated_at)
VALUES
('Tricone Drill Bit', 'Tricone Drill Bit used in upstream oil & gas operations.', 'tricone-drill-bit', 2935, 131, 41, 64, FALSE, FALSE, NOW(), NOW()),
('High-Pressure Mud Pump', 'High-Pressure Mud Pump used in upstream oil & gas operations.', 'high-pressure-mud-pump', 282, 175, 50, 93, TRUE, FALSE, NOW(), NOW()),
('20-Inch Steel Casing Pipe', '20-Inch Steel Casing Pipe used in upstream oil & gas operations.', '20-inch-steel-casing-pipe', 1289, 162, 69, 46, TRUE, TRUE, NOW(), NOW()),
('Annular Blowout Preventer', 'Annular Blowout Preventer used in upstream oil & gas operations.', 'annular-blowout-preventer', 3013, 98, 83, 60, TRUE, FALSE, NOW(), NOW()),
('Dual Deck Shale Shaker', 'Dual Deck Shale Shaker used in upstream oil & gas operations.', 'dual-deck-shale-shaker', 1385, 105, 76, 87, FALSE, FALSE, NOW(), NOW()),
('500-BBL Frac Tank', '500-BBL Frac Tank used in upstream oil & gas operations.', '500-bbl-frac-tank', 2102, 236, 45, 60, FALSE, TRUE, NOW(), NOW()),
('2-Inch Coiled Tubing Reel', '2-Inch Coiled Tubing Reel used in upstream oil & gas operations.', '2-inch-coiled-tubing-reel', 1110, 183, 29, 94, FALSE, FALSE, NOW(), NOW()),
('3.5-Inch Production Tubing', '3.5-Inch Production Tubing used in upstream oil & gas operations.', '3.5-inch-production-tubing', 2804, 60, 56, 40, FALSE, TRUE, NOW(), NOW()),
('Standard API Wellhead', 'Standard API Wellhead used in upstream oil & gas operations.', 'standard-api-wellhead', 2945, 51, 46, 85, TRUE, FALSE, NOW(), NOW()),
('Xmas Tree Assembly', 'Xmas Tree Assembly used in upstream oil & gas operations.', 'xmas-tree-assembly', 460, 108, 43, 85, TRUE, FALSE, NOW(), NOW()),
('Downhole Motor', 'Downhole Motor used in upstream oil & gas operations.', 'downhole-motor', 1752, 86, 37, 90, FALSE, FALSE, NOW(), NOW()),
('Hydraulic Power Skid', 'Hydraulic Power Skid used in upstream oil & gas operations.', 'hydraulic-power-skid', 2057, 146, 84, 60, FALSE, TRUE, NOW(), NOW()),
('Water-Based Drilling Mud', 'Water-Based Drilling Mud used in upstream oil & gas operations.', 'water-based-drilling-mud', 1351, 73, 91, 98, TRUE, TRUE, NOW(), NOW()),
('Mobile Cementing Skid', 'Mobile Cementing Skid used in upstream oil & gas operations.', 'mobile-cementing-skid', 3230, 216, 82, 96, FALSE, FALSE, NOW(), NOW()),
('36-Inch Adjustable Pipe Wrench', '36-Inch Adjustable Pipe Wrench used in upstream oil & gas operations.', '36-inch-adjustable-pipe-wrench', 188, 36, 12, 8, TRUE, FALSE, NOW(), NOW()),
('BOP Control Accumulator', 'BOP Control Accumulator used in upstream oil & gas operations.', 'bop-control-accumulator', 2450, 128, 69, 55, TRUE, TRUE, NOW(), NOW()),
('Vertical Gas-Liquid Separator', 'Vertical Gas-Liquid Separator used in upstream oil & gas operations.', 'vertical-gas-liquid-separator', 1773, 160, 66, 74, FALSE, FALSE, NOW(), NOW()),
('Offshore Flare Stack', 'Offshore Flare Stack used in upstream oil & gas operations.', 'offshore-flare-stack', 2984, 240, 50, 95, FALSE, TRUE, NOW(), NOW()),
('Mud-Gas Separator Unit', 'Mud-Gas Separator Unit used in upstream oil & gas operations.', 'mud-gas-separator-unit', 1992, 135, 45, 61, TRUE, FALSE, NOW(), NOW()),
('Rotary Table Drive', 'Rotary Table Drive used in upstream oil & gas operations.', 'rotary-table-drive', 1889, 92, 65, 58, FALSE, FALSE, NOW(), NOW()),
('Kelly Drive System', 'Kelly Drive System used in upstream oil & gas operations.', 'kelly-drive-system', 2176, 140, 60, 65, TRUE, TRUE, NOW(), NOW()),
('Drill Collar (Heavyweight)', 'Drill Collar (Heavyweight) used in upstream oil & gas operations.', 'drill-collar-heavyweight', 1491, 90, 40, 45, FALSE, TRUE, NOW(), NOW()),
('High-Speed Centrifuge', 'High-Speed Centrifuge used in upstream oil & gas operations.', 'high-speed-centrifuge', 1320, 77, 33, 40, TRUE, FALSE, NOW(), NOW()),
('Vacuum Degasser', 'Vacuum Degasser used in upstream oil & gas operations.', 'vacuum-degasser', 1422, 80, 38, 44, TRUE, TRUE, NOW(), NOW()),
('Choke Manifold System', 'Choke Manifold System used in upstream oil & gas operations.', 'choke-manifold-system', 1625, 94, 52, 66, FALSE, TRUE, NOW(), NOW());


select * from public.shipments_shipmentitem

-- INSERT INTO shipmentitem
INSERT INTO public.shipments_shipmentitem (shipment_id, asset_id, quantity, unit_weight_lb, notes)
VALUES
(5, 1, 2, 2935, 'Load with crane'),
(1, 2, 3, 282, NULL),
(9, 3, 4, 1289, 'Handle with care'),
(6, 4, 1, 3013, NULL),
(2, 5, 2, 1385, NULL),
(4, 6, 1, 2102, 'Ensure calibration before use'),
(8, 7, 3, 1110, NULL),
(7, 8, 2, 2804, NULL),
(10, 9, 1, 2945, NULL),
(3, 10, 2, 460, 'Handle with care'),
(2, 11, 3, 1752, NULL),
(1, 12, 1, 2057, NULL),
(7, 13, 2, 1351, 'Handle with care'),
(9, 14, 1, 3230, NULL),
(8, 15, 4, 188, NULL),
(3, 16, 1, 2450, 'Load with crane'),
(6, 17, 2, 1773, NULL),
(10, 18, 2, 2984, 'Ensure calibration before use'),
(4, 19, 3, 1992, NULL),
(5, 20, 2, 1889, NULL),
(3, 21, 2, 2176, 'Handle with care'),
(1, 22, 1, 1491, NULL),
(9, 23, 1, 1320, NULL),
(2, 24, 2, 1422, 'Handle with care'),
(7, 25, 3, 1625, NULL);
