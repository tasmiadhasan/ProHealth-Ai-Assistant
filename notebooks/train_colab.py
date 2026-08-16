"""
=============================================================================
Google Colab Training Script: Bio_ClinicalBERT (Optimized & Upgraded)
=============================================================================
Major Improvements Included:
1. Class-Weighted Loss (WeightedTrainer) to fix minority class imbalance (boosts Macro F1 & Recall).
2. Non-destructive Clinical Text Preprocessing (preserves punctuation and medical symbols for BERT).
3. Optimized Hyperparameters (Cosine Annealing LR Scheduler, LR=2.5e-5, Warmup Ratio=0.06, Epochs=6, MaxLen=384).
4. Full Multilingual Evaluation & Detailed Per-Department Metrics Breakdown.
=============================================================================
Instructions for Google Colab:
1. Open https://colab.research.google.com/
2. Runtime -> Change runtime type -> Hardware accelerator -> T4 GPU
3. Mount Google Drive and run this script!
=============================================================================
"""

import os
import re
import sys
import json
import torch
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, f1_score, accuracy_score, precision_score, recall_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset

# 1. Mount Google Drive (if running on Colab)
try:
    from google.colab import drive
    print("📁 Mounting Google Drive...")
    drive.mount('/content/drive')
    IN_COLAB = True
except ImportError:
    IN_COLAB = False
    print("ℹ️ Running in local environment (Colab drive not mounted).")

# 2. Optimized Configuration & Drive Paths
MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"
BATCH_SIZE = 16
EPOCHS = 6
MAX_LEN = 384
LEARNING_RATE = 2.5e-5
WARMUP_RATIO = 0.06
WEIGHT_DECAY = 0.01

# Primary Google Drive Path
DRIVE_PROJECT_DIR = "/content/drive/MyDrive/CSE440 Project"

POSSIBLE_PATHS = [
    f"{DRIVE_PROJECT_DIR}/data/processed",
    f"{DRIVE_PROJECT_DIR}/data",
    f"{DRIVE_PROJECT_DIR}",
    "/content/drive/MyDrive/data/processed",
    "./data/processed",
    "./data/raw",
    "."
]

# Output directory for saving the model directly into Google Drive
if IN_COLAB and os.path.exists(DRIVE_PROJECT_DIR):
    OUTPUT_DIR = f"{DRIVE_PROJECT_DIR}/saved_models/clinicalbert_department"
elif IN_COLAB and os.path.exists("/content/drive/MyDrive"):
    OUTPUT_DIR = "/content/drive/MyDrive/saved_models/clinicalbert_department"
else:
    OUTPUT_DIR = "./saved_models/clinicalbert_department"

