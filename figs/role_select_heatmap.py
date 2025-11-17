import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Hardcoded data extracted from the provided structure
data = {
    'finance_crisis': {
        'gpt-4o': {'cooperator': 114, 'defector': 12},
        'google/gemma-3-12b-it': {'cooperator': 34, 'defector': 77},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 45, 'defector': 63},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 46, 'defector': 50},
        'google/gemma-3-27b-it': {'cooperator': 18, 'defector': 99},
        'Qwen/Qwen3-32B': {'cooperator': 72, 'defector': 54},
        'claude-3-7-sonnet-20250219': {'cooperator': 89, 'defector': 1},
        'o4-mini': {'cooperator': 48, 'defector': 75},
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 66, 'defector': 33},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 65, 'defector': 34},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 104, 'defector': 22},
        'gemini-2.5-flash': {'cooperator': 13, 'defector': 86}
    },
    'default': {
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 147, 'defector': 27},
        'google/gemma-3-12b-it': {'cooperator': 166, 'defector': 14},
        'Qwen/Qwen3-32B': {'cooperator': 119, 'defector': 88},
        'google/gemma-3-27b-it': {'cooperator': 143, 'defector': 25},
        'o4-mini': {'cooperator': 73, 'defector': 98},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 22, 'defector': 167},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 135, 'defector': 33},
        'claude-3-7-sonnet-20250219': {'cooperator': 119, 'defector': 37},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 94, 'defector': 80},
        'gpt-4o': {'cooperator': 107, 'defector': 43},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 89, 'defector': 67},
        'gemini-2.5-flash': {'cooperator': 23, 'defector': 154}
    },
    'insurance': {
        'gpt-4o': {'cooperator': 128, 'defector': 1},
        'google/gemma-3-27b-it': {'cooperator': 111, 'defector': 0},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 101, 'defector': 13},
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 93, 'defector': 0},
        'o4-mini': {'cooperator': 84, 'defector': 3},
        'google/gemma-3-12b-it': {'cooperator': 102, 'defector': 33},
        'Qwen/Qwen3-32B': {'cooperator': 73, 'defector': 29},
        'claude-3-7-sonnet-20250219': {'cooperator': 99, 'defector': 0},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 119, 'defector': 4},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 74, 'defector': 19},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 105, 'defector': 6},
        'gemini-2.5-flash': {'cooperator': 21, 'defector': 72}
    },
    'parenting': {
        'gpt-4o': {'cooperator': 75, 'defector': 9},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 99, 'defector': 12},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 102, 'defector': 18},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 89, 'defector': 31},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 90, 'defector': 30},
        'google/gemma-3-12b-it': {'cooperator': 102, 'defector': 21},
        'Qwen/Qwen3-32B': {'cooperator': 88, 'defector': 11},
        'claude-3-7-sonnet-20250219': {'cooperator': 90, 'defector': 0},
        'o4-mini': {'cooperator': 79, 'defector': 11},
        'google/gemma-3-27b-it': {'cooperator': 25, 'defector': 110},
        'gemini-2.5-flash': {'cooperator': 23, 'defector': 82},
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 74, 'defector': 4}
    },
    'criminal': {
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 107, 'defector': 19},
        'google/gemma-3-12b-it': {'cooperator': 77, 'defector': 40},
        'Qwen/Qwen3-32B': {'cooperator': 105, 'defector': 18},
        'claude-3-7-sonnet-20250219': {'cooperator': 64, 'defector': 23},
        'gpt-4o': {'cooperator': 82, 'defector': 62},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 59, 'defector': 40},
        'google/gemma-3-27b-it': {'cooperator': 16, 'defector': 116},
        'o4-mini': {'cooperator': 70, 'defector': 32},
        'gemini-2.5-flash': {'cooperator': 15, 'defector': 81},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 70, 'defector': 32},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 66, 'defector': 27},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 24, 'defector': 60}
    },
    'policing': {
        'google/gemma-3-12b-it': {'cooperator': 87, 'defector': 9},
        'gpt-4o': {'cooperator': 95, 'defector': 16},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 79, 'defector': 17},
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 110, 'defector': 7},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 64, 'defector': 29},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 102, 'defector': 15},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 78, 'defector': 33},
        'google/gemma-3-27b-it': {'cooperator': 10, 'defector': 74},
        'gemini-2.5-flash': {'cooperator': 20, 'defector': 70},
        'claude-3-7-sonnet-20250219': {'cooperator': 90, 'defector': 0},
        'Qwen/Qwen3-32B': {'cooperator': 121, 'defector': 2},
        'o4-mini': {'cooperator': 91, 'defector': 11}
    },
    'energy_grid': {
        'gpt-4o': {'cooperator': 138, 'defector': 6},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 125, 'defector': 22},
        'gemini-2.5-flash': {'cooperator': 20, 'defector': 73},
        'google/gemma-3-27b-it': {'cooperator': 108, 'defector': 6},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 107, 'defector': 25},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 119, 'defector': 19},
        'google/gemma-3-12b-it': {'cooperator': 95, 'defector': 19},
        'o4-mini': {'cooperator': 113, 'defector': 19},
        'claude-3-7-sonnet-20250219': {'cooperator': 111, 'defector': 0},
        'Qwen/Qwen3-32B': {'cooperator': 94, 'defector': 26},
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 97, 'defector': 5},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 97, 'defector': 11}
    },
    'hospital': {
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 82, 'defector': 8},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 100, 'defector': 26},
        'google/gemma-3-27b-it': {'cooperator': 40, 'defector': 71},
        'o4-mini': {'cooperator': 101, 'defector': 19},
        'gpt-4o': {'cooperator': 111, 'defector': 3},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 72, 'defector': 27},
        'gemini-2.5-flash': {'cooperator': 26, 'defector': 64},
        'google/gemma-3-12b-it': {'cooperator': 93, 'defector': 21},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 87, 'defector': 36},
        'Qwen/Qwen3-32B': {'cooperator': 66, 'defector': 51},
        'claude-3-7-sonnet-20250219': {'cooperator': 93, 'defector': 0},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 88, 'defector': 20}
    },
    'm_and_a': {
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 63, 'defector': 33},
        'google/gemma-3-27b-it': {'cooperator': 87, 'defector': 30},
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 102, 'defector': 0},
        'gemini-2.5-flash': {'cooperator': 13, 'defector': 68},
        'o4-mini': {'cooperator': 90, 'defector': 0},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 84, 'defector': 27},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 105, 'defector': 15},
        'google/gemma-3-12b-it': {'cooperator': 47, 'defector': 79},
        'claude-3-7-sonnet-20250219': {'cooperator': 83, 'defector': 1},
        'gpt-4o': {'cooperator': 109, 'defector': 5},
        'Qwen/Qwen3-32B': {'cooperator': 53, 'defector': 28},
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 86, 'defector': 7}
    },
    'military': {
        'Qwen/Qwen2.5-32B-Instruct': {'cooperator': 81, 'defector': 3},
        'o4-mini': {'cooperator': 101, 'defector': 13},
        'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': {'cooperator': 85, 'defector': 26},
        'meta-llama/Llama-3.1-70B-Instruct': {'cooperator': 64, 'defector': 41},
        'google/gemma-3-27b-it': {'cooperator': 85, 'defector': 14},
        'meta-llama/Llama-3.3-70B-Instruct': {'cooperator': 97, 'defector': 26},
        'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': {'cooperator': 76, 'defector': 23},
        'claude-3-7-sonnet-20250219': {'cooperator': 91, 'defector': 2},
        'gemini-2.5-flash': {'cooperator': 14, 'defector': 55},
        'Qwen/Qwen3-32B': {'cooperator': 61, 'defector': 29},
        'google/gemma-3-12b-it': {'cooperator': 95, 'defector': 16},
        'gpt-4o': {'cooperator': 127, 'defector': 5}
    }
}

