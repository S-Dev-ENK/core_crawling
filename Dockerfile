FROM python:3.12.4

# 시스템 패키지 설치 및 캐시 정리
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Chrome 관련 환경 변수 설정
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/lib/chromium/
ENV CHROMIUM_FLAGS="--no-sandbox --headless --disable-gpu --disable-software-rasterizer --disable-dev-shm-usage"

# 필요한 파일 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8001

# 애플리케이션 실행 (재시작 정책 추가)
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--workers", "4", "--timeout-keep-alive", "300"]