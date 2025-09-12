# src/__init__.py
# db 초기화, 블루프린트(앱 분리 현재는 main, auth분리) 등록

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# db 생성
db=SQLAlchemy()

def create_app():
    app=Flask(__name__)
    db_path = '/data/database.db'

    # 데이터베이스 파일이 위치할 디렉터리 경로
    db_dir = os.path.dirname(db_path)
    
    # 디렉터리가 존재하지 않으면 생성합니다.
    os.makedirs(db_dir, exist_ok=True)
    print(f"✅ Database directory '{db_dir}' is ready.")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    db.init_app(app)

    from . import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    with app.app_context():
        from . import models
        # ❗️ DB 테이블을 생성하는 코드를 추가합니다.
        db.create_all()
    return app