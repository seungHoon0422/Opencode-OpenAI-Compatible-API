# 실제 Request/Response 예제

이 문서는 실제 API 호출 로그를 바탕으로 작성된 Request/Response 예제입니다.

## 📋 목차

- [설정 파일 (opencode.json)](#설정-파일-opencodejson)
- [스트리밍 요청/응답 예제](#스트리밍-요청응답-예제)
- [Tool Calls 포함 요청](#tool-calls-포함-요청)
- [모델 매핑 예제](#모델-매핑-예제)
- [로그 분석](#로그-분석)

---

## ⚙️ 설정 파일 (opencode.json)

### 파일 구조

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

### 설정 설명

| 필드 | 설명 |
|------|------|
| `$schema` | 설정 스키마 URL |
| `provider` | 프로바이더 목록 |
| `provider.{name}.api` | API 엔드포인트 |
| `provider.{name}.options.baseURL` | 실제 호출될 Base URL |
| `provider.{name}.options.apiKey` | API 키 (선택사항) |
| `provider.{name}.models` | 사용 가능한 모델 목록 |

---

## 🌊 스트리밍 요청/응답 예제

### Request

**엔드포인트:** `POST /chat/completions`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "model": "local-model",
  "messages": [
    {
      "role": "system",
      "content": "You are opencode, an interactive CLI tool that helps users with software engineering tasks."
    },
    {
      "role": "user",
      "content": "너에 대해서 소개해줘"
    }
  ],
  "stream": true,
  "stream_options": {
    "include_usage": true
  }
}
```

### LiteLLM 변환 파라미터

요청이 LiteLLM으로 전달될 때 다음과 같이 변환됩니다:

```json
{
  "model": "openai/gemini-2.5-flash",
  "messages": [
    {
      "role": "system",
      "content": "You are opencode, an interactive CLI tool that helps users with software engineering tasks."
    },
    {
      "role": "user",
      "content": "너에 대해서 소개해줘"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "api_key": "AIzaSyAjvi-s0iKtQoFoS7yNRXJ4zZDkQqv6XJ8",
  "api_base": "https://generativelanguage.googleapis.com/v1beta/openai/",
  "stream": true,
  "custom_llm_provider": "openai"
}
```

### Response Stream

**Status Code:** `200 OK`

**Content-Type:** `text/event-stream`

#### Chunk #1

```json
data: {
  "id": "ZQt6aeD2G5Oe0-kP9dOBgAE",
  "object": "chat.completion.chunk",
  "created": 1769605989,
  "model": "local-model",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "저는 구글에서 훈련한 대규모 언어 모델이며, 소프트웨어 엔지니어링 작업을 지원합니다."
      },
      "finish_reason": null
    }
  ]
}
```

#### Chunk #2 (Final)

```json
data: {
  "id": "ZQt6aeD2G5Oe0-kP9dOBgAE",
  "object": "chat.completion.chunk",
  "created": 1769605989,
  "model": "local-model",
  "choices": [
    {
      "index": 0,
      "delta": {},
      "finish_reason": "stop"
    }
  ]
}
```

#### Stream End

```
data: [DONE]
```

### 응답 분석

- **총 청크 수**: 2개
- **첫 번째 청크**: `role`과 `content` 포함
- **마지막 청크**: 빈 `delta`와 `finish_reason: "stop"` 포함
- **응답 시간**: 약 1초

---

## 🛠️ Tool Calls 포함 요청

### Request with Tools

```json
{
  "model": "local-model",
  "messages": [
    {
      "role": "system",
      "content": "You are opencode, an interactive CLI tool that helps users with software engineering tasks."
    },
    {
      "role": "user",
      "content": "너에 대해서 소개해줘"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "question",
        "description": "Use this tool when you need to ask the user questions during execution.",
        "parameters": {
          "$schema": "https://json-schema.org/draft/2020-12/schema",
          "type": "object",
          "properties": {
            "questions": {
              "description": "Questions to ask",
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "question": {
                    "description": "Complete question",
                    "type": "string"
                  },
                  "header": {
                    "description": "Very short label (max 30 chars)",
                    "type": "string"
                  },
                  "options": {
                    "description": "Available choices",
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "label": {
                          "description": "Display text (1-5 words, concise)",
                          "type": "string"
                        },
                        "description": {
                          "description": "Explanation of choice",
                          "type": "string"
                        }
                      },
                      "required": ["label", "description"]
                    }
                  },
                  "multiple": {
                    "description": "Allow selecting multiple choices",
                    "type": "boolean"
                  }
                },
                "required": ["question", "header", "options"]
              }
            }
          },
          "required": ["questions"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "bash"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "read"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "glob"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "grep"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "edit"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "write"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "task"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "webfetch"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "todowrite"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "todoread"
      }
    },
    {
      "type": "function",
      "function": {
        "name": "skill"
      }
    }
  ],
  "tool_choice": "auto",
  "stream": true,
  "stream_options": {
    "include_usage": true
  }
}
```

### Tools 목록

이 요청에는 **12개의 도구**가 포함되어 있습니다:

| # | Tool Name | 설명 |
|---|-----------|------|
| 0 | `question` | 사용자에게 질문하기 (복잡한 파라미터 스키마 포함) |
| 1 | `bash` | 쉘 명령 실행 |
| 2 | `read` | 파일 읽기 |
| 3 | `glob` | 파일 검색 (glob 패턴) |
| 4 | `grep` | 텍스트 검색 |
| 5 | `edit` | 파일 편집 |
| 6 | `write` | 파일 쓰기 |
| 7 | `task` | 작업 관리 |
| 8 | `webfetch` | 웹 데이터 가져오기 |
| 9 | `todowrite` | TODO 작성 |
| 10 | `todoread` | TODO 읽기 |
| 11 | `skill` | 스킬 관리 |

### 로그 출력

```
🔧 Tools: 12 tools (첫 번째만 전체 표시, 나머지는 name만)
  [0] question (전체 표시됨)
  [1] bash
  [2] read
  [3] glob
  [4] grep
  [5] edit
  [6] write
  [7] task
  [8] webfetch
  [9] todowrite
  [10] todoread
  [11] skill
