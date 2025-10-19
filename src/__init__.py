from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    
    # 1. 시크릿 키 설정 (변경 없음)
    app.config['SECRET_KEY'] = 'a-very-long-and-unique-secret-key-for-this-app'
    
    # 2. 세션 쿠키 설정 (변경 없음)
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
    
    
    # 3. Supabase DB 설정 (변경 없음)
    db_uri = os.environ.get('DATABASE_URL')
    if not db_uri:
        # If DATABASE_URL is not set, use a local SQLite database.
        db_uri = f"sqlite:///{os.path.join(app.instance_path, 'emotion.db')}"
        os.makedirs(app.instance_path, exist_ok=True)

    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 4. DB 초기화 (변경 없음)
    db.init_app(app)

    # 5. 블루프린트 등록 (변경 없음)
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # 6. AI 모델 로더 (Recommender 관련 코드 삭제)
    from .emotion_engine import load_emotion_classifier
    # from .recommender import Recommender  <- 이 줄 삭제
    
    app.emotion_classifier = load_emotion_classifier()
    # app.recommender = Recommender()      <- 이 줄 삭제

    # 7. DB 테이블 생성 (주석 해제)
    # --- 아래 3줄의 주석을 반드시 해제해주세요 ---
    with app.app_context():
        from . import models
        db.create_all()
       
        
    return app