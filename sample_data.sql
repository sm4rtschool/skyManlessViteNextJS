-- ========================================
-- SAMPLE DATA UNTUK DATABASE SKYPARKING
-- ========================================

-- Sample data untuk tabel cards
INSERT INTO `cards` (`card_id`, `card_type`, `owner_name`, `is_active`, `registered_at`, `last_used`) VALUES
('CARD001', 'employee', 'Ahmad Wijaya', 1, '2024-01-15 08:00:00', '2024-12-23 09:30:00'),
('CARD002', 'visitor', 'Siti Nurhaliza', 1, '2024-01-20 10:15:00', '2024-12-22 14:45:00'),
('CARD003', 'employee', 'Budi Santoso', 1, '2024-02-01 07:30:00', '2024-12-23 08:15:00'),
('CARD004', 'monthly', 'Dewi Lestari', 1, '2024-02-10 11:00:00', '2024-12-21 16:20:00'),
('CARD005', 'visitor', 'Rahman Ali', 1, '2024-03-05 13:45:00', '2024-12-20 12:10:00'),
('CARD006', 'employee', 'Linda Sari', 0, '2024-01-25 09:20:00', '2024-11-15 17:30:00'),
('CARD007', 'vip', 'Hendra Kusuma', 1, '2024-03-15 14:00:00', '2024-12-23 10:45:00'),
('CARD008', 'monthly', 'Rina Permata', 1, '2024-04-01 08:30:00', '2024-12-22 15:50:00');

-- Sample data untuk tabel vehicles
INSERT INTO `vehicles` (`license_plate`, `owner_name`, `vehicle_type`, `card_id`, `registered_at`, `is_active`) VALUES
('B1234ABC', 'Ahmad Wijaya', 'car', 'CARD001', '2024-01-15 08:00:00', 1),
('B5678DEF', 'Siti Nurhaliza', 'motorcycle', 'CARD002', '2024-01-20 10:15:00', 1),
('B9012GHI', 'Budi Santoso', 'car', 'CARD003', '2024-02-01 07:30:00', 1),
('B3456JKL', 'Dewi Lestari', 'car', 'CARD004', '2024-02-10 11:00:00', 1),
('B7890MNO', 'Rahman Ali', 'motorcycle', 'CARD005', '2024-03-05 13:45:00', 1),
('B2468PQR', 'Linda Sari', 'car', 'CARD006', '2024-01-25 09:20:00', 0),
('B1357STU', 'Hendra Kusuma', 'car', 'CARD007', '2024-03-15 14:00:00', 1),
('B8024VWX', 'Rina Permata', 'motorcycle', 'CARD008', '2024-04-01 08:30:00', 1),
('B4680YZA', 'Teguh Prakoso', 'car', NULL, '2024-05-10 09:15:00', 1),
('B9753BCD', 'Maya Indah', 'motorcycle', NULL, '2024-06-20 11:30:00', 1);

-- Sample data untuk tabel parking_slots
INSERT INTO `parking_slots` (`slot_number`, `slot_type`, `is_occupied`, `current_vehicle_id`, `occupied_since`) VALUES
('A001', 'car', 1, 1, '2024-12-23 08:15:00'),
('A002', 'car', 0, NULL, NULL),
('A003', 'car', 1, 3, '2024-12-23 09:30:00'),
('A004', 'car', 0, NULL, NULL),
('A005', 'car', 1, 4, '2024-12-23 07:45:00'),
('B001', 'motorcycle', 1, 2, '2024-12-23 08:45:00'),
('B002', 'motorcycle', 0, NULL, NULL),
('B003', 'motorcycle', 1, 5, '2024-12-23 10:15:00'),
('B004', 'motorcycle', 0, NULL, NULL),
('B005', 'motorcycle', 0, NULL, NULL),
('VIP001', 'vip', 1, 7, '2024-12-23 09:00:00'),
('VIP002', 'vip', 0, NULL, NULL),
('DISABLE001', 'disabled', 0, NULL, NULL),
('DISABLE002', 'disabled', 0, NULL, NULL);

-- Sample data untuk tabel payments
INSERT INTO `payments` (`vehicle_id`, `card_id`, `amount`, `payment_method`, `payment_status`, `entry_time`, `exit_time`, `duration_hours`, `created_at`) VALUES
(1, 'CARD001', 4000.0, 'card', 'completed', '2024-12-22 14:00:00', '2024-12-22 16:00:00', 2.0, '2024-12-22 16:00:00'),
(2, 'CARD002', 6000.0, 'cash', 'completed', '2024-12-22 10:30:00', '2024-12-22 13:30:00', 3.0, '2024-12-22 13:30:00'),
(3, 'CARD003', 2000.0, 'card', 'completed', '2024-12-22 08:15:00', '2024-12-22 09:15:00', 1.0, '2024-12-22 09:15:00'),
(4, 'CARD004', 0.0, 'monthly_pass', 'completed', '2024-12-22 07:45:00', '2024-12-22 17:30:00', 9.75, '2024-12-22 17:30:00'),
(5, 'CARD005', 8000.0, 'cash', 'completed', '2024-12-21 11:00:00', '2024-12-21 15:00:00', 4.0, '2024-12-21 15:00:00'),
(7, 'CARD007', 0.0, 'vip_pass', 'completed', '2024-12-21 09:30:00', '2024-12-21 18:00:00', 8.5, '2024-12-21 18:00:00'),
(9, NULL, 12000.0, 'cash', 'pending', '2024-12-23 08:00:00', NULL, NULL, '2024-12-23 08:00:00'),
(10, NULL, 4000.0, 'card', 'completed', '2024-12-22 13:15:00', '2024-12-22 15:15:00', 2.0, '2024-12-22 15:15:00');

