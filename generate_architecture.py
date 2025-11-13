"""
Generate architecture diagram for UAV AoI-Energy Simulator project.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import matplotlib.patheffects as path_effects

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')

# Colors
color_cli = '#4A90E2'
color_core = '#50C878'
color_models = '#FF6B6B'
color_utils = '#FFA500'
color_output = '#9B59B6'
color_config = '#E74C3C'

# Title
ax.text(8, 11.5, 'UAV-Assisted Energy and AoI-aware Communications Simulator', 
        ha='center', va='top', fontsize=20, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.3))

# ========== CLI Layer ==========
cli_box = FancyBboxPatch((0.5, 9.5), 15, 1.2, 
                         boxstyle="round,pad=0.1", 
                         facecolor=color_cli, edgecolor='black', linewidth=2, alpha=0.7)
ax.add_patch(cli_box)
ax.text(8, 10.4, 'CLI Entry Point (main.py)', ha='center', va='center', 
        fontsize=14, fontweight='bold', color='white')

# Commands
commands = ['run', 'compare-policies', 'sweep-alpha']
for i, cmd in enumerate(commands):
    x = 2 + i * 4.5
    cmd_box = Rectangle((x-0.4, 9.7), 0.8, 0.6, 
                       facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(cmd_box)
    ax.text(x, 10, cmd, ha='center', va='center', fontsize=10, fontweight='bold')

# ========== Configuration Layer ==========
config_box = FancyBboxPatch((0.5, 8), 3.5, 1.2, 
                           boxstyle="round,pad=0.1", 
                           facecolor=color_config, edgecolor='black', linewidth=2, alpha=0.7)
ax.add_patch(config_box)
ax.text(2.25, 8.6, 'Configuration', ha='center', va='center', 
        fontsize=12, fontweight='bold', color='white')
ax.text(2.25, 8.2, 'configs/default.yaml\nParameter Randomization', 
        ha='center', va='center', fontsize=9)

# ========== Core Modules ==========
core_modules = [
    ('env.py', 'Environment Models', 5.5, 8),
    ('aoi.py', 'AoI State', 9.5, 8),
    ('planner.py', 'Policies & Routing', 13.5, 8),
]

for x, (name, desc, x_pos, y_pos) in enumerate(core_modules):
    box = FancyBboxPatch((x_pos-1.2, y_pos), 2.4, 1.2, 
                        boxstyle="round,pad=0.1", 
                        facecolor=color_core, edgecolor='black', linewidth=2, alpha=0.7)
    ax.add_patch(box)
    ax.text(x_pos, y_pos+0.7, name, ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white')
    ax.text(x_pos, y_pos+0.3, desc, ha='center', va='center', 
            fontsize=8, color='white')

# ========== Simulation Engine ==========
sim_box = FancyBboxPatch((5.5, 6.2), 5, 1.3, 
                        boxstyle="round,pad=0.1", 
                        facecolor=color_models, edgecolor='black', linewidth=2.5, alpha=0.8)
ax.add_patch(sim_box)
ax.text(8, 7.1, 'sim.py', ha='center', va='center', 
        fontsize=14, fontweight='bold', color='white')
ax.text(8, 6.6, 'Simulation Loop\nTime Advance | Energy Drain | AoI Updates', 
        ha='center', va='center', fontsize=10, color='white')

# ========== Utility Modules ==========
utils = [
    ('metrics.py', 'Compute Metrics', 1, 6.2),
    ('viz.py', 'Generate Plots', 12.5, 6.2),
]

for name, desc, x_pos, y_pos in utils:
    box = FancyBboxPatch((x_pos-1, y_pos), 2, 1.3, 
                        boxstyle="round,pad=0.1", 
                        facecolor=color_utils, edgecolor='black', linewidth=2, alpha=0.7)
    ax.add_patch(box)
    ax.text(x_pos, y_pos+0.8, name, ha='center', va='center', 
            fontsize=11, fontweight='bold', color='white')
    ax.text(x_pos, y_pos+0.4, desc, ha='center', va='center', 
            fontsize=9, color='white')

# ========== Data Flow Arrows ==========
# CLI to Config
arrow1 = FancyArrowPatch((2.25, 8), (2.25, 8.5), 
                        arrowstyle='->', mutation_scale=20, 
                        linewidth=2, color='black', zorder=1)
ax.add_patch(arrow1)

# CLI to Core Modules
for x_pos in [5.5, 9.5, 13.5]:
    arrow = FancyArrowPatch((x_pos, 8), (x_pos, 8.5), 
                           arrowstyle='->', mutation_scale=20, 
                           linewidth=2, color='black', zorder=1)
    ax.add_patch(arrow)

# Core to Simulation
for x_pos in [5.5, 9.5, 13.5]:
    arrow = FancyArrowPatch((x_pos, 6.2), (x_pos, 7.5), 
                           arrowstyle='->', mutation_scale=20, 
                           linewidth=2, color='black', zorder=1)
    ax.add_patch(arrow)

# Simulation to Utils
arrow2 = FancyArrowPatch((7, 6.2), (1, 7.5), 
                        arrowstyle='->', mutation_scale=20, 
                        linewidth=2, color='black', zorder=1)
ax.add_patch(arrow2)

arrow3 = FancyArrowPatch((9, 6.2), (12.5, 7.5), 
                         arrowstyle='->', mutation_scale=20, 
                         linewidth=2, color='black', zorder=1)
ax.add_patch(arrow3)

# ========== Output Layer ==========
output_box = FancyBboxPatch((0.5, 0.5), 15, 4.5, 
                           boxstyle="round,pad=0.2", 
                           facecolor=color_output, edgecolor='black', linewidth=2.5, alpha=0.6)
ax.add_patch(output_box)
ax.text(8, 4.5, 'Outputs (runs/YYYYMMDD_HHMMSS/)', ha='center', va='center', 
        fontsize=14, fontweight='bold', color='white')

# Output files
outputs = [
    ('resolved_config.yaml', 2, 3.5),
    ('log.csv', 5, 3.5),
    ('*.png', 8, 3.5),
    ('summary.csv', 11, 3.5),
    ('subfolders/', 14, 3.5),
]

for name, x_pos, y_pos in outputs:
    file_box = Rectangle((x_pos-0.6, y_pos-0.3), 1.2, 0.6, 
                        facecolor='white', edgecolor='black', linewidth=1.5)
    ax.add_patch(file_box)
    ax.text(x_pos, y_pos, name, ha='center', va='center', 
            fontsize=9, fontweight='bold')

# Output descriptions
descriptions = [
    'Config\nTraceability', 'Time-series\nLogs', 'Plots with\nFooters', 
    'Summary\nTables', 'Per-run\nLogs'
]
for desc, x_pos in zip(descriptions, [2, 5, 8, 11, 14]):
    ax.text(x_pos, 2.5, desc, ha='center', va='center', 
            fontsize=8, style='italic', color='white')

# Arrow from Utils to Output
arrow4 = FancyArrowPatch((8, 6.2), (8, 4.8), 
                        arrowstyle='->', mutation_scale=25, 
                        linewidth=3, color='darkgreen', zorder=1)
ax.add_patch(arrow4)
ax.text(8.5, 5.3, 'Save', ha='left', va='center', 
        fontsize=10, fontweight='bold', color='darkgreen')

# ========== Legend ==========
legend_elements = [
    mpatches.Patch(facecolor=color_cli, alpha=0.7, label='CLI Layer'),
    mpatches.Patch(facecolor=color_config, alpha=0.7, label='Configuration'),
    mpatches.Patch(facecolor=color_core, alpha=0.7, label='Core Modules'),
    mpatches.Patch(facecolor=color_models, alpha=0.7, label='Simulation Engine'),
    mpatches.Patch(facecolor=color_utils, alpha=0.7, label='Utilities'),
    mpatches.Patch(facecolor=color_output, alpha=0.6, label='Outputs'),
]

ax.legend(handles=legend_elements, loc='upper right', fontsize=9, 
         framealpha=0.9, bbox_to_anchor=(0.98, 0.98))

# ========== Key Features Box ==========
features_box = FancyBboxPatch((0.5, 0.5), 3, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor='lightyellow', edgecolor='black', 
                             linewidth=2, alpha=0.8)
ax.add_patch(features_box)
ax.text(2, 1.8, 'Key Features', ha='center', va='top', 
        fontsize=11, fontweight='bold')
features_text = '• Auto Randomization\n• Session Folders\n• Config Footers\n• Alpha-Aware Sweep\n• Scenario Locking'
ax.text(2, 1.2, features_text, ha='center', va='top', 
        fontsize=8)

plt.tight_layout()
plt.savefig('docs/architecture.png', dpi=300, bbox_inches='tight', facecolor='white')
print("Architecture diagram saved to docs/architecture.png")
plt.close()

