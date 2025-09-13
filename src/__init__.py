from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 1. DB 경로를 영구 저장소(/data)가 아닌, 임시 로컬 경로로 먼저 설정합니다.
    #    Hugging Face Spaces의 sqlite 권한 문제를 우회하기 위함입니다.
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    
    # 2. DB 초기화
    db.init_app(app)

    # 3. 블루프린트 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # 4. AI 모델과 추천기를 앱 생성 마지막 단계에서 로드하여 app 객체에 저장합니다.
    from .emotion_engine import load_emotion_classifier
    from .recommender import Recommender
    
    app.emotion_classifier = load_emotion_classifier()
    app.recommender = Recommender()

    # 5. 모든 것이 준비된 후 DB 테이블 생성
    with app.app_context():
        from . import models
        db.create_all()
        
    return app