-- Sample data untuk tabel parking_log
INSERT INTO `parking_log` (`timestamp`, `event_type`, `details`, `card_id`) VALUES
('2024-12-23 08:15:00', 'entry', 'Vehicle B1234ABC entered parking slot A001', 'CARD001'),
('2024-12-23 08:45:00', 'entry', 'Vehicle B5678DEF entered parking slot B001', 'CARD002'),
('2024-12-23 09:30:00', 'entry', 'Vehicle B9012GHI entered parking slot A003', 'CARD003'),
('2024-12-23 09:00:00', 'entry', 'Vehicle B1357STU entered VIP parking slot VIP001', 'CARD007'),
('2024-12-23 10:15:00', 'entry', 'Vehicle B7890MNO entered parking slot B003', 'CARD005'),
('2024-12-22 16:00:00', 'exit', 'Vehicle B1234ABC exited from parking slot A001, payment completed', 'CARD001'),
('2024-12-22 13:30:00', 'exit', 'Vehicle B5678DEF exited from parking slot B001, cash payment', 'CARD002'),
('2024-12-23 07:30:00', 'system', 'Daily backup completed successfully', NULL),
('2024-12-23 08:00:00', 'gate', 'Entry gate opened for vehicle B4680YZA', NULL),
('2024-12-23 06:00:00', 'system', 'System maintenance completed', NULL),
('2024-12-22 23:55:00', 'alert', 'Low card reader battery detected', NULL),
('2024-12-23 01:00:00', 'system', 'Automatic gate closed due to schedule', NULL);

-- Sample data untuk tabel system_alerts
INSERT INTO `system_alerts` (`alert_type`, `severity`, `message`, `is_resolved`, `created_at`, `resolved_at`) VALUES
('hardware', 'medium', 'Card reader battery low - requires replacement within 48 hours', 0, '2024-12-22 23:55:00', NULL),
('system', 'low', 'Daily backup completed with warnings - some log files were skipped', 1, '2024-12-23 07:30:00', '2024-12-23 07:35:00'),
('security', 'high', 'Multiple failed card authentication attempts detected', 1, '2024-12-22 15:20:00', '2024-12-22 15:45:00'),
('hardware', 'medium', 'Camera 2 connection unstable - intermittent disconnections', 0, '2024-12-23 09:15:00', NULL),
('system', 'low', 'Parking capacity at 85% - approaching maximum limit', 1, '2024-12-23 10:30:00', '2024-12-23 11:00:00'),
('payment', 'medium', 'Payment gateway timeout - 3 transactions affected', 1, '2024-12-22 14:20:00', '2024-12-22 14:25:00'),
('hardware', 'high', 'Gate motor overheating detected - emergency shutdown activated', 1, '2024-12-21 16:30:00', '2024-12-21 18:00:00'),
('security', 'medium', 'Unauthorized access attempt to admin panel', 1, '2024-12-20 22:15:00', '2024-12-20 22:30:00');

-- ========================================
-- QUERY UNTUK VERIFIKASI DATA
-- ========================================

-- Cek total data di setiap tabel
SELECT 'cards' as table_name, COUNT(*) as record_count FROM cards
UNION ALL
SELECT 'vehicles', COUNT(*) FROM vehicles
UNION ALL
SELECT 'parking_slots', COUNT(*) FROM parking_slots
UNION ALL
SELECT 'payments', COUNT(*) FROM payments
UNION ALL
SELECT 'parking_log', COUNT(*) FROM parking_log
UNION ALL
SELECT 'system_alerts', COUNT(*) FROM system_alerts
UNION ALL
SELECT 'system_config', COUNT(*) FROM system_config;

-- Cek status parking slots
SELECT 
    slot_type,
    COUNT(*) as total_slots,
    SUM(is_occupied) as occupied_slots,
    COUNT(*) - SUM(is_occupied) as available_slots
FROM parking_slots 
GROUP BY slot_type;

-- Cek revenue harian
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_transactions,
    SUM(amount) as total_revenue
FROM payments 
WHERE payment_status = 'completed'
GROUP BY DATE(created_at)
ORDER BY date DESC; 