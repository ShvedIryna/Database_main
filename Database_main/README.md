# IoT Sensor System - Azure Serverless

Система для обробки даних з IoT-датчиків за допомогою Azure Serverless технологій.

## Структура проекту

```
Database_main/
├── iot_sensor_emulator.py      # Емулятор датчиків
├── iot_config.json              # Конфігурація датчиків
├── database_schema.sql           # Схема бази даних
├── setup_database.py             # Налаштування БД
├── Dockerfile.iot                # Dockerfile для емулятора
├── requirements_iot.txt          # Python залежності
│
├── azure_iot_setup.ps1           # Створення Azure ресурсів
├── start_all_services.ps1         # Запуск сервісів
├── stop_all_services.ps1          # Зупинка сервісів (економія бюджету)
├── delete_all_resources.ps1      # Видалення всіх ресурсів
│
└── iot_functions/                # Azure Functions
    ├── process_sensor_data/      # Обробка черги
    ├── get_sensor_history/        # REST API
    └── handle_dlq/               # Dead Letter Queue
```

## Швидкий старт

### 1. Створення Azure ресурсів

```powershell
powershell -ExecutionPolicy Bypass -File azure_iot_setup.ps1
```

### 2. Налаштування бази даних

```powershell
python setup_database.py
```

### 3. Деплой Azure Functions

```powershell
cd iot_functions
func azure functionapp publish iot-sensors-processor
```

### 4. Запуск емулятора (локально)

```powershell
python iot_sensor_emulator.py
```

### 5. Запуск емулятора в контейнері

Команди для створення контейнера див. в `azure_iot_setup.ps1`

## Управління сервісами

### Зупинити всі сервіси (економія бюджету)

```powershell
powershell -ExecutionPolicy Bypass -File stop_all_services.ps1
```

### Запустити сервіси назад

```powershell
powershell -ExecutionPolicy Bypass -File start_all_services.ps1
```

### Видалити всі ресурси

```powershell
powershell -ExecutionPolicy Bypass -File delete_all_resources.ps1
```

## Тестування REST API

```powershell
# Отримати ключ
$KEY = az functionapp function keys list --name iot-sensors-processor --resource-group iot-project-rg --function-name get_sensor_history --query "default" --output tsv

# Запит даних
$URL = "https://iot-sensors-processor.azurewebsites.net/api/get_sensor_history?code=$KEY&sensor_id=photoresistor_1&limit=10"
Invoke-RestMethod -Uri $URL -Method Get | ConvertTo-Json -Depth 5
```

## Ресурси Azure

- **Resource Group:** `iot-project-rg`
- **Service Bus:** `iot-sensors-namespace`
- **Function App:** `iot-sensors-processor`
- **MySQL Server:** `iot-sql-flexible-server`
- **Container Registry:** `iotsensorsacr`

