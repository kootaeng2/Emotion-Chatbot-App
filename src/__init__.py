from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Redirect to auth.login if not logged in

def create_app():
    app = Flask(__name__)
    
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

    # 로깅 설정
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 2. DB 초기화 및 테이블 생성
    db.init_app(app)
    with app.app_context():
        from . import models
        db.create_all()

   # 3. AI 모델 로딩
    from .emotion_engine import load_emotion_classifier
    # 앱 컨텍스트 안에서 모델을 로드하고 app 객체에 저장합니다.
    with app.app_context():
        app.emotion_classifier = load_emotion_classifier()
        


    # 5. 블루프린트 등록
    # --- 💡 여기까지 수정 ---
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app
