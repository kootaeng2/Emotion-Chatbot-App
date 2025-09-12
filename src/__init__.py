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

    # @app.before_first_request를 사용하여 첫 요청 직전에 DB 테이블을 생성합니다.
    # 이렇게 하면 앱 시작 시점의 타이밍 문제를 피할 수 있습니다.
    @app.before_first_request
    def create_tables():
        with app.app_context():
            db.create_all()
        
    return app