```

---

## 🔄 모델 매핑 예제

### 매핑 흐름

```
Client Request                LiteLLM Params               Gemini API
┌─────────────────┐          ┌──────────────────────┐     ┌─────────────────┐
│ model:          │          │ model:               │     │                 │
│ "local-model"   │  ─────>  │ "openai/gemini-2.5-  │ ──> │ Gemini API Call │
│                 │          │  flash"              │     │                 │
└─────────────────┘          └──────────────────────┘     └─────────────────┘
```

### 상세 매핑 정보

1. **클라이언트 요청 모델**: `"local-model"`
2. **해석된 모델**: `"openai/gemini-2.5-flash"`
3. **프로바이더**: `"openai"` (custom_llm_provider)
4. **API Base**: `"https://generativelanguage.googleapis.com/v1beta/openai/"`

### 매핑 로직

```python
# app/utils/model_resolver.py
def resolve_model(user_model, model_mapping):
    """
    사용자 모델명을 실제 LiteLLM 모델명으로 변환
    
    예:
    - "local-model" -> "openai/gemini-2.5-flash"
    - "gpt-4" -> "gemini-1.5-pro"
    """
    return model_mapping.get(user_model, "default-model")
```

---

## 📊 로그 분석

### Request 처리 과정

```
================================================================================
🚀 ENDPOINT CALLED: /chat/completions
================================================================================

📥 REQUEST BODY (요약):
  - model: "local-model"
  - messages: 2개 (system, user)
  - tools: 12개
  - stream: true

🔧 Tools: 12 tools (첫 번째만 전체 표시, 나머지는 name만)

================================================================================
🔵 LITELLM PARAMS (요약):
================================================================================
  - model: "openai/gemini-2.5-flash"
  - temperature: 0.7
  - max_tokens: 1000
  - api_base: "https://generativelanguage.googleapis.com/v1beta/openai/"
  - stream: true

🔑 FULL API KEY: AIzaSyAjvi-s0iKtQoFoS7yNRXJ4zZDkQqv6XJ8
🔑 API KEY from env: AIzaSyAjvi-s0iKtQoFoS7yNRXJ4zZDkQqv6XJ8
🔑 API KEY from config: AIzaSyAjvi-s0iKtQoFoS7yNRXJ4zZDkQqv6XJ8

🔵 Starting streaming response...

📦 Chunk #1 (RAW):
  - id: "ZQt6aeD2G5Oe0-kP9dOBgAE"
  - model: "gemini-2.5-flash"
  - role: "assistant"
  - content: "저는 구글에서 훈련한 대규모 언어 모델이며, 소프트웨어 엔지니어링 작업을 지원합니다."

