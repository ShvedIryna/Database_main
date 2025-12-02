import json
import logging
import pymysql
import os
from datetime import datetime

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
    host = conn_params.get('server', '') or conn_params.get('host', '')
    host = host.replace('tcp://', '').replace(',1433', '').replace(',3306', '')
    
    port = 3306
    if 'port' in conn_params:
        port = int(conn_params['port'])
    elif ',' in conn_params.get('server', ''):
        port = int(conn_params['server'].split(',')[-1])
    
    user = conn_params.get('user id', '') or conn_params.get('user', '') or conn_params.get('uid', '')
    password = conn_params.get('password', '') or conn_params.get('pwd', '')
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

def handle_dlq_message(msg: func.ServiceBusMessage) -> None:
    try:
        message_body = msg.get_body().decode('utf-8')
        message_id = str(msg.message_id) if hasattr(msg, 'message_id') else None
        
        logger.warning(f"Received message from Dead Letter Queue: {message_id}")
        
        try:
            data = json.loads(message_body)
            sensor_id = data.get('sensor_id', 'unknown')
        except:
            sensor_id = 'unknown'
            data = {"raw_message": message_body}
        
        error_reason = f"Message expired or max delivery count exceeded. Message ID: {message_id}"
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO dead_letter_messages 
                    (original_message_id, sensor_id, message_body, error_reason, received_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    message_id,
                    sensor_id,
                    json.dumps(data, ensure_ascii=False),
                    error_reason,
                    datetime.utcnow()
                ))
            conn.commit()
            logger.info(f"DLQ message saved to database: {message_id}")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving DLQ message: {e}")
            raise
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error processing DLQ message: {e}")
        raise

def main(msg: func.ServiceBusMessage) -> None:
    """Main function for Azure Function DLQ trigger"""
    handle_dlq_message(msg)

