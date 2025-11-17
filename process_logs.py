import sys
import glob
import json
from collections import defaultdict
import pandas as pd


# aggregator[(model, theme)] = { 'n_cooperator': int, 'n_defector': int, 'total': int }
aggregator = defaultdict(lambda: {'n_cooperator': 0, 'n_defector': 0, 'total': 0, 'n_games': 0})

for path in glob.glob('*.json'):
    with open(path, 'r') as f:
        data = json.load(f)

    # assume all players use same model
    # TODO change when players differ
    model = data['config']['players'][0]['model_name']
    prompt = data['prompt_templates']['system_prompt']
    try:
        theme = data['config']['theme']
    except:
        theme = None        
        raise ValueError(prompt + path)
    
    if model is None:
        print('Model is None ' + path + "Is likely a default game with stub players, skipping...")
        continue
    entry = aggregator[(model, theme)]
    entry['n_games'] += 1
    for mission_id, mission in enumerate(data.get('missions', [])):
        # adjust if your logs name this field differently
        for action in mission.get('actions', []):
            if action.get('phase') != 'select_role':
                continue
            role = action['payload'].get('role_default_theme')
            if role not in ('cooperator', 'defector'):
                print(f'No role for {model}-{theme} mission: {mission_id}')
                continue
            if role == 'cooperator':
                entry['n_cooperator'] += 1
            else:
                entry['n_defector'] += 1
            entry['total'] += 1

# turn into a table
rows = []
for (model, theme), counts in aggregator.items():
    if counts['total'] == 0:
        continue
    rows.append({
        'model': model,
        'theme': theme,
        'n_cooperator': counts['n_cooperator']/counts['total'],
        'n_defector': counts['n_defector']/counts['total'],
        'role_select_total': counts['total'],
        'n_games': counts['n_games']
    })
rows.sort(key=lambda row: row['model'])
df = pd.DataFrame(rows)
pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_colwidth', None) # To prevent truncation within cells

print(df)
sys.exit(0)
# optionally save
df.to_csv("role_summary.csv", index=False)

import matplotlib.pyplot as plt
import os
# assume df is your DataFrame from above
# for each model, plot cooperator vs defector counts by theme
for model in df['model'].unique():
    subset = df[df['model'] == model]
    # pivot so themes are the index and columns are the two roles
    pivot = subset.set_index('theme')[['n_cooperator', 'n_defector']]
    
    # create the bar chart
    try:
        ax = pivot.plot(
            kind='bar',
            fontsize=18,
            figsize=(10, 6),      # you can tweak size as needed
            width=0.8,            # bar width
            rot=45               # rotate x‐labels for readability
        )
    except:
        breakpoint()
    ax.set_title(f"Role Selections by Theme for {model}", fontsize=16)
    ax.set_xlabel("Theme", fontsize=16)
    ax.set_ylabel("Number of Selections (%)", fontsize=16)
    ax.legend(title="Role")
    plt.tight_layout()
    os.makedirs('prelim_results', exist_ok=True)
    model_name = model.split('/')[-1]
    plt.savefig(f'prelim_results/{model_name}_coop_defect_themes.png')
