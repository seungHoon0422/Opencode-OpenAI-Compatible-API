from flask import Flask
from .config import Config
import logging

def create_app():
    app = Flask(__name__)
    
    # 설정 로드
    app.config.from_object(Config)
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 블루프린트 등록
    from .routes.health import health_bp
    from .routes.chat import chat_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    
    return app
