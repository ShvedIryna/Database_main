import json
import logging
import pymysql
import os
from datetime import datetime
from typing import Dict, Any

import azure.functions as func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    connection_string = os.environ.get('SqlConnectionString')
    if not connection_string:
        raise ValueError("SqlConnectionString is not configured")
    
    conn_params = {}
    for param in connection_string.split(';'):
        if '=' in param:
            key, value = param.split('=', 1)
            conn_params[key.lower().strip()] = value.strip()
    
    # Support both SQL Server and MySQL connection strings
    host = conn_params.get('server', '')
    if not host:
        host = conn_params.get('host', '')
    
    # Remove tcp:// prefix if present
    host = host.replace('tcp://', '').replace(',1433', '').replace(',3306', '')
    
    # Get port (default 3306 for MySQL, 1433 for SQL Server)
    port = 3306
    if 'port' in conn_params:
        port = int(conn_params['port'])
    elif ',' in conn_params.get('server', ''):
        port = int(conn_params['server'].split(',')[-1])
    
    # Get user (different keys for SQL Server vs MySQL)
    user = conn_params.get('user id', '') or conn_params.get('user', '') or conn_params.get('uid', '')
    
    # Get password
    password = conn_params.get('password', '') or conn_params.get('pwd', '')
    
    # Get database (different keys for SQL Server vs MySQL)
    database = conn_params.get('initial catalog', '') or conn_params.get('database', '') or conn_params.get('db', '')
    
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        ssl={'ca': None},
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def process_sensor_data(msg: func.ServiceBusMessage) -> None:
    try:
        message_body = msg.get_body().decode('utf-8')
        data = json.loads(message_body)
        
        logger.info(f"Received data from sensor: {data.get('sensor_id')}")
        
        sensor_id = data.get('sensor_id')
        sensor_type = data.get('sensor_type')
        sensor_name = data.get('sensor_name')
        timestamp_str = data.get('timestamp')
        location = data.get('location', {})
        measurements = data.get('measurements', {})
        
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Universal processing for different sensor types
        light_level = None
        temperature = None
        humidity = None
        
        if 'light_level' in measurements:
            light_level = measurements['light_level'].get('value')
        if 'temperature' in measurements:
            temp_value = measurements['temperature'].get('value')
            temperature = float(temp_value) if temp_value is not None else None
        if 'humidity' in measurements:
            hum_value = measurements['humidity'].get('value')
            humidity = float(hum_value) if hum_value is not None else None
        
        # Store all measurements in JSON for future expansion
        measurements_json = json.dumps(measurements, ensure_ascii=False) if measurements else None
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO sensor_data 
                    (sensor_id, sensor_type, sensor_name, timestamp, latitude, longitude, room, 
                     light_level, temperature, humidity, measurements_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    sensor_id,
                    sensor_type,
                    sensor_name,
                    timestamp,
                    location.get('latitude'),
                    location.get('longitude'),
                    location.get('room'),
                    light_level,
                    temperature,
                    humidity,
                    measurements_json
                ))
                
                update_metadata_sql = """
                    INSERT INTO sensor_metadata 
                    (sensor_id, sensor_type, sensor_name, location_room, location_latitude, location_longitude, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        sensor_name = VALUES(sensor_name),
                        location_room = VALUES(location_room),
                        location_latitude = VALUES(location_latitude),
                        location_longitude = VALUES(location_longitude),
                        updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(update_metadata_sql, (
                    sensor_id,
                    sensor_type,
                    sensor_name,
                    location.get('room'),
                    location.get('latitude'),
                    location.get('longitude'),
                    True
                ))
            
            conn.commit()
            logger.info(f"Data successfully saved for sensor {sensor_id}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving to database: {e}")
            raise
        finally:
            conn.close()
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise

def main(msg: func.ServiceBusMessage) -> None:
    """Main function for Azure Function trigger"""
    process_sensor_data(msg)

