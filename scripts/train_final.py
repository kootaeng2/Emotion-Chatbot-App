# 파일 이름: train_final.py
# 최종 감정 분류 모델을 학습하는 스크립트

import os
import pandas as pd
import json
import re
import torch
import numpy as np
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.utils import class_weight
from torch.nn import CrossEntropyLoss
from typing import Dict, List, Tuple
from dataclasses import dataclass
import platform
import matplotlib.pyplot as plt
import seaborn as sns

# --- Matplotlib 한글 폰트 설정 (로컬 PC용) ---
try:
    if platform.system() == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif platform.system() == 'Darwin': # Mac OS
        plt.rc('font', family='AppleGothic')
    else: # Linux (코랩 등)
        # 나눔 폰트가 설치되어 있어야 합니다.
        plt.rc('font', family='NanumBarunGothic')
    
    # 마이너스 부호 깨짐 방지
    plt.rcParams['axes.unicode_minus'] = False
except:
    print("한글 폰트 설정에 실패했습니다. 혼동 행렬의 라벨이 깨질 수 있습니다.")


# --- 1. 설정부 ---
@dataclass
class TrainingConfig:
    mode: str = "emotion" 
    data_dir: str = "./data"
    output_dir: str = "./results"
    base_model_name: str = "klue/roberta-base"
    eval_batch_size: int = 64
    num_train_epochs: int = 10
    learning_rate: float = 1e-5
    train_batch_size: int = 16
    weight_decay: float = 0.01
    max_length: int = 128
    warmup_ratio: float = 0.1
    
    def get_model_name(self) -> str:
        if self.mode == 'emotion':
            return os.path.join(self.output_dir, 'nsmc_model')
        return self.base_model_name
        
    def get_output_dir(self) -> str:
        if self.mode == 'emotion':
            return os.path.join(self.output_dir, 'emotion_model_final')
        return os.path.join(self.output_dir, 'nsmc_model')

# --- 2. 커스텀 클래스 및 함수 ---
class EmotionDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach() for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.labels)

class CustomTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        if class_weights is not None:
            self.loss_fct = CrossEntropyLoss(weight=class_weights)
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss = self.loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    return {'accuracy': acc, 'f1': f1}

def clean_text(text: str) -> str:
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', str(text))

# --- 3. 데이터 로더 ---
def get_data(config: TrainingConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if config.mode == 'nsmc':
      print("--- NSMC 데이터 로딩 ---")
      df = pd.read_csv(os.path.join(config.data_dir, "nsmc_ratings_train.txt"), sep='\t').dropna()
      df['document'] = df['document'].apply(clean_text)
      return train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])

    elif config.mode == 'emotion':
        print("--- 감정 데이터 로딩 및 6클래스 레이블로 통합 ---")
        
        # E코드 숫자를 기준으로 6개의 대분류로 매핑하는 함수
        def map_ecode_to_major_emotion(ecode):
            try:
                code_num = int(ecode[1:])
            except (ValueError, TypeError):
                return None

            # 6클래스 분류 기준으로 변경
            if 10 <= code_num <= 19:
                return '분노'
            elif 20 <= code_num <= 29:
                return '슬픔'
            elif 30 <= code_num <= 39:
                return '불안'
            elif 40 <= code_num <= 49:
                return '상처'
            elif 50 <= code_num <= 59:
                return '당황'
            elif 60 <= code_num <= 69:
                return '기쁨'
            else:
                return None

    def load_and_map_labels(file_name):
        with open(os.path.join(config.data_dir, file_name), 'r', encoding='utf-8') as f:
            raw = json.load(f)
        data = [{'text': " ".join(d['talk']['content'].values()), 'emotion': d['profile']['emotion']['type']} for d in raw]
        df = pd.DataFrame(data)

        df['major_emotion'] = df['emotion'].apply(map_ecode_to_major_emotion)
        df.dropna(subset=['major_emotion'], inplace=True)
        df['cleaned_text'] = df['text'].apply(clean_text)
        return df
    
    df_train = load_and_map_labels("training-label.json")
    df_val = load_and_map_labels("validation-label.json")
    
    print("\n--- 6클래스 레이블 통합 후 클래스 분포 ---")
    if not df_train.empty:
        print(df_train['major_emotion'].value_counts())
    else:
        print("경고: 처리 후 학습 데이터가 비어있습니다. E코드 매핑 범위를 확인해주세요.")

    return df_train, df_val
