# src/main.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from . import db
from .models import User, Diary
from .emotion_engine import load_emotion_classifier, predict_emotion
from .recommender import Recommender
import random

bp=Blueprint('main', __name__)

emotion_classifier=load_emotion_classifier()
recommender=Recommender()

# 추천된 6개의 핵심 감정 코드에 대해서만 이모지를 정의합니다.
# 모델이 이 6개 외의 다른 E코드를 출력하면 기본값 '🤔'가 사용됩니다.
emotion_emoji_map = {
    'E10': '😄', # 기쁨
    'E14': '😢', # 슬픔
    'E13': '😠', # 분노
    'E12': '😟', # 불안
    'E15': '😮', # 놀람
    'E16': '😐', # 중립
}

@bp.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template("emotion_homepage.html", username=session.get('username'))

@bp.route("/api/recommend", methods=["POST"])
def api_recommend():
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    user_diary = request.json.get("diary")
    if not user_diary:
        return jsonify({"error": "일기 내용이 없습니다."}), 400

    predicted_emotion = predict_emotion(emotion_classifier, user_diary)

    try:
        user_id = session['user_id']
        new_diary_entry = Diary(content=user_diary, emotion=predicted_emotion, user_id=user_id)
        db.session.add(new_diary_entry)
        db.session.commit()
    except Exception as e:
        print(f"DB 저장 오류: {e}")
        db.session.rollback()
    
    accept_recs = recommender.recommend(predicted_emotion, "수용")
    change_recs = recommender.recommend(predicted_emotion, "전환")
    
    accept_choice = random.choice(accept_recs) if accept_recs else "추천 없음"
    change_choice = random.choice(change_recs) if change_recs else "추천 없음"

    recommendation_text = (
        f"<b>[ 이 감정을 더 깊이 느끼고 싶다면... (수용) ]</b><br>"
        f"• {accept_choice}<br><br>"
        f"<b>[ 이 감정에서 벗어나고 싶다면... (전환) ]</b><br>"
        f"• {change_choice}"
    )

    response_data = {
        "emotion": predicted_emotion,
        "emoji": emotion_emoji_map.get(predicted_emotion, '🤔'),
        "recommendation": recommendation_text
    }
    return jsonify(response_data)

@bp.route('/my_diary')
def my_diary():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user_diaries = Diary.query.filter_by(user_id=user_id).order_by(Diary.created_at.desc()).all()
    
    return render_template('my_diary.html', diaries=user_diaries)

@bp.route('/show_users')
def show_users():
    """데이터베이스에 저장된 모든 사용자를 확인하기 위한 테스트용 페이지"""
    try:
        # User 테이블의 모든 사용자 정보를 가져옵니다.
        all_users = User.query.all()
        
        # 사용자가 한 명도 없으면 메시지를 표시합니다.
        if not all_users:
            return "저장된 사용자가 아무도 없습니다."
            
        # 각 사용자의 이름을 리스트로 만들어 출력합니다.
        usernames = [user.username for user in all_users]
        return f"현재 저장된 사용자 목록: {', '.join(usernames)}"

    except Exception as e:
        # 오류 발생 시 오류 메시지를 출력합니다.
        return f"사용자 목록을 불러오는 중 오류 발생: {e}"