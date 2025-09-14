class Recommender:
    def __init__(self):
        self.recommendation_db = {
            '기쁨': { # 기쁨
                '수용': ["음악: Pharrell Williams - Happy", "영화: 월터의 상상은 현실이 된다"],
                '전환': ["음악: 이루마 - River Flows In You", "영화: 쇼생크 탈출"]
            },
            '슬픔': { # 슬픔
                '수용': ["음악: 박효신 - 눈의 꽃", "영화: 이터널 선샤인"],
                '전환': ["음악: 거북이 - 비행기", "영화: 월-E"]
            },
            '분노': { # 분노
                '수용': ["음악: 람슈타인 - Du Hast", "영화: 존 윅"],
                '전환': ["음악: 노라 존스 - Don't Know Why", "영화: 리틀 포레스트"]
            },
            '불안': { # 불안
                '수용': ["음악: 위로가 되는 연주곡 플레이리스트", "영화: 인사이드 아웃"],
                '전환': ["음악: Maroon 5 - Moves Like Jagger", "영화: 극한직업"]
            },
            '놀람': { # 놀람
                '수용': ["영화: 식스 센스", "음악: 박진영 - 어머님이 누구니"],
                '전환': ["음악: Bach - Air on G String", "책: 고요할수록 밝아지는 것들"]
            },
            '당황': { # 당황
                '수용': ["음악: 잔잔한 Lo-fi 플레이리스트", "영화: 패터슨"],
                '전환': ["음악: Queen - Don't Stop Me Now", "영화: 스파이더맨: 뉴 유니버스"]
            },
        }

    def recommend(self, emotion: str, choice: str) -> list:
        return self.recommendation_db.get(emotion, {}).get(choice, ["😥 아쉽지만, 아직 준비된 추천이 없어요."])