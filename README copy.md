# OpenCode API

Flask 기반의 Gemini API 프록시 서버

## 설치

```bash
# 의존성 설치
pip install -e .

# 또는 uv 사용
uv pip install -e .
```

## 환경 변수 설정

```bash
export GEMINI_API_KEY="your-api-key-here"
```

## 실행

### 방법 1: Flask CLI 사용 (권장)
```bash
# 기본 포트 5000 (macOS에서 AirPlay와 충돌 가능)
flask run

# 포트 지정
flask run --port 8000

# 외부 접속 허용
flask run --host 0.0.0.0 --port 8000

# 디버그 모드
flask run --debug --port 8000
```

### 방법 2: Python 직접 실행
```bash
# 기본 포트 8000
python app.py

# 포트 지정
python app.py 9000
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 환경 변수 설정 (선택사항)
```bash
# Flask 앱은 app.py를 자동으로 감지합니다

# 디버그 모드
export FLASK_DEBUG=1

# 포트 설정
export FLASK_RUN_PORT=8000
export FLASK_RUN_HOST=0.0.0.0
```

## API 엔드포인트

### 1. 헬스 체크
```bash
curl http://localhost:8000/
```

### 2. 채팅 완성
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "안녕하세요! 간단한 Python 함수를 작성해주세요."}
    ],
    "model": "gemini/gemini-2.0-flash-exp",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### 3. 모델 목록
```bash
curl http://localhost:8000/api/models
```

## 요청 예제 (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "messages": [
            {"role": "user", "content": "Python으로 피보나치 수열을 구현해주세요"}
        ],
        "temperature": 0.7
    }
)

print(response.json())
```

## 포트 충돌 문제 해결

macOS에서 포트 5000이 AirPlay Receiver에 사용되는 경우:

### 옵션 1: 다른 포트 사용 (권장)
```bash
flask run --port 8000
```

### 옵션 2: AirPlay Receiver 비활성화
시스템 설정 → 일반 → AirDrop & Handoff → AirPlay Receiver 끄기

## 응답 형식

### 성공 응답
```json
{
  "success": true,
  "response": "AI 모델의 응답 텍스트",
  "model": "gemini-2.0-flash-exp",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### 에러 응답
```json
{
  "success": false,
  "error": "에러 메시지"
}
```
