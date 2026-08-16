"""
Dataset Preprocessing Pipeline for Medical Complaint Classification
Processes `data/raw/mtsamples.csv` into clean, balanced train/val/test splits.
"""

import os
import sys
import json
import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "mtsamples.csv"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Specialty Mapping & Standardization
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
    'Allergy / Immunology': 'General Medicine'  # Merged with General Medicine due to low sample count
}

def clean_clinical_text(text: str) -> str:
    """Removes noise, unwanted headers, boilerplate, and extra whitespace."""
    if not isinstance(text, str):
        return ""
    
    # Remove standard transcription section headers (e.g., 'HISTORY OF PRESENT ILLNESS:', 'SUBJECTIVE:')
    text = re.sub(r'([A-Z\s]{4,}):', ' ', text)
    
    # Remove special punctuation and multiple spaces
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[^\w\s\.,\?-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def preprocess_dataset():
    print("=" * 60)
    print("🏥 Starting Medical Dataset Preprocessing Pipeline")
    print("=" * 60)
    
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset not found at {RAW_DATA_PATH}")
        
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"📊 Original Dataset Shape: {df.shape}")
    
    # 1. Clean column names and strip whitespace
    df['medical_specialty'] = df['medical_specialty'].astype(str).str.strip()
    
    # 2. Filter and Map Clinical Specialties
    df['department'] = df['medical_specialty'].map(DEPARTMENT_MAPPING)
    df = df.dropna(subset=['department']).copy()
    print(f"🎯 Records after filtering administrative/non-clinical categories: {len(df)}")
    
    # 3. Handle Text (Combine description + transcription for rich clinical signal)
    df['description'] = df['description'].fillna('').astype(str)
    df['transcription'] = df['transcription'].fillna('').astype(str)
    
    # Combine description (chief complaint) and transcription (details)
    df['full_text'] = df['description'] + " " + df['transcription']
    df['cleaned_text'] = df['full_text'].apply(clean_clinical_text)
    
    # Filter out empty or very short records (< 20 characters)
    df = df[df['cleaned_text'].str.len() > 20].copy()
    print(f"✅ Records after removing empty/short text: {len(df)}")
    
    # 4. Encode Target Labels
    le = LabelEncoder()
    df['label'] = le.fit_transform(df['department'])
    
    label_mapping = {int(i): name for i, name in enumerate(le.classes_)}
    print(f"\n🏷️ Target Classes ({len(label_mapping)} Departments):")
    for idx, name in label_mapping.items():
        count = (df['label'] == idx).sum()
        print(f"   [{idx:02d}] {name:<32} (Count: {count})")
        
    # Save Label Mapping
    label_map_path = PROCESSED_DATA_DIR / "label_mapping.json"
    with open(label_map_path, "w") as f:
        json.dump(label_mapping, f, indent=4)
    print(f"\n💾 Saved Label Mapping to: {label_map_path}")
    
    # 5. Stratified Train / Validation / Test Split (80% Train, 10% Val, 10% Test)
    # Prepare dataframe for output
    final_df = df[['cleaned_text', 'department', 'label']].rename(columns={'cleaned_text': 'text'})
    
    train_df, temp_df = train_test_split(
        final_df, test_size=0.20, random_state=42, stratify=final_df['label']
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=42, stratify=temp_df['label']
    )
    
    print(f"\n📈 Split Summary:")
    print(f"   - Training Set:   {len(train_df)} samples ({len(train_df)/len(final_df)*100:.1f}%)")
    print(f"   - Validation Set: {len(val_df)} samples ({len(val_df)/len(final_df)*100:.1f}%)")
    print(f"   - Test Set:       {len(test_df)} samples ({len(test_df)/len(final_df)*100:.1f}%)")
    
    # 6. Save Processed CSVs
    final_df.to_csv(PROCESSED_DATA_DIR / "cleaned_dataset.csv", index=False)
    train_df.to_csv(PROCESSED_DATA_DIR / "train.csv", index=False)
    val_df.to_csv(PROCESSED_DATA_DIR / "val.csv", index=False)
    test_df.to_csv(PROCESSED_DATA_DIR / "test.csv", index=False)
    
    print(f"🎉 All processed datasets saved successfully in: {PROCESSED_DATA_DIR}")

if __name__ == "__main__":
    preprocess_dataset()
