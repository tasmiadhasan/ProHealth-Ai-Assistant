import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# ProHealth AI Assistant - Project Progress & Status Pie Chart
# ----------------------------------------------------------------------

# 1. Overall Capstone Project Progress Status (Donut Style)
status_labels = [
    'Completed & Verified Modules (88%)',
    'Final QA & Evaluation Testing (7%)',
    'Planned Future Enhancements (5%)'
]

status_shares = [88, 7, 5]
status_colors = ['#10B981', '#0EA5E9', '#F59E0B']  # Green (Done), Blue (QA), Amber (Planned)
explode_status = (0.05, 0.03, 0.03)

fig, ax = plt.subplots(figsize=(9, 6.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')

wedges, texts, autotexts = ax.pie(
    status_shares,
    explode=explode_status,
    labels=status_labels,
    colors=status_colors,
    autopct='%1.0f%%',
    pctdistance=0.75,
    startangle=140,
    textprops=dict(color="#0F172A", fontsize=10.5, fontweight='bold'),
    wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2.5)
)

for autotext in autotexts:
    autotext.set_color('#FFFFFF')
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

# Center Text
ax.text(
    0, 0,
    'Overall Project\nStatus: 100%\nOn Schedule',
    ha='center',
    va='center',
    fontsize=11.5,
    fontweight='bold',
    color='#0F172A'
)

plt.title('ProHealth AI Assistant — Overall Project Progress Status', fontsize=13.5, fontweight='bold', color='#0F172A', pad=25)
plt.tight_layout()

output_progress_file = 'project_progress_pie_chart.png'
plt.savefig(output_progress_file, dpi=300, bbox_inches='tight')
print(f"[SUCCESS] Progress pie chart saved as: {output_progress_file}")


# ----------------------------------------------------------------------
# 2. Completed Deliverables Work-Package Contribution Breakdown
# ----------------------------------------------------------------------
wp_labels = [
    'WP1: Data Prep & MTSamples (17%)',
    'WP2: Bio_ClinicalBERT Fine-Tuning (22%)',
    'WP3: FastAPI Backend & API (18%)',
    'WP4: Web Portal & Bilingual UI (16%)',
    'WP5: Google Auth & Dashboard (14%)',
    'WP6: Vercel Deploy & PDF (13%)'
]

wp_weights = [17, 22, 18, 16, 14, 13]
wp_colors = ['#0284C7', '#2563EB', '#6366F1', '#8B5CF6', '#0D9488', '#10B981']
explode_wp = (0.02, 0.04, 0.02, 0.02, 0.02, 0.02)

fig2, ax2 = plt.subplots(figsize=(9.5, 6.8), dpi=300)
fig2.patch.set_facecolor('#FFFFFF')

wedges2, texts2, autotexts2 = ax2.pie(
    wp_weights,
    explode=explode_wp,
    labels=wp_labels,
    colors=wp_colors,
    autopct='%1.0f%%',
    pctdistance=0.75,
    startangle=130,
    textprops=dict(color="#0F172A", fontsize=9.5, fontweight='bold'),
    wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2)
)

for autotext in autotexts2:
    autotext.set_color('#FFFFFF')
    autotext.set_fontsize(9)
    autotext.set_fontweight('bold')

ax2.text(
    0, 0,
    'All 6 WPs\nAchieved\n(100%)',
    ha='center',
    va='center',
    fontsize=11.5,
    fontweight='bold',
    color='#0F172A'
)

plt.title('Work Package Deliverables Contribution Breakdown', fontsize=13.5, fontweight='bold', color='#0F172A', pad=25)
plt.tight_layout()

output_wp_file = 'project_wp_progress_pie_chart.png'
plt.savefig(output_wp_file, dpi=300, bbox_inches='tight')
print(f"[SUCCESS] Work-package contribution chart saved as: {output_wp_file}")