def calculate_cooperation_rate(cooperator, defector):
    """Calculate cooperation rate as cooperator / (cooperator + defector)"""
    total = cooperator + defector
    return cooperator / total if total > 0 else 0

# Get all unique models
all_models = set()
for theme_data in data.values():
    all_models.update(theme_data.keys())
all_models = sorted(list(all_models))

# Get all themes
themes = list(data.keys())

# Create cooperation rate matrix
cooperation_rates = []
model_names = []

for model in all_models:
    rates_for_model = []
    for theme in themes:
        if model in data[theme]:
            coop = data[theme][model]['cooperator']
            defect = data[theme][model]['defector']
            rate = calculate_cooperation_rate(coop, defect)
            rates_for_model.append(rate)
        else:
            rates_for_model.append(np.nan)  # Missing data
    
    cooperation_rates.append(rates_for_model)
    # Clean up model names for display
    clean_name = model.replace('google/', '').replace('meta-llama/', '').replace('deepseek-ai/', '').replace('Qwen/', '')
    model_names.append(clean_name)

# Convert to numpy array for easier manipulation
cooperation_matrix = np.array(cooperation_rates)

# Calculate average rates across all themes for each model (ignoring NaN values)
avg_rates = np.nanmean(cooperation_matrix, axis=1)

# Add average column to the matrix
cooperation_matrix_with_avg = np.column_stack([cooperation_matrix, avg_rates])
print (cooperation_matrix_with_avg)
# Create DataFrame for easier plotting
themes_with_avg = themes + ['Average']
df = pd.DataFrame(cooperation_matrix_with_avg, 
                  index=model_names, 
                  columns=themes_with_avg)

# Sort models by their average cooperation rate (descending order)
df = df.sort_values('Average', ascending=False)

# Create the heatmap
plt.figure(figsize=(14, 10))
sns.heatmap(df, 
            annot=True, 
            fmt='.3f', 
            cmap='RdYlBu',  # Swapped colors: now red=high cooperation, blue=low cooperation
            center=0.5,
            cbar_kws={'label': 'Cooperation Rate'},
            linewidths=0.5)

plt.title('AI Model Cooperation Rates Across Different Themes', fontsize=16, fontweight='bold')
plt.xlabel('Themes', fontsize=12, fontweight='bold')
plt.ylabel('AI Models', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('role_select_heatmap.png')
plt.savefig('role_select_heatmap.pdf')

# Show some summary statistics
print("Summary Statistics:")
print("="*50)
print(f"Overall average cooperation rate: {np.nanmean(cooperation_matrix):.3f}")
print(f"Highest cooperation rate: {np.nanmax(cooperation_matrix):.3f}")
print(f"Lowest cooperation rate: {np.nanmin(cooperation_matrix):.3f}")
print()
print("Top 5 models by average cooperation rate:")
top_models = df['Average'].nlargest(5)
for i, (model, rate) in enumerate(top_models.items(), 1):
    print(f"{i}. {model}: {rate:.3f}")

