from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # --- ▼▼▼▼▼ 진단 코드 추가 ▼▼▼▼▼ ---
    # 1. Secret에서 DATABASE_URL 값을 읽어옵니다.
    db_uri = os.environ.get('DATABASE_URL')
    
    # 2. 읽어온 주소를 서버 로그에 그대로 출력하여 어떤 포트를 사용하는지 확인합니다.
    print("==========================================================")
    print(f"✅ HUGGING FACE SECRET에서 읽어온 DATABASE_URL: {db_uri}")
    print("==========================================================")
    # --- ▲▲▲▲▲ 진단 코드 추가 끝 ▲▲▲▲▲ ---
    
    # Supabase URI의 'postgres://'를 SQLAlchemy가 인식하는 'postgresql://'로 변경합니다.
    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    db.init_app(app)

    # 블루프린트 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # AI 모델과 추천기 로딩
    from .emotion_engine import load_emotion_classifier
    from .recommender import Recommender
    app.emotion_classifier = load_emotion_classifier()
    app.recommender = Recommender()

    # DB 테이블 생성
    with app.app_context():
        from . import models
        db.create_all()
        
    return app