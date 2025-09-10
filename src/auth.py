# src/ auth.py
# 기존 app.py에서 auth와 관련해서 분리
# 로그인이나 회원가입 인증 관련한 스크립트

from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 회원가입 파트
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 이미 존재하는 사용자인지 데이터베이스에서 확인
        if User.query.filter_by(username=username).first():
            # (나중에는 플래시 메시지 등으로 사용자에게 알림)
            return "이미 존재하는 사용자 이름입니다."

        # 새 사용자 생성 및 비밀번호 암호화
        new_user = User(username=username)
        new_user.set_password(password)
        
        # 데이터베이스에 추가 및 저장
        db.session.add(new_user)
        db.session.commit()
        
        # 회원가입 성공 후 로그인 페이지로 이동
        return redirect(url_for('auth.login'))

    # GET 요청 시 회원가입 페이지를 보여줌
    return render_template('signup.html')


# 로그인 파트
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 데이터베이스에서 사용자 정보 조회
        user = User.query.filter_by(username=username).first()

        # 사용자가 존재하고 비밀번호가 일치하는지 확인
        if user and user.check_password(password):
            # 세션에 사용자 정보 저장
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            
            # 로그인 성공 후 메인 페이지로 이동
            return redirect(url_for('main.home'))
        else:
            # (나중에는 플래시 메시지 등으로 사용자에게 알림)
            return "로그인 정보가 올바르지 않습니다."

    # GET 요청 시 로그인 페이지를 보여줌
    return render_template('login.html')

# 로그아웃 part
@bp.route('/logout')
def logout():

    # 세션에서 사용자 정보 제거
    session.clear()
    # 로그아웃 후 로그인 페이지로 이동
    return redirect(url_for('auth.login'))