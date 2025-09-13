# src/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # --- ▼▼▼▼▼ 핵심 수정 부분 ▼▼▼▼▼ ---
    # 1. Hugging Face Spaces Secret에서 DATABASE_URL을 읽어옵니다.
    #    'postgresql://...' 로 시작하는 주소의 'postgres'를 'postgresql'로 변경해줍니다.
    db_uri = os.environ.get('DATABASE_URL')
    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    # 2. 앱 설정에 적용합니다.
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    # --- ▲▲▲▲▲ 핵심 수정 부분 끝 ▲▲▲▲▲ ---

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    db.init_app(app)

    # auth, models, main 블루프린트를 다시 가져옵니다.
    from . import auth, models, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    # AI 모델 로딩 (이전과 동일)
    from .emotion_engine import load_emotion_classifier
    from .recommender import Recommender
    app.emotion_classifier = load_emotion_classifier()
    app.recommender = Recommender()

    with app.app_context():
        db.create_all()

    return app