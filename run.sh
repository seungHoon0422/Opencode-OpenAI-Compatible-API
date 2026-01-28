#!/bin/bash
# Flask 서버 실행 스크립트

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 포트 설정 (기본값: 8000)
PORT=${1:-8000}

echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🚀 OpenCode API 서버 시작${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 환경 변수 확인
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  경고: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다${NC}"
    echo -e "${YELLOW}   하드코딩된 기본값이 사용됩니다${NC}"
    echo ""
fi

# Flask 환경 변수 설정
# Flask는 app.py를 자동으로 감지하므로 FLASK_APP 설정 불필요
export FLASK_ENV=development

echo -e "📍 URL: ${GREEN}http://localhost:${PORT}${NC}"
echo -e "🔧 Mode: ${GREEN}Development${NC}"
echo -e "🐛 Debug: ${GREEN}Enabled${NC}"
echo ""
echo -e "${BLUE}================================================${NC}"
echo ""

# Flask 서버 실행
flask run --host 0.0.0.0 --port "$PORT" --debug
