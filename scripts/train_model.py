import pandas as pd
import json
import re
import sys
import torch
import transformers
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# --- 1. 데이터 로딩 및 전처리 ---
print("--- [Phase 1] 데이터 로딩 및 전처리 시작 ---")
file_path = 'E:/sentiment_analysis_project/data/'

with open(file_path + 'training-label.json', 'r', encoding='utf-8') as file:
    training_data_raw = json.load(file)
with open(file_path + 'validation-label.json', 'r', encoding='utf-8') as file:
    validation_data_raw = json.load(file)

def create_dataframe(data_raw):
    extracted_data = []
    for dialogue in data_raw:
        try:
            emotion_type = dialogue['profile']['emotion']['type']
            dialogue_content = dialogue['talk']['content']
            full_text = " ".join(list(dialogue_content.values()))
            if full_text and emotion_type:
                extracted_data.append({'text': full_text, 'emotion': emotion_type})
        except KeyError:
            continue
    return pd.DataFrame(extracted_data)

df_train = create_dataframe(training_data_raw)
df_val = create_dataframe(validation_data_raw)

def clean_text(text):
    return re.sub(r'[^가-힣a-zA-Z0-9 ]', '', text)

df_train['cleaned_text'] = df_train['text'].apply(clean_text)
df_val['cleaned_text'] = df_val['text'].apply(clean_text)
print("✅ 데이터 로딩 및 전처리 완료!")


# --- 2. AI 모델링 준비 ---
print("\n--- [Phase 2] AI 모델링 준비 시작 ---")
MODEL_NAME = "beomi/kcbert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

train_tokenized = tokenizer(list(df_train['cleaned_text']), return_tensors="pt", max_length=128, padding=True, truncation=True)
val_tokenized = tokenizer(list(df_val['cleaned_text']), return_tensors="pt", max_length=128, padding=True, truncation=True)

unique_labels = sorted(df_train['emotion'].unique())
label_to_id = {label: id for id, label in enumerate(unique_labels)}
id_to_label = {id: label for label, id in label_to_id.items()}
df_train['label'] = df_train['emotion'].map(label_to_id)
df_val['label'] = df_val['emotion'].map(label_to_id)
print("✅ 토큰화 및 라벨 인코딩 완료!")


# --- 3. 모델 학습 및 평가 ---
print("\n--- [Phase 3] 모델 학습 및 평가 시작 ---")

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

train_dataset = EmotionDataset(train_tokenized, df_train['label'].tolist())
val_dataset = EmotionDataset(val_tokenized, df_val['label'].tolist())
print("✅ PyTorch 데이터셋 생성이 완료되었습니다.")

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, 
    num_labels=len(unique_labels),
    id2label=id_to_label,
    label2id=label_to_id
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"✅ 모델 로딩 완료! 모델은 {device}에서 실행됩니다.")

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    acc = accuracy_score(labels, preds)
    return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

print("\n🔥 AI 모델 훈련을 시작합니다...")
trainer.train()
print("\n🎉 모델 훈련 완료!")

# --- 4. 최종 모델 평가 ---
print("\n--- 최종 모델 성능 평가 ---")
final_evaluation = trainer.evaluate(eval_dataset=val_dataset) 
print(final_evaluation)

print("\n모든 과정이 성공적으로 끝났습니다! results 폴더에서 훈련된 모델을 확인하세요.")
