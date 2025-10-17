-- ========================================
-- SETUP DATABASE SKYPARKING
-- Script untuk membuat struktur database lengkap
-- ========================================

-- Hapus database lama jika ada (HATI-HATI!)
-- DROP DATABASE IF EXISTS skyparking;

-- Buat database baru
CREATE DATABASE IF NOT EXISTS skyparking 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Gunakan database skyparking
USE skyparking;

-- ========================================
-- STRUKTUR TABEL
-- ========================================

-- Tabel parking_log: Log semua event sistem
CREATE TABLE IF NOT EXISTS `parking_log` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `event_type` VARCHAR(50) NOT NULL,
  `details` TEXT NULL,
  `card_id` VARCHAR(100) NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_timestamp` (`timestamp`),
  INDEX `idx_event_type` (`event_type`),
  INDEX `idx_card_id` (`card_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabel vehicles: Data kendaraan terdaftar
CREATE TABLE IF NOT EXISTS `vehicles` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `license_plate` VARCHAR(20) NOT NULL,
  `owner_name` VARCHAR(100) NOT NULL,
  `vehicle_type` VARCHAR(50) NOT NULL COMMENT 'car, motorcycle, truck, etc.',
  `card_id` VARCHAR(100) NULL,
  `registered_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_license_plate` (`license_plate`),
  INDEX `idx_card_id` (`card_id`),
  INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabel cards: Data kartu akses
CREATE TABLE IF NOT EXISTS `cards` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `card_id` VARCHAR(100) NOT NULL,
  `card_type` VARCHAR(50) NOT NULL COMMENT 'employee, visitor, monthly, vip, etc.',
  `owner_name` VARCHAR(100) NOT NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `registered_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_used` DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_card_id` (`card_id`),
  INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabel system_config: Konfigurasi sistem
CREATE TABLE IF NOT EXISTS `system_config` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `config_key` VARCHAR(100) NOT NULL,
  `config_value` TEXT NOT NULL,
  `description` TEXT NULL,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabel parking_slots: Slot parkir
CREATE TABLE IF NOT EXISTS `parking_slots` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `slot_number` VARCHAR(10) NOT NULL,
  `slot_type` VARCHAR(20) NOT NULL COMMENT 'car, motorcycle, disabled, vip',
  `is_occupied` BOOLEAN NOT NULL DEFAULT FALSE,
  `current_vehicle_id` INT NULL,
  `occupied_since` DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `idx_slot_number` (`slot_number`),
  INDEX `idx_is_occupied` (`is_occupied`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabel payments: Pembayaran parkir
CREATE TABLE IF NOT EXISTS `payments` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `vehicle_id` INT NOT NULL,
  `card_id` VARCHAR(100) NULL,
  `amount` FLOAT NOT NULL,
  `payment_method` VARCHAR(50) NOT NULL COMMENT 'cash, card, digital, monthly_pass, vip_pass',
  `payment_status` VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'pending, completed, failed',
  `entry_time` DATETIME NOT NULL,
  `exit_time` DATETIME NULL,
  `duration_hours` FLOAT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_vehicle_id` (`vehicle_id`),
  INDEX `idx_card_id` (`card_id`),
  INDEX `idx_payment_status` (`payment_status`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabel system_alerts: Alert sistem
CREATE TABLE IF NOT EXISTS `system_alerts` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `alert_type` VARCHAR(50) NOT NULL COMMENT 'hardware, system, security, payment',
  `severity` VARCHAR(20) NOT NULL COMMENT 'low, medium, high, critical',
  `message` TEXT NOT NULL,
  `is_resolved` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_alert_type` (`alert_type`),
  INDEX `idx_severity` (`severity`),
  INDEX `idx_is_resolved` (`is_resolved`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- DATA AWAL KONFIGURASI SISTEM
-- ========================================

INSERT INTO `system_config` (`config_key`, `config_value`, `description`) VALUES
('gate_auto_close_delay', '5', 'Auto close gate delay in seconds'),
('camera_resolution', '1920x1080', 'Camera resolution setting'),
('parking_rate_per_hour', '2000', 'Parking rate per hour in IDR'),
('max_parking_capacity', '100', 'Maximum parking capacity'),
('card_reader_timeout', '10', 'Card reader timeout in seconds'),
('system_timezone', 'Asia/Jakarta', 'System timezone'),
('backup_enabled', 'true', 'Enable automatic database backup'),
('notification_email', 'admin@manlessparking.com', 'System notification email'),
('gate_open_duration', '10', 'Gate open duration in seconds'),
('log_retention_days', '90', 'Log retention period in days');

-- ========================================
-- SELESAI
-- ========================================

SELECT '✅ Database skyparking berhasil dibuat!' as Status;
SELECT 'Total tabel yang dibuat:' as Info, COUNT(*) as Jumlah 
FROM information_schema.tables 
WHERE table_schema = 'skyparking';