print("🔍 Checking GPU Availability...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

# 3. Clinical Department Taxonomy Mapping (13 Unified Classes)
DEPARTMENT_MAPPING = {
    'Cardiovascular / Pulmonary': 'Cardiology & Pulmonology',
    'Orthopedic': 'Orthopedics',
    'Gastroenterology': 'Gastroenterology',
    'Neurology': 'Neurology',
    'Neurosurgery': 'Neurology',
    'Dermatology': 'Dermatology',
    'ENT - Otolaryngology': 'ENT (Otolaryngology)',
    'Urology': 'Urology & Nephrology',
    'Nephrology': 'Urology & Nephrology',
    'Obstetrics / Gynecology': 'Gynecology & Obstetrics',
    'Pediatrics - Neonatal': 'Pediatrics',
    'Ophthalmology': 'Ophthalmology',
    'General Medicine': 'General Medicine',
    'Hematology - Oncology': 'Hematology & Oncology',
    'Psychiatry / Psychology': 'Psychiatry & Behavioral Health',
    'Allergy / Immunology': 'General Medicine'
}

def clean_clinical_text(text: str) -> str:
    """Intelligent text normalization preserving clinical symbols and sentence boundaries."""
    if not isinstance(text, str):
        return ""
    # Normalize whitespace while preserving punctuation for BERT tokenizer
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

# 4. Locate Dataset Files from Google Drive or Local Paths
data_found_dir = None
for p in POSSIBLE_PATHS:
    if (os.path.exists(os.path.join(p, "train.csv")) and os.path.exists(os.path.join(p, "val.csv"))) or os.path.exists(os.path.join(p, "mtsamples.csv")):
        data_found_dir = p
        break

if data_found_dir:
    print(f"🎯 Dataset files detected in: {data_found_dir}")
else:
    print("⚠️ Dataset files not found in standard paths. Searching current directory...")
    data_found_dir = "."

train_file = os.path.join(data_found_dir, "train.csv")
val_file = os.path.join(data_found_dir, "val.csv")
raw_file = os.path.join(data_found_dir, "mtsamples.csv")
mapping_file = os.path.join(data_found_dir, "label_mapping.json")

if os.path.exists(train_file) and os.path.exists(val_file):
    print(f"📂 Loading existing datasets: {train_file} & {val_file}")
    train_df = pd.read_csv(train_file)
    val_df = pd.read_csv(val_file)
    train_texts = [clean_clinical_text(t) for t in train_df['text'].tolist()]
    train_labels = train_df['label'].tolist()
    val_texts = [clean_clinical_text(t) for t in val_df['text'].tolist()]
    val_labels = val_df['label'].tolist()
    
    if os.path.exists(mapping_file):
        with open(mapping_file) as f:
            label_mapping = {int(k): v for k, v in json.load(f).items()}
    else:
        label_mapping = {int(i): name for i, name in enumerate(sorted(train_df['department'].unique()))}
    num_classes = len(label_mapping)
elif os.path.exists(raw_file):
    print(f"📂 Preprocessing raw dataset from {raw_file}...")
    df = pd.read_csv(raw_file)
    df['medical_specialty'] = df['medical_specialty'].astype(str).str.strip()
    df['department'] = df['medical_specialty'].map(DEPARTMENT_MAPPING)
    df = df.dropna(subset=['department']).copy()
    
    df['description'] = df['description'].fillna('').astype(str)
    df['transcription'] = df['transcription'].fillna('').astype(str)
    
    # Clean text preserving punctuation for contextual transformers
    df['text'] = (df['description'] + ". " + df['transcription']).apply(clean_clinical_text)
    df = df[df['text'].str.len() > 30].copy()
    
    le = LabelEncoder()
    df['label'] = le.fit_transform(df['department'])
    num_classes = len(le.classes_)
    label_mapping = {int(i): name for i, name in enumerate(le.classes_)}
    
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['text'].tolist(), df['label'].tolist(), test_size=0.2, random_state=42, stratify=df['label']
    )
else:
    raise FileNotFoundError("❌ Could not find train.csv, val.csv or mtsamples.csv! Please check dataset folder.")

print(f"📊 Total Training Samples: {len(train_texts)} | Validation Samples: {len(val_texts)}")
print(f"🏷️ Target Classes ({num_classes}): {list(label_mapping.values())}")

# 5. Compute Class Weights for Imbalanced Medical Classes
class_weights_arr = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_labels),
    y=train_labels
)
class_weights_tensor = torch.tensor(class_weights_arr, dtype=torch.float)
print(f"⚖️ Balanced Class Weights applied to Loss Function.")

# 6. Tokenizer & Dataset Preparation
print(f"🔤 Tokenizing with {MODEL_NAME} (Max Length: {MAX_LEN})...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=False)

def tokenize_fn(batch):
    return tokenizer(batch['text'], padding='max_length', truncation=True, max_length=MAX_LEN)

train_dataset = Dataset.from_dict({'text': train_texts, 'label': train_labels}).map(tokenize_fn, batched=True)
val_dataset = Dataset.from_dict({'text': val_texts, 'label': val_labels}).map(tokenize_fn, batched=True)

# 7. Model Initialization
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=num_classes, token=False)

# 8. Custom Weighted Trainer to Optimize Macro F1 & Recall
class WeightedTrainer(Trainer):
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        if self.class_weights is not None:
            loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights.to(model.device))
        else:
            loss_fct = torch.nn.CrossEntropyLoss()
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# 9. Comprehensive Metric Evaluation
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    macro_f1 = f1_score(labels, preds, average='macro', zero_division=0)
    weighted_f1 = f1_score(labels, preds, average='weighted', zero_division=0)
    macro_rec = recall_score(labels, preds, average='macro', zero_division=0)
    return {
        'accuracy': acc,
        'macro_f1': macro_f1,
        'weighted_f1': weighted_f1,
        'macro_recall': macro_rec
    }

# 10. Optimized Training Arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    lr_scheduler_type="cosine",
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    warmup_ratio=WARMUP_RATIO,
    weight_decay=WEIGHT_DECAY,
    logging_dir="./logs",
    logging_steps=25,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="macro_f1",
    fp16=torch.cuda.is_available()
)

