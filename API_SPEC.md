# API 명세서

## 📋 목차

- [인증](#인증)
- [Chat Completions API](#chat-completions-api)
  - [기본 요청](#기본-요청)
  - [스트리밍 요청](#스트리밍-요청)
  - [Function Calling](#function-calling)
- [에러 처리](#에러-처리)

---

## 🔐 인증

현재 버전은 API 키 인증을 사용하지 않습니다. 모든 요청은 서버 환경 변수에 설정된 Gemini API 키를 사용합니다.

---

## 💬 Chat Completions API

### 엔드포인트

```
POST /chat/completions
POST /v1/chat/completions
```

OpenAI Chat Completions API와 완벽히 호환되는 채팅 완성 엔드포인트입니다.

---

### 기본 요청

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body Parameters:**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `model` | string | ✅ | - | 사용할 모델명 |
| `messages` | array | ✅ | - | 대화 메시지 배열 |
| `temperature` | float | ❌ | 0.7 | 응답의 무작위성 (0.0 ~ 2.0) |
| `max_tokens` | integer | ❌ | 1000 | 생성할 최대 토큰 수 |
| `stream` | boolean | ❌ | false | 스트리밍 모드 활성화 |
| `top_p` | float | ❌ | 1.0 | 핵심 샘플링 파라미터 |
| `n` | integer | ❌ | 1 | 생성할 응답 개수 |
| `stop` | string/array | ❌ | null | 생성 중단 시퀀스 |
| `presence_penalty` | float | ❌ | 0 | 새로운 주제 패널티 (-2.0 ~ 2.0) |
| `frequency_penalty` | float | ❌ | 0 | 반복 패널티 (-2.0 ~ 2.0) |

**Messages 형식:**

```json
{
  "role": "user|assistant|system",
  "content": "메시지 내용"
}
```

#### Request Example

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello! How are you?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

#### Response

**Status Code:** `200 OK`

**Body:**

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'm doing well, thank you for asking. How can I assist you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 18,
    "total_tokens": 37
  }
}
```

**Response Fields:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | 고유한 요청 ID |
| `object` | string | 객체 타입 (항상 "chat.completion") |
| `created` | integer | Unix 타임스탬프 |
| `model` | string | 사용된 모델명 |
| `choices` | array | 생성된 응답 배열 |
| `choices[].index` | integer | 선택지 인덱스 |
| `choices[].message` | object | 응답 메시지 |
| `choices[].message.role` | string | 역할 (항상 "assistant") |
| `choices[].message.content` | string | 응답 내용 |
| `choices[].finish_reason` | string | 종료 이유 ("stop", "length", "tool_calls") |
| `usage` | object | 토큰 사용량 정보 |
| `usage.prompt_tokens` | integer | 입력 토큰 수 |
| `usage.completion_tokens` | integer | 출력 토큰 수 |
| `usage.total_tokens` | integer | 총 토큰 수 |

---

### 스트리밍 요청

Server-Sent Events (SSE)를 사용하여 실시간으로 응답을 스트리밍합니다.

#### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "Write a short story about a robot."
    }
  ],
  "stream": true
}
```

#### Response

**Status Code:** `200 OK`

**Content-Type:** `text/event-stream`

**스트림 형식:**

```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"Once"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{"content":" upon"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{"content":" a"},"finish_reason":null}]}

...

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

**Chunk 구조:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | 고유한 요청 ID |
| `object` | string | 객체 타입 (항상 "chat.completion.chunk") |
| `created` | integer | Unix 타임스탬프 |
| `model` | string | 사용된 모델명 |
| `choices[].index` | integer | 선택지 인덱스 |
| `choices[].delta` | object | 증분 메시지 |
| `choices[].delta.role` | string | 역할 (첫 청크에만 포함) |
| `choices[].delta.content` | string | 증분 콘텐츠 |
| `choices[].finish_reason` | string/null | 종료 이유 (마지막 청크에만 포함) |

**스트림 종료:**
- 마지막 청크는 `finish_reason`이 포함됨
- 최종 메시지로 `data: [DONE]` 전송

---

### Function Calling (Tool Calls)

모델이 외부 함수를 호출하도록 할 수 있습니다.

#### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "What's the weather like in Seoul?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and country, e.g. Seoul, South Korea"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "The temperature unit to use"
            }
          },
          "required": ["location"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

**Tool Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `tools` | array | ❌ | 사용 가능한 도구 목록 |
| `tools[].type` | string | ✅ | 도구 타입 (항상 "function") |
| `tools[].function` | object | ✅ | 함수 정의 |
| `tools[].function.name` | string | ✅ | 함수명 |
| `tools[].function.description` | string | ✅ | 함수 설명 |
| `tools[].function.parameters` | object | ✅ | JSON Schema 형식의 파라미터 정의 |
| `tool_choice` | string/object | ❌ | 도구 선택 방식 ("auto", "none", 또는 특정 함수 지정) |

#### Response (Tool Call)

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"Seoul, South Korea\", \"unit\": \"celsius\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 82,
    "completion_tokens": 17,
    "total_tokens": 99
  }
}
```

**Tool Call Fields:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `tool_calls` | array | 호출할 도구 목록 |
| `tool_calls[].id` | string | 도구 호출 ID |
| `tool_calls[].type` | string | 도구 타입 (항상 "function") |
| `tool_calls[].function.name` | string | 호출할 함수명 |
| `tool_calls[].function.arguments` | string | JSON 문자열 형식의 함수 인자 |

#### Request (Tool Call Result)

도구 실행 결과를 다시 모델에 전달:

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "What's the weather like in Seoul?"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_abc123",
          "type": "function",
          "function": {
            "name": "get_weather",
            "arguments": "{\"location\": \"Seoul, South Korea\", \"unit\": \"celsius\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_abc123",
      "content": "{\"temperature\": 22, \"condition\": \"sunny\"}"
    }
  ]
}
```

#### Response (Final Answer)

```json
{
  "id": "chatcmpl-abc456",
  "object": "chat.completion",
  "created": 1677858252,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The weather in Seoul is currently sunny with a temperature of 22°C."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 120,
    "completion_tokens": 18,
    "total_tokens": 138
  }
}
```

---

### Function Calling with Streaming

스트리밍 모드에서도 Function Calling을 사용할 수 있습니다.

#### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "What's the weather in Tokyo and Seoul?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and country"
            }
          },
          "required": ["location"]
        }
      }
    }
  ],
  "stream": true
}
```

#### Response Stream

```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{"role":"assistant","tool_calls":[{"index":0,"id":"call_abc123","type":"function","function":{"name":"get_weather","arguments":""}}]},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{"tool_calls":[{"index":0,"function":{"arguments":"{\""}}]},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{"tool_calls":[{"index":0,"function":{"arguments":"location"}}]},"finish_reason":null}]}

...

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1677858242,"model":"gpt-4","choices":[{"index":0,"delta":{},"finish_reason":"tool_calls"}]}

data: [DONE]
```

**스트리밍 Tool Call 특징:**
- `tool_calls` 배열의 각 요소는 `index`로 식별
- `function.arguments`는 청크 단위로 점진적으로 전달
- 첫 청크에서 함수명(`name`)과 ID 제공
- 이후 청크에서는 `arguments` 문자열의 일부분만 전달
- 마지막 청크에서 `finish_reason: "tool_calls"` 설정

---

## ⚠️ 에러 처리

### 에러 응답 형식

모든 에러는 OpenAI 표준 형식으로 반환됩니다.

```json
{
  "error": {
    "message": "에러 메시지",
    "type": "error_type",
    "code": 400
  }
}
```

### 주요 에러 코드

| HTTP 상태 코드 | 에러 타입 | 설명 |
|---------------|----------|------|
| 400 | `invalid_request_error` | 잘못된 요청 형식 또는 필수 파라미터 누락 |
| 401 | `authentication_error` | 인증 실패 |
| 429 | `rate_limit_error` | API 호출 한도 초과 |
| 500 | `api_error` | 서버 내부 오류 |
| 503 | `service_unavailable` | 서비스 일시적으로 사용 불가 |

### 에러 예제

#### 400 Bad Request - 필수 파라미터 누락

**Request:**
```json
{
  "model": "gpt-4"
}
```

**Response:**
```json
{
  "error": {
    "message": "Invalid request",
    "type": "invalid_request_error",
    "code": 400
  }
}
```

#### 429 Rate Limit Error

**Response:**
```json
{
  "error": {
    "message": "Rate limit exceeded. Please retry after some time.",
    "type": "rate_limit_error",
    "code": 429
  }
}
```

#### 500 Internal Server Error

**Response:**
```json
{
  "error": {
    "message": "An unexpected error occurred while processing your request.",
    "type": "api_error",
    "code": 500
  }
}
```

---

## 📝 사용 예제

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"  # API 키는 사용되지 않지만 SDK에서 필수
)

