from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

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

# Custom family palette (must align with number of families)
custom_colors = ['#F4C476', '#295133', '#5C69FF', '#2D2C71', '#11101E', '#979797', '#B0473C']
families = sorted(set(FAMILY_MAP.values()))
FAMILY_PALETTE = dict(zip(families, custom_colors))

if __name__ == '__main__':

    data_mean = defaultdict(list,
                {'Qwen/Qwen2.5-32B-Instruct': [np.float64(1.1037037037037036),
                  np.float64(1.1962962962962962),
                  np.float64(1.1777777777777778),
                  np.float64(1.1185185185185185)],
                 'Qwen/Qwen3-32B': [np.float64(1.1296296296296295),
                  np.float64(1.1814814814814816),
                  np.float64(1.2814814814814814),
                  np.float64(1.1814814814814814)],
                 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B': [np.float64(0.5222222222222221),
                  np.float64(0.5481481481481482),
                  np.float64(0.662962962962963),
                  np.float64(0.537037037037037)],
                 'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B': [np.float64(1.2851851851851852),
                  np.float64(1.3851851851851853),
                  np.float64(1.422222222222222),
                  np.float64(1.3888888888888888)],
                 'google/gemma-3-12b-it': [np.float64(1.3800000000000001),
                  np.float64(1.52),
                  np.float64(1.6600000000000001),
                  np.float64(1.5999999999999999)],
                 'google/gemma-3-27b-it': [np.float64(2.58),
                  np.float64(2.311111111111111),
                  np.float64(2.6599999999999997),
                  np.float64(2.66)],
                 'meta-llama/Llama-3.1-70B-Instruct': [np.float64(1.3766666666666667),
                  np.float64(1.4333333333333333),
                  np.float64(1.4037037037037037),
                  np.float64(1.348148148148148)],
                 'meta-llama/Llama-3.3-70B-Instruct': [np.float64(0.9185185185185184),
                  np.float64(0.8300000000000001),
                  np.float64(0.7606060606060606),
                  np.float64(0.8333333333333334)]})
    scales = [1, 10, 100, 1000]
    
    # Define a set of marker shapes to cycle within a family
    marker_shapes = ['o', 's', '^', 'D', 'P', 'X', 'v', '<', '>']

    # Build per-family model lists to assign unique markers
    family_to_models = {}
    for model_key, *_ in data_mean.items():
        fam = FAMILY_MAP.get(model_key, "other")
        family_to_models.setdefault(fam, []).append(model_key)
    # Assign a shape to each model within its family
    model_marker = {}
    for fam, models_in_family in family_to_models.items():
        for idx, mk in enumerate(models_in_family):
            shape = marker_shapes[idx % len(marker_shapes)]
            model_marker[mk] = shape
    
    plt.figure(figsize=(10, 4))
    for k, v in data_mean.items():
        family = FAMILY_MAP[k]
        name = NAME_MAP[k]
        marker = model_marker[k]
        color = FAMILY_PALETTE.get(family, (0.5, 0.5, 0.5))
        plt.plot(scales, v, label=name, color=color, marker=marker)

    handles, labels = plt.gca().get_legend_handles_labels()
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
    plt.grid(True, alpha=0.3)
    plt.title('Reward Scale vs Defector Selection', fontsize=18)
    plt.xlabel('Reward Scale', fontsize=17)
    plt.xscale('log')
    plt.ylabel('Defector Counts Per Game', fontsize=17)
    plt.tight_layout()
    plt.savefig('score_sensitivity_plot.png')
    plt.savefig('score_sensitivity_plot.pdf')