📤 Formatted Chunk #1:
  - model 변환: "gemini-2.5-flash" -> "local-model"
  - content 인코딩: UTF-8 이스케이프 시퀀스로 변환

📦 Chunk #2 (RAW):
  - finish_reason: "stop"
  - delta: {} (빈 객체)

✅ Streaming completed: 2 total chunks
```

### 처리 시간

| 단계 | 시간 |
|------|------|
| Request 수신 | 22:13:08 |
| LiteLLM 호출 | 22:13:08 |
| 첫 번째 청크 | 22:13:09 |
| 스트리밍 완료 | 22:13:09 |
| **총 소요 시간** | **약 1초** |

### Response 크기

- **Chunk #1**: ~350 bytes
- **Chunk #2**: ~180 bytes
- **총 크기**: ~530 bytes

---

## 🔍 디버깅 정보

### API 키 처리

로그에서 API 키가 세 가지 형태로 출력됩니다:

1. **마스킹된 키**: `AIzaSyAjvi...6XJ8`
2. **전체 키**: `AIzaSyAjvi-s0iKtQoFoS7yNRXJ4zZDkQqv6XJ8`
3. **환경 변수 키**: 환경 변수에서 읽어온 키
4. **설정 파일 키**: config에서 읽어온 키

### 긴 내용 요약

요청 본문의 긴 문자열은 자동으로 요약됩니다:

```
"content": "You are opencode, an interactive CLI tool... (총 10070자)"
```

### Tool 정보 요약

- **첫 번째 도구**: 전체 스키마 표시
- **나머지 도구**: 이름만 표시

---

## 💡 Best Practices

### 1. 스트리밍 모드 사용

빠른 응답을 위해 `stream: true` 사용:

```json
{
  "stream": true,
  "stream_options": {
    "include_usage": true
  }
}
```

### 2. 적절한 max_tokens 설정

응답 길이를 제한하여 비용 절감:

```json
{
  "max_tokens": 1000
}
```

### 3. Tool Choice 최적화

필요한 경우에만 특정 도구 강제 사용:

```json
{
  "tool_choice": "auto"  // 또는 {"type": "function", "function": {"name": "specific_tool"}}
}
```

### 4. 모델 선택

용도에 맞는 모델 선택:

- **빠른 응답**: `gemini-2.5-flash`
- **복잡한 작업**: `gemini-1.5-pro`

---

## 📈 성능 측정

### 응답 시간 분석

```
요청 시작 ────> LiteLLM 호출 ────> 첫 청크 ────> 완료
   |               |                |            |
 0ms            50ms            1000ms       1100ms
```

### 토큰 사용량 (예상)

- **Prompt Tokens**: ~150
- **Completion Tokens**: ~20
- **Total Tokens**: ~170

---

## 🧪 테스트 스크립트

### Python 테스트

```python
import requests
import json

url = "http://localhost:8000/chat/completions"
headers = {"Content-Type": "application/json"}

data = {
    "model": "local-model",
    "messages": [
        {"role": "user", "content": "너에 대해서 소개해줘"}
    ],
    "stream": True
}

response = requests.post(url, headers=headers, json=data, stream=True)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data_str = line_str[6:]
            if data_str != '[DONE]':
                chunk = json.loads(data_str)
                content = chunk['choices'][0]['delta'].get('content', '')
                if content:
                    print(content, end='', flush=True)
```

### cURL 테스트

```bash
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-model",
    "messages": [
      {"role": "user", "content": "너에 대해서 소개해줘"}
    ],
    "stream": true
  }' \
  --no-buffer
```

---

## 📝 주요 특징 요약

### ✅ 성공 케이스

1. **모델 매핑**: `local-model` → `openai/gemini-2.5-flash` 정상 변환
2. **스트리밍**: 2개의 청크로 정상 응답
3. **Tool 전달**: 12개의 도구가 정상적으로 LiteLLM으로 전달
4. **한글 지원**: UTF-8 인코딩으로 정상 처리

### 🔧 개선 가능 사항

1. **응답 시간**: 추가 최적화 가능
2. **토큰 사용량**: usage 정보 포함 옵션 활성화
3. **에러 처리**: 더 상세한 에러 메시지 제공
4. **캐싱**: 반복 요청에 대한 캐싱 고려

---

## 📞 문의

실제 사용 중 문제나 질문이 있으시면 이슈를 생성해주세요.
