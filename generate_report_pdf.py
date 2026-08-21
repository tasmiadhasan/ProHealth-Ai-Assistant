"""
Generates the official Project Progress Report PDF adhering to Template Version 3.0.1
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on cover page
        
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header
        self.drawRightString(A4[0] - 36, A4[1] - 25, "ProHealth AI Assistant | Project Progress Report")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, A4[1] - 30, A4[0] - 36, A4[1] - 30)
        
        # Footer
        self.line(36, 35, A4[0] - 36, 35)
        self.drawString(36, 24, "Date: 16 Aug 2026")
        self.drawCentredString(A4[0] / 2.0, 24, f"{self._pageNumber} / {page_count}")
        self.drawRightString(A4[0] - 36, 24, "Doc. Version: 1.0.0")
        self.restoreState()

def build_progress_report_pdf():
    pdf_path = "Project_Progress_Report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()
    primary = colors.HexColor("#0284C7")
    dark_text = colors.HexColor("#0F172A")
    muted_text = colors.HexColor("#334155")
    table_border = colors.HexColor("#CBD5E1")
    th_bg = colors.HexColor("#F1F5F9")

    # Custom styles
    cover_title = ParagraphStyle('CoverTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=primary, alignment=1, spaceAfter=8)
    cover_sub = ParagraphStyle('CoverSub', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=16, textColor=muted_text, alignment=1)
    
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=primary, spaceBefore=10, spaceAfter=6)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor("#1E293B"), spaceBefore=8, spaceAfter=4)
    
    body = ParagraphStyle('BodyText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=dark_text)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=dark_text)
    th_style = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=dark_text, alignment=1)
    cell_style = ParagraphStyle('TD', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=dark_text)
    cell_center = ParagraphStyle('TDCenter', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=dark_text, alignment=1)
    foot_style = ParagraphStyle('Foot', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=colors.HexColor("#64748B"))

    elements = []

    # ---------------- PAGE 1: COVER ----------------
    elements.append(Spacer(1, 70))
    elements.append(Paragraph("<b>DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING</b>", cover_sub))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>CSE440 Capstone Project</b>", cover_sub))
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("&lt;Project Progress Report&gt;", cover_sub))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>ProHealth AI Assistant</b>", cover_title))
    elements.append(Paragraph("Intelligent Hospital Portal & Bio_ClinicalBERT Triage System", cover_sub))
    elements.append(Spacer(1, 30))
    
    # Team Members Box on Cover Page
    members_cover_text = (
        "<b>Project Team Members:</b><br/>"
        "<b>1. Tasmiad Hasan</b> — ID: 2223017042 (Lead AI/ML Engineer & PM)<br/>"
        "<b>2. Al Mamun Oualid</b> — ID: 2312850642 (Data & Backend Engineer)<br/>"
        "<b>3. S M Tazbid Siddiqui</b> — ID: 2321986042 (Frontend UI/UX & QA)"
    )
    elements.append(Paragraph(members_cover_text, ParagraphStyle('CoverTeam', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=16, textColor=dark_text, alignment=1)))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<b>Date:</b> August 16, 2026", cover_sub))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>Doc. Version:</b> 1.0.0", cover_sub))
    elements.append(Spacer(1, 50))
    elements.append(Paragraph("<font size=8 color='#94A3B8'>Template Version: 3.0.1</font>", ParagraphStyle('Tmp', alignment=1)))
    elements.append(PageBreak())

    # ---------------- PAGE 2: DOC CONTROL & TOC ----------------
    elements.append(Paragraph("<b>Document Control Information</b>", h2))
    doc_control_data = [
        [Paragraph("<b>Settings</b>", th_style), Paragraph("<b>Value</b>", th_style)],
        [Paragraph("Document Title:", body_bold), Paragraph("Project Progress Report", cell_style)],
        [Paragraph("Project Title:", body_bold), Paragraph("ProHealth AI Assistant — Bio_ClinicalBERT Triage Portal", cell_style)],
        [Paragraph("Document Authors:", body_bold), Paragraph("Tasmiad Hasan (2223017042), Al Mamun Oualid (2312850642), S M Tazbid Siddiqui (2321986042)", cell_style)],
        [Paragraph("Project Owner (PO):", body_bold), Paragraph("Department of Computer Science & Engineering", cell_style)],
        [Paragraph("Project Manager (PM):", body_bold), Paragraph("Tasmiad Hasan (Student ID: 2223017042)", cell_style)],
        [Paragraph("Core Team Members:", body_bold), Paragraph("Tasmiad Hasan (2223017042), Al Mamun Oualid (2312850642), S M Tazbid Siddiqui (2321986042)", cell_style)],
        [Paragraph("Doc. Version:", body_bold), Paragraph("1.0.0", cell_style)],
        [Paragraph("Date:", body_bold), Paragraph("August 16, 2026", cell_style)],
    ]
    t_control = Table(doc_control_data, colWidths=[1.8 * inch, 5.2 * inch])
    t_control.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_control)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Table of Contents</b>", h2))
    toc_data = [
        [Paragraph("<b>1. PROJECT OVERVIEW</b>", body_bold), Paragraph("<b>3</b>", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.1. EXECUTIVE SUMMARY", cell_style), Paragraph("3", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.2. PROJECT STAKEHOLDERS & TEAM MEMBERS", cell_style), Paragraph("3", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.3. MILESTONES AND DELIVERABLES", cell_style), Paragraph("3", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.4. PROJECT PLAN & GANTT CHART", cell_style), Paragraph("4", cell_center)],
        [Paragraph("<b>2. PROJECT DETAILS</b>", body_bold), Paragraph("<b>4</b>", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.1. SCOPE CHANGES", cell_style), Paragraph("4", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.2. MAJOR RISKS AND ACTIONS TAKEN", cell_style), Paragraph("4", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.3. MAJOR ISSUES AND ACTIONS TAKEN", cell_style), Paragraph("5", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.4. OTHER ON-GOING AND PLANNED ACTIONS", cell_style), Paragraph("6", cell_center)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.5. ACHIEVEMENTS", cell_style), Paragraph("6", cell_center)],
    ]
    t_toc = Table(toc_data, colWidths=[6.2 * inch, 0.8 * inch])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_toc)
    elements.append(PageBreak())

    # ---------------- PAGE 3: SECTION 1 OVERVIEW ----------------
    elements.append(Paragraph("1. PROJECT OVERVIEW", h1))
    elements.append(Paragraph("1.1. Executive Summary", h2))
    exec_summary = (
        "<b>ProHealth AI Assistant</b> is an end-to-end intelligent hospital management portal and clinical triage referral "
        "system developed to eliminate patient misdirection, optimize hospital resource utilization, and accelerate emergency routing. "
        "Powered by <b>Bio_ClinicalBERT</b> (emilyalsentzer/Bio_ClinicalBERT, pre-trained on MIMIC-III & PubMed) and fine-tuned on "
        "the benchmark <b>MTSamples (Medical Transcriptions) Dataset</b> (mtsamples.csv), the system analyzes unstructured multilingual "
        "complaints (Pure Bengali, phonetic Banglish, and English) and maps them across <b>13 core medical specialties</b> with confidence probabilities. "
        "Simultaneously, a deterministic rule-based urgency triage evaluator identifies critical red-flag triggers across 3 levels (Emergency, Urgent, Routine). "
        "The application integrates Google Identity Services OAuth, interactive doctor booking, persistent database tracking, and ReportLab PDF referral tickets, "
        "and is fully deployed live on <b>Vercel</b>."
    )
    elements.append(Paragraph(exec_summary, body))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("1.2. Project Stakeholders & Team Members", h2))
    stakeholders_data = [
        [Paragraph("<b>Role / Field</b>", th_style), Paragraph("<b>Team Member / Details</b>", th_style), Paragraph("<b>Student ID</b>", th_style), Paragraph("<b>Key Responsibilities</b>", th_style)],
        [Paragraph("Project Lead & PM", body_bold), Paragraph("<b>Tasmiad Hasan</b>", cell_style), Paragraph("2223017042", cell_center), Paragraph("AI/ML Architecture, Bio_ClinicalBERT Fine-Tuning & Vercel Deploy", cell_style)],
        [Paragraph("Core Member", body_bold), Paragraph("<b>Al Mamun Oualid</b>", cell_style), Paragraph("2312850642", cell_center), Paragraph("Data Engineering, MTSamples Preprocessing & Backend API", cell_style)],
        [Paragraph("Core Member", body_bold), Paragraph("<b>S M Tazbid Siddiqui</b>", cell_style), Paragraph("2321986042", cell_center), Paragraph("Frontend UI/UX, Bilingual Localization, PDF Slip & Testing", cell_style)],
        [Paragraph("External Reviewers", body_bold), Paragraph("Course Supervisors & Evaluation Board", cell_style), Paragraph("—", cell_center), Paragraph("Capstone Review, Guidance & Final Examination", cell_style)],
    ]
    t_stakeholders = Table(stakeholders_data, colWidths=[1.4 * inch, 1.6 * inch, 1.0 * inch, 3.0 * inch])
    t_stakeholders.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_stakeholders)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("1.3. Milestones and Deliverables", h2))
    m_data = [
        [Paragraph("<b>ID</b>", th_style), Paragraph("<b>Milestone Name</b>", th_style), Paragraph("<b>Target Date</b>", th_style), Paragraph("<b>Actual Date</b>", th_style), Paragraph("<b>Status</b>", th_style), Paragraph("<b>Assigned</b>", th_style)],
        [Paragraph("M1", cell_center), Paragraph("MTSamples Dataset Annotation", cell_style), Paragraph("10 Jul 2026", cell_center), Paragraph("10 Jul 2026", cell_center), Paragraph("<font color='#059669'><b>Achieved</b></font>", cell_center), Paragraph("Al Mamun Oualid", cell_style)],
        [Paragraph("M2", cell_center), Paragraph("Bio_ClinicalBERT Fine-Tuning", cell_style), Paragraph("20 Jul 2026", cell_center), Paragraph("20 Jul 2026", cell_center), Paragraph("<font color='#059669'><b>Achieved</b></font>", cell_center), Paragraph("Tasmiad Hasan", cell_style)],
        [Paragraph("M3", cell_center), Paragraph("FastAPI Backend & Triage API", cell_style), Paragraph("28 Jul 2026", cell_center), Paragraph("28 Jul 2026", cell_center), Paragraph("<font color='#059669'><b>Achieved</b></font>", cell_center), Paragraph("Al Mamun Oualid", cell_style)],
        [Paragraph("M4", cell_center), Paragraph("Web Portal & Bilingual I18N", cell_style), Paragraph("05 Aug 2026", cell_center), Paragraph("05 Aug 2026", cell_center), Paragraph("<font color='#059669'><b>Achieved</b></font>", cell_center), Paragraph("S M Tazbid Siddiqui", cell_style)],
        [Paragraph("M5", cell_center), Paragraph("Google Auth & User Dashboard", cell_style), Paragraph("12 Aug 2026", cell_center), Paragraph("12 Aug 2026", cell_center), Paragraph("<font color='#059669'><b>Achieved</b></font>", cell_center), Paragraph("Tasmiad Hasan", cell_style)],
        [Paragraph("M6", cell_center), Paragraph("PDF Referral & Vercel Deploy", cell_style), Paragraph("16 Aug 2026", cell_center), Paragraph("16 Aug 2026", cell_center), Paragraph("<font color='#059669'><b>Achieved</b></font>", cell_center), Paragraph("All PCT Members", cell_style)],
    ]
    t_m = Table(m_data, colWidths=[0.4 * inch, 1.8 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 2.1 * inch])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_m)
    elements.append(PageBreak())

    # ---------------- PAGE 4: PLAN & GANTT CHART ----------------
    elements.append(Paragraph("1.4. Project Plan & Gantt Chart", h1))
    elements.append(Paragraph("<b>Project Execution Gantt Chart Timeline:</b>", h2))

    # Visual Gantt Chart Table in PDF
    gantt_chart_data = [
        [Paragraph("<b>Work Package / Phase</b>", th_style), Paragraph("<b>Lead</b>", th_style), Paragraph("<b>Jul W1-2</b>", th_style), Paragraph("<b>Jul W3</b>", th_style), Paragraph("<b>Jul W4</b>", th_style), Paragraph("<b>Aug W1</b>", th_style), Paragraph("<b>Aug W2</b>", th_style), Paragraph("<b>Status</b>", th_style)],
        [Paragraph("WP1: Data Engineering", cell_style), Paragraph("Al Mamun", cell_style), Paragraph("<font color='#0284C7'>■■■■■■■</font>", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("<font color='#059669'><b>Done</b></font>", cell_center)],
        [Paragraph("WP2: BERT Fine-Tuning", cell_style), Paragraph("Tasmiad", cell_style), Paragraph("—", cell_center), Paragraph("<font color='#0284C7'>■■■■■■■</font>", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("<font color='#059669'><b>Done</b></font>", cell_center)],
        [Paragraph("WP3: Backend REST API", cell_style), Paragraph("Al Mamun", cell_style), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("<font color='#0284C7'>■■■■■■■</font>", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("<font color='#059669'><b>Done</b></font>", cell_center)],
        [Paragraph("WP4: Web Portal & I18N", cell_style), Paragraph("S M Tazbid", cell_style), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("<font color='#0284C7'>■■■■■■■</font>", cell_center), Paragraph("—", cell_center), Paragraph("<font color='#059669'><b>Done</b></font>", cell_center)],
        [Paragraph("WP5: Auth & PDF Generator", cell_style), Paragraph("Tasmiad", cell_style), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("<font color='#0284C7'>■■■■■■■</font>", cell_center), Paragraph("<font color='#059669'><b>Done</b></font>", cell_center)],
        [Paragraph("WP6: Vercel Cloud Deploy", cell_style), Paragraph("All PCT", cell_style), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("—", cell_center), Paragraph("<font color='#10B981'>■■■■■■■</font>", cell_center), Paragraph("<font color='#059669'><b>Done</b></font>", cell_center)],
    ]
    t_gantt = Table(gantt_chart_data, colWidths=[1.8 * inch, 0.9 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch, 0.55 * inch])
    t_gantt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    elements.append(t_gantt)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Detailed Work Package Schedule Breakdown:</b>", h2))
    plan_data = [
        [Paragraph("<b>Work Package</b>", th_style), Paragraph("<b>Assigned Lead</b>", th_style), Paragraph("<b>Planned Start</b>", th_style), Paragraph("<b>Planned End</b>", th_style), Paragraph("<b>Actual Start</b>", th_style), Paragraph("<b>Actual End</b>", th_style), Paragraph("<b>Progress</b>", th_style)],
        [Paragraph("WP1: Data Engineering", cell_style), Paragraph("Al Mamun Oualid", cell_style), Paragraph("01 Jul 2026", cell_center), Paragraph("10 Jul 2026", cell_center), Paragraph("01 Jul 2026", cell_center), Paragraph("10 Jul 2026", cell_center), Paragraph("<b>100%</b>", cell_center)],
        [Paragraph("WP2: Model Training (Colab)", cell_style), Paragraph("Tasmiad Hasan", cell_style), Paragraph("11 Jul 2026", cell_center), Paragraph("22 Jul 2026", cell_center), Paragraph("11 Jul 2026", cell_center), Paragraph("20 Jul 2026", cell_center), Paragraph("<b>100%</b>", cell_center)],
        [Paragraph("WP3: Backend REST API", cell_style), Paragraph("Al Mamun Oualid", cell_style), Paragraph("23 Jul 2026", cell_center), Paragraph("30 Jul 2026", cell_center), Paragraph("23 Jul 2026", cell_center), Paragraph("28 Jul 2026", cell_center), Paragraph("<b>100%</b>", cell_center)],
        [Paragraph("WP4: Web Portal & I18N", cell_style), Paragraph("S M Tazbid Siddiqui", cell_style), Paragraph("31 Jul 2026", cell_center), Paragraph("08 Aug 2026", cell_center), Paragraph("31 Jul 2026", cell_center), Paragraph("05 Aug 2026", cell_center), Paragraph("<b>100%</b>", cell_center)],
        [Paragraph("WP5: Auth, Dashboard & PDF", cell_style), Paragraph("Tasmiad Hasan", cell_style), Paragraph("09 Aug 2026", cell_center), Paragraph("15 Aug 2026", cell_center), Paragraph("09 Aug 2026", cell_center), Paragraph("14 Aug 2026", cell_center), Paragraph("<b>100%</b>", cell_center)],
        [Paragraph("WP6: Vercel Deploy & QA", cell_style), Paragraph("All PCT Members", cell_style), Paragraph("15 Aug 2026", cell_center), Paragraph("17 Aug 2026", cell_center), Paragraph("15 Aug 2026", cell_center), Paragraph("16 Aug 2026", cell_center), Paragraph("<b>100%</b>", cell_center)],
    ]
    t_plan = Table(plan_data, colWidths=[1.8 * inch, 1.4 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch, 0.8 * inch])
    t_plan.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_plan)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. PROJECT DETAILS", h1))
    elements.append(Paragraph("2.1. Scope Changes", h2))
    scope_data = [
        [Paragraph("<b>ID</b>", th_style), Paragraph("<b>Category</b>", th_style), Paragraph("<b>Title & Description</b>", th_style), Paragraph("<b>Status</b>", th_style), Paragraph("<b>Size</b>", th_style), Paragraph("<b>Prio</b>", th_style), Paragraph("<b>Approved By</b>", th_style), Paragraph("<b>Date</b>", th_style)],
        [Paragraph("SC1", cell_center), Paragraph("Technical", cell_style), Paragraph("<b>Google OAuth Migration:</b> Switched from Clerk to Google Identity Services (GIS)", cell_style), Paragraph("Done", cell_center), Paragraph("3", cell_center), Paragraph("5", cell_center), Paragraph("PCT / Sup", cell_center), Paragraph("15 Aug", cell_center)],
        [Paragraph("SC2", cell_center), Paragraph("New Req", cell_style), Paragraph("<b>Vector PDF Generator:</b> Server-side ReportLab streaming referral tickets", cell_style), Paragraph("Done", cell_center), Paragraph("4", cell_center), Paragraph("4", cell_center), Paragraph("PCT", cell_center), Paragraph("14 Aug", cell_center)],
        [Paragraph("SC3", cell_center), Paragraph("Technical", cell_style), Paragraph("<b>Bilingual I18N & Banglish:</b> Dynamic Bangla/English UI & phonetic normalizer", cell_style), Paragraph("Done", cell_center), Paragraph("3", cell_center), Paragraph("5", cell_center), Paragraph("PCT", cell_center), Paragraph("08 Aug", cell_center)],
        [Paragraph("SC4", cell_center), Paragraph("Technical", cell_style), Paragraph("<b>Render Cloud Deployment:</b> CPU wheel optimization for free cloud tier", cell_style), Paragraph("Done", cell_center), Paragraph("2", cell_center), Paragraph("4", cell_center), Paragraph("PCT", cell_center), Paragraph("16 Aug", cell_center)],
    ]
    t_scope = Table(scope_data, colWidths=[0.35 * inch, 0.85 * inch, 2.7 * inch, 0.55 * inch, 0.45 * inch, 0.45 * inch, 0.95 * inch, 0.7 * inch])
    t_scope.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_scope)
    elements.append(Paragraph("<font size=7 color='#64748B'>Footnotes: Size/Priority scale: 5=Very High, 4=High, 3=Medium, 2=Low, 1=Very Low.</font>", foot_style))
    elements.append(PageBreak())

    # ---------------- PAGE 5: RISKS & ISSUES ----------------
    elements.append(Paragraph("2.2. Major Risks and Actions Taken", h2))
    risk_data = [
        [Paragraph("<b>ID</b>", th_style), Paragraph("<b>Risk Name</b>", th_style), Paragraph("<b>Description</b>", th_style), Paragraph("<b>Status</b>", th_style), Paragraph("<b>L</b>", th_style), Paragraph("<b>I</b>", th_style), Paragraph("<b>RL</b>", th_style), Paragraph("<b>Strategy</b>", th_style), Paragraph("<b>Action Details</b>", th_style)],
        [Paragraph("R1", cell_center), Paragraph("Cold Start Delay", cell_style), Paragraph("BERT loading from disk on first web request causing >10s latency", cell_style), Paragraph("Closed", cell_center), Paragraph("4", cell_center), Paragraph("4", cell_center), Paragraph("<b>16</b>", cell_center), Paragraph("Reduce", cell_center), Paragraph("Cached model in RAM at startup", cell_style)],
        [Paragraph("R2", cell_center), Paragraph("Cloud Size Quota", cell_style), Paragraph("GPU PyTorch wheels (>2GB) exceeding free cloud memory limits", cell_style), Paragraph("Closed", cell_center), Paragraph("5", cell_center), Paragraph("4", cell_center), Paragraph("<b>20</b>", cell_center), Paragraph("Avoid", cell_center), Paragraph("Used CPU wheel index", cell_style)],
        [Paragraph("R3", cell_center), Paragraph("Auth Origin Block", cell_style), Paragraph("Google OAuth blocking requests from unlisted live cloud URLs", cell_style), Paragraph("Closed", cell_center), Paragraph("4", cell_center), Paragraph("5", cell_center), Paragraph("<b>20</b>", cell_center), Paragraph("Reduce", cell_center), Paragraph("Whitelisted Render domain in GCP", cell_style)],
        [Paragraph("R4", cell_center), Paragraph("Medical Triage Error", cell_style), Paragraph("Potential misclassification of emergency cases", cell_style), Paragraph("Closed", cell_center), Paragraph("2", cell_center), Paragraph("5", cell_center), Paragraph("<b>10</b>", cell_center), Paragraph("Reduce", cell_center), Paragraph("Added rule-based red-flag layer", cell_style)],
    ]
    t_risk = Table(risk_data, colWidths=[0.35 * inch, 1.2 * inch, 1.9 * inch, 0.55 * inch, 0.3 * inch, 0.3 * inch, 0.35 * inch, 0.65 * inch, 1.4 * inch])
    t_risk.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_risk)
    elements.append(Paragraph("<font size=7 color='#64748B'>Risk Level RL = L × I (Scale 1-25). Strategy: Avoid, Transfer, Reduce, Accept.</font>", foot_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2.3. Major Issues and Actions Taken", h2))
    issue_data = [
        [Paragraph("<b>ID</b>", th_style), Paragraph("<b>Title</b>", th_style), Paragraph("<b>Description & Status</b>", th_style), Paragraph("<b>Action Taken</b>", th_style), Paragraph("<b>Urg</b>", th_style), Paragraph("<b>Imp</b>", th_style), Paragraph("<b>Size</b>", th_style), Paragraph("<b>Owner</b>", th_style)],
        [Paragraph("I1", cell_center), Paragraph("Blank PDF Bug", cell_style), Paragraph("Canvas capture rendering black screen<br/><b>[Resolved]</b>", cell_style), Paragraph("Switched to ReportLab vector generation", cell_style), Paragraph("5", cell_center), Paragraph("5", cell_center), Paragraph("3", cell_center), Paragraph("Tasmiad", cell_center)],
        [Paragraph("I2", cell_center), Paragraph("JSON Persistence", cell_style), Paragraph("Missing module import skipping booking saves<br/><b>[Resolved]</b>", cell_style), Paragraph("Imported json and added error handling", cell_style), Paragraph("5", cell_center), Paragraph("4", cell_center), Paragraph("1", cell_center), Paragraph("Tasmiad", cell_center)],
        [Paragraph("I3", cell_center), Paragraph("Navbar Stacking", cell_style), Paragraph("Buttons breaking into 2 rows on laptops<br/><b>[Resolved]</b>", cell_style), Paragraph("Enforced flexbox nowrap & height:42px", cell_style), Paragraph("4", cell_center), Paragraph("3", cell_center), Paragraph("2", cell_center), Paragraph("Tasmiad", cell_center)],
        [Paragraph("I4", cell_center), Paragraph("I18N Desync", cell_style), Paragraph("Modal text remaining Bangla on English toggle<br/><b>[Resolved]</b>", cell_style), Paragraph("Populated I18N dict & DOM hooks", cell_style), Paragraph("4", cell_center), Paragraph("4", cell_center), Paragraph("2", cell_center), Paragraph("Tasmiad", cell_center)],
    ]
    t_issue = Table(issue_data, colWidths=[0.35 * inch, 1.1 * inch, 1.8 * inch, 1.8 * inch, 0.4 * inch, 0.4 * inch, 0.4 * inch, 0.75 * inch])
    t_issue.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_issue)
    elements.append(PageBreak())

    # ---------------- PAGE 6: ACTIONS & ACHIEVEMENTS ----------------
    elements.append(Paragraph("2.4. Other On-Going and Planned Actions", h2))
    ongoing_data = [
        [Paragraph("<b>Actions</b>", th_style), Paragraph("<b>Due Date</b>", th_style), Paragraph("<b>Who & Comments</b>", th_style)],
        [Paragraph("<b>Interactive Chatbot Triage Assistant:</b> Multi-turn symptom questioning agent", cell_style), Paragraph("Q4 2026", cell_center), Paragraph("Tasmiad Hasan — Handling underspecified patient complaints", cell_style)],
        [Paragraph("<b>Hospital EHR / FHIR Protocol Integration:</b> Direct database sync", cell_style), Paragraph("Q1 2027", cell_center), Paragraph("Tasmiad Hasan — Integration with hospital management software", cell_style)],
        [Paragraph("<b>Automated SMS & WhatsApp Booking Delivery:</b> Instant SMS notifications", cell_style), Paragraph("Q1 2027", cell_center), Paragraph("Tasmiad Hasan — Twilio gateway integration for booking tickets", cell_style)],
    ]
    t_ongoing = Table(ongoing_data, colWidths=[3.2 * inch, 1.1 * inch, 2.7 * inch])
    t_ongoing.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_ongoing)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("2.5. Achievements", h2))
    achieve_data = [
        [Paragraph("<b>Project Highlights / Achievements</b>", th_style), Paragraph("<b>Comments</b>", th_style)],
        [Paragraph("<b>State-of-the-Art Clinical Transformer (Bio_ClinicalBERT)</b>", cell_style), Paragraph("Fine-tuned BERT model on Google Colab, achieving <b>77.0% overall accuracy</b> and <b>1.00 F1-score</b> on key departments (Ophthalmology, Urology, Gastroenterology).", cell_style)],
        [Paragraph("<b>End-to-End Hospital Management Web Portal</b>", cell_style), Paragraph("Built responsive hospital website with 13 doctor directories, facilities explorer, voice recognition, and instant AI triage referral.", cell_style)],
        [Paragraph("<b>Seamless Google Identity OAuth & Dashboard</b>", cell_style), Paragraph("Implemented 1-tap Google login, appointment persistence in data/appointments.json, and active patient management.", cell_style)],
        [Paragraph("<b>100% Reliable Vector PDF Referral Generator</b>", cell_style), Paragraph("Implemented server-side ReportLab vector PDF generator embedding patient name, Google ID, department, and doctor recommendations.", cell_style)],
        [Paragraph("<b>Live Production Cloud Deployment</b>", cell_style), Paragraph("Successfully deployed and hosted live on <b>Render.com</b> (https://prohealth-ai-assistant.onrender.com/) with automated CI/CD from GitHub.", cell_style)],
    ]
    t_achieve = Table(achieve_data, colWidths=[2.5 * inch, 4.5 * inch])
    t_achieve.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), th_bg),
        ('GRID', (0, 0), (-1, -1), 0.5, table_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_achieve)

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
    build_progress_report_pdf()
