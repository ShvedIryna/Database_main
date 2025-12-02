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

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        sensor_id = req.params.get('sensor_id')
        limit = int(req.params.get('limit', 100))
        start_date = req.params.get('start_date')
        end_date = req.params.get('end_date')
        
        if not sensor_id:
            return func.HttpResponse(
                json.dumps({"error": "sensor_id parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT 
                        id, sensor_id, sensor_type, sensor_name, 
                        timestamp, latitude, longitude, room, 
                        light_level, temperature, humidity, measurements_json, created_at
                    FROM sensor_data
                    WHERE sensor_id = %s
                """
                params = [sensor_id]
                
                if start_date:
                    sql += " AND timestamp >= %s"
                    params.append(start_date)
                
                if end_date:
                    sql += " AND timestamp <= %s"
                    params.append(end_date)
                
                sql += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(sql, params)
                results = cursor.fetchall()
                
                for row in results:
                    if isinstance(row.get('timestamp'), datetime):
                        row['timestamp'] = row['timestamp'].isoformat()
                    if isinstance(row.get('created_at'), datetime):
                        row['created_at'] = row['created_at'].isoformat()
                
                return func.HttpResponse(
                    json.dumps({
                        "sensor_id": sensor_id,
                        "count": len(results),
                        "data": results
                    }, ensure_ascii=False, default=str),
                    status_code=200,
                    mimetype="application/json"
                )
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


