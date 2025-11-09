FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY telemetry.py ./
EXPOSE 8082
CMD ["python", "telemetry.py"]
