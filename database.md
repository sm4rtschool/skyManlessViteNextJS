-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.22-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.11.0.7065
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table skyparking.cards
CREATE TABLE IF NOT EXISTS `cards` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `card_id` varchar(100) NOT NULL,
  `card_type` varchar(50) NOT NULL,
  `owner_name` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `registered_at` datetime NOT NULL,
  `last_used` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_cards_card_id` (`card_id`),
  KEY `ix_cards_id` (`id`),
  KEY `ix_cards_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table skyparking.cards: ~0 rows (approximately)
DELETE FROM `cards`;

-- Dumping structure for table skyparking.parking_log
CREATE TABLE IF NOT EXISTS `parking_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `event_type` varchar(50) DEFAULT NULL,
  `details` text DEFAULT NULL,
  `card_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table skyparking.parking_log: ~0 rows (approximately)
DELETE FROM `parking_log`;

-- Dumping structure for table skyparking.parking_slots
CREATE TABLE IF NOT EXISTS `parking_slots` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `slot_number` varchar(10) NOT NULL,
  `slot_type` varchar(20) NOT NULL,
  `is_occupied` tinyint(1) NOT NULL,
  `current_vehicle_id` int(11) DEFAULT NULL,
  `occupied_since` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_parking_slots_slot_number` (`slot_number`),
  KEY `ix_parking_slots_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table skyparking.parking_slots: ~0 rows (approximately)
DELETE FROM `parking_slots`;

-- Dumping structure for table skyparking.payments
CREATE TABLE IF NOT EXISTS `payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vehicle_id` int(11) NOT NULL,
  `card_id` varchar(100) DEFAULT NULL,
  `amount` float NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `payment_status` varchar(20) NOT NULL,
  `entry_time` datetime NOT NULL,
  `exit_time` datetime DEFAULT NULL,
  `duration_hours` float DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_payments_id` (`id`),
  KEY `ix_payments_card_id` (`card_id`),
  KEY `ix_payments_vehicle_id` (`vehicle_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table skyparking.payments: ~0 rows (approximately)
DELETE FROM `payments`;

-- Dumping structure for table skyparking.system_alerts
CREATE TABLE IF NOT EXISTS `system_alerts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alert_type` varchar(50) NOT NULL,
  `severity` varchar(20) NOT NULL,
  `message` text NOT NULL,
  `is_resolved` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `resolved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_system_alerts_id` (`id`),
  KEY `ix_system_alerts_alert_type` (`alert_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table skyparking.system_alerts: ~0 rows (approximately)
DELETE FROM `system_alerts`;

-- Dumping structure for table skyparking.system_config
CREATE TABLE IF NOT EXISTS `system_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `config_key` varchar(100) NOT NULL,
  `config_value` text NOT NULL,
  `description` text DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_system_config_config_key` (`config_key`),
  KEY `ix_system_config_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;

-- Dumping data for table skyparking.system_config: ~10 rows (approximately)
DELETE FROM `system_config`;
INSERT INTO `system_config` (`id`, `config_key`, `config_value`, `description`, `updated_at`) VALUES
	(1, 'gate_auto_close_delay', '5', 'Auto close gate delay in seconds', '2025-06-19 06:22:14'),
	(2, 'camera_resolution', '1920x1080', 'Camera resolution setting', '2025-06-19 06:22:14'),
	(3, 'parking_rate_per_hour', '2000', 'Parking rate per hour in IDR', '2025-06-19 06:22:14'),
	(4, 'max_parking_capacity', '100', 'Maximum parking capacity', '2025-06-19 06:22:14'),
	(5, 'card_reader_timeout', '10', 'Card reader timeout in seconds', '2025-06-19 06:22:14'),
	(6, 'system_timezone', 'Asia/Jakarta', 'System timezone', '2025-06-19 06:22:14'),
	(7, 'backup_enabled', 'true', 'Enable automatic database backup', '2025-06-19 06:22:14'),
	(8, 'notification_email', 'admin@manlessparking.com', 'System notification email', '2025-06-19 06:22:14'),
	(9, 'gate_open_duration', '10', 'Gate open duration in seconds', '2025-06-19 06:22:14'),
	(10, 'log_retention_days', '90', 'Log retention period in days', '2025-06-19 06:22:14');

-- Dumping structure for table skyparking.vehicles
CREATE TABLE IF NOT EXISTS `vehicles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `license_plate` varchar(20) NOT NULL,
  `owner_name` varchar(100) NOT NULL,
  `vehicle_type` varchar(50) NOT NULL,
  `card_id` varchar(100) DEFAULT NULL,
  `registered_at` datetime NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_vehicles_license_plate` (`license_plate`),
  KEY `ix_vehicles_is_active` (`is_active`),
  KEY `ix_vehicles_card_id` (`card_id`),
  KEY `ix_vehicles_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dumping data for table skyparking.vehicles: ~0 rows (approximately)
DELETE FROM `vehicles`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
