# src/__init__.py
# db 초기화, 블루프린트(앱 분리 현재는 main, auth분리) 등록

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# db 생성
db=SQLAlchemy()
def create_app():
    app=Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key-for-flask-session'
    db.init_app(app)

    from . import main, auth
    app. register_blueprint(main.bp)
    app.register_blueprint(auth.bp)


    return app