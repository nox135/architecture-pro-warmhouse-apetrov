FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY devices.py ./
EXPOSE 8083
CMD ["python", "devices.py"]
