import sys
import glob
import json
from collections import defaultdict, Counter
import pandas as pd

from collections import Counter
from typing import Dict, Tuple

import pickle

def resolve_accusation(
    player_name_map: Dict[str, str],
    player_role_map: Dict[int, str], 
    accusations: Dict[int, str]
) -> Tuple[bool, bool]:
    """
    Resolve accusations made by cooperators against other players.
    
    Args:
        player_name_map: Maps player ID strings to names (e.g., {'0': 'Alice'})
        player_role_map: Maps player ID integers to roles (e.g., {0: 'cooperator'})
        accusations: Maps cooperator IDs to their nominated player names (e.g., {0: 'Eve'})
    
    Returns:
        Tuple of (defector_found, cooperator_found) booleans
    """
    # Get nominations from cooperators only
    cooperator_ids = [pid for pid, role in player_role_map.items() if role == "cooperator"]
    nominations = [accusations.get(pid) for pid in cooperator_ids if pid in accusations]
    
    # 1. Drop abstentions (None values or 'Unknown')
    valid = [name for name in nominations if name and name != 'Unknown']
    
    # 2. No one voted
    if not valid:
        return False, False
    
    # 3. Count and find top vote-getter(s)
    counts = Counter(valid)
    max_votes = max(counts.values())
    top = [name for name, v in counts.items() if v == max_votes]
    
    # 4. Ties mean no clear nominee
    if len(top) != 1:
        return False, False
    
    nominee_name = top[0]
    
    # Find the nominee's ID and role
    nominee_id = None
    for pid_str, name in player_name_map.items():
        if name == nominee_name:
            nominee_id = int(pid_str)
            break
    
    if nominee_id is None:
        return False, False
    
    nominee_role = player_role_map.get(nominee_id)
    if nominee_role is None:
        return False, False
    
    # 5. Check threshold and role
    threshold = len(valid) / 2
    defector_found = (max_votes > threshold) and (nominee_role == "defector")
    cooperator_found = (max_votes > threshold) and (nominee_role == "cooperator")
    
    return defector_found, cooperator_found

def parse_game_logs(log_dir: str = "multiplayer_game_logs"):
    log_dir= "multiplayer_game_logs"
    incomplete_games = 0
    finished_games = []
    for path in glob.glob(f'{log_dir}/*.json'):
        with open(path, 'r') as f:
            data = json.load(f)
            theme = data['config']['theme']
            game_finished = 'outcome' in data.keys()
            
            if game_finished:
                outdata = {}
                #need to loop over each mission, grab roles and scores and such. Compute who was accused
                outdata['game_id'] = data['game_id']
                outdata['theme'] = theme
                outdata['players'] = []
                for player in data['config']['players']:
                    outdata['players'].append({
                        'player_id': player['player_id'],
                        'model_name': player['model_name'],
                        'username': player['username'],
                    })
                    
                prev_score = {str(player['player_id']): 0 for player in data['config']['players']}
                for mission in data['missions']:
                    # role selection
                    player_role_map = {}
                    for action in mission['actions']:
                        if action['phase'] != 'select_role':
                            continue
                        role = action['payload']['role_default_theme']
                        player_id = action['player_id']
                        if role not in ('cooperator', 'defector'):
                            raise ValueError(f'No role for {player_id} in mission {mission["mission_id"]}')
                        player_role_map[player_id] = role
                        
                    #store vote/accusation history
                    accusations = {}
                    retreat_counts = defaultdict(int)
                    for event in mission['events']:
                        for action in event['actions']:
                            #votes
                            if action['phase'] == 'vote' and action['payload']['vote_choice'] == 'yes':
                                retreat_counts[action['player_id']] += 1
                            #accusations
                            if action['phase'] == 'nominate' and player_role_map[action['player_id']] == "cooperator":
                                #accusation made
                                accusations[action['player_id']] = action['payload']['nominated_player_id']
                    #check who was accused
                    
                    defector_accused, cooperator_accused = resolve_accusation(
                        {str(player['player_id']): player['username'] for player in data['config']['players']}, 
                        player_role_map, 
                        accusations
                    )    
                            
                    #used scores to backwards compute who won the mission
                    scores = mission['scores']
                    score_diff = {player_id: scores[player_id] - prev_score[player_id] for player_id in scores}
                    prev_score = scores
                    #compute if cooperators or defectors got more points
                    cooperator_score = None
                    defector_score = None
                    for player_id, score in score_diff.items():
                        if player_role_map[int(player_id)] == 'cooperator':
                            cooperator_score = score if cooperator_score is None else cooperator_score
                        elif player_role_map[int(player_id)] == 'defector':
                            defector_score = score if defector_score is None else defector_score
                    
                    mission_outcome = {
                        'mission_id': mission['mission_id'],
                        'cooperator_score': cooperator_score,
                        'defector_score': defector_score,
                        'defector_accused': defector_accused,
                        'cooperator_accused': cooperator_accused,
                        'retreat_counts': retreat_counts,
                        'accusations': accusations,
                        'player_roles': list(player_role_map.values()),
                        'defector_won': defector_score is not None and (defector_score > cooperator_score),
                        'cooperator_won': (defector_score is not None and cooperator_score > defector_score) and not cooperator_accused,
                        'accused': "defector" if defector_accused else "cooperator" if cooperator_accused else "none",
                    }
                    outdata.setdefault('missions', []).append(mission_outcome)
                    

                finished_games.append(outdata)
            else:
                incomplete_games+=1

    # Save the finished games to a file
    with open(f'{log_dir}/finished_games.pkl', 'wb') as f:
        pickle.dump(finished_games, f)
        
    return finished_games

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import os

