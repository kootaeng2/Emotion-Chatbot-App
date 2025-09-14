# src/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 1. 시크릿 키를 가장 먼저 설정합니다.
    app.config['SECRET_KEY'] = 'a-very-long-and-unique-secret-key-for-this-app'
    
    # 2. Supabase DB 설정
    db_uri = os.environ.get('DATABASE_URL')
    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 3. DB 초기화
    db.init_app(app)

    # 4. 블루프린트 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # 5. AI 모델과 추천기를 앱 생성 마지막 단계에서 로드하여 app 객체에 저장합니다.
    from .emotion_engine import load_emotion_classifier
    from .recommender import Recommender
    
    app.emotion_classifier = load_emotion_classifier()
    app.recommender = Recommender()

    # 6. 모든 것이 준비된 후 DB 테이블 생성
    with app.app_context():
        from . import models
        db.create_all()
        
    return app