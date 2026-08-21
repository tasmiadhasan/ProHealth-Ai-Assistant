import matplotlib.pyplot as plt

# -------------------------------------------------------------
# 1. Project Work Breakdown / Effort Distribution Pie Chart
# -------------------------------------------------------------
labels = [
    'Bio_ClinicalBERT Fine-Tuning (25%)',
    'Data Engineering & Preprocessing (20%)',
    'FastAPI Backend & Triage API (18%)',
    'Modern Web UI & Bilingual I18N (15%)',
    'Auth, Dashboard & PDF Engine (12%)',
    'Cloud Deployment & Testing (10%)'
]

sizes = [25, 20, 18, 15, 12, 10]
colors = ['#0284C7', '#0EA5E9', '#38BDF8', '#6366F1', '#10B981', '#F59E0B']
explode = (0.05, 0.03, 0.02, 0.02, 0.02, 0.02)  # Explode slices slightly for modern look

fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
fig.patch.set_facecolor('#FFFFFF')

wedges, texts, autotexts = ax.pie(
    sizes,
    explode=explode,
    labels=labels,
    colors=colors,
    autopct='%1.1f%%',
    pctdistance=0.75,
    startangle=140,
    textprops=dict(color="#0F172A", fontsize=10, fontweight='bold'),
    wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2)  # Donut style
)

for autotext in autotexts:
    autotext.set_color('#FFFFFF')
    autotext.set_fontsize(9.5)
    autotext.set_fontweight('bold')

# Center circle text
ax.text(0, 0, 'ProHealth AI\nProject Effort', ha='center', va='center', fontsize=12, fontweight='bold', color='#0F172A')

plt.title('Project Work Breakdown & Phase Distribution', fontsize=14, fontweight='bold', color='#0F172A', pad=25)
plt.tight_layout()

output_file = 'project_effort_pie_chart.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"[SUCCESS] Pie chart successfully saved as: {output_file}")


# -------------------------------------------------------------
# 2. Medical Specialty Dataset Distribution Pie Chart
# -------------------------------------------------------------
dept_labels = [
    'Cardiology & Pulmonology',
    'Orthopedics & Trauma',
    'Neurology & Stroke',
    'General Internal Medicine',
    'Urology & Nephrology',
    'Gastroenterology',
    'Gynecology & Obstetrics',
    'ENT (Otolaryngology)',
    'Hematology & Oncology',
    'Ophthalmology',
    'Pediatrics',
    'Psychiatry & Behavioral',
    'Dermatology & Laser'
]

dept_samples = [37, 35, 31, 27, 24, 23, 16, 10, 9, 8, 7, 6, 3]
dept_colors = [
    '#0284C7', '#0EA5E9', '#38BDF8', '#7DD3FC', '#6366F1',
    '#818CF8', '#10B981', '#34D399', '#F59E0B', '#FBBF24',
    '#EC4899', '#8B5CF6', '#14B8A6'
]

fig2, ax2 = plt.subplots(figsize=(11, 7.5), dpi=300)
fig2.patch.set_facecolor('#FFFFFF')

wedges2, texts2, autotexts2 = ax2.pie(
    dept_samples,
    labels=dept_labels,
    colors=dept_colors,
    autopct='%1.1f%%',
    pctdistance=0.8,
    startangle=120,
    textprops=dict(color="#0F172A", fontsize=9.5, fontweight='bold'),
    wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=1.5)
)

for autotext in autotexts2:
    autotext.set_color('#FFFFFF')
    autotext.set_fontsize(8.5)
    autotext.set_fontweight('bold')

ax2.text(0, 0, '13 Clinical\nDepartments', ha='center', va='center', fontsize=12, fontweight='bold', color='#0F172A')

plt.title('MTSamples Clinical Dataset — 13 Medical Departments Distribution', fontsize=13.5, fontweight='bold', color='#0F172A', pad=25)
plt.tight_layout()

output_file2 = 'dataset_departments_pie_chart.png'
plt.savefig(output_file2, dpi=300, bbox_inches='tight')
print(f"[SUCCESS] Dataset Pie chart successfully saved as: {output_file2}")
