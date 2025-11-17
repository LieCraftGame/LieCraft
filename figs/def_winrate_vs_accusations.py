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
NAME_MAP = {  # 
    "claude-3-7-sonnet-20250219": 'Claude 3.7',
    'gpt-4o': 'GPT-4o',
    'o4-mini': 'o4-mini',
    'gemini-2.5-flash': 'Gemini 2.5 Flash',
    "meta-llama/Llama-3.1-70B-Instruct": 'Llama 3.1',
    "meta-llama/Llama-3.3-70B-Instruct": 'Llama',# 3.3',
    "google/gemma-3-27b-it": 'Gemma3', # 'Gemma3-27B',
    "google/gemma-3-12b-it": 'Gemma3-12B',
    "Qwen/Qwen2.5-32B-Instruct": 'Qwen2.5',
    "Qwen/Qwen3-32B": 'Qwen',#3',
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B": 'Deepseek',#-Qwen',
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": 'Deepseek-Llama',
    'mlabonne/gemma-3-27b-it-abliterated': 'Gemma-Unsafe',
    'roslein/Qwen3-32B-abliterated': 'Qwen-Unsafe',
    'huihui-ai/Llama-3.3-70B-Instruct-abliterated': 'Llama-Unsafe',
    'huihui-ai/DeepSeek-R1-Distill-Qwen-32B-abliterated': 'Deepseek-Unsafe',
}

# Data from the tables
data = [
    # Model name, Accusation Score, Win Rate (%), Wins, Total
    ("claude-3-7-sonnet-20250219", 1.648, 46.88, 30, 64),
    ("gemini-2.5-flash", 1.718, 32.55, 262, 805),
    ("gpt-4o", 1.497, 30.25, 49, 162),
    ("Llama-3.1-70B-Instruct", 1.378, 29.78, 106, 356),
    ("Llama-3.3-70B-Instruct", 1.419, 28.35, 74, 261),
    ("DeepSeek-R1-Distill-Qwen-32B", 1.299, 27.47, 89, 324),
    ("Qwen2.5-32B-Instruct", 1.385, 26.71, 86, 322),
    ("o4-mini", 1.558, 25.98, 73, 281),
    ("gemma-3-12b-it", 1.108, 25.84, 85, 329),
    ("DeepSeek-R1-Distill-Llama-70B", 1.364, 25.58, 33, 129),
    ("Qwen3-32B", 1.271, 20.83, 70, 336),
    ("gemma-3-27b-it", 1.188, 20.73, 113, 545)
]

# Extract data for plotting
models = [NAME_MAP[d[0]] for d in data]
accusation_scores = [d[1] for d in data]
win_rates = [d[2] for d in data]
wins = [d[3] for d in data]
totals = [d[4] for d in data]

# Create the plot
plt.figure(figsize=(8, 4))

# Create scatter plot with point sizes based on total games
families = sorted(set(FAMILY_MAP.values()))
palette_list = sns.color_palette('tab10', n_colors=len(families))
FAMILY_PALETTE = dict(zip(families, palette_list))
FAMILY_HANDLES = [Patch(color=FAMILY_PALETTE[f], label=f) for f in families]
scatter = plt.scatter(accusation_scores, win_rates,  alpha=0.7, cmap=FAMILY_HANDLES)#c=range(len(models)), cmap='viridis')

# Add labels for each point
for i, model in enumerate(models):
    # Shorten model names for better readability
   #  short_name = model.replace("meta-llama/", "").replace("deepseek-ai/", "").replace("Qwen/", "").replace("google/", "")
    plt.annotate(model, (accusation_scores[i], win_rates[i]), 
                xytext=(5, 5), textcoords='offset points', fontsize=14, alpha=0.8)

# Customize the plot
plt.xlabel('Average Accusation Score', fontsize=16)
plt.ylabel('Defector Sabotage Rate (%)', fontsize=16)
plt.title('Defector Sabotage Rate vs Accusation Score', fontsize=16)
plt.grid(True, alpha=0.3)




plt.legend()
plt.tight_layout()
# plt.show()
plt.savefig('win_rate_vs_accusations.png')
plt.savefig('win_rate_vs_accusations.pdf')

# Print summary statistics
print("Model Performance Summary:")
print("=" * 50)
for model, acc_score, win_rate, wins, total in data:
    print(f"{model:35} | Acc: {acc_score:5.3f} | Win Rate: {win_rate:5.1f}% | Games: {total:4d}")
