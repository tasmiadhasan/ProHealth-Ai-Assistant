import os
import json
from typing import Dict, Any, List
from src.config import MODEL_PATH, DEFAULT_DEPARTMENTS
from src.utils import (
    clean_text,
    evaluate_triage_urgency,
    translate_to_english_if_needed,
    BANGLA_DEPARTMENT_MAP,
    BANGLA_SPECIALIST_MAP
)

class MedicalDepartmentPredictor:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or MODEL_PATH
        self.model = None
        self.tokenizer = None
        self.label_mapping = None
        self._load_model_if_available()

    def _load_model_if_available(self):
        """Loads trained PyTorch / HuggingFace model if present in saved_models directory."""
        if os.path.exists(self.model_dir) and (os.path.exists(os.path.join(self.model_dir, "config.json"))):
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                import torch
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
                self.model.eval()

                mapping_file = os.path.join(self.model_dir, "label_mapping.json")
                if os.path.exists(mapping_file):
                    with open(mapping_file, "r") as f:
                        raw_map = json.load(f)
                        self.label_mapping = {int(k): v for k, v in raw_map.items()}
                else:
                    self.label_mapping = {i: dept for i, dept in enumerate(DEFAULT_DEPARTMENTS)}
                print(" Successfully loaded fine-tuned Bio_ClinicalBERT model.")
            except Exception as e:
                print(f" Warning: Could not load transformer model ({e}). Using clinical fallback.")
                self.model = None
        else:
            self.model = None

    def _fallback_heuristic_prediction(self, text: str) -> Dict[str, float]:
        """
        Expert clinical keyword matching heuristic fallback.
        """
        text_lower = text.lower()
        dept_scores = {dept: 0.05 for dept in DEFAULT_DEPARTMENTS}

        keywords_map = {
            "Cardiology": ["chest pain", "heart", "palpitation", "cardiac", "angina", "pulse", "blood pressure", "hypertension", "arm numbness", "left arm"],
            "Neurology": ["headache", "migraine", "dizziness", "seizure", "numbness", "brain", "spine", "stroke", "tremor", "memory loss", "paralysis", "vertigo"],
            "Orthopedics": ["bone", "joint", "fracture", "knee", "back pain", "shoulder", "ligament", "muscle", "dislocation", "swelling in ankle", "spine ache"],
            "Gastroenterology": ["stomach", "vomiting", "diarrhea", "nausea", "abdominal pain", "gastric", "acidity", "indigestion", "constipation", "liver", "cramps"],
            "Dermatology": ["skin", "rash", "itching", "eczema", "acne", "allergy", "hair loss", "blister", "mole", "lesion", "peeling"],
            "Pulmonology": ["cough", "breathing", "shortness of breath", "asthma", "wheezing", "chest tightness", "lungs", "sputum", "respiratory"],
            "ENT (Otolaryngology)": ["ear", "nose", "throat", "sinus", "tonsil", "hearing", "nasal", "earache", "sore throat", "tinnitus"],
            "Urology": ["urine", "urinary", "kidney", "bladder", "burning urination", "flank pain", "prostate", "frequent urination", "uti"],
            "Gynecology & Obstetrics": ["pregnancy", "period", "menstrual", "pelvic pain", "vaginal", "ovary", "uterus", "cramps"],
            "Pediatrics": ["child", "baby", "infant", "toddler", "growth", "newborn", "pediatric"],
            "Ophthalmology": ["eye", "vision", "blur", "red eye", "cataract", "retina", "cornea", "eye pain", "dry eye"],
            "General Medicine": ["fever", "weakness", "fatigue", "body ache", "shivering", "malaise", "loss of appetite"]
        }

        for dept, words in keywords_map.items():
            for w in words:
                if w in text_lower:
                    dept_scores[dept] += 1.8

        total = sum(dept_scores.values())
        return {dept: (score / total) for dept, score in dept_scores.items()}

    def predict(self, complaint_text: str) -> Dict[str, Any]:
        """
        Classifies medical complaints with support for Pure Bangla, Banglish, and English.
        """
        raw_text = complaint_text.strip() if complaint_text else ""
        if not raw_text:
            return {"error": "Empty complaint text provided."}

        # 1. Translate / Normalize Bangla or Banglish into Clinical English
        english_text, detected_lang = translate_to_english_if_needed(raw_text)
        cleaned = clean_text(english_text)

        # 2. Evaluate Clinical Urgency / Triage
        triage_info = evaluate_triage_urgency(cleaned, lang=detected_lang)

        # 3. Model Inference or Heuristic Fallback
        heuristic_scores = self._fallback_heuristic_prediction(cleaned)
        if self.model is not None and self.tokenizer is not None:
            import torch
            inputs = self.tokenizer(cleaned, return_tensors="pt", truncation=True, max_length=256, padding="max_length")
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=1).squeeze().tolist()
                
            bert_dict = {self.label_mapping.get(i, f"Dept {i}"): float(probs[i]) for i in range(len(probs))}
            
            # Hybrid Clinical Ensemble: 75% fine-tuned BERT + 25% verified clinical prior
            prob_dict = {}
            for dept in bert_dict.keys():
                b_score = bert_dict.get(dept, 0.0)
                # Map heuristic department names to 13 unified departments
                h_score = heuristic_scores.get(dept, 0.0)
                if dept == "Cardiology & Pulmonology":
                    h_score = max(h_score, heuristic_scores.get("Cardiology", 0.0), heuristic_scores.get("Pulmonology", 0.0))
                elif dept == "Urology & Nephrology":
                    h_score = max(h_score, heuristic_scores.get("Urology", 0.0))
                prob_dict[dept] = (0.75 * b_score) + (0.25 * h_score)
                
            total_sum = sum(prob_dict.values()) or 1.0
            prob_dict = {k: v / total_sum for k, v in prob_dict.items()}
        else:
            prob_dict = heuristic_scores

        # 4. Rank and Format Results
        sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        top_department, top_confidence = sorted_probs[0]

        specialist_lookup = {
            "Cardiology": "Cardiologist / Heart Specialist",
            "Cardiology & Pulmonology": "Cardiologist / Pulmonologist",
            "Neurology": "Neurologist / Neuro-Physician",
            "Orthopedics": "Orthopedic Surgeon",
            "Gastroenterology": "Gastroenterologist",
            "Dermatology": "Dermatologist / Skin Specialist",
            "Pulmonology": "Pulmonologist / Chest Specialist",
            "ENT (Otolaryngology)": "ENT Specialist",
            "Urology": "Urologist / Nephrologist",
            "Urology & Nephrology": "Urologist / Nephrologist",
            "Gynecology & Obstetrics": "Gynecologist & Obstetrician",
            "Pediatrics": "Pediatrician (Child Specialist)",
            "Ophthalmology": "Ophthalmologist (Eye Specialist)",
            "General Medicine": "General Physician / Internist",
            "Hematology & Oncology": "Hematologist & Oncologist",
            "Psychiatry & Behavioral Health": "Psychiatrist"
        }

        # Map to Bangla Names
        top_dept_bn = BANGLA_DEPARTMENT_MAP.get(top_department, top_department)
        specialist_bn = BANGLA_SPECIALIST_MAP.get(top_department, "বিশেষজ্ঞ ডাক্তার")

        return {
            "original_complaint": raw_text,
            "detected_language": detected_lang,
            "processed_english_text": cleaned,
            "recommended_department": top_department,
            "recommended_department_bn": top_dept_bn,
            "confidence_score": round(top_confidence * 100, 2),
            "specialist": specialist_lookup.get(top_department, "Consultant Physician"),
            "specialist_bn": specialist_bn,
            "triage_urgency": triage_info,
            "top_3_recommendations": [
                {
                    "department": dept,
                    "department_bn": BANGLA_DEPARTMENT_MAP.get(dept, dept),
                    "confidence_percentage": round(conf * 100, 2)
                }
                for dept, conf in sorted_probs[:3]
            ],
            "all_distribution": {k: round(v * 100, 2) for k, v in sorted_probs}
        }