def create_all_plots(data):
    """
    Create comprehensive visualizations for multiplayer game data.
    
    Args:
        data: List of game dictionaries with mission data
    """
    # Create output directory
    os.makedirs('figs', exist_ok=True)
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    # Prepare data structures
    model_role_counts = defaultdict(lambda: {'cooperator': 0, 'defector': 0})
    model_wins = defaultdict(lambda: {'cooperator_wins': 0, 'cooperator_total': 0, 
                                     'defector_wins': 0, 'defector_total': 0})
    model_accusations = defaultdict(lambda: {'true_positive': 0, 'false_positive': 0,
                                           'true_negative': 0, 'false_negative': 0})
    cooperator_accused_counts = defaultdict(int)
    retreat_by_role = {'cooperator': [], 'defector': []}
    betrayal_patterns = defaultdict(list)  # model -> list of mission roles
    scores_by_role = {'cooperator': [], 'defector': []}
    theme_performance = defaultdict(lambda: {'wins': 0, 'total': 0})
    accusation_over_missions = {1: defaultdict(int), 2: defaultdict(int), 3: defaultdict(int)}
    
    # Process data
    for game in data:
        players = {p['player_id']: p['username'] for p in game['players']}
        models = {p['player_id']: p['model_name'] for p in game['players']}
        theme = game['theme']
        
        for mission in game['missions']:
            mission_id = mission['mission_id']
            
            # Process each player's data
            for player_id, player_name in players.items():
                model = models[player_id]
                
                # Get role from mission data
                role_idx = list(players.keys()).index(player_id)
                if role_idx < len(mission['player_roles']):
                    role = mission['player_roles'][role_idx]
                    
                    # Count role selections
                    model_role_counts[model][role] += 1
                    
                    # Track betrayal patterns
                    if len(betrayal_patterns[model]) < mission_id:
                        betrayal_patterns[model].extend([''] * (mission_id - len(betrayal_patterns[model])))
                    if mission_id <= len(betrayal_patterns[model]):
                        betrayal_patterns[model][mission_id-1] = role
                    else:
                        betrayal_patterns[model].append(role)
                    
                    # Count wins
                    if role == 'cooperator':
                        model_wins[model]['cooperator_total'] += 1
                        if mission['cooperator_won']:
                            model_wins[model]['cooperator_wins'] += 1
                    else:
                        model_wins[model]['defector_total'] += 1
                        if mission['defector_won']:
                            model_wins[model]['defector_wins'] += 1
                    
                    # Track retreat votes
                    retreat_count = mission['retreat_counts'].get(player_id, 0)
                    retreat_by_role[role].append(retreat_count)
                    
                    # Track scores
                    if role == 'cooperator' and mission['cooperator_score'] is not None:
                        scores_by_role['cooperator'].append(mission['cooperator_score'])
                    elif role == 'defector' and mission['defector_score'] is not None:
                        scores_by_role['defector'].append(mission['defector_score'])
            
            # Track theme performance
            theme_performance[theme]['total'] += 1
            if mission['cooperator_won'] or mission['defector_won']:
                theme_performance[theme]['wins'] += 1
            
            # Process accusations
            for accuser_id, accused_name in mission['accusations'].items():
                if accused_name and accused_name != 'Unknown':
                    accuser_model = models[accuser_id]
                    # Find accused player's role
                    accused_id = None
                    for pid, pname in players.items():
                        if pname == accused_name:
                            accused_id = pid
                            break
                    
                    if accused_id is not None:
                        accused_role_idx = list(players.keys()).index(accused_id)
                        if accused_role_idx < len(mission['player_roles']):
                            accused_role = mission['player_roles'][accused_role_idx]
                            
                            # Track accusation accuracy
                            if accused_role == 'defector':
                                model_accusations[accuser_model]['true_positive'] += 1
                            else:
                                model_accusations[accuser_model]['false_positive'] += 1
                                cooperator_accused_counts[models[accused_id]] += 1
                            
                            # Track accusations over missions
                            accusation_over_missions[mission_id][accused_role] += 1
    
    # Create visualizations
    
    # 1. Role Selection Rates
    fig, ax = plt.subplots(figsize=(12, 6))
    models_list = list(model_role_counts.keys())
    coop_rates = [model_role_counts[m]['cooperator'] / 
                  (model_role_counts[m]['cooperator'] + model_role_counts[m]['defector']) 
                  for m in models_list]
    
    # Shorten model names for readability
    short_models = [m.split('/')[-1] if '/' in m else m for m in models_list]
    
    bars = ax.bar(range(len(models_list)), coop_rates, color='skyblue', alpha=0.8)
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='50% baseline')
    ax.set_xticks(range(len(models_list)))
    ax.set_xticklabels(short_models, rotation=45, ha='right')
    ax.set_ylabel('Cooperator Selection Rate')
    ax.set_title('Role Selection Preferences by Model')
    ax.legend()
    
    # Add value labels on bars
    for i, (bar, rate) in enumerate(zip(bars, coop_rates)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{rate:.2f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('figs/role_selection_rates.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Win Rates by Model and Role
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Cooperator win rates
    coop_win_rates = []
    defector_win_rates = []
    models_with_data = []
    
    for model in models_list:
        if model_wins[model]['cooperator_total'] > 0:
            coop_rate = model_wins[model]['cooperator_wins'] / model_wins[model]['cooperator_total']
            coop_win_rates.append(coop_rate)
        else:
            coop_win_rates.append(0)
            
        if model_wins[model]['defector_total'] > 0:
            def_rate = model_wins[model]['defector_wins'] / model_wins[model]['defector_total']
            defector_win_rates.append(def_rate)
        else:
            defector_win_rates.append(0)
        
        models_with_data.append(model.split('/')[-1] if '/' in model else model)
    
    x = np.arange(len(models_with_data))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, coop_win_rates, width, label='As Cooperator', color='green', alpha=0.7)
    bars2 = ax1.bar(x + width/2, defector_win_rates, width, label='As Defector', color='red', alpha=0.7)
    
    ax1.set_ylabel('Win Rate')
    ax1.set_title('Win Rates by Model and Role')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models_with_data, rotation=45, ha='right')
    ax1.legend()
    ax1.set_ylim(0, 1)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=8)
    
    # 3. Accusation Accuracy (Precision)
    precisions = []
    for model in models_list:
        tp = model_accusations[model]['true_positive']
        fp = model_accusations[model]['false_positive']
        if tp + fp > 0:
            precision = tp / (tp + fp)
            precisions.append(precision)
        else:
            precisions.append(0)
    
    bars = ax2.bar(range(len(models_with_data)), precisions, color='purple', alpha=0.7)
    ax2.set_xticks(range(len(models_with_data)))
    ax2.set_xticklabels(models_with_data, rotation=45, ha='right')
    ax2.set_ylabel('Precision')
    ax2.set_title('Accusation Precision by Model\n(True Positives / All Accusations)')
    ax2.set_ylim(0, 1)
    
    # Add value labels
    for bar, prec in zip(bars, precisions):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{prec:.2f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('figs/win_rates_and_accuracy.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Worst Cooperator Analysis
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Sort by most accused
    sorted_accused = sorted(cooperator_accused_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    if sorted_accused:
        models_accused = [m.split('/')[-1] if '/' in m else m for m, _ in sorted_accused]
        counts = [c for _, c in sorted_accused]
        
        bars = ax.bar(range(len(models_accused)), counts, color='orange', alpha=0.8)
        ax.set_xticks(range(len(models_accused)))
        ax.set_xticklabels(models_accused, rotation=45, ha='right')
        ax.set_ylabel('Times Falsely Accused as Cooperator')
        ax.set_title('Most Suspected Cooperators\n(False Positive Accusations)')
        
        # Add value labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(count)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('figs/worst_cooperators.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Retreat Vote Strategy
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate average retreat votes by role
    avg_retreat_coop = np.mean(retreat_by_role['cooperator']) if retreat_by_role['cooperator'] else 0
    avg_retreat_def = np.mean(retreat_by_role['defector']) if retreat_by_role['defector'] else 0
    
    # Create box plot
    retreat_data = []
    retreat_labels = []
    
    if retreat_by_role['cooperator']:
        retreat_data.append(retreat_by_role['cooperator'])
        retreat_labels.append('Cooperator')
    if retreat_by_role['defector']:
        retreat_data.append(retreat_by_role['defector'])
        retreat_labels.append('Defector')
    
    if retreat_data:
        box_plot = ax.boxplot(retreat_data, labels=retreat_labels)
        ax.set_ylabel('Number of Retreat Votes')
        ax.set_title('Retreat Voting Patterns by Role')
        
        # Add mean values
        for i, (data, label) in enumerate(zip(retreat_data, retreat_labels)):
            mean_val = np.mean(data)
            ax.text(i+1, mean_val, f'μ={mean_val:.2f}', ha='center', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('figs/retreat_vote_strategy.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. Trust-then-Betray Pattern
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Analyze betrayal patterns (cooperator in early missions, defector in last)
    betrayal_scores = {}
    for model, roles in betrayal_patterns.items():
        if len(roles) >= 3:
            # Check if they were cooperator in missions 1-2 and defector in mission 3
            early_coop = sum(1 for r in roles[:2] if r == 'cooperator')
            late_defect = 1 if len(roles) > 2 and roles[2] == 'defector' else 0
            betrayal_score = (early_coop / 2) * late_defect
            betrayal_scores[model] = betrayal_score
    
    # Sort by betrayal score
    sorted_betrayals = sorted(betrayal_scores.items(), key=lambda x: x[1], reverse=True)[:15]
    if sorted_betrayals:
        models_betrayal = [m.split('/')[-1] if '/' in m else m for m, _ in sorted_betrayals]
        scores = [s for _, s in sorted_betrayals]
        
        bars = ax.bar(range(len(models_betrayal)), scores, color='darkred', alpha=0.8)
        ax.set_xticks(range(len(models_betrayal)))
        ax.set_xticklabels(models_betrayal, rotation=45, ha='right')
        ax.set_ylabel('Betrayal Score')
        ax.set_title('Trust-then-Betray Pattern\n(Cooperate Early, Defect Late)')
        ax.set_ylim(0, 1)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            if score > 0:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{score:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('figs/betrayal_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 7. Score Distribution by Role
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    if scores_by_role['cooperator']:
        ax1.hist(scores_by_role['cooperator'], bins=20, color='green', alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Score')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Cooperator Score Distribution')
        ax1.axvline(np.mean(scores_by_role['cooperator']), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(scores_by_role["cooperator"]):.1f}')
        ax1.legend()
    
    if scores_by_role['defector']:
        ax2.hist(scores_by_role['defector'], bins=20, color='red', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Score')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Defector Score Distribution')
        ax2.axvline(np.mean(scores_by_role['defector']), color='blue', linestyle='--',
                   label=f'Mean: {np.mean(scores_by_role["defector"]):.1f}')
        ax2.legend()
    
    plt.tight_layout()
    plt.savefig('figs/score_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 8. Performance by Theme
    fig, ax = plt.subplots(figsize=(10, 6))
    
    themes = list(theme_performance.keys())
    win_rates_theme = [theme_performance[t]['wins'] / theme_performance[t]['total'] 
                      if theme_performance[t]['total'] > 0 else 0 for t in themes]
    
    bars = ax.bar(range(len(themes)), win_rates_theme, color='teal', alpha=0.8)
    ax.set_xticks(range(len(themes)))
    ax.set_xticklabels(themes, rotation=45, ha='right')
    ax.set_ylabel('Mission Success Rate')
    ax.set_title('Mission Success Rate by Game Theme')
    ax.set_ylim(0, 1)
    
    # Add value labels
    for bar, rate in zip(bars, win_rates_theme):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{rate:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('figs/theme_performance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 9. Accusation Dynamics Over Missions
    fig, ax = plt.subplots(figsize=(10, 6))
    
    missions = [1, 2, 3]
    defector_accusations = [accusation_over_missions[m]['defector'] for m in missions]
    cooperator_accusations = [accusation_over_missions[m]['cooperator'] for m in missions]
    
    x = np.arange(len(missions))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, defector_accusations, width, label='Defectors Accused', color='red', alpha=0.7)
    bars2 = ax.bar(x + width/2, cooperator_accusations, width, label='Cooperators Accused', color='green', alpha=0.7)
    
    ax.set_xlabel('Mission Number')
    ax.set_ylabel('Number of Accusations')
    ax.set_title('Accusation Patterns Across Missions')
    ax.set_xticks(x)
    ax.set_xticklabels(missions)
    ax.legend()
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{int(height)}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('figs/accusation_dynamics.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 10. Model Performance Summary
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Calculate overall performance score for each model
    model_scores = {}
    for model in models_list:
        # Combine win rate, accusation accuracy, and role balance
        coop_wr = model_wins[model]['cooperator_wins'] / model_wins[model]['cooperator_total'] \
                  if model_wins[model]['cooperator_total'] > 0 else 0
        def_wr = model_wins[model]['defector_wins'] / model_wins[model]['defector_total'] \
                 if model_wins[model]['defector_total'] > 0 else 0
        
        tp = model_accusations[model]['true_positive']
        fp = model_accusations[model]['false_positive']
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.5
        
        # Overall score: average of win rates + precision bonus
        overall_score = (coop_wr + def_wr) / 2 * 0.7 + precision * 0.3
        model_scores[model] = overall_score
    
    # Sort by score
    sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
    models_ranked = [m.split('/')[-1] if '/' in m else m for m, _ in sorted_models]
    scores_ranked = [s for _, s in sorted_models]
    
    # Create horizontal bar chart
    bars = ax.barh(range(len(models_ranked)), scores_ranked, color='indigo', alpha=0.8)
    ax.set_yticks(range(len(models_ranked)))
    ax.set_yticklabels(models_ranked)
    ax.set_xlabel('Performance Score')
    ax.set_title('Overall Model Performance Ranking\n(Combined Win Rate + Accusation Accuracy)')
    ax.set_xlim(0, 1)
    
    # Add value labels
    for bar, score in zip(bars, scores_ranked):
        width = bar.get_width()
        ax.text(width + 0.01, bar.get_y() + bar.get_height()/2.,
                f'{score:.3f}', ha='left', va='center')
    
    plt.tight_layout()
    plt.savefig('figs/model_rankings.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created {len(os.listdir('figs'))} plots in 'figs' directory")
    
    # Return summary statistics
    return {
        'total_games': len(data),
        'models_analyzed': len(models_list),
        'plots_created': len(os.listdir('figs'))
    }

def main():
    if False:
        data = parse_game_logs()
    else:
        # Load the finished games from a file
        with open('multiplayer_game_logs/finished_games.pkl', 'rb') as f:
            data = pickle.load(f)
        
    create_all_plots(data)
        

if __name__ == "__main__":
    main()
    