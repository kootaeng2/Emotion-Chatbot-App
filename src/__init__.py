# src/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

# AI 모델과 추천기는 여기서 전역 변수로 선언합니다.
emotion_classifier = None
recommender = None

def create_app():
    app = Flask(__name__)

    # --- 기본 설정 ---
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- DB 초기화 ---
    db.init_app(app)

    # --- AI 엔진 및 추천기 로딩 ---
    global emotion_classifier, recommender
    from .emotion_engine import load_emotion_classifier
    from .recommender import Recommender
    print("AI 엔진 및 추천기를 로드합니다...")
    emotion_classifier = load_emotion_classifier()
    recommender = Recommender()
    print("AI 엔진 및 추천기 로드 완료.")

    # --- 블루프린트(부서) 등록 ---
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    
    # --- DB 테이블 생성 ---
    with app.app_context():
        from . import models
        db.create_all()

    return app