# 기본 요청
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)

# 스트리밍 요청
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a poem."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### cURL

```bash
# 기본 요청
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'

# 스트리밍 요청
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Write a story."}
    ],
    "stream": true
  }' \
  --no-buffer
```

### JavaScript (Node.js)

```javascript
const OpenAI = require('openai');

const client = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'dummy'
});

async function main() {
  // 기본 요청
  const response = await client.chat.completions.create({
    model: 'gpt-4',
    messages: [
      { role: 'user', content: 'Hello!' }
    ]
  });
  console.log(response.choices[0].message.content);

  // 스트리밍 요청
  const stream = await client.chat.completions.create({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Write a poem.' }],
    stream: true
  });

  for await (const chunk of stream) {
    process.stdout.write(chunk.choices[0]?.delta?.content || '');
  }
}

main();
```

---

## 🔧 추가 정보

### 지원되는 메시지 역할 (Roles)

| 역할 | 설명 |
|-----|------|
| `system` | 시스템 프롬프트 (모델의 행동 정의) |
| `user` | 사용자 메시지 |
| `assistant` | 어시스턴트(모델) 응답 |
| `tool` | 도구 실행 결과 (Function Calling 시) |

### Finish Reasons

| 값 | 설명 |
|----|------|
| `stop` | 모델이 자연스럽게 응답 완료 |
| `length` | max_tokens 제한에 도달 |
| `tool_calls` | 모델이 함수 호출을 요청 |
| `content_filter` | 콘텐츠 필터에 의해 중단 |

### 모델 매핑

사용자가 요청한 모델명은 `opencode.json` 설정 파일에 정의된 매핑에 따라 실제 Gemini 모델로 변환됩니다.

예:
- `gpt-4` → `gemini-1.5-pro`
- `gpt-3.5-turbo` → `gemini-1.5-flash`

---

## 📞 문의 및 지원

API 사용 중 문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.
