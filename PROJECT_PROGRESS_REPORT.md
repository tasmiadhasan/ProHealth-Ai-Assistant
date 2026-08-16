# <Project Progress Report>
# ProHealth AI Assistant

**Organisation:** Department of Computer Science & Engineering  
**Department:** CSE440 Capstone Project  
**Date:** August 16, 2026  
**Doc. Version:** 1.0.0  
**Template Version:** 3.0.1  

---

## Document Control Information

| Settings | Value |
| :--- | :--- |
| **Document Title:** | Project Progress Report |
| **Project Title:** | ProHealth AI Assistant — Intelligent Hospital Portal & Bio_ClinicalBERT Triage System |
| **Document Author:** | Tasmiad Hasan |
| **Project Owner (PO):** | Department of Computer Science & Engineering |
| **Project Manager (PM):** | Tasmiad Hasan |
| **Other Members:** | Project Core Team |
| **Doc. Version:** | 1.0.0 |
| **Date:** | August 16, 2026 |

---

## Table of Contents

- [1. PROJECT OVERVIEW](#1-project-overview)
  - [1.1. EXECUTIVE SUMMARY](#11-executive-summary)
  - [1.2. PROJECT STAKEHOLDERS](#12-project-stakeholders)
  - [1.3. MILESTONES AND DELIVERABLES](#13-milestones-and-deliverables)
  - [1.4. PROJECT PLAN (PER WORK PROGRESS)](#14-project-plan-per-work-progress)
- [2. PROJECT DETAILS](#2-project-details)
  - [2.1. SCOPE CHANGES](#21-scope-changes)
  - [2.2. MAJOR RISKS AND ACTIONS TAKEN](#22-major-risks-and-actions-taken)
  - [2.3. MAJOR ISSUES AND ACTIONS TAKEN](#23-major-issues-and-actions-taken)
  - [2.4. OTHER ON-GOING AND PLANNED ACTIONS](#24-other-on-going-and-planned-actions)
  - [2.5. ACHIEVEMENTS](#25-achievements)

---

# 1. PROJECT OVERVIEW

## 1.1. Executive Summary

**ProHealth AI Assistant** is an end-to-end intelligent hospital management portal and clinical triage referral system developed to eliminate patient misdirection, optimize hospital resource utilization, and accelerate emergency patient routing. 

The core technological engine is powered by fine-tuned **Bio_ClinicalBERT** (`emilyalsentzer/Bio_ClinicalBERT`), a deep transformer neural network specialized in clinical medical language processing. The system analyzes raw, unstructured, multilingual patient complaints written in Pure Bengali (বাংলা), phonetic Banglish (e.g., *"amar 2 din dhore buk betha korche"*), and English. It maps symptoms across **13 core medical specialties** (Cardiology, Orthopedics, Neurology, Gastroenterology, Dermatology, Pediatrics, Gynecology, ENT, Urology, Ophthalmology, Hematology, Psychiatry, and General Medicine) with multi-class confidence probability distributions.

Simultaneously, a deterministic rule-based triage evaluator inspects clinical red-flag triggers to classify urgency into **3 Tiers** (Level 1 Emergency, Level 2 Urgent, Level 3 Routine). The web application features a responsive glassmorphism portal, integrated **Google Identity Services (GIS) OAuth** patient authentication, an interactive appointment booking engine with slot reservation, an active **Patient Dashboard ("My Appointments")**, and vector-rendered **PDF referral slips** generated via Python ReportLab. The application has been fully deployed and verified live on **Render.com**.

---

## 1.2. Project Stakeholders

| Role | Details |
| :--- | :--- |
| **Project Due Date** | Final Evaluation / Capstone Submission 2026 |
| **Project Core Team (PCT)** | **Tasmiad Hasan** (Lead AI/ML Engineer & Full-Stack Developer) |
| **Other Stakeholders** | Course Supervisor, External Reviewers, Evaluation Board, Clinical Consultants |

---

## 1.3. Milestones and Deliverables

| ID | Milestone / Deliverable Name | Target Delivery Date | Actual Delivery Date | Status | Comments |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **M1** | Medical Dataset Collection & Clinical Annotation | 10 Jul 2026 | 10 Jul 2026 | **Achieved** | Multi-specialty clinical transcriptions dataset mapped to 13 departments. |
| **M2** | Bio_ClinicalBERT Fine-Tuning on Google Colab | 20 Jul 2026 | 20 Jul 2026 | **Achieved** | Fine-tuned transformer model with PyTorch; achieved 77% accuracy & 1.00 F1 on key classes. |
| **M3** | FastAPI Backend & Triage Logic Implementation | 28 Jul 2026 | 28 Jul 2026 | **Achieved** | RESTful endpoints for prediction, doctor rosters, booking, and PDF generation. |
| **M4** | Glassmorphism Web Portal & Bilingual Engine | 05 Aug 2026 | 05 Aug 2026 | **Achieved** | Full English & Bangla dynamic I18N toggle with hero slider and voice input. |
| **M5** | Google Identity Services OAuth & Patient Dashboard | 12 Aug 2026 | 12 Aug 2026 | **Achieved** | 1-tap Google login, appointment persistence in `appointments.json`, and cancellation. |
| **M6** | Vector PDF Referral Slip & Live Cloud Deployment | 16 Aug 2026 | 16 Aug 2026 | **Achieved** | ReportLab streaming PDF slips and live continuous deployment on Render.com. |

---

## 1.4. Project Plan (per Work Progress)

| Work Package / Task | Planned Start Date | Planned End Date | Actual Start Date | Actual End Date | Progress (In %) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **WP1: Data Engineering & Preprocessing** | 01 Jul 2026 | 10 Jul 2026 | 01 Jul 2026 | 10 Jul 2026 | **100%** |
| **WP2: Model Training & Evaluation** | 11 Jul 2026 | 22 Jul 2026 | 11 Jul 2026 | 20 Jul 2026 | **100%** |
| **WP3: Backend REST API Development** | 23 Jul 2026 | 30 Jul 2026 | 23 Jul 2026 | 28 Jul 2026 | **100%** |
| **WP4: Modern Web Frontend & I18N** | 31 Jul 2026 | 08 Aug 2026 | 31 Jul 2026 | 05 Aug 2026 | **100%** |
| **WP5: Auth, Dashboard & PDF Integration** | 09 Aug 2026 | 15 Aug 2026 | 09 Aug 2026 | 14 Aug 2026 | **100%** |
| **WP6: Cloud Deployment & Final QA** | 15 Aug 2026 | 17 Aug 2026 | 15 Aug 2026 | 16 Aug 2026 | **100%** |

---

# 2. PROJECT DETAILS

## 2.1. Scope Changes

| ID | Category<sup>1</sup> | Title | Description | Status<sup>2</sup> | Action Details (effort & responsible) | Size<sup>3</sup> | Priority<sup>4</sup> | Approval decided by | Actual Delivery Date |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :---: |
| **SC-01** | Technical | Google OAuth Migration | Replaced third-party Clerk SDK with official Google Identity Services (GIS) for unified client authentication. | **Implemented** | Refactored auth flow, integrated JWT decoding, and token storage in localStorage (Tasmiad Hasan). | 3 | 5 | PCT / Supervisor | 15 Aug 2026 |
| **SC-02** | New Requirement | Vector PDF Referral Slip | Replaced client-side HTML canvas PDF with server-side ReportLab vector PDF generator. | **Implemented** | Built `/api/generate-pdf` streaming endpoint to generate crisp, non-blank medical slips (Tasmiad Hasan). | 4 | 4 | PCT | 14 Aug 2026 |
| **SC-03** | Technical | Bilingual UI & Banglish Translation | Added full dynamic I18N system supporting Pure Bangla and phonetic Banglish complaints. | **Implemented** | Created rule-based phonetic normalizer and bilingual JSON dictionary in `app.js` (Tasmiad Hasan). | 3 | 5 | PCT | 08 Aug 2026 |
| **SC-04** | Technical | Live Cloud Hosting on Render | Configured production build commands with CPU PyTorch wheels to deploy within free cloud tier. | **Implemented** | Configured `render.yaml`, environment variables, and live HTTPS deployment (Tasmiad Hasan). | 2 | 4 | PCT | 16 Aug 2026 |

*Footnotes:*  
<sup>1</sup> **Categories:** New Requirement, Technical, Issue/Risk Related, Business Improvement.  
<sup>2</sup> **Status:** Submitted, Assessing, Waiting For Approval, Approved, Rejected, Postponed, Merged, Implemented.  
<sup>3</sup> **Size:** 5 = Very High, 4 = High, 3 = Medium, 2 = Low, 1 = Very Low.  
<sup>4</sup> **Priority:** 5 = Very High, 4 = High, 3 = Medium, 2 = Low, 1 = Very Low.  

---

## 2.2. Major Risks and Actions Taken

| ID | Category<sup>5</sup> | Risk Name | Description | Status<sup>6</sup> | Likelihood<sup>7</sup> | Impact<sup>8</sup> | Risk Level<sup>9</sup> (L×I) | Risk Owner | Risk Response Strategy<sup>10</sup> | Action Details | Target Date |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :---: |
| **R-01** | Technical | Transformer Cold Start Latency | Bio_ClinicalBERT model loading from disk on cold start causing initial request delay (>10s). | **Closed** | 4 | 4 | **16** | Tasmiad Hasan | **Reduce** | Implemented singleton model loader caching weights in RAM during startup. | 25 Jul 2026 |
| **R-02** | Technical | Cloud Bundle Size Limit | PyTorch standard GPU wheels (>2GB) exceeding serverless free memory quotas. | **Closed** | 5 | 4 | **20** | Tasmiad Hasan | **Reduce / Avoid** | Utilized lightweight PyTorch CPU wheel index (`--extra-index-url https://download.pytorch.org/whl/cpu`). | 15 Aug 2026 |
| **R-03** | IT / Security | Unauthorized Google Auth Domain | Google One-Tap rejecting web requests from unverified cloud domains. | **Closed** | 4 | 5 | **20** | Tasmiad Hasan | **Reduce** | Whitelisted production Render URL and local origins in Google Cloud Console OAuth credentials. | 16 Aug 2026 |
| **R-04** | Business | Medical Misclassification Risk | Non-critical complaints wrongly prioritized as Level 1 or vice-versa. | **Closed** | 2 | 5 | **10** | Tasmiad Hasan | **Reduce** | Added hybrid rule-based clinical red-flag override layer on top of BERT probabilities. | 02 Aug 2026 |

*Footnotes:*  
<sup>5</sup> **Categories:** Business, IT, People & Organisation, External and Legal.  
<sup>6</sup> **Status:** Proposed, Investigating, Waiting for Approval, Approved, Rejected, Closed.  
<sup>7</sup> **Likelihood:** 5 = Very High, 4 = High, 3 = Medium, 2 = Low, 1 = Very Low.  
<sup>8</sup> **Impact:** 5 = Very High, 4 = High, 3 = Medium, 2 = Low, 1 = Very Low.  
<sup>9</sup> **Risk Level:** Product of Likelihood and Impact (RL = L × I).  
<sup>10</sup> **Response Strategy:** Avoid, Transfer/Share, Reduce, Accept.  

---

## 2.3. Major Issues and Actions Taken

| ID | Category<sup>16</sup> | Title | Description | Status<sup>11</sup> | Action Details | Urgency<sup>12</sup> | Impact<sup>13</sup> | Size<sup>14</sup> | Target Date | Issue Owner |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **ISS-01** | Technical | Client-Side PDF Generation Blank Page Bug | `html2pdf.js` capturing black/blank canvases under modern CSS glassmorphism styles. | **Resolved** | Built Python ReportLab streaming endpoint (`/api/generate-pdf`) to generate pristine vector PDFs natively on the server. | 5 | 5 | 3 | 12 Aug 2026 | Tasmiad Hasan |
| **ISS-02** | Technical | JSON Serialization Failure in Appointments | Missing `import json` at module root causing booking requests to bypass disk persistence. | **Resolved** | Added `json` import and structured try-catch disk reader/writer in `server.py`. | 5 | 4 | 1 | 16 Aug 2026 | Tasmiad Hasan |
| **ISS-03** | UI / UX | Navbar Button Vertical Stacking | Sign In and Book Appointment buttons breaking onto two rows on narrower laptop screens. | **Resolved** | Enforced flexbox nowrap and unified 42px height constraints in `.nav-actions`. | 4 | 3 | 2 | 16 Aug 2026 | Tasmiad Hasan |
| **ISS-04** | UI / UX | Partial Language Synchronization | Dynamic text in Sign-In modal and Dashboard remaining in Bengali when switching to English. | **Resolved** | Populated `I18N.en` and `I18N.bn` dictionaries and added dynamic DOM updater triggers in `switchLanguage()`. | 4 | 4 | 2 | 16 Aug 2026 | Tasmiad Hasan |

*Footnotes:*  
<sup>11</sup> **Status:** Open, Postponed, Resolved, Closed.  
<sup>12</sup> **Urgency:** 5 = Very High, 4 = High, 3 = Medium, 2 = Low, 1 = Very Low.  
<sup>13</sup> **Impact:** 5 = Very High, 4 = High, 3 = Medium, 2 = Low, 1 = Very Low.  
<sup>14</sup> **Size:** 5 = Very High, 4 = High, 3 = Medium, 2 = Low, 1 = Very Low.  

---

## 2.4. Other On-Going and Planned Actions

| Actions | Due Date | Who & Comments |
| :--- | :---: | :--- |
| **Interactive Chatbot Triage Assistant** | Q4 2026 | Tasmiad Hasan — Multi-turn conversational symptom elicitation agent for uncertain complaints. |
| **Hospital EHR / FHIR Protocol Integration** | Q1 2027 | Tasmiad Hasan — Direct synchronization with electronic hospital patient management databases. |
| **Automated SMS & WhatsApp Booking Reminders** | Q1 2027 | Tasmiad Hasan — Integration of Twilio SMS gateway for live appointment ticket delivery. |

---

## 2.5. Achievements

| Project Highlights / Achievements | Comments |
| :--- | :--- |
| **State-of-the-Art Clinical Transformer (Bio_ClinicalBERT)** | Fine-tuned clinical BERT model on Google Colab, achieving **77.0% overall accuracy** and **1.00 F1-score** across multiple specialized departments (Ophthalmology, Urology, Gastroenterology). |
| **End-to-End Hospital Management Web Portal** | Built a responsive hospital website with 13 doctor directories, facilities explorer, speech recognition, and instant AI referral. |
| **Seamless Google Identity OAuth & Dashboard** | Implemented Google 1-Tap authentication, persistent booking storage, and real-time appointment management. |
| **100% Reliable Vector PDF Referral Generator** | Implemented ReportLab server-side PDF generator embedding verified patient name, Google ID, department, and doctor recommendations. |
| **Live Production Cloud Deployment** | Successfully deployed and hosted live on **[Render.com](https://prohealth-ai-assistant.onrender.com/)** with automated CI/CD from GitHub. |

---
*Report successfully generated in compliance with Template Version 3.0.1.*
