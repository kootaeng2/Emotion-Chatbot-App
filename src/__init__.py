from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 영구 저장소에 데이터베이스 경로 설정
    db_path = '/data/database.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    db.init_app(app)

    # 블루프린트 등록
    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # with app.app_context()를 사용하여 앱이 시작될 때 DB 테이블을 생성합니다.
    # 이것이 가장 표준적이고 안정적인 방식입니다.
    with app.app_context():
        db.create_all()
        
    return app