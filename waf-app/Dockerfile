FROM python:3.11-slim
WORKDIR /app
COPY app.py .
RUN pip install flask requests redis
CMD ["python", "app.py"]
