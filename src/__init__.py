from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 1. 앱 기본 설정 (DB 경로 등)
    db_path = '/data/database.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    
    # 2. DB 초기화
    db.init_app(app)

    # 3. 블루프린트 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # --- ▼▼▼▼▼ 핵심 수정 부분 ▼▼▼▼▼ ---
    # 4. 무거운 AI 모델과 추천기를 앱 생성 마지막 단계에서 로드합니다.
    #    그리고 Flask의 app 객체에 저장하여 어디서든 안전하게 접근할 수 있게 합니다.
    from .emotion_engine import load_emotion_classifier
    from .recommender import Recommender
    
    app.emotion_classifier = load_emotion_classifier()
    app.recommender = Recommender()
    # --- ▲▲▲▲▲ 핵심 수정 부분 끝 ▲▲▲▲▲ ---

    # 5. 모든 것이 준비된 후 DB 테이블 생성
    with app.app_context():
        from . import models
        db.create_all()
        
    return app