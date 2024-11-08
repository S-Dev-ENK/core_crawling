FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]