from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' 

def create_app():
    app = Flask(__name__, static_folder='templates/static')
    
    # 1. 설정
    app.config['SECRET_KEY'] = 'a-very-long-and-unique-secret-key-for-this-app'
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
    
    db_uri = os.environ.get('DATABASE_URL')
    if not db_uri:
        db_uri = "sqlite:///emotion.db"

    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # SQLAlchemy 엔진 옵션 설정 (pgbouncer Session 모드 호환)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_size": 15,  # pgbouncer의 pool_size와 일치시키거나 더 작게 설정
        "max_overflow": 5, # pool_size 초과 시 임시로 열 수 있는 연결 수
        "pool_recycle": 3600, # 1시간마다 연결 재활용 (오래된 연결 방지)
        "pool_pre_ping": True, # 연결 사용 전 유효성 검사
        "pool_timeout": 30, # 연결 풀에서 연결을 기다리는 최대 시간 (초)
        # pgbouncer Session 모드에서는 'rollback'이 기본값이므로 명시적으로 설정하지 않아도 됨
        # "pool_reset_on_return": 'rollback' 
    }

    # 로깅 설정
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 2. DB 초기화 및 테이블 생성
    db.init_app(app)
    with app.app_context():
        from . import models
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

   # 3. AI 모델 로딩
    from .emotion_engine import load_emotion_classifier
    # 앱 컨텍스트 안에서 모델을 로드하고 app 객체에 저장합니다.
    with app.app_context():
        app.emotion_classifier = load_emotion_classifier()
        


    # 5. 블루프린트 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app
