import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"
MODEL_PATH = SAVED_MODELS_DIR / "clinicalbert_department"

# Default Classes / Medical Departments
DEFAULT_DEPARTMENTS = [
    "Cardiology",
    "Neurology",
    "Orthopedics",
    "Gastroenterology",
    "Dermatology",
    "Pulmonology",
    "ENT (Otolaryngology)",
    "Urology",
    "Gynecology & Obstetrics",
    "Pediatrics",
    "Ophthalmology",
    "General Medicine"
]

# Urgency / Triage Red-Flag Keywords
EMERGENCY_KEYWORDS = [
    "chest pain", "cardiac arrest", "unconscious", "stroke", "paralysis",
    "sudden numbness", "heavy bleeding", "difficulty breathing", "severe trauma",
    "anaphylaxis", "cyanosis", "heart attack", "choking", "seizure"
]

URGENT_KEYWORDS = [
    "high fever", "severe pain", "fracture", "blood in urine", "vomiting blood",
    "deep laceration", "asthma attack", "dislocation", "acute abdominal pain"
]
