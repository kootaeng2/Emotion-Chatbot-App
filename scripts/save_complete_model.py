# save_complete_model.py
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# 기존 훈련 결과물이 저장된 경로
checkpoint_path = "./results/checkpoint-9681"

# '완전한 모델'을 저장할 새 폴더 이름
output_dir = "./korean-emotion-classifier-final"

print(f"'{checkpoint_path}'에서 모델과 토크나이저를 불러옵니다...")
model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
print("불러오기 완료.")

print(f"'{output_dir}' 폴더에 완전한 모델과 토크나이저를 저장합니다...")
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

print("저장 완료! 'korean-emotion-classifier-final' 폴더를 확인하세요.")
print("이 폴더 안의 파일들을 'my-local-model' 폴더로 옮겨주시면 됩니다.")