# Opencode OpenAI-Compatible API

OpenAI API 형식을 사용하여 Gemini 모델을 호출할 수 있는 호환 레이어입니다.

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [설치 및 실행](#설치-및-실행)
- [API 엔드포인트](#api-엔드포인트)
- [상세 API 문서](#상세-api-문서)

## 🎯 개요

이 프로젝트는 OpenAI Chat Completions API와 호환되는 인터페이스를 제공하여 Gemini 모델을 사용할 수 있도록 합니다. LiteLLM을 활용하여 모델 호출을 중계합니다.

## ✨ 주요 기능

### 1. OpenAI 호환 API
- `/chat/completions` 및 `/v1/chat/completions` 엔드포인트 제공
- OpenAI SDK와 완벽하게 호환되는 요청/응답 형식

### 2. 스트리밍 지원
- Server-Sent Events (SSE)를 통한 실시간 스트리밍 응답
- `stream: true` 파라미터로 활성화

### 3. Tool Calls (Function Calling) 지원
- OpenAI Function Calling과 동일한 방식으로 도구 호출 가능
- `tools` 및 `tool_choice` 파라미터 지원

### 4. 모델 매핑
- 사용자 정의 모델명을 실제 Gemini 모델로 자동 매핑
- 설정 파일(`opencode.json`)을 통한 유연한 모델 관리

### 5. 상세한 로깅
- 요청/응답 내용의 상세한 로깅
- 디버깅을 위한 각 청크(chunk) 단위 출력

## 🚀 설치 및 실행

### 필수 요구사항
- Python 3.8+
- Gemini API 키

### 환경 변수 설정

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export GEMINI_API_BASE="https://your-gemini-endpoint.com/v1"
```

### 실행

```bash
# 개발 모드
python app.py

# 또는 run.sh 사용
./run.sh
```

## 📡 API 엔드포인트

### 1. Health Check
```
GET /health
```

서버 상태 확인

### 2. Chat Completions
```
POST /chat/completions
POST /v1/chat/completions
```

OpenAI Chat Completions API와 호환되는 채팅 완성 엔드포인트

**주요 파라미터:**
- `model` (string, required): 사용할 모델명
- `messages` (array, required): 대화 메시지 배열
- `temperature` (float, optional): 응답의 무작위성 (기본값: 0.7)
- `max_tokens` (integer, optional): 최대 토큰 수 (기본값: 1000)
- `stream` (boolean, optional): 스트리밍 모드 활성화 (기본값: false)
- `tools` (array, optional): Function calling용 도구 정의
- `tool_choice` (string/object, optional): 도구 선택 방식 (기본값: "auto")

## 📚 상세 문서

상세한 요청/응답 형식과 예제는 다음 문서를 참고하세요:

- [API 명세서 (API_SPEC.md)](./API_SPEC.md) - OpenAI 호환 API 상세 스펙
- [실제 예제 (EXAMPLES.md)](./EXAMPLES.md) - 실제 Request/Response 로그 기반 예제

## ⚙️ 설정 파일 (opencode.json)

`opencode.json` 파일을 통해 프로바이더와 모델을 설정할 수 있습니다.

### 설정 예제

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "KTDS Model": {
      "api": "https://generativelanguage.googleapis.com",
      "options": {
        "baseURL": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "apiKey": "your-api-key-here"
      },
      "models": {
        "gemini-3-flash-preview": {
          "name": "Gemini 3 Flash"
        }
      }
    },
    "Local Provider": {
      "api": "http://localhost:8000",
      "options": {
        "baseURL": "http://localhost:8000"
      },
      "models": {
        "local-model": {
          "name": "Local Model"
        }
      }
    }
  }
}
```

### 설정 구조

- **provider**: 프로바이더 목록을 정의
  - **api**: API 엔드포인트 URL
  - **options**: 추가 옵션
    - **baseURL**: 실제 호출될 Base URL
    - **apiKey**: API 키 (선택사항)
  - **models**: 사용 가능한 모델 정의
    - **모델 ID**: 내부적으로 사용할 모델 식별자
    - **name**: 표시될 모델 이름

## 🔧 아키텍처

### 주요 컴포넌트

1. **app/routes/chat.py**: Chat Completions API 엔드포인트 구현
   - 요청 파라미터 추출 및 검증
   - 모델명 해석 (resolve_model)
   - LiteLLM을 통한 Gemini API 호출
   - 스트리밍/비스트리밍 응답 처리
   - Tool calls 처리

2. **app/utils/model_resolver.py**: 모델명 매핑 로직
   - 사용자 정의 모델명 → 실제 Gemini 모델명 변환

3. **app/utils/formatter.py**: 응답 포맷팅
   - LiteLLM 응답을 OpenAI 형식으로 변환
   - 스트리밍 청크 포맷팅

4. **app/config.py**: 애플리케이션 설정
   - 환경 변수 관리
   - 모델 매핑 설정 로드

## 📝 호출 흐름

```
Client Request (OpenAI format)
    ↓
Chat Blueprint (/chat/completions)
    ↓
Request Validation & Parameter Extraction
    ↓
Model Name Resolution (model_resolver)
    ↓
LiteLLM Completion Call (Gemini API)
    ↓
Response Formatting (formatter)
    ↓
Client Response (OpenAI format)
```

### 상세 처리 단계

1. **요청 접수**: Flask Blueprint에서 POST 요청 수신
2. **파라미터 추출**: `model`, `messages`, `temperature`, `max_tokens`, `stream`, `tools` 등 추출
3. **모델 매핑**: `resolve_model()` 함수로 사용자 모델명을 실제 Gemini 모델로 변환
   - 예: `"local-model"` → `"openai/gemini-2.5-flash"`
4. **API 호출**: LiteLLM의 `completion()` 함수로 Gemini API 호출
5. **응답 처리**:
   - 비스트리밍: 전체 응답을 JSON으로 반환
   - 스트리밍: SSE 형식으로 청크 단위 스트리밍
6. **포맷팅**: OpenAI 응답 형식으로 변환하여 반환
   - 모델명을 사용자가 요청한 이름으로 되돌림

### 실제 처리 예제

```
📥 Client Request
   model: "local-model"
   
   ↓

🔄 Model Resolution
   "local-model" → "openai/gemini-2.5-flash"
   
   ↓

🔵 LiteLLM Call
   model: "openai/gemini-2.5-flash"
   api_base: "https://generativelanguage.googleapis.com/v1beta/openai/"
   
   ↓

🌊 Gemini API Response
   model: "gemini-2.5-flash"
   content: "저는 구글에서 훈련한 대규모 언어 모델..."
   
   ↓

📤 Client Response
   model: "local-model" (원래 요청 모델명으로 복원)
   content: "저는 구글에서 훈련한 대규모 언어 모델..."
```

## 🔍 로깅 기능

개발 및 디버깅을 위해 상세한 로깅을 제공합니다:

- ✅ 요청 본문 (긴 내용은 자동 요약)
- ✅ LiteLLM 파라미터
- ✅ API 키 정보 (마스킹 및 전체)
- ✅ 스트리밍 청크 단위 출력
- ✅ 최종 응답 내용
- ✅ 에러 발생 시 상세 스택 추적

### 로그 출력 예제

```
================================================================================
🚀 ENDPOINT CALLED: /chat/completions
================================================================================

📥 REQUEST BODY (요약):
{
  "model": "local-model",
  "messages": [...],
  "tools": [...],
  "stream": true
}

🔧 Tools: 12 tools (첫 번째만 전체 표시, 나머지는 name만)
  [0] question (전체 표시됨)
  [1] bash
  [2] read
  ...

================================================================================
🔵 LITELLM PARAMS (요약):
================================================================================
{
  "model": "openai/gemini-2.5-flash",
  "temperature": 0.7,
  "max_tokens": 1000,
  "api_base": "https://generativelanguage.googleapis.com/v1beta/openai/",
  "stream": true
}

🔑 FULL API KEY: AIzaSyAjvi-s0iKtQoFoS7yNRXJ4zZDkQqv6XJ8
🔑 API KEY from env: AIzaSyAjvi-s0iKtQoFoS7yNRXJ4zZDkQqv6XJ8
🔑 API KEY from config: AIzaSyAjvi-s0iKtQoFoS7yNRXJ4zZDkQqv6XJ8

🔵 Starting streaming response...

📦 Chunk #1 (RAW):
{
  "id": "ZQt6aeD2G5Oe0-kP9dOBgAE",
  "model": "gemini-2.5-flash",
  "choices": [...]
}

📤 Formatted Chunk #1:
data: {"id": "...", "model": "local-model", ...}

✅ Streaming completed: 2 total chunks
```

### 로그 특징

- **긴 문자열 자동 요약**: 10,000자 이상의 긴 content는 "... (총 N자)" 형태로 요약
- **Tools 요약**: 첫 번째 tool만 전체 표시, 나머지는 이름만 표시
- **API 키 마스킹**: 요약본에서는 마스킹, 디버깅용으로 전체 키도 출력
- **청크 단위 출력**: 스트리밍 모드에서 각 청크를 RAW 및 Formatted 형태로 출력
- **실시간 플러시**: 모든 로그는 `flush=True`로 즉시 출력

## 🛠️ 개발

### 테스트

```bash
# 빠른 테스트
./quick_test.sh

# Python 테스트 스크립트
python test_api.py

# cURL 테스트
./test_chat_completions.sh
```

## 📄 라이센스

프로젝트 라이센스 정보를 추가하세요.