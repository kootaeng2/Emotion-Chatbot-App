# src/ auth.py
# 기존 app.py에서 auth와 관련해서 분리
# 로그인이나 회원가입 인증 관련한 스크립트

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

# 로그인 파트
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logging.warning(f"--- 로그인 시도: 사용자명 '{username}' ---")

        # 데이터베이스에서 사용자 정보 조회
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('로그인 정보가 올바르지 않습니다.')
            # 로그인 실패 시 다시 로그인 화면(앞면)
            return render_template('auth_combined.html')
        
        # 로그인 성공
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('main.home'))

    return render_template('auth_combined.html')

# 회원가입 파트
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            # 1. 중복 사용자 확인
            if User.query.filter_by(username=username).first():
                 flash('이미 존재하는 사용자입니다.')
                 # [핵심] 이미 존재하면 카드가 뒤집힌 상태(회원가입 화면)를 유지하기 위해 mode='signup'을 전달
                 return redirect(url_for('auth.login', mode='signup'))

            # 2. 새 사용자 생성
            new_user = User(username=username)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            logging.warning("✅ DB 저장 성공: 사용자 '{}'가 추가되었습니다.".format(username))
            
            # 3. 가입 성공 시 로그인 화면(앞면)으로 이동
            flash('회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect(url_for('auth.login'))

    except Exception as e:
        db.session.rollback()
        logging.exception("🔥🔥🔥 signup 함수에서 DB 오류 발생! 🔥🔥🔥")
        return "Internal Server Error", 500

    
    return render_template('auth_combined.html')

# 로그아웃 part
@bp.route('/logout')
def logout():

    # 세션에서 사용자 정보 제거
    session.clear()
    # 로그아웃 후 로그인 페이지로 이동
    return redirect(url_for('auth.login'))