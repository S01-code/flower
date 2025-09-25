# Jupyter Notebook Setup (run this in a cell before the rest):
# %matplotlib notebook  # For interactive animation (recommended)
# OR %matplotlib inline  # For static, but use plt.show() for display

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.text import Text
import numpy as np
import math
import seaborn as sns  # For enhanced color palettes

# Set seaborn style for better visuals
sns.set_style("whitegrid", {'grid.linestyle': '--', 'grid.alpha': 0.3})
sns.set_palette("husl")  # Vibrant color cycle

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(12, 9))  # Larger for labels
ax.set_xlim(-200, 200)
ax.set_ylim(-250, 150)
ax.set_aspect('equal')
ax.set_facecolor('lightblue')
ax.axis('off')  # Hide axes
plt.title("", fontsize=16)  # Dynamic title

# Colors (enhanced with seaborn palette)
BG_COLOR = 'lightblue'
CENTER_COLOR = 'gold'
STEM_COLOR = 'forestgreen'
LEAF_COLOR = 'darkgreen'
# Seaborn-inspired petal colors (more vibrant cycle)
PETAL_COLORS = sns.color_palette("husl", 12)  # 12 colors for 12 petals
PETAL_COLORS = [(int(c[0]*255), int(c[1]*255), int(c[2]*255)) for c in PETAL_COLORS]  # Convert to RGB

# Animation parameters (different/custom timings)
num_petals = 12
petal_length = 50  # For complex PathPatch
petal_width = 30
center_radius = 25
stem_height = 220
leaf_size = 30
total_frames = 600  # Longer for sway
center_fade_duration = 40  # Faster fade-in
bloom_duration = 40  # Faster per-petal bloom
bloom_stagger = 20  # Frames between petal starts (denser)
unfurl_duration = 20  # Quicker leaves
unfurl_stagger = 10  # Slight delay for wave effect
phase_delay = 20  # Pause between phases
sway_speed = 0.03  # Slower sway
label_duration = 10  # Frames for phase labels to show/fade

