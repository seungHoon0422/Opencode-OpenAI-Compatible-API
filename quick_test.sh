#!/bin/bash
echo "🏥 헬스 체크 테스트..."
echo ""
curl -s http://localhost:8000/ | python -m json.tool
echo ""
echo "✅ 완료!"
