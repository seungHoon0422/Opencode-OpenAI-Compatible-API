#!/usr/bin/env python3
"""OpenCode API 테스트 스크립트"""

import requests
import json
import sys

# 기본 포트 (명령줄 인자로 변경 가능)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
BASE_URL = f"http://localhost:{PORT}"


def test_health_check():
    """헬스 체크 테스트"""
    print("🔍 헬스 체크 테스트...")
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Status: {response.status_code}")
    print(f"📦 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")


def test_list_models():
    """모델 목록 테스트"""
    print("🔍 모델 목록 테스트...")
    response = requests.get(f"{BASE_URL}/api/models")
    print(f"✅ Status: {response.status_code}")
    print(f"📦 Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")


def test_chat():
    """채팅 API 테스트"""
    print("🔍 채팅 API 테스트...")
    
    payload = {
        "messages": [
            {"role": "user", "content": "안녕하세요! 간단하게 자기소개를 해주세요."}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload
    )
    
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    
    if result.get("success"):
        print(f"🤖 AI 응답: {result['response']}")
        print(f"📊 토큰 사용량: {result['usage']}\n")
    else:
        print(f"❌ 에러: {result.get('error')}\n")


def test_chat_with_conversation():
    """대화 맥락을 포함한 채팅 테스트"""
    print("🔍 대화 맥락 테스트...")
    
    payload = {
        "messages": [
            {"role": "user", "content": "Python으로 간단한 계산기를 만들어주세요"},
            {"role": "assistant", "content": "네, 간단한 계산기 클래스를 만들어드리겠습니다..."},
            {"role": "user", "content": "이제 테스트 코드도 추가해주세요"}
        ],
        "temperature": 0.5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json=payload
    )
    
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    
    if result.get("success"):
        print(f"🤖 AI 응답: {result['response'][:200]}...")
        print(f"📊 토큰 사용량: {result['usage']}\n")
    else:
        print(f"❌ 에러: {result.get('error')}\n")


if __name__ == "__main__":
    print("=" * 60)
    print(f"🚀 OpenCode API 테스트 시작 (포트: {PORT})")
    print(f"📍 Base URL: {BASE_URL}")
    print("=" * 60 + "\n")
    
    try:
        test_health_check()
        test_list_models()
        test_chat()
        test_chat_with_conversation()
        
        print("=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 서버에 연결할 수 없습니다. Flask 서버가 {BASE_URL}에서 실행 중인지 확인하세요.")
        print(f"   실행 방법: flask run --port {PORT}")
        print(f"   또는: python app.py {PORT}")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