# Animation state
frame_count = 0
current_petal_index = 0
animation_phase = 0  # 0: center, 1: petals, 2: stem/leaves, 3: sway
petal_bloom_starts = [0] * num_petals
leaf_unfurl_starts = [0] * (num_petals // 2 * 2)  # 6 leaves
sway_angle = 0
phase_labels = []  # List for dynamic text

# Rotation matrix helper
def get_rotation_matrix(angle):
    return np.array([[math.cos(angle), -math.sin(angle)],
                     [math.sin(angle), math.cos(angle)]])

# Complex Petal Path using PathPatch (Bézier-like curve for realism)
def create_petal_path(center_x, center_y, angle_deg, length, width, rotation=0):
    angle_rad = math.radians(angle_deg + rotation)
    # Control points for a curved petal (tip, sides, base)
    # Start at base left
    verts = [
        (center_x + length * math.cos(angle_rad - math.pi/2), center_y + length * math.sin(angle_rad - math.pi/2)),  # Base left
        # Quadratic curve to tip (control point for curve)
        (center_x + length * 1.2 * math.cos(angle_rad), center_y + length * 1.2 * math.sin(angle_rad)),  # Tip
        (center_x + length * math.cos(angle_rad + math.pi/2), center_y + length * math.sin(angle_rad + math.pi/2)),  # Base right
        # Curve back to start
        (center_x + length * 0.8 * math.cos(angle_rad - math.pi/2), center_y + length * 0.8 * math.sin(angle_rad - math.pi/2)),  # Close curve
    ]
    # Add width variation (wider in middle)
    mid_x = center_x + (length * 0.5) * math.cos(angle_rad)
    mid_y = center_y + (length * 0.5) * math.sin(angle_rad)
    verts.insert(2, (mid_x - width/2 * math.sin(angle_rad), mid_y + width/2 * math.cos(angle_rad)))  # Left bulge
    verts.insert(3, (mid_x + width/2 * math.sin(angle_rad), mid_y - width/2 * math.cos(angle_rad)))  # Right bulge
    
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
    path = Path(verts, codes)
    return path

# Initialize center
center_patch = patches.Circle((0, 0), center_radius, color=CENTER_COLOR, alpha=0)
ax.add_patch(center_patch)

# Initialize petals with PathPatch
petals = []
for i in range(num_petals):
    angle = i * (360 / num_petals)
    color = PETAL_COLORS[i]
    # Start with zero size (scale later)
    path = create_petal_path(0, 0, angle, 0, 0)  # Initial zero size
    petal = patches.PathPatch(path, facecolor=color, alpha=0, lw=0)
    petals.append(petal)
    ax.add_patch(petal)

# Stem
stem_line = plt.Line2D([], [], color=STEM_COLOR, linewidth=10, alpha=0)
ax.add_line(stem_line)

# Leaves (Ellipses, but with rotation)
leaves = []
leaf_positions = [-70, -10, 60]  # Adjusted for longer stem
for i, pos in enumerate(leaf_positions):
    # Left leaf
    left_leaf = patches.Ellipse((-40, pos), 0, 0, angle=-30, color=LEAF_COLOR, alpha=0)
    leaves.append(left_leaf)
    ax.add_patch(left_leaf)
    # Right leaf
    right_leaf = patches.Ellipse((40, pos), 0, 0, angle=30, color=LEAF_COLOR, alpha=0)
    leaves.append(right_leaf)
    ax.add_patch(right_leaf)

# Dynamic title text
title_text = ax.text(0, 120, "Animated Blooming Flower", ha='center', va='center', fontsize=18, 
                     color='darkblue', alpha=0, transform=ax.transAxes, fontweight='bold')

# Phase label (bottom)
phase_label = ax.text(0, -0.05, "", ha='center', va='bottom', fontsize=12, 
                      color='black', alpha=0, transform=ax.transAxes)

def animate(frame):
    global frame_count, current_petal_index, animation_phase, sway_angle
    frame_count = frame
    local_sway = sway_angle  # For title sway
    
    # Update sway
    sway_angle += sway_speed
    rotation_matrix = get_rotation_matrix(sway_angle)
    
    # Phase 0: Center fade-in
    if animation_phase == 0:
        progress = min(frame / center_fade_duration, 1)
        center_patch.set_alpha(progress)
        title_text.set_alpha(progress)  # Fade title with center
        phase_label.set_text("Center Appearing...")
        phase_label.set_alpha(min((frame % (label_duration * 2)) / label_duration, 1) if frame < label_duration * 2 else 0)
        
        if frame >= center_fade_duration + phase_delay:
            animation_phase = 1
            current_petal_index = 0
            frame_count = 0
    
    # Phase 1: Petals bloom (staggered, complex PathPatch scaling)
    elif animation_phase == 1:
        phase_label.set_text("Petals Blooming...")
        label_progress = (frame % (label_duration * 3)) / label_duration
        phase_label.set_alpha(min(label_progress, 1) if label_progress < 1 else max(2 - label_progress, 0))
        
        for i, petal in enumerate(petals):
            if petal_bloom_starts[i] > 0:
                elapsed = frame - petal_bloom_starts[i]
                progress = min(elapsed / bloom_duration, 1)
                alpha = progress
                # Scale path for growth
                if progress > 0:
                    path = create_petal_path(0, 0, i * (360 / num_petals), 
                                             petal_length * progress, petal_width * progress, 
                                             progress * 15)  # Rotate as it blooms
                    petal.set_path(path)
                    petal.set_alpha(alpha)
                else:
                    petal.set_alpha(0)
        
        # Trigger next petal
        if frame % bloom_stagger == 0 and current_petal_index < num_petals:
            petal_bloom_starts[current_petal_index] = frame
            current_petal_index += 1
        
        # All petals done?
        if current_petal_index >= num_petals and frame - petal_bloom_starts[-1] >= bloom_duration:
            animation_phase = 2
            frame_count = 0
    
    # Phase 2: Stem and leaves
    elif animation_phase == 2:
        phase_label.set_text("Leaves Unfurling...")
        label_progress = (frame % (label_duration * 3)) / label_duration
        phase_label.set_alpha(min(label_progress, 1) if label_progress < 1 else max(2 - label_progress, 0))
        
        # Draw stem once
        if frame == 0:
            stem_line.set_data([0, 0], [center_radius, stem_height])
            stem_line.set_alpha(1)
        
        # Unfurl leaves with wave (left then right)
        for i, leaf in enumerate(leaves):
            pair_idx = i // 2
            side_delay = 0 if i % 2 == 0 else unfurl_stagger  # Left first
            if leaf_unfurl_starts[i] == 0 and frame % unfurl_duration == side_delay:
                leaf_unfurl_starts[i] = frame
            
            if leaf_unfurl_starts[i] > 0:
                elapsed = frame - leaf_unfurl_starts[i]
                progress = min(elapsed / unfurl_duration, 1)
                size = leaf_size * progress
                alpha = progress
                leaf.set_width(size)
                leaf.set_height(size * 0.7)
                leaf.set_alpha(alpha)
        
        # All leaves done?
        if all(leaf_unfurl_starts[i] > 0 and frame - leaf_unfurl_starts[i] >= unfurl_duration for i in range(len(leaves))):
            animation_phase = 3
            frame_count = 0
    
    # Phase 3: Sway (rotate everything)
    elif animation_phase == 3:
        phase_label.set_text("Flower Swaying...")
        phase_label.set_alpha(0.7)  # Persistent but faint
        
        # Rotate petals (apply to path center)
        for i, petal in enumerate(petals):
            base_angle = i * (360 / num_petals)
            dx = (petal_length / 2) * math.cos(math.radians(base_angle))
            dy = (petal_length / 2) * math.sin(math.radians(base_angle))
            rotated = rotation_matrix @ np.array([dx, dy])
            # Recreate path at rotated position
            path = create_petal_path(rotated[0], rotated[1], base_angle, petal_length, petal_width, 0)
            petal.set_path(path)
            petal.set_alpha(1)
        
        # Rotate leaves
        for i, leaf in enumerate(leaves):
            pos_y = leaf_positions[i // 2]
            side = -50 if i % 2 == 0 else 50
            dx, dy = side, pos_y
            rotated = rotation_matrix @ np.array([dx, dy])
            leaf.set_center((rotated[0], rotated[1]))
            leaf.set_width(leaf_size)
            leaf.set_height(leaf_size * 0.7)
            leaf.set_alpha(1)
        
        # Sway title slightly
        title_sway = math.sin(sway_angle * 2) * 5  # Subtle
        title_text.set_position((title_sway * 0.01, 1.1))  # Transform axes
    
    # Always draw center (full after phase 0)
    center_alpha = 1 if animation_phase > 0 else 0
    center_patch.set_alpha(center_alpha)
    
    return [center_patch] + petals + [stem_line] + leaves + [title_text, phase_label]

# Create animation (FPS=30 for balanced speed; higher = faster)
fps = 30
ani = animation.FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps, blit=False, repeat=True)

# Display (works in Jupyter with %matplotlib notebook or inline)
plt.tight_layout()
plt.show()

# Optional: Save as GIF (requires Pillow; adjust fps as needed)
# ani.save('enhanced_flower_bloom.gif', writer='pillow', fps=fps)

# Optional: Save as MP4 (requires FFmpeg; adjust fps as needed)
# ani.save('enhanced_flower_bloom.mp4', writer='ffmpeg', fps=fps, extra_args=['-vcodec', 'libx264'])