import os
import sys
import logging

# --- 프로젝트 루트 경로 설정 ---
# 이 스크립트가 'scripts' 폴더 안에 있으므로, 부모 디렉토리(프로젝트 루트)를 경로에 추가합니다.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src import create_app, db
from src.models import Diary
from src.main import generate_recommendation, recommender # generate_recommendation 사용
import datetime

# --- 로깅 설정 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def migrate_diaries_with_recommendations():
    """
    기존의 모든 일기를 순회하며 'recommendation' 필드가 비어있는 경우,
    새로운 추천을 생성하여 채워넣습니다.
    """
    app = create_app()
    with app.app_context():
        logging.info("데이터 마이그레이션을 시작합니다...")
        
        # 추천이 비어있는 모든 일기를 조회합니다.
        diaries_to_update = Diary.query.filter((Diary.recommendation == None) | (Diary.recommendation == '')).all()
        
        if not diaries_to_update:
            logging.info("업데이트할 일기가 없습니다. 모든 일기에 추천이 이미 존재합니다.")
            return

        logging.info(f"총 {len(diaries_to_update)}개의 일기를 업데이트합니다.")
        
        updated_count = 0
        failed_count = 0

        for diary in diaries_to_update:
            try:
                logging.info(f"ID: {diary.id} 일기 처리 중...")
                
                # 1. Gemini API를 통해 추천 생성 시도
                recommendation_text = generate_recommendation(diary.content, diary.emotion)

                # 2. 실패 시, Recommender 클래스로 대체
                if recommendation_text is None:
                    logging.warning(f"ID: {diary.id} - Gemini 추천 실패. Recommender 클래스로 대체합니다.")
                    su_yoong_recs = recommender.recommend(diary.emotion, '수용')
                    jeon_hwan_recs = recommender.recommend(diary.emotion, '전환')
                    
                    # diary_logic.js가 파싱할 수 있는 형식으로 만듭니다.
                    recommendation_text = f"## [수용]\n"
                    for rec in su_yoong_recs:
                        recommendation_text += f"* {rec}\n"
                    
                    recommendation_text += f"\n## [전환]\n"
                    for rec in jeon_hwan_recs:
                        recommendation_text += f"* {rec}\n"
                
                # 3. 데이터베이스에 반영
                diary.recommendation = recommendation_text
                updated_count += 1
                logging.info(f"ID: {diary.id} - 추천 생성 완료.")

            except Exception as e:
                failed_count += 1
                logging.error(f"ID: {diary.id} 처리 중 오류 발생: {e}")

        if updated_count > 0:
            try:
                db.session.commit()
                logging.info(f"성공: {updated_count}개 일기의 추천 정보 업데이트 완료.")
            except Exception as e:
                db.session.rollback()
                logging.error(f"데이터베이스 커밋 중 오류 발생: {e}")

        if failed_count > 0:
            logging.warning(f"실패: {failed_count}개 일기 처리 중 오류 발생.")
        
        logging.info("마이그레이션 완료.")

if __name__ == '__main__':
    migrate_diaries_with_recommendations()