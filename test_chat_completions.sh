#!/bin/bash
# /chat/completions 엔드포인트 테스트 스크립트

PORT=${1:-8000}
BASE_URL="http://localhost:${PORT}"

echo "================================================"
echo "🧪 Testing /chat/completions endpoint"
echo "📍 URL: ${BASE_URL}/chat/completions"
echo "================================================"
echo ""

# 테스트 1: 기본 요청
echo "📝 Test 1: 기본 채팅 요청"
echo "----------------------------------------"
curl -X POST "${BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.0-flash-exp",
    "messages": [
      {
        "role": "user",
        "content": "안녕하세요! 간단하게 자기소개를 해주세요."
      }
    ],
    "temperature": 0.7,
    "max_tokens": 500
  }' | python -m json.tool

echo ""
echo ""

# 테스트 2: 대화 맥락 포함
echo "📝 Test 2: 대화 맥락 포함"
echo "----------------------------------------"
curl -X POST "${BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.0-flash-exp",
    "messages": [
      {
        "role": "system",
        "content": "당신은 친절한 AI 어시스턴트입니다."
      },
      {
        "role": "user",
        "content": "Python으로 간단한 Hello World를 작성해주세요."
      }
    ],
    "temperature": 0.5,
    "max_tokens": 200
  }' | python -m json.tool

echo ""
echo ""

# 테스트 3: v1 엔드포인트
echo "📝 Test 3: /v1/chat/completions 엔드포인트"
echo "----------------------------------------"
curl -X POST "${BASE_URL}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.0-flash-exp",
    "messages": [
      {
        "role": "user",
        "content": "1+1은?"
      }
    ]
  }' | python -m json.tool

echo ""
echo "================================================"
echo "✅ 테스트 완료!"
echo "================================================"
