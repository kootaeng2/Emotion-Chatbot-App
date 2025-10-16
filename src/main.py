# src/main.py
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request, current_app
from . import db
from .models import Diary
from .emotion_engine import predict_emotion
import logging
import os
import google.generativeai as genai

bp = Blueprint('main', __name__)

# --- Gemini API 설정 ---
try:
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logging.warning("🔥🔥🔥 GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. 🔥🔥🔥")
    genai.configure(api_key=api_key)
except Exception as e:
    logging.error(f"🔥🔥🔥 Gemini API 설정 중 오류 발생: {e} 🔥🔥🔥")


# 감정별 이모지 맵
emotion_emoji_map = {
    '분노': '😠', '불안': '😟', '슬픔': '😢',
    '당황': '😮', '기쁨': '😄', '상처': '💔',
}

@bp.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    logged_in = 'user_id' in session
    username = session.get('username') if logged_in else None
    logging.info(f"메인 페이지 접속: 로그인 상태: {logged_in}, 사용자: {username}")
    return render_template("main.html", logged_in=logged_in, username=username)


@bp.route("/api/recommend", methods=["POST"])
def api_recommend():
    user_diary = request.json.get("diary")
    if not user_diary:
        return jsonify({"error": "일기 내용이 없습니다."}), 400

    # 1. 감정 분석
    predicted_emotion = predict_emotion(current_app.emotion_classifier, user_diary)

    # 2. (선택적) DB에 일기 저장
    if 'user_id' in session:
        try:
            user_id = session['user_id']
            new_diary_entry = Diary(content=user_diary, emotion=predicted_emotion, user_id=user_id)
            db.session.add(new_diary_entry)
            db.session.commit()
        except Exception as e:
            logging.exception("DB 저장 오류 발생!")
            db.session.rollback()

    # 3. Gemini API를 통한 문화생활 추천
    recommendation_text = "추천 내용을 생성하지 못했습니다."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 제미나이 API에 전달할 프롬프트
        prompt = f"""
        사용자의 일기 내용과 감정을 바탕으로 문화생활을 추천해줘.
        사용자는 현재 '{predicted_emotion}' 감정을 느끼고 있어.

        일기 내용:
        ---
        {user_diary}
        ---

        아래 두 가지 시나리오에 맞춰 영화, 음악, 도서, 공연, 전시 등 다양한 문화 콘텐츠를 추천해줘.
        각 추천 항목은 "종류: 추천 콘텐츠 제목 (아티스트/감독/작가 등)" 형식으로 작성하고, 간단한 추천 이유를 덧붙여줘.
        결과는 Markdown 형식으로 보기 좋게 정리해줘.

        1.  **[감정 몰입 (수용)]**: 현재 감정을 더 깊이 느끼거나 위로받고 싶을 때.
        2.  **[감정 전환]**: 현재 감정에서 벗어나 새로운 활력을 얻고 싶을 때.
        """
        
        response = model.generate_content(prompt)
        recommendation_text = response.text

    except Exception as e:
        logging.error(f"🔥🔥🔥 Gemini API 호출 중 오류 발생: {e} 🔥🔥🔥")
        recommendation_text = "추천을 생성하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."


    # 4. 프론트엔드로 결과 전송
    response_data = {
        "emotion": predicted_emotion,
        "emoji": emotion_emoji_map.get(predicted_emotion, '🤔'),
        "recommendation": recommendation_text
    }
    return jsonify(response_data)


# --- 이하 다른 라우트들 (my_diary, delete_diary 등)은 기존 코드와 동일 ---

@bp.route('/my_diary')
def my_diary():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    user_diaries = Diary.query.filter_by(user_id=user_id).order_by(Diary.created_at.desc()).all()
    return render_template('my_diary.html', diaries=user_diaries)

@bp.route('/diary/delete/<string:diary_id>', methods=['DELETE'])
def delete_diary(diary_id):
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    diary_to_delete = Diary.query.get(diary_id)

    if not diary_to_delete:
        return jsonify({"error": "일기를 찾을 수 없습니다."}), 404

    if diary_to_delete.user_id != session['user_id']:
        return jsonify({"error": "삭제 권한이 없습니다."}), 403

    try:
        db.session.delete(diary_to_delete)
        db.session.commit()
        return jsonify({"success": "일기가 삭제되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "삭제 중 오류가 발생했습니다."}), 500