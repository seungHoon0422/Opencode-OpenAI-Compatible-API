from flask import Flask
import os
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    print("\n" + "=" * 80, flush=True)
    print("🔧 Flask App Initialization", flush=True)
    print("=" * 80, flush=True)
    
    # 환경변수 로드 및 설정
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_api_base = os.getenv("GEMINI_API_BASE")
    
    app.config['GEMINI_API_KEY'] = gemini_api_key
    app.config['GEMINI_API_BASE'] = gemini_api_base
    
    print(f"🔑 API Key (FULL): {gemini_api_key}", flush=True)
    print(f"🔑 API Key Length: {len(gemini_api_key)}", flush=True)
    print(f"📡 API Base: {gemini_api_base}", flush=True)
    
    # 모델 매핑 정의 (2026년 1월 최신 모델)
    app.config['MODEL_MAPPING'] = {
        "local-model": "gemini-2.5-flash",
        "gpt-4": "gemini-2.5-pro",
        "gpt-3.5-turbo": "gemini-2.5-flash",
        "default": "gemini-2.5-flash"
    }
    
    print(f"📦 Model Mapping: {app.config['MODEL_MAPPING']}", flush=True)
    print("=" * 80 + "\n", flush=True)
    
    register_routes(app)
    return app

def register_routes(app):
    """Blueprint 라우트 등록"""
    from app.routes.chat import chat_bp
    from app.routes.health import health_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    
    print("✅ Routes registered", flush=True)

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # use_debugger=False, use_reloader=False로 설정하면 breakpoint()가 작동
    app.run(host="0.0.0.0", port=port, debug=True, use_debugger=False, use_reloader=False)
