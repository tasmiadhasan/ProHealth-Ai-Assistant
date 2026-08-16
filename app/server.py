"""
ProHealth AI Assistant - FastAPI Backend Server
Integrates Bio_ClinicalBERT AI Department Predictor, Hospital Portal Services & PDF Generator
"""

import os
import sys
import json
import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

# ReportLab for 100% reliable, non-blank vector PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predictor import MedicalDepartmentPredictor

app = FastAPI(
    title="ProHealth AI Assistant API",
    description="Intelligent Hospital Triage & Department Referral System",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Predictor
predictor = MedicalDepartmentPredictor()

# Static Directory Path
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Mock Doctors Database across all 13 Specialized Departments
# ---------------------------------------------------------
DOCTORS_DATABASE = [
    {
        "id": "doc-1",
        "name": "Prof. Dr. Rafiqul Islam",
        "name_bn": "অধ্যাপক ডাঃ রফিকুল ইসলাম",
        "department": "Cardiology & Pulmonology",
        "dept_key": "cardiology",
        "title": "Senior Consultant - Cardiology",
        "degrees": "MBBS, FCPS (Cardiology), MD (USA), FACC",
        "experience": "18+ Years",
        "room": "Room 402, Block A",
        "days": "Sat - Thu (5:00 PM - 9:00 PM)",
        "fee": "৳ 1,200",
        "rating": 4.9,
        "reviews": 342,
        "avatar": "👨‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-2",
        "name": "Dr. Farhana Yasmin",
        "name_bn": "ডাঃ ফারহানা ইয়াসমিন",
        "department": "Cardiology & Pulmonology",
        "dept_key": "cardiology",
        "title": "Associate Professor - Pulmonology",
        "degrees": "MBBS, DTCD, MD (Chest Diseases)",
        "experience": "12+ Years",
        "room": "Room 405, Block A",
        "days": "Sat, Mon, Wed (4:00 PM - 8:00 PM)",
        "fee": "৳ 1,000",
        "rating": 4.8,
        "reviews": 215,
        "avatar": "👩‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-3",
        "name": "Prof. Dr. Mahbubur Rahman",
        "name_bn": "অধ্যাপক ডাঃ মাহবুবুর রহমান",
        "department": "Orthopedics",
        "dept_key": "orthopedics",
        "title": "Chief Orthopedic & Spine Surgeon",
        "degrees": "MBBS, MS (Ortho), Fellow Arthroplasty (Singapore)",
        "experience": "20+ Years",
        "room": "Room 301, Block B",
        "days": "Daily except Friday (6:00 PM - 10:00 PM)",
        "fee": "৳ 1,500",
        "rating": 5.0,
        "reviews": 480,
        "avatar": "👨‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-4",
        "name": "Dr. Tanjina Akter",
        "name_bn": "ডাঃ তানজিনা আক্তার",
        "department": "Orthopedics",
        "dept_key": "orthopedics",
        "title": "Consultant - Trauma & Joint Reconstruction",
        "degrees": "MBBS, D-Ortho, FCPS (Ortho)",
        "experience": "10+ Years",
        "room": "Room 304, Block B",
        "days": "Sun, Tue, Thu (3:00 PM - 7:00 PM)",
        "fee": "৳ 1,000",
        "rating": 4.7,
        "reviews": 160,
        "avatar": "👩‍⚕️",
        "available_today": False
    },
    {
        "id": "doc-5",
        "name": "Dr. Shamim Ahmed",
        "name_bn": "ডাঃ শামীম আহমেদ",
        "department": "Neurology",
        "dept_key": "neurology",
        "title": "Senior Neuro-Physician & Stroke Specialist",
        "degrees": "MBBS, MD (Neurology), MACP (USA)",
        "experience": "15+ Years",
        "room": "Room 501, Block A",
        "days": "Sat - Thu (5:30 PM - 9:30 PM)",
        "fee": "৳ 1,300",
        "rating": 4.9,
        "reviews": 310,
        "avatar": "👨‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-6",
        "name": "Dr. Nusrat Jahan",
        "name_bn": "ডাঃ নুসরাত জাহান",
        "department": "Gastroenterology",
        "dept_key": "gastroenterology",
        "title": "Consultant - Gastroenterology & Hepatology",
        "degrees": "MBBS, FCPS (Medicine), MD (Gastro)",
        "experience": "11+ Years",
        "room": "Room 202, Block C",
        "days": "Sat - Wed (4:00 PM - 8:30 PM)",
        "fee": "৳ 1,000",
        "rating": 4.8,
        "reviews": 195,
        "avatar": "👩‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-7",
        "name": "Dr. Ahsan Habib",
        "name_bn": "ডাঃ আহসান হাবীব",
        "department": "Dermatology",
        "dept_key": "dermatology",
        "title": "Skin, Allergy & Laser Specialist",
        "degrees": "MBBS, DDV, FCPS (Dermatology)",
        "experience": "14+ Years",
        "room": "Room 108, Block C",
        "days": "Daily except Thursday (5:00 PM - 9:00 PM)",
        "fee": "৳ 1,000",
        "rating": 4.9,
        "reviews": 275,
        "avatar": "👨‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-8",
        "name": "Prof. Dr. Nazmul Huda",
        "name_bn": "অধ্যাপক ডাঃ নাজমুল হুদা",
        "department": "ENT (Otolaryngology)",
        "dept_key": "ent",
        "title": "Head of ENT & Head-Neck Surgery",
        "degrees": "MBBS, DLO, MS (ENT)",
        "experience": "22+ Years",
        "room": "Room 204, Block B",
        "days": "Sat - Wed (6:00 PM - 9:30 PM)",
        "fee": "৳ 1,400",
        "rating": 4.9,
        "reviews": 380,
        "avatar": "👨‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-9",
        "name": "Dr. Salma Begum",
        "name_bn": "ডাঃ সালমা বেগম",
        "department": "Gynecology & Obstetrics",
        "dept_key": "gynecology",
        "title": "Senior Gynecologist & High-Risk Pregnancy Specialist",
        "degrees": "MBBS, FCPS (Gynae & Obs), MRCOG (UK)",
        "experience": "16+ Years",
        "room": "Room 303, Block A",
        "days": "Sat - Thu (4:30 PM - 8:30 PM)",
        "fee": "৳ 1,200",
        "rating": 5.0,
        "reviews": 520,
        "avatar": "👩‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-10",
        "name": "Dr. Kamrul Hasan",
        "name_bn": "ডাঃ কামরুল হাসান",
        "department": "Pediatrics",
        "dept_key": "pediatrics",
        "title": "Associate Professor - Child Health & Neonatology",
        "degrees": "MBBS, DCH, MD (Pediatrics)",
        "experience": "13+ Years",
        "room": "Room 102, Block A (Kids Care)",
        "days": "Daily (5:00 PM - 9:00 PM)",
        "fee": "৳ 1,000",
        "rating": 4.9,
        "reviews": 410,
        "avatar": "👨‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-11",
        "name": "Dr. Masud Alam",
        "name_bn": "ডাঃ মাসুদ আলম",
        "department": "Urology & Nephrology",
        "dept_key": "urology",
        "title": "Consultant Urologist & Kidney Surgeon",
        "degrees": "MBBS, MS (Urology), Fellow Endourology",
        "experience": "14+ Years",
        "room": "Room 208, Block B",
        "days": "Sat, Mon, Wed (5:00 PM - 9:00 PM)",
        "fee": "৳ 1,100",
        "rating": 4.8,
        "reviews": 230,
        "avatar": "👨‍⚕️",
        "available_today": True
    },
    {
        "id": "doc-12",
        "name": "Dr. Arif Chowdhury",
        "name_bn": "ডাঃ আরিফ চৌধুরী",
        "department": "General Medicine",
        "dept_key": "general",
        "title": "Senior Consultant - Internal Medicine & Diabetology",
        "degrees": "MBBS, FCPS (Medicine), MACP (USA)",
        "experience": "17+ Years",
        "room": "Room 101, Block A",
        "days": "Daily (9:00 AM - 1:00 PM & 6:00 PM - 9:30 PM)",
        "fee": "৳ 1,000",
        "rating": 4.9,
        "reviews": 600,
        "avatar": "👨‍⚕️",
        "available_today": True
    }
]

# ---------------------------------------------------------
# Hospital Facilities Database
# ---------------------------------------------------------
FACILITIES_DATABASE = [
    {
        "title": "24/7 Emergency & Trauma Care",
        "title_bn": "২৪/৭ জরুরি ও ট্রমা সেন্টার",
        "desc": "Round-the-clock emergency physicians, dedicated crash-carts, and rapid-response resuscitation team.",
        "icon": "🚑",
        "badge": "24/7 Available"
    },
    {
        "title": "Modern ICU & CCU Suites",
        "title_bn": "আধুনিক আইসিইউ ও সিসিইউ",
        "desc": "Equipped with Hamilton C6 ventilators, multipara monitors, and continuous specialist monitoring.",
        "icon": "🏥",
        "badge": "Level 3 Critical Care"
    },
    {
        "title": "Advanced 3T MRI & 128-Slice CT",
        "title_bn": "উন্নত ৩টি এমআরআই ও সিটি স্ক্যান",
        "desc": "Ultra-high-definition diagnostic imaging for neurology, cardiology, and orthopedics.",
        "icon": "🔬",
        "badge": "High Precision"
    },
    {
        "title": "Automated Robotic Pathology",
        "title_bn": "অটোমেটেড ল্যাব ও প্যাথলজি",
        "desc": "100% computerized zero-error reports within fastest turnaround times.",
        "icon": "🧪",
        "badge": "ISO Certified"
    },
    {
        "title": "Neonatal & Pediatric Care (NICU)",
        "title_bn": "নবজাতক ও শিশু আইসিইউ (এনআইসিইউ)",
        "desc": "Specialized incubators, phototherapy, and dedicated pediatric intensive care specialists.",
        "icon": "👶",
        "badge": "Specialized Care"
    },
    {
        "title": "Modular Surgical Theatres",
        "title_bn": "মডুলার অপারেশন থিয়েটার",
        "desc": "HEPA-filtered laminar airflow OTs for orthopedic joint replacement, neurosurgery, and laparoscopy.",
        "icon": "🩺",
        "badge": "100% Sterile"
    }
]

# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------
# Request Models & Persistent Appointment Store
# ---------------------------------------------------------
class SymptomRequest(BaseModel):
    complaint: str

class AppointmentRequest(BaseModel):
    patient_name: str
    patient_phone: str
    patient_age: Optional[str] = None
    department: str
    doctor_id: Optional[str] = None
    doctor_name: Optional[str] = None
    preferred_date: str
    symptoms: Optional[str] = None
    user_email: Optional[str] = None

class PdfRequest(BaseModel):
    prediction_result: Dict[str, Any]
    language: str = "en"
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    patient_id: Optional[str] = None

APPOINTMENTS_FILE = PROJECT_ROOT / "data" / "appointments.json"

def load_appointments() -> List[Dict[str, Any]]:
    if not APPOINTMENTS_FILE.exists():
        return []
    try:
        with open(APPOINTMENTS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        return []

def save_appointments(data: List[Dict[str, Any]]):
    try:
        APPOINTMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(APPOINTMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving appointments: {e}")

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.post("/api/predict")
def predict_symptom(req: SymptomRequest):
    """Predicts department, triage urgency, and fetches matching specialist doctors."""
    if not req.complaint.strip():
        raise HTTPException(status_code=400, detail="Complaint text cannot be empty.")
    
    result = predictor.predict(req.complaint)
    recommended_dept = result["recommended_department"]
    
    # Match available doctors in recommended department
    matching_doctors = [
        doc for doc in DOCTORS_DATABASE 
        if doc["department"].lower() in recommended_dept.lower() or recommended_dept.lower() in doc["department"].lower()
    ]
    if not matching_doctors:
        # Fallback to general medicine if no direct match
        matching_doctors = [doc for doc in DOCTORS_DATABASE if doc["dept_key"] == "general"]
        
    result["recommended_doctors"] = matching_doctors
    return result

@app.get("/api/doctors")
def get_doctors(department: Optional[str] = None):
    """Returns list of doctors with optional department filtering."""
    if department and department.lower() != "all":
        return [doc for doc in DOCTORS_DATABASE if doc["dept_key"].lower() == department.lower()]
    return DOCTORS_DATABASE

@app.get("/api/facilities")
def get_facilities():
    """Returns hospital facilities and infrastructure."""
    return FACILITIES_DATABASE

@app.get("/api/stats")
def get_stats():
    """Returns live hospital stats for dashboard counters."""
    return {
        "specialized_departments": 25,
        "senior_specialists": 120,
        "successful_triages": 18450,
        "patient_satisfaction": "99.4%",
        "emergency_response_mins": 3
    }

@app.post("/api/book-appointment")
def book_appointment(req: AppointmentRequest):
    """Generates and saves an appointment confirmation ticket."""
    import uuid
    ticket_id = f"PH-{uuid.uuid4().hex[:6].upper()}"
    
    doc_info = next((d for d in DOCTORS_DATABASE if d["name"] == req.doctor_name or d["id"] == req.doctor_id), None)
    
    appointment_record = {
        "ticket_id": ticket_id,
        "patient_name": req.patient_name,
        "phone": req.patient_phone,
        "patient_age": req.patient_age or "N/A",
        "doctor_name": req.doctor_name or (doc_info["name"] if doc_info else "Assigned Specialist"),
        "doctor_title": doc_info["title"] if doc_info else "Specialist Consultant",
        "department": req.department,
        "date": req.preferred_date,
        "room": doc_info["room"] if doc_info else "OPD Desk 101",
        "time": doc_info["days"] if doc_info else "5:00 PM - 9:00 PM",
        "fee": doc_info["fee"] if doc_info else "৳ 1,000",
        "avatar": doc_info["avatar"] if doc_info else "👨‍⚕️",
        "symptoms": req.symptoms or "General Consultation",
        "user_email": (req.user_email or "").strip().lower(),
        "status": "Confirmed",
        "created_at": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    
    appointments = load_appointments()
    appointments.insert(0, appointment_record)
    save_appointments(appointments)
    
    return {
        "status": "confirmed",
        "ticket_id": ticket_id,
        "appointment": appointment_record,
        "patient_name": req.patient_name,
        "phone": req.patient_phone,
        "department": req.department,
        "doctor_name": req.doctor_name or (doc_info["name"] if doc_info else "Assigned Specialist"),
        "date": req.preferred_date,
        "message": f"আপনার অ্যাপয়েন্টমেন্ট সফলভাবে বুক করা হয়েছে। ট্র্যাকিং আইডি: {ticket_id}",
        "message_en": f"Appointment successfully booked. Confirmation ID: {ticket_id}"
    }

@app.get("/api/user/appointments")
def get_user_appointments(email: Optional[str] = None):
    """Fetches booked appointments for a logged-in Google user."""
    appointments = load_appointments()
    clean_email = (email or "").strip().lower()
    if clean_email:
        filtered = [a for a in appointments if (a.get("user_email") or "").strip().lower() == clean_email or not a.get("user_email")]
        return filtered
    return appointments

@app.delete("/api/user/appointments/{ticket_id}")
def cancel_user_appointment(ticket_id: str):
    """Cancels an appointment by ticket ID."""
    appointments = load_appointments()
    new_list = [a for a in appointments if a.get("ticket_id") != ticket_id]
    if len(new_list) == len(appointments):
        raise HTTPException(status_code=404, detail="Appointment not found.")
    save_appointments(new_list)
    return {"status": "success", "message": "Appointment cancelled successfully."}

# ---------------------------------------------------------
# 100% Reliable PDF Referral Generator (ReportLab)
# ---------------------------------------------------------
@app.post("/api/generate-pdf")
def generate_referral_pdf(req: PdfRequest):
    """Generates a clean, simple, and elegant hospital referral ticket PDF."""
    res = req.prediction_result
    triage = res.get("triage_urgency", {})
    level = triage.get("level", "routine").lower()
    is_bn = req.language == "bn"
    
    import random
    ticket_id = f"PH-REF-{random.randint(100000, 999999)}"
    now_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#0284C7")
    navy_dark = colors.HexColor("#0F172A")
    gray_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#CBD5E1")
    
    if level == "emergency":
        badge_text_color = colors.HexColor("#DC2626")
        badge_label = "LEVEL 1 - EMERGENCY CARE"
    elif level == "urgent":
        badge_text_color = colors.HexColor("#D97706")
        badge_label = "LEVEL 2 - URGENT CARE"
    else:
        badge_text_color = colors.HexColor("#059669")
        badge_label = "LEVEL 3 - ROUTINE CONSULTATION"

    title_style = ParagraphStyle(
        'HospitalTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=3
    )
    
    sub_style = ParagraphStyle(
        'HospitalSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748B")
    )

    sec_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=navy_dark
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyDark',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=navy_dark
    )

    elements = []

    # 1. Header with Hospital Brand
    header_data = [
        [
            Paragraph("<b>ProHealth Specialized Hospital</b><br/><font size=8 color='#64748B'>Plot 15, Road 71, Gulshan-2, Dhaka 1212 | Hotline: 10666</font><br/><font size=9.5 color='#0284C7'><b>OFFICIAL AI CLINICAL REFERRAL SLIP</b></font>", title_style),
            Paragraph(f"<b>Tracking ID:</b> {ticket_id}<br/><b>Date:</b> {now_str}<br/><font color='{badge_text_color.hexval()}'><b>{badge_label}</b></font>", sub_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[4.0 * inch, 3.0 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceBefore=4, spaceAfter=14))

    # 2. Patient Profile & Identification (Included if user signed in)
    elements.append(Paragraph("1. PATIENT IDENTIFICATION & PROFILE", sec_header_style))
    p_name = req.patient_name or "Guest Patient"
    p_email = req.patient_email or "Not Provided (Guest)"
    p_id = req.patient_id or ticket_id
    acc_status = "Verified Google Patient" if req.patient_email else "Guest Access"

    patient_data = [
        [
            Paragraph("<b>Patient Name:</b>", bold_body_style), Paragraph(f"<b>{p_name}</b>", body_style),
            Paragraph("<b>Patient ID / MRN:</b>", bold_body_style), Paragraph(f"<font size=8.5><b>{p_id}</b></font>", body_style)
        ],
        [
            Paragraph("<b>Google Email:</b>", bold_body_style), Paragraph(p_email, body_style),
            Paragraph("<b>Verification:</b>", bold_body_style), Paragraph(f"<font color='#059669'><b>{acc_status}</b></font>", body_style)
        ]
    ]
    patient_table = Table(patient_data, colWidths=[1.5 * inch, 2.2 * inch, 1.5 * inch, 1.8 * inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 10))

    # 3. Patient Complaint
    elements.append(Paragraph("2. PATIENT COMPLAINT / SYMPTOMS", sec_header_style))
    complaint_str = str(res.get("processed_english_text") or res.get("original_complaint", "N/A"))
    complaint_data = [
        [Paragraph("<b>Reported Symptoms:</b>", bold_body_style), Paragraph(complaint_str, body_style)],
        [Paragraph("<b>AI Diagnosis Engine:</b>", bold_body_style), Paragraph(f"Bio_ClinicalBERT (Confidence: {res.get('confidence_score', 0)}%)", body_style)],
    ]
    complaint_table = Table(complaint_data, colWidths=[2.0 * inch, 5.0 * inch])
    complaint_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), gray_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(complaint_table)
    elements.append(Spacer(1, 10))

    # 4. Recommended Department & Doctor
    elements.append(Paragraph("3. RECOMMENDED DEPARTMENT & SPECIALIST", sec_header_style))
    dept_name = res.get("recommended_department", "General Medicine")
    spec_name = res.get("specialist", "Consultant Physician")
    guidance = triage.get("guidance_en") or "Please consult the recommended specialist doctor for clinical evaluation."

    rec_data = [
        [Paragraph("<b>Department:</b>", bold_body_style), Paragraph(f"<font size=11 color='#0284C7'><b>{dept_name}</b></font>", body_style)],
        [Paragraph("<b>Suggested Doctor:</b>", bold_body_style), Paragraph(f"<b>{spec_name}</b>", body_style)],
        [Paragraph("<b>Clinical Guidance:</b>", bold_body_style), Paragraph(str(guidance), body_style)],
    ]
    rec_table = Table(rec_data, colWidths=[2.0 * inch, 5.0 * inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(rec_table)
    elements.append(Spacer(1, 10))

    # 5. Top 3 Probability Breakdown
    elements.append(Paragraph("4. TOP MATCHED DEPARTMENTS", sec_header_style))
    top_3 = res.get("top_3_recommendations", [])
    top3_table_data = [
        [Paragraph("<b>Rank</b>", bold_body_style), Paragraph("<b>Department Name</b>", bold_body_style), Paragraph("<b>Confidence Match</b>", bold_body_style)]
    ]
    for idx, item in enumerate(top_3[:3], 1):
        top3_table_data.append([
            Paragraph(f"#{idx}", body_style),
            Paragraph(str(item.get("department", "N/A")), body_style),
            Paragraph(f"<b>{item.get('confidence_percentage', 0)}%</b>", body_style)
        ])
    
    top3_table = Table(top3_table_data, colWidths=[1.0 * inch, 4.3 * inch, 1.7 * inch])
    top3_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ]))
    elements.append(top3_table)
    elements.append(Spacer(1, 20))

    # 5. Simple Footer & Reception Note
    footer_data = [
        [
            Paragraph("<b>Registration Note:</b><br/><font size=8 color='#64748B'>Please show this slip at the hospital reception/OPD counter for quick department check-in.</font>", body_style),
            Paragraph("<br/>_______________________<br/><b>ProHealth Desk</b>", ParagraphStyle('Sign', parent=body_style, alignment=1))
        ]
    ]
    footer_table = Table(footer_data, colWidths=[4.8 * inch, 2.2 * inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ]))
    elements.append(footer_table)
    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=4, spaceAfter=6))
    elements.append(Paragraph("<font size=7.5 color='#94A3B8'>Disclaimer: This referral ticket is generated by an AI assistant (Bio_ClinicalBERT) for automated initial patient routing. It does not replace definitive medical diagnosis by a physician.</font>", sub_style))

    # Build Document
    doc.build(elements)
    buffer.seek(0)

    filename = f"ProHealth_Referral_Ticket_{ticket_id}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ---------------------------------------------------------
# Static Files & SPA Route
# ---------------------------------------------------------
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(
        content={"message": "ProHealth AI Assistant API is running. UI is initializing."},
        status_code=200
    )

if __name__ == "__main__":
    print("🏥 Starting ProHealth AI Assistant Web Portal on http://localhost:8000 ...")
    uvicorn.run("app.server:app", host="0.0.0.0", port=8000, reload=True)
