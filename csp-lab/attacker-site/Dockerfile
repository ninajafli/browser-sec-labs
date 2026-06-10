FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY index.html /app/index.html
COPY evil.js /app/evil.js
COPY app.py /app/app.py

EXPOSE 9090

CMD ["python", "app.py"]
