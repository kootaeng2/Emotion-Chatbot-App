# src/ auth.py
# 기존 app.py에서 auth와 관련해서 분리
# 로그인이나 회원가입 인증 관련한 스크립트

from flask import Blueprint, render_template, request, redirect, url_for, session
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 회원가입 파트
# src/ auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # --- try 블록의 위치를 함수 시작 부분으로 이동 ---
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # DB 조회 작업도 try 블록 안으로 이동
            if User.query.filter_by(username=username).first():
                return "이미 존재하는 사용자 이름입니다."

            new_user = User(username=username)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            logging.warning("✅ DB 저장 성공: 사용자 '{}'가 추가되었습니다.".format(username))
            return redirect(url_for('auth.login'))

    except Exception as e:
        db.session.rollback()
        logging.exception("🔥🔥🔥 signup 함수에서 DB 오류 발생! 🔥🔥🔥")
        return "Internal Server Error", 500

    return render_template('signup.html')


# 로그인 파트
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logging.warning(f"--- 로그인 시도: 사용자명 '{username}' ---")

        # 데이터베이스에서 사용자 정보 조회
        user = User.query.filter_by(username=username).first()

        # 1. 사용자가 DB에 존재하는지 확인
        if not user:
            logging.warning(f"로그인 실패: 사용자 '{username}'을(를) 찾을 수 없습니다.")
            return "로그인 정보가 올바르지 않습니다."

        # 2. 비밀번호가 일치하는지 확인
        if user.check_password(password):
            # 성공
            logging.warning(f"✅ 로그인 성공: 사용자 '{username}'")
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.home'))
        else:
            # 실패
            logging.warning(f"로그인 실패: 사용자 '{username}'의 비밀번호가 일치하지 않습니다.")
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