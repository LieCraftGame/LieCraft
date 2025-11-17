import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.patches import Patch

FAMILY_MAP = {
    "claude-3-7-sonnet-20250219": 'claude',
    'gpt-4o': 'gpt',
    'o4-mini': 'gpt',
    'gemini-2.5-flash': 'gemini',
    "meta-llama/Llama-3.1-70B-Instruct": 'llama',
    "meta-llama/Llama-3.3-70B-Instruct": 'llama',
    "google/gemma-3-27b-it": 'gemma',
    "google/gemma-3-12b-it": 'gemma',
    "Qwen/Qwen2.5-32B-Instruct": 'qwen',
    "Qwen/Qwen3-32B": 'qwen',
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B": 'deepseek',
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": 'deepseek',
    'mlabonne/gemma-3-27b-it-abliterated': 'gemma',
    'roslein/Qwen3-32B-abliterated': 'qwen',
    'huihui-ai/Llama-3.3-70B-Instruct-abliterated': 'llama',
    'huihui-ai/DeepSeek-R1-Distill-Qwen-32B-abliterated': 'deepseek',
}
NAME_MAP = {
    "claude-3-7-sonnet-20250219": 'Claude 3.7',
    'gpt-4o': 'GPT-4o',
    'o4-mini': 'o4-mini',
    'gemini-2.5-flash': 'Gemini 2.5 Flash',
    "meta-llama/Llama-3.1-70B-Instruct": 'Llama 3.1',
    "meta-llama/Llama-3.3-70B-Instruct": 'Llama 3.3',
    "google/gemma-3-27b-it": 'Gemma3-27B',
    "google/gemma-3-12b-it": 'Gemma3-12B',
    "Qwen/Qwen2.5-32B-Instruct": 'Qwen2.5',
    "Qwen/Qwen3-32B": 'Qwen3',
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B": 'Deepseek-Qwen',
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": 'Deepseek-Llama',
    'mlabonne/gemma-3-27b-it-abliterated': 'Gemma-Unsafe',
    'roslein/Qwen3-32B-abliterated': 'Qwen-Unsafe',
    'huihui-ai/Llama-3.3-70B-Instruct-abliterated': 'Llama-Unsafe',
    'huihui-ai/DeepSeek-R1-Distill-Qwen-32B-abliterated': 'Deepseek-Unsafe',
}

# Raw data: canonical keys
data = [
    ("claude-3-7-sonnet-20250219", 1.648, 46.88, 30, 64),
    ("gemini-2.5-flash", 1.718, 32.55, 262, 805),
    ("gpt-4o", 1.497, 30.25, 49, 162),
    ("meta-llama/Llama-3.1-70B-Instruct", 1.378, 29.78, 106, 356),
    ("meta-llama/Llama-3.3-70B-Instruct", 1.419, 28.35, 74, 261),
    ("deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", 1.299, 27.47, 89, 324),
    ("Qwen/Qwen2.5-32B-Instruct", 1.385, 26.71, 86, 322),
    ("o4-mini", 1.558, 25.98, 73, 281),
    ("google/gemma-3-12b-it", 1.108, 25.84, 85, 329),
    ("deepseek-ai/DeepSeek-R1-Distill-Llama-70B", 1.364, 25.58, 33, 129),
    ("Qwen/Qwen3-32B", 1.271, 20.83, 70, 336),
    ("google/gemma-3-27b-it", 1.188, 20.73, 113, 545)
]

# Custom family palette (must align with number of families)
custom_colors = ['#F4C476', '#295133', '#5C69FF', '#2D2C71', '#11101E', '#979797', '#B0473C']
families = sorted(set(FAMILY_MAP.values()))
FAMILY_PALETTE = dict(zip(families, custom_colors))

# Define a set of marker shapes to cycle within a family
marker_shapes = ['o', 's', '^', 'D', 'P', 'X', 'v', '<', '>']

# Build per-family model lists to assign unique markers
family_to_models = {}
for model_key, *_ in data:
    fam = FAMILY_MAP.get(model_key, "other")
    family_to_models.setdefault(fam, []).append(model_key)

# Assign a shape to each model within its family
model_marker = {}
for fam, models_in_family in family_to_models.items():
    for idx, mk in enumerate(models_in_family):
        shape = marker_shapes[idx % len(marker_shapes)]
        model_marker[mk] = shape

# Plotting
plt.figure(figsize=(10, 6))

# Determine max total for sizing
totals = [total for *_ , total in data]
max_total = max(totals)

for model_key, acc_score, win_rate, win_count, total in data:
    display_name = NAME_MAP.get(model_key, model_key)
    family = FAMILY_MAP.get(model_key, "other")
    color = FAMILY_PALETTE.get(family, (0.5, 0.5, 0.5))
    marker = model_marker.get(model_key, 'o')
    size = 250  # scale for visibility

    plt.scatter(acc_score, win_rate,
                s=size,
                color=color,
                alpha=0.7,
                marker=marker,
                edgecolor='k',
                linewidth=0.5,
                label=display_name)

# Build legend: one entry per model (handles created automatically, but dedupe)
handles, labels = plt.gca().get_legend_handles_labels()
# preserve order and avoid duplicates
seen = set()
unique = []
unique_labels = []
for h, l in zip(handles, labels):
    if l in seen:
        continue
    seen.add(l)
    unique.append(h)
    unique_labels.append(l)

plt.legend(unique, unique_labels,
           #title="Model",
           bbox_to_anchor=(1.02, 1),
           loc='upper left',
           fontsize=14,
           labelspacing=1.1,    # more space between rows
           title_fontsize=14,
           frameon=False)

plt.xlabel('Average Accusation Score', fontsize=16)
plt.ylabel('Defector Sabotage Rate (%)', fontsize=16)
plt.title('Defector Sabotage Rate vs Accusation Score', fontsize=16)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('win_rate_vs_accusations.png', dpi=200)
plt.savefig('win_rate_vs_accusations.pdf')