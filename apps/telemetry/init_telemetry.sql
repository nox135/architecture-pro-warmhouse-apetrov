-- Initialize telemetry database
CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    temperature NUMERIC(6,3),
    metadata JSONB
);
