import torch
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.metrics import accuracy_score
import os
import json


# 1. 데이터 로딩 및 전처리 함수 (01_check_data.py 내용 통합)
def load_and_process_data(base_path="."):
    """
    데이터를 로드하고 전처리하여 통합 데이터프레임을 반환합니다.
    """
    data_path = os.path.join(base_path, 'data')
    
    # 파일 경로 설정
    train_text_path = os.path.join(data_path, 'training-origin.xlsx')
    train_label_path = os.path.join(data_path, 'training-label.json')
    val_text_path = os.path.join(data_path, 'validation-origin.xlsx')
    val_label_path = os.path.join(data_path, 'validation-label.json')

    # 데이터 불러오기
    try:
        df_train_text = pd.read_excel(train_text_path, header=0)
        df_val_text = pd.read_excel(val_text_path, header=0)
        with open(train_label_path, 'r', encoding='utf-8') as f:
            train_labels_raw = json.load(f)
        with open(val_label_path, 'r', encoding='utf-8') as f:
            val_labels_raw = json.load(f)
        print("파일 로딩 성공")
    except FileNotFoundError as e:
        print(f"파일을 찾을 수 없습니다: {e}")
        return None, None

    # 라벨 데이터 정제
    def extract_emotions(raw_labels):
        return [dialogue['profile']['emotion']['type'] for dialogue in raw_labels]

    df_train_labels = pd.DataFrame({'emotion': extract_emotions(train_labels_raw)})
    df_val_labels = pd.DataFrame({'emotion': extract_emotions(val_labels_raw)})

    # 텍스트와 라벨 데이터 병합
    df_train = pd.concat([df_train_text, df_train_labels], axis=1)
    df_val = pd.concat([df_val_text, df_val_labels], axis=1)

    # 대화 문장 병합
    def combine_dialogues(df):
        dialogue_cols = [col for col in df.columns if '문장' in str(col)]
        df['text'] = df[dialogue_cols].astype(str).apply(lambda row: ' '.join(row), axis=1)
        return df[['text', 'emotion']]

    df_train = combine_dialogues(df_train)
    df_val = combine_dialogues(df_val)
    
    # 결측치 제거
    df_train.dropna(subset=['emotion', 'text'], inplace=True)
    df_val.dropna(subset=['emotion', 'text'], inplace=True)
    
    print("데이터 병합 및 전처리 완료")
    return df_train, df_val

# 2. PyTorch 데이터셋 클래스
class EmotionDataset(torch.utils.data.Dataset):
    """PyTorch 데이터셋 클래스"""
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# 3. 평가 지표 함수
def compute_metrics(pred):
    """정확도 계산을 위한 함수"""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    return {'accuracy': acc}

# 4. 메인 훈련 및 평가 로직
def main():
    """모델 훈련 및 평가를 수행하는 메인 함수"""
    # --- 1. 데이터 준비 ---
    print("--- 1. 데이터 준비 시작 ---")
    df_train, df_val = load_and_process_data(base_path=".")
    if df_train is None or df_val is None:
        return

    # --- 2. 모델 및 토크나이저 불러오기 ---
    print("--- 2. 모델 및 토크나이저 로딩 ---")
    MODEL_NAME = 'klue/roberta-base'
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(df_train['emotion'].unique()))
    except OSError as e:
        print(f"모델 로딩 오류: {e}")
        print("인터넷 연결을 확인하거나 모델 이름을 확인하세요.")
        return

    # --- 3. 데이터 전처리 및 데이터셋 생성 ---
    print("--- 3. 데이터 전처리 및 데이터셋 생성 ---")
    
    # 라벨 인코딩
    unique_labels = sorted(df_train['emotion'].unique())
    label2id = {label: i for i, label in enumerate(unique_labels)}
    id2label = {i: label for label, i in label2id.items()}
    
    # 모델 config에 라벨 정보 저장
    model.config.label2id = label2id
    model.config.id2label = id2label

    train_labels = df_train['emotion'].map(label2id).tolist()
    val_labels = df_val['emotion'].map(label2id).tolist()

    train_texts = df_train['text'].tolist()
    val_texts = df_val['text'].tolist()

    # 토크나이징
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128, return_tensors="pt")
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128, return_tensors="pt")

    # 데이터셋 생성
    train_dataset = EmotionDataset(train_encodings, train_labels)
    val_dataset = EmotionDataset(val_encodings, val_labels)

    # --- 4. TrainingArguments 설정 ---
    # 정확도 저장을 위해 evaluation_strategy를 "steps"로 설정하고,
    # logging_steps와 eval_steps를 지정합니다.
    print("--- 4. TrainingArguments 설정 ---")
    training_args = TrainingArguments(
        output_dir='./results',          # 결과물 저장 경로
        num_train_epochs=3,              # 총 훈련 에폭
        per_device_train_batch_size=32,  # 훈련용 배치 사이즈
        warmup_steps=500,                # 학습률 스케줄러를 위한 웜업 스텝
        weight_decay=0.01,               # 가중치 감쇠
        logging_dir='./logs',            # 로그 저장 경로
        logging_steps=500,               # 500 스텝마다 로그 기록
        save_steps=500,                  # 500 스텝마다 모델 저장
        save_total_limit=10             # 최대 10개의 체크포인트만 저장
    )

    # --- 5. Trainer 생성 및 훈련 시작 ---
    print("--- 5. Trainer 생성 및 훈련 시작 ---")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset
    )

    trainer.train()

    # --- 6. 최종 모델 저장 ---
    print("--- 6. 최종 모델 저장 ---")
    final_model_path = os.path.join(training_args.output_dir, "final_model")
    trainer.save_model(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"훈련된 모델을 '{final_model_path}'에 저장했습니다.")


if __name__ == "__main__":
    main()