# --- 4. 메인 실행 함수 ---
def run_training():
    config = TrainingConfig()
    
    # 1. 데이터 준비
    df_train, df_val = get_data(config)
    text_column = 'document' if config.mode == 'nsmc' else 'cleaned_text'
    label_column_str = 'label' if config.mode == 'nsmc' else 'major_emotion'
    
    # 2. 토크나이저 및 라벨 인코딩
    tokenizer = AutoTokenizer.from_pretrained(config.get_model_name())

    if config.mode == 'nsmc':
        # NSMC의 라벨(0, 1)이 numpy 타입일 수 있으므로 int로 변환합니다.
        unique_labels = sorted([int(l) for l in df_train[label_column_str].unique()])
    else:
        # 감정 라벨은 문자열이므로 그대로 사용합니다.
        unique_labels = sorted(df_train[label_column_str].unique())

    label_to_id = {label: i for i, label in enumerate(unique_labels)}
    # id_to_label을 label_to_id의 역으로 올바르게 생성합니다.
    id_to_label = {i: label for label, i in label_to_id.items()}
    
    df_train['label'] = df_train[label_column_str].map(label_to_id)
    df_val['label'] = df_val[label_column_str].map(label_to_id)

    # 3. 데이터셋 생성 및 클래스 가중치 계산
    train_encodings = tokenizer(list(df_train[text_column]), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    val_encodings = tokenizer(list(df_val[text_column]), max_length=config.max_length, padding=True, truncation=True, return_tensors="pt")
    
    train_dataset = EmotionDataset(train_encodings, df_train['label'].tolist())
    val_dataset = EmotionDataset(val_encodings, df_val['label'].tolist())
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}")
    class_weights = torch.tensor(class_weight.compute_class_weight('balanced', classes=np.unique(df_train['label']), y=df_train['label'].values), dtype=torch.float).to(device)
    print(f"계산된 클래스 가중치: {class_weights.tolist()}")

    # 4. 모델 로딩
    model = AutoModelForSequenceClassification.from_pretrained(
        config.get_model_name(),
        num_labels=len(unique_labels),
        id2label=id_to_label,
        label2id=label_to_id,
        ignore_mismatched_sizes=(config.mode == 'emotion') # 감정분류 시에만 사이즈 불일치 무시
    ).to(device)

    # 5. 훈련 실행
    training_args = TrainingArguments(
        output_dir=config.get_output_dir(),
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.train_batch_size,
        per_device_eval_batch_size=config.eval_batch_size,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        report_to="none"
    )

    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        class_weights=class_weights
    )
    
    print(f"\n '{config.mode}' 모드로 모델 훈련을 시작합니다...")
    trainer.train()
    print("\n 모델 훈련 완료!")

    output_dir = config.get_output_dir()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"최종 모델과 토크나이저가 {output_dir} 경로에 저장되었습니다.")
    
    results = trainer.evaluate()
    print(f"최종 평가 결과: {results}")
    
    results_path = os.path.join(output_dir, "final_evaluation_results.json")
    with open(results_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"최종 평가 결과가 {results_path}에 저장되었습니다.")

    # --- [추가] 혼동 행렬 생성 및 저장 ---
    print("\n--- 혼동 행렬 생성 ---")
    predictions = trainer.predict(val_dataset)
    y_pred = predictions.predictions.argmax(-1)
    y_true = predictions.label_ids

    labels = [id_to_label[i] for i in sorted(id_to_label.keys())]
    cm = confusion_matrix(y_true, y_pred, labels=[label_to_id[l] for l in labels])
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.xlabel('예측 라벨 (Predicted Label)')
    plt.ylabel('실제 라벨 (True Label)')
    plt.title('Confusion Matrix')
    
    cm_path = os.path.join(output_dir, "confusion_matrix.png")
    plt.savefig(cm_path)
    print(f"혼동 행렬이 {cm_path}에 저장되었습니다.")

if __name__ == "__main__":
    run_training()

