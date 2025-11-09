from flask import Flask, request, jsonify
from datetime import datetime
import os
import json

app = Flask(__name__)
from flask import Flask, request, jsonify
from datetime import datetime
import os
import json

app = Flask(__name__)

# DB connection (optional)
USE_DB = True
DB_CONN = None

def init_db_connection():
    global DB_CONN, USE_DB
    try:
        import psycopg2
        from psycopg2.extras import Json

        db_host = os.environ.get('TELEMETRY_DB_HOST', 'telemetry-postgres')
        db_port = int(os.environ.get('TELEMETRY_DB_PORT', 5432))
        db_name = os.environ.get('TELEMETRY_DB_NAME', 'telemetry')
        db_user = os.environ.get('TELEMETRY_DB_USER', 'telemetry')
        db_pass = os.environ.get('TELEMETRY_DB_PASSWORD', 'telemetry')

        conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_pass)
        conn.autocommit = True
        DB_CONN = conn
        # ensure table exists
        with conn.cursor() as cur:
            cur.execute(r"""
            CREATE TABLE IF NOT EXISTS telemetry (
                id SERIAL PRIMARY KEY,
                sensor_id INTEGER NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
                temperature NUMERIC(6,3),
                metadata JSONB
            );
            """)
        app.logger.info('Connected to telemetry DB')
    except Exception as e:
        USE_DB = False
        app.logger.warning(f'Could not connect to telemetry DB, falling back to in-memory store: {e}')

# In-memory fallback store
telemetry_store = {}


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "db": USE_DB}), 200


@app.route('/telemetry', methods=['GET'])
def list_telemetry():
    if USE_DB and DB_CONN:
        limit = int(request.args.get('limit', 100))
        with DB_CONN.cursor() as cur:
            cur.execute('SELECT sensor_id, timestamp, temperature, metadata FROM telemetry ORDER BY timestamp DESC LIMIT %s', (limit,))
            rows = cur.fetchall()
            results = []
            for r in rows:
                results.append({
                    'sensorId': r[0],
                    'timestamp': r[1].isoformat() if r[1] else None,
                    'temperature': float(r[2]) if r[2] is not None else None,
                    'metadata': r[3]
                })
            return jsonify(results), 200

    return jsonify(telemetry_store), 200


@app.route('/telemetry/<sensor_id>', methods=['GET'])
def get_telemetry(sensor_id):
    if USE_DB and DB_CONN:
        limit = int(request.args.get('limit', 100))
        with DB_CONN.cursor() as cur:
            cur.execute('SELECT sensor_id, timestamp, temperature, metadata FROM telemetry WHERE sensor_id = %s ORDER BY timestamp DESC LIMIT %s', (int(sensor_id), limit))
            rows = cur.fetchall()
            readings = []
            for r in rows:
                readings.append({
                    'sensorId': r[0],
                    'timestamp': r[1].isoformat() if r[1] else None,
                    'temperature': float(r[2]) if r[2] is not None else None,
                    'metadata': r[3]
                })
            return jsonify({'sensorId': sensor_id, 'readings': readings}), 200

    readings = telemetry_store.get(sensor_id, [])
    if not readings:
        return jsonify({"sensorId": sensor_id, "readings": []}), 200
    return jsonify({"sensorId": sensor_id, "readings": readings}), 200


@app.route('/telemetry', methods=['POST'])
def post_telemetry():
    data = request.get_json(force=True)
    sensor_id = int(data.get('sensorId', 0))
    value = data.get('value') if 'value' in data else data.get('temperature')
    timestamp = data.get('timestamp') or datetime.utcnow().isoformat()
    metadata = data.get('metadata')

    if value is None:
        return jsonify({'error': 'value (temperature) required'}), 400

    if USE_DB and DB_CONN:
        try:
            import psycopg2.extras
            with DB_CONN.cursor() as cur:
                cur.execute('INSERT INTO telemetry (sensor_id, timestamp, temperature, metadata) VALUES (%s, %s, %s, %s) RETURNING id', 
                          (sensor_id, timestamp, float(value), json.dumps(metadata) if metadata is not None else None))
                inserted = cur.fetchone()[0]
            return jsonify({'status': 'ok', 'id': inserted}), 201
        except Exception as e:
            app.logger.error(f'DB insert failed: {e}')
            return jsonify({'error': 'db insert failed'}), 500

    # fallback to in-memory
    entry = {
        "value": value,
        "timestamp": timestamp,
        "metadata": metadata
    }
    key = str(sensor_id)
    telemetry_store.setdefault(key, []).append(entry)
    return jsonify({"status": "ok", "entry": entry}), 201


if __name__ == '__main__':
    init_db_connection()
    app.run(host='0.0.0.0', port=8082)