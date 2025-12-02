-- Database is created separately, just use it
-- CREATE DATABASE IF NOT EXISTS iot_sensors_db;
-- USE iot_sensors_db;

CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(100) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    sensor_name VARCHAR(255),
    timestamp DATETIME NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    room VARCHAR(100),
    -- Параметри для різних типів датчиків
    light_level INT,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    -- JSON поле для зберігання додаткових параметрів (майбутнє розширення)
    measurements_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_sensor_timestamp (sensor_id, timestamp),
    INDEX idx_sensor_type (sensor_type)
);

CREATE TABLE IF NOT EXISTS sensor_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(100) UNIQUE NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    sensor_name VARCHAR(255),
    location_room VARCHAR(100),
    location_latitude DECIMAL(10, 8),
    location_longitude DECIMAL(11, 8),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dead_letter_messages (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    original_message_id VARCHAR(255),
    sensor_id VARCHAR(100),
    message_body TEXT,
    error_reason TEXT,
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_received_at (received_at)
);


