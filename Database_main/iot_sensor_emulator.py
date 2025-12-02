import json
import time
import random
import requests
from datetime import datetime
from typing import Dict, List
import os
import logging
import hmac
import hashlib
import base64
from urllib.parse import quote
from azure.servicebus import ServiceBusClient, ServiceBusMessage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SensorEmulator:
    def __init__(self, config_path: str = "iot_config.json"):
        config_path = os.getenv('IOT_CONFIG_PATH', config_path)
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._create_default_config()
        
        self.service_bus_conn = os.getenv('SERVICE_BUS_CONNECTION_STRING') or self.config['service_bus']['connection_string']
        self.queue_name = os.getenv('QUEUE_NAME') or self.config['service_bus']['queue_name']
        self.sensors = self.config['sensors']
        self.service_bus_client = None
        # Опція використання REST API напряму (за замовчуванням використовується SDK, який також використовує REST API під капотом)
        self.use_rest_api = os.getenv('USE_REST_API', 'false').lower() == 'true'
    
    def _create_default_config(self):
        return {
            "service_bus": {
                "connection_string": os.getenv('SERVICE_BUS_CONNECTION_STRING', ''),
                "queue_name": os.getenv('QUEUE_NAME', 'sensor-data-queue')
            },
            "sensors": [
                {
                    "sensor_id": "photoresistor_1",
                    "sensor_type": "photoresistor",
                    "sensor_name": "Photoresistor - Room Illumination",
                    "location": {"latitude": 50.4501, "longitude": 30.5234, "room": "Room 101"},
                    "frequency_ms": 50,
                    "parameters": {"light_level": {"min": 0, "max": 1024, "unit": "lux"}}
                },
                {
                    "sensor_id": "dht22_1",
                    "sensor_type": "dht22",
                    "sensor_name": "DHT22 - Temperature and Humidity",
                    "location": {"latitude": 50.4510, "longitude": 30.5240, "room": "Room 102"},
                    "frequency_ms": 80,
                    "parameters": {
                        "temperature": {"min": 18, "max": 28, "unit": "celsius"},
                        "humidity": {"min": 30, "max": 70, "unit": "percent"}
                    }
                }
            ],
            "emulation": {"duration_seconds": 3600, "ramp_up_seconds": 10}
        }
        
    def connect_service_bus(self):
        try:
            self.service_bus_client = ServiceBusClient.from_connection_string(
                self.service_bus_conn
            )
            logger.info("Connected to Azure Service Bus")
        except Exception as e:
            logger.error(f"Error connecting to Service Bus: {e}")
            raise
    
    def generate_sensor_data(self, sensor_config: Dict) -> Dict:
        sensor_id = sensor_config['sensor_id']
        sensor_type = sensor_config['sensor_type']
        location = sensor_config['location']
        params = sensor_config['parameters']
        
        data = {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "sensor_name": sensor_config['sensor_name'],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "location": {
                "latitude": location['latitude'],
                "longitude": location['longitude'],
                "room": location['room']
            },
            "measurements": {}
        }
        
        # Generate data based on sensor type
        if sensor_type == "photoresistor":
            light_config = params['light_level']
            light_value = random.randint(light_config['min'], light_config['max'])
            data['measurements']['light_level'] = {
                "value": light_value,
                "unit": light_config['unit']
            }
        elif sensor_type == "dht22":
            # Temperature and humidity sensor
            temp_config = params['temperature']
            humidity_config = params['humidity']
            temp_value = round(random.uniform(temp_config['min'], temp_config['max']), 1)
            humidity_value = round(random.uniform(humidity_config['min'], humidity_config['max']), 1)
            data['measurements']['temperature'] = {
                "value": temp_value,
                "unit": temp_config['unit']
            }
            data['measurements']['humidity'] = {
                "value": humidity_value,
                "unit": humidity_config['unit']
            }
        else:
            # Universal handling for other sensor types
            for param_name, param_config in params.items():
                if isinstance(param_config, dict) and 'min' in param_config and 'max' in param_config:
                    if param_config.get('unit') == 'celsius' or param_config.get('unit') == 'percent':
                        value = round(random.uniform(param_config['min'], param_config['max']), 1)
                    else:
                        value = random.randint(param_config['min'], param_config['max'])
                    data['measurements'][param_name] = {
                        "value": value,
                        "unit": param_config.get('unit', '')
                    }
        
        return data
    
    def _parse_connection_string(self, conn_str: str) -> Dict[str, str]:
        """Parse connection string to extract components"""
        parts = {}
        for part in conn_str.split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                parts[key.lower()] = value
        return parts
    
    def _generate_sas_token(self, uri: str, key_name: str, key: str, expiry: int = 3600) -> str:
        """Generate SAS token for REST API authorization"""
        import time
        expiry = int(time.time()) + expiry
        
        # URI must be lowercase and properly encoded
        uri_lower = uri.lower()
        encoded_uri = quote(uri_lower, safe='')
        
        # String to sign: encoded_uri + "\n" + expiry
        string_to_sign = f"{encoded_uri}\n{expiry}"
        
        # Generate signature using HMAC-SHA256
        decoded_key = base64.b64decode(key)
        signature = base64.b64encode(
            hmac.new(
                decoded_key,
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        # URL encode the signature
        encoded_sig = quote(signature, safe='')
        
        return f"SharedAccessSignature sr={encoded_uri}&sig={encoded_sig}&se={expiry}&skn={key_name}"
    
    def send_to_queue_rest(self, data: Dict):
        """Send message to queue via REST API (HTTP requests)"""
        try:
            # Parse connection string
            conn_parts = self._parse_connection_string(self.service_bus_conn)
            endpoint = conn_parts.get('endpoint', '').replace('sb://', 'https://').rstrip('/')
            key_name = conn_parts.get('sharedaccesskeyname', 'RootManageSharedAccessKey')
            key = conn_parts.get('sharedaccesskey', '')
            
            # Form REST API URL
            queue_url = f"{endpoint}/{self.queue_name}/messages"
            
            # Generate SAS token
            sas_token = self._generate_sas_token(queue_url, key_name, key)
            
            # Form message
            message_body = json.dumps(data, ensure_ascii=False)
            
            # Send via REST API
            headers = {
                'Authorization': sas_token,
                'Content-Type': 'application/json',
                'BrokerProperties': json.dumps({
                    'Label': f"sensor_{data.get('sensor_id', 'unknown')}",
                    'MessageId': f"{data.get('sensor_id', 'unknown')}_{int(time.time() * 1000)}"
                })
            }
            
            response = requests.post(queue_url, data=message_body.encode('utf-8'), headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Sent data via REST API from {data['sensor_id']}: {data['measurements']}")
            
        except Exception as e:
            logger.error(f"Error sending via REST API: {e}")
            raise
    
    def send_to_queue(self, data: Dict):
        """Send message to queue (uses SDK or REST API depending on configuration)"""
        if self.use_rest_api:
            # Use REST API directly (HTTP requests)
            self.send_to_queue_rest(data)
        else:
            # Use SDK (which also uses REST API under the hood)
            try:
                with self.service_bus_client:
                    sender = self.service_bus_client.get_queue_sender(queue_name=self.queue_name)
                    with sender:
                        message_body = json.dumps(data, ensure_ascii=False)
                        message = ServiceBusMessage(message_body)
                        sender.send_messages(message)
                        logger.info(f"Sent data from {data['sensor_id']}: {data['measurements']}")
            except Exception as e:
                logger.error(f"Error sending to queue: {e}")
                raise
    
    def run_emulation(self):
        logger.info("Starting sensor emulation...")
        if not self.use_rest_api:
            # Connect to Service Bus only if using SDK
            self.connect_service_bus()
        else:
            logger.info("Using REST API for sending messages")
        
        duration = self.config['emulation'].get('duration_seconds', 3600)
        ramp_up = self.config['emulation'].get('ramp_up_seconds', 10)
        start_time = time.time()
        
        sensor_timers = {}
        for sensor in self.sensors:
            sensor_timers[sensor['sensor_id']] = {
                'last_send': 0,
                'frequency_ms': sensor['frequency_ms']
            }
        
        try:
            while time.time() - start_time < duration:
                current_time = time.time() * 1000
                
                for sensor in self.sensors:
                    sensor_id = sensor['sensor_id']
                    timer = sensor_timers[sensor_id]
                    
                    if current_time - timer['last_send'] >= timer['frequency_ms']:
                        data = self.generate_sensor_data(sensor)
                        self.send_to_queue(data)
                        timer['last_send'] = current_time
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            logger.info("Emulation stopped by user")
        except Exception as e:
            logger.error(f"Error during emulation: {e}")
        finally:
            if self.service_bus_client:
                self.service_bus_client.close()
            logger.info("Emulation completed")

if __name__ == "__main__":
    config_path = os.getenv('IOT_CONFIG_PATH', 'iot_config.json')
    emulator = SensorEmulator(config_path)
    emulator.run_emulation()

