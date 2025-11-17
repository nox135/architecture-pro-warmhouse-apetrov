from flask import Flask, request, jsonify
import random

app = Flask(__name__)

def get_location_by_sensor(sensor_id: str) -> str:
    return {
        "1": "Living Room",
        "2": "Bedroom",
        "3": "Kitchen"
    }.get(sensor_id, "Unknown")

@app.route('/temperature', methods=['GET'])
def get_temperature():
    # Получаем query-параметры
    location = request.args.get('location', "")
    sensor_id = request.args.get('sensorId', "")

    # Если location не указан, используем sensor_id
    if location == "":
        if sensor_id == "1":
            location = "Living Room"
        elif sensor_id == "2":
            location = "Bedroom"
        elif sensor_id == "3":
            location = "Kitchen"
        else:
            location = "Unknown"

    # Если sensor_id не указан, используем location
    if sensor_id == "":
        if location == "Living Room":
            sensor_id = "1"
        elif location == "Bedroom":
            sensor_id = "2"
        elif location == "Kitchen":
            sensor_id = "3"
        else:
            sensor_id = "0"

    # Генерируем случайную температуру
    temperature = round(random.uniform(15, 30), 2)

    return jsonify({
        "sensorId": sensor_id,
        "location": location,
        "value": temperature
    })

@app.route('/temperature/<sensor_id>', methods=['GET'])
def get_temperature_by_id(sensor_id):
    location = get_location_by_sensor(sensor_id)
    temperature = round(random.uniform(18, 26), 2)

    return jsonify({
        "sensorId": sensor_id,
        "location": location,
        "value": temperature
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
