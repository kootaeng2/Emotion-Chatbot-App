# src/main.py
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request, current_app
from sqlalchemy import extract
import datetime
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

default_recommendations = {
    '분노': '화가 날 때는 신나는 음악을 듣거나, 가벼운 코미디 영화를 보며 기분을 전환해 보세요.',
    '불안': '불안할 때는 차분한 클래식 음악을 듣거나, 따뜻한 차를 마시며 명상을 해보는 건 어떨까요?',
    '슬픔': '슬플 때는 위로가 되는 영화나 책을 보며 감정을 충분히 느껴보는 것도 좋아요. 혹은 친구와 대화를 나눠보세요.',
    '당황': '당황스러울 때는 잠시 숨을 고르고, 좋아하는 음악을 들으며 마음을 진정시켜 보세요.',
    '기쁨': '기쁠 때는 신나는 댄스 음악과 함께 춤을 추거나, 친구들과 만나 즐거움을 나눠보세요!',
    '상처': '마음의 상처를 받았을 때는, 위로가 되는 음악을 듣거나, 조용한 곳에서 책을 읽으며 마음을 달래보세요.'
}

def generate_recommendation(user_diary, predicted_emotion):
    """
    주어진 일기 내용과 감정을 바탕으로 Gemini API를 사용하여 문화생활 추천을 생성합니다.
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        사용자의 일기 내용과 감정을 바탕으로 문화생활을 추천해줘.
        사용자는 현재 '{predicted_emotion}' 감정을 느끼고 있어.

        일기 내용:
        ---
        {user_diary}
        ---

        아래 두 가지 시나리오에 맞춰 영화, 음악, 도서만 추천해줘.
        각 추천 항목은 "종류: 추천 콘텐츠 제목 (아티스트/감독/작가 등)" 형식으로 작성하고, 간단한 추천 이유를 덧붙여줘.
        결과는 Markdown 형식으로 보기 좋게 정리해줘.
        
        ## [수용]
        현재 감정을 더 깊이 느끼거나 위로받고 싶을 때.

        ## [전환]
        현재 감정에서 벗어나 새로운 활력을 얻고 싶을 때.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"🔥🔥🔥 Gemini API 호출 중 오류 발생: {e} 🔥🔥🔥")
        return default_recommendations.get(predicted_emotion, "오늘은 좋아하는 음악을 들으며 편안한 하루를 보내는 건 어떠세요?")


@bp.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    logged_in = 'user_id' in session
    username = session.get('username') if logged_in else None
    logging.info(f"메인 페이지 접속: 로그인 상태: {logged_in}, 사용자: {username}")
    return render_template("main.html", logged_in=logged_in, username=username)


@bp.route("/api/predict", methods=["POST"])
def api_predict():
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
        
    user_id = session['user_id']
    user_diary = request.json.get("diary")
    if not user_diary:
        return jsonify({"error": "일기 내용이 없습니다."}), 400

    try:
        # 1. Predict emotion
        predicted_emotion = predict_emotion(user_diary)
        
        # 2. Generate recommendation
        recommendation_text = generate_recommendation(user_diary, predicted_emotion)

        # 3. Save diary
        new_diary = Diary(
            content=user_diary,
            emotion=predicted_emotion,
            recommendation=recommendation_text,
            user_id=user_id
        )
        db.session.add(new_diary)
        db.session.commit()

        # 4. Return everything
        return jsonify({
            "emotion": predicted_emotion,
            "emoji": emotion_emoji_map.get(predicted_emotion, '🤔'),
            "recommendation": recommendation_text
        })
    except Exception as e:
        logging.error(f"[/api/predict] 처리 중 오류 발생: {e}")
        return jsonify({"error": "처리 중 오류가 발생했습니다."}), 500


@bp.route("/api/recommend", methods=["POST"])
def api_recommend():
    logging.info("[/api/recommend] 요청 수신됨.")
    user_diary = request.json.get("diary")
    predicted_emotion = request.json.get("emotion") # 감정을 직접 받음

    if not user_diary or not predicted_emotion:
        logging.warning("[/api/recommend] 일기 내용 또는 감정이 없습니다.")
        return jsonify({"error": "일기 내용 또는 감정이 없습니다."}), 400

    recommendation_text = generate_recommendation(user_diary, predicted_emotion)
    
    response_data = {
        "emotion": predicted_emotion,
        "emoji": emotion_emoji_map.get(predicted_emotion, '🤔'),
        "recommendation": recommendation_text
    }
    return jsonify(response_data)


@bp.route('/api/diaries')
def api_diaries():
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    user_id = session['user_id']
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        today = datetime.date.today()
        year = today.year
        month = today.month

    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1)
    else:
        end_date = datetime.date(year, month + 1, 1)

    user_diaries = Diary.query.filter(
        Diary.user_id == user_id,
        Diary.created_at >= start_date,
        Diary.created_at < end_date
    ).order_by(Diary.created_at.asc()).all()

    diaries_data = []
    utc_tz = datetime.timezone.utc
    kst_tz = datetime.timezone(datetime.timedelta(hours=9))

    for diary in user_diaries:
        # Assume created_at from DB is a naive datetime representing UTC, make it aware
        utc_time = diary.created_at.replace(tzinfo=utc_tz)
        
        # Convert to KST for display
        kst_time = utc_time.astimezone(kst_tz)
        
        diaries_data.append({
            "id": diary.id,
            "date": kst_time.strftime('%Y-%m-%d'),
            "createdAt": kst_time.strftime('%Y-%m-%d %H:%M:%S'),
            "content": diary.content,
            "emotion": diary.emotion,
            "recommendation": diary.recommendation
        })

    return jsonify(diaries_data)


@bp.route('/my_diary')
def my_diary():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('my_diary.html')


@bp.route('/mypage')
def mypage():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    username = session.get('username')
    return render_template('mypage.html', username=username)


@bp.route('/diary/save', methods=['POST'])
def diary_save():
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    user_id = session['user_id']
    diary_content = request.form.get('diary')
    predicted_emotion = request.form.get('emotion')

    if not diary_content or not predicted_emotion:
        return jsonify({"error": "일기 내용이나 감정이 없습니다."}), 400

    try:
        # 추천 생성
        recommendation_text = generate_recommendation(diary_content, predicted_emotion)

        # 일기 저장
        new_diary = Diary(
            content=diary_content,
            emotion=predicted_emotion,
            recommendation=recommendation_text,
            user_id=user_id
        )
        db.session.add(new_diary)
        db.session.commit()

        return jsonify({
            "success": "일기가 성공적으로 저장되었습니다.",
            "recommendation": recommendation_text # 클라이언트에서 바로 사용할 수 있도록 추천 내용 반환
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"일기 저장 중 오류 발생: {e}")
        return jsonify({"error": "일기 저장 중 오류가 발생했습니다."}), 500

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
