from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

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
    
    # 2. DB 초기화 및 테이블 생성
    db.init_app(app)
    with app.app_context():
        from . import models
        db.create_all()

    # 3. 블루프린트 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # 4. AI 모델은 이제 요청 시 로드됩니다 (지연 로딩).

    return app