# 11. Execute Fine-Tuning
trainer = WeightedTrainer(
    class_weights=class_weights_tensor,
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

print("\n🚀 Starting High-Performance Fine-Tuning on T4 GPU...")
trainer.train()

# 12. Detailed Post-Training Evaluation Report
print("\n" + "=" * 75)
print("📊 FINAL CLASSIFICATION REPORT (VAL SET):")
print("=" * 75)
preds_output = trainer.predict(val_dataset)
final_preds = np.argmax(preds_output.predictions, axis=-1)
target_names = [label_mapping[i] for i in range(num_classes)]
print(classification_report(val_labels, final_preds, target_names=target_names, digits=4, zero_division=0))

# 13. Save Model & Artifacts
os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

with open(os.path.join(OUTPUT_DIR, "label_mapping.json"), "w") as f:
    json.dump(label_mapping, f, indent=4)
print(f"\n🎉 Model & Tokenizer successfully saved to: {OUTPUT_DIR}")
print("💡 If Google Drive is mounted, all model files are permanently saved in your Google Drive!")

# =============================================================================
# 14. 🧪 MULTILINGUAL TEST ENGINE (BANGLA, BANGLISH & ENGLISH)
# =============================================================================
print("\n" + "=" * 75)
print("🧪 TESTING MODEL WITH BANGLA, BANGLISH & ENGLISH INPUTS")
print("=" * 75)

BANGLA_DEPT_MAP = {
    "Cardiology & Pulmonology": "কার্ডিওলজি ও পালমোনোলজি (হৃদরোগ ও বক্ষব্যাধি বিভাগ)",
    "Orthopedics": "অর্থোপেডিকস (হাড় ও জয়েন্ট বিভাগ)",
    "Neurology": "নিউরোলজি (মস্তিষ্ক ও স্নায়ুরোগ বিভাগ)",
    "Gastroenterology": "গ্যাস্ট্রোএন্টারোলজি (পাকস্থলী ও পরিপাকতন্ত্র বিভাগ)",
    "Dermatology": "ডার্মাটোলজি (চর্ম ও অ্যালার্জি বিভাগ)",
    "ENT (Otolaryngology)": "ইএনটি (নাক, কান ও গলা বিভাগ)",
    "Urology & Nephrology": "ইউরোলজি ও নেফ্রোলজি (কিডনি ও মূত্রনালী বিভাগ)",
    "Gynecology & Obstetrics": "গাইনিকোলজি (নারী ও প্রসূতি বিভাগ)",
    "Pediatrics": "পেডিয়াট্রিক্স (শিশু বিভাগ)",
    "Ophthalmology": "অপথালমোলজি (চক্ষু বিভাগ)",
    "General Medicine": "জেনারেল মেডিসিন (সাধারণ চিকিৎসা ও মেডিসিন)",
    "Hematology & Oncology": "হেমাটোলজি ও অনকোলজি (রক্ত ও ক্যান্সার বিভাগ)",
    "Psychiatry & Behavioral Health": "সাইকিয়াট্রি (মানসিক স্বাস্থ্য বিভাগ)"
}

specialist_dict = {
    "Cardiology & Pulmonology": ("Cardiologist / Pulmonologist", "কার্ডিওলজিস্ট / বক্ষব্যাধি বিশেষজ্ঞ"),
    "Orthopedics": ("Orthopedic Surgeon", "অর্থোপেডিক সার্জন"),
    "Neurology": ("Neurologist", "নিউরোলজিস্ট"),
    "Gastroenterology": ("Gastroenterologist", "গ্যাস্ট্রোএন্টারোলজিস্ট"),
    "Dermatology": ("Dermatologist", "ডার্মাটোলজিস্ট"),
    "ENT (Otolaryngology)": ("ENT Specialist", "ইএনটি বিশেষজ্ঞ"),
    "Urology & Nephrology": ("Urologist / Nephrologist", "কিডনি ও মূত্র বিশেষজ্ঞ"),
    "Gynecology & Obstetrics": ("Gynecologist", "স্ত্রী ও প্রসূতি বিশেষজ্ঞ"),
    "Pediatrics": ("Pediatrician", "শিশু বিশেষজ্ঞ"),
    "Ophthalmology": ("Ophthalmologist", "চক্ষু বিশেষজ্ঞ"),
    "General Medicine": ("General Physician", "জেনারেল মেডিসিন ডাক্তার"),
    "Hematology & Oncology": ("Oncologist", "ক্যান্সার বিশেষজ্ঞ"),
    "Psychiatry & Behavioral Health": ("Psychiatrist", "মানসিক রোগ বিশেষজ্ঞ")
}

def is_bangla(text):
    return bool(re.search(r'[\u0980-\u09FF]', text))

def translate_to_en(text):
    if is_bangla(text):
        try:
            from deep_translator import GoogleTranslator
            return GoogleTranslator(source='bn', target='en').translate(text)
        except Exception:
            return text
            
    banglish_dict = {
        'buke betha': 'chest pain',
        'buk betha': 'chest pain',
        'matha betha': 'headache migraine',
        'matha ghurano': 'dizziness',
        'pete betha': 'abdominal pain',
        'bomi': 'vomiting nausea',
        'sas nite kosto': 'shortness of breath',
        'haphani': 'asthma',
        'jor': 'fever',
        'kashi': 'cough',
        'chulkani': 'skin rash itching',
        'bachar jor': 'child high fever'
    }
    t = text.lower()
    for b_kw, e_kw in banglish_dict.items():
        if b_kw in t:
            t = t.replace(b_kw, e_kw)
    return t

def predict_medical_complaint(complaint_text: str):
    """Predicts department, confidence, specialist and urgency level."""
    model.eval()
    processed_text = translate_to_en(complaint_text)
    
    inputs = tokenizer(processed_text.lower(), return_tensors="pt", truncation=True, max_length=MAX_LEN, padding="max_length")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1).squeeze().tolist()
        
    prob_dict = {label_mapping[i]: probs[i] for i in range(len(probs))}
    sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    
    top_dept, top_conf = sorted_probs[0]
    dept_bn = BANGLA_DEPT_MAP.get(top_dept, top_dept)
    spec_en, spec_bn = specialist_dict.get(top_dept, ("Consultant", "বিশেষজ্ঞ"))
    
    emergency_keywords = ["chest pain", "shortness of breath", "unconscious", "stroke", "numbness", "heavy bleeding", "fracture", "seizure"]
    is_emergency = any(kw in processed_text.lower() for kw in emergency_keywords)
    
    out_lang = "bn" if is_bangla(complaint_text) or any(w in complaint_text.lower() for w in ['amar', 'buke', 'betha', 'matha', 'bomi', 'pete', 'kosto']) else "en"

    print("\n" + "=" * 65)
    if out_lang == "bn":
        print(f"📝 ইনপুট: \"{complaint_text}\"")
        print(f"🎯 প্রস্তাবিত বিভাগ: {dept_bn}")
        print(f"📊 নিশ্চিততা: {top_conf * 100:.2f}%")
        print(f"👨‍⚕️ পরামর্শক ডাক্তার: {spec_bn}")
        urgency = "🔴 জরুরি ইমার্জেন্সি (লেভেল ১)" if is_emergency else ("🟡 অতি জরুরি কেয়ার (লেভেল ২)" if top_conf < 0.6 else "🟢 সাধারণ পরামর্শ (লেভেল ৩)")
        print(f"🚨 জরুরি পর্যায়: {urgency}")
        print("\n📈 শীর্ষ ৩টি সম্ভাব্য বিভাগ:")
        for dept, conf in sorted_probs[:3]:
            print(f"   • {BANGLA_DEPT_MAP.get(dept, dept):<40}: {conf * 100:.2f}%")
    else:
        print(f"📝 Input: \"{complaint_text}\"")
        print(f"🎯 Proposed Department: {top_dept}")
        print(f"📊 Confidence Score: {top_conf * 100:.2f}%")
        print(f"👨‍⚕️ Specialist Doctor: {spec_en}")
        urgency = "🔴 EMERGENCY (Level 1)" if is_emergency else ("🟡 URGENT (Level 2)" if top_conf < 0.6 else "🟢 ROUTINE (Level 3)")
        print(f"🚨 Priority: {urgency}")
        print("\n📈 Top 3 Possible Departments:")
        for dept, conf in sorted_probs[:3]:
            print(f"   • {dept:<35}: {conf * 100:.2f}%")
    print("=" * 65)
    return top_dept, top_conf

# Sample Test Cases
test_samples = [
    "আমার বুকে প্রচণ্ড চাপ ও ব্যথা হচ্ছে এবং শ্বাস নিতে কষ্ট হচ্ছে", # Bangla
    "amar matha onek betha r bomi hocche 2 din dhore",            # Banglish
    "আমার বাচ্চার ৩ দিন ধরে তীব্র জ্বর আর শরীরে লাল র‍্যাশ উঠেছে",  # Bangla
    "Severe abdominal pain and burning in stomach after food",    # English
    "Knee joint swelling and severe pain after a football injury", # English
    "Red itchy skin rash with peeling over arms"                   # English
]

print("\n🚀 বিভিন্ন ভাষার ৬টি টেস্ট কেস রান করা হচ্ছে:\n")
for sample in test_samples:
    predict_medical_complaint(sample)

print("\n🎉 আপনার আপগ্রেডেড মডেল প্রস্তুত! যেকোনো সমস্যায় টেস্ট করতে লিখুন:")
print("predict_medical_complaint(\"আপনার যেকোনো সমস্যা এখানে লিখুন\")")
