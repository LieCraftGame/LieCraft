import pandas as pd
import numpy as np
from collections import defaultdict

import multiprocessing as mp
from itertools import product
import time
import random



def make_tables(n_coop, coop_mod, def_mod, bonus_coop, bonus_def, def_starting_score, n_events=5):
    n_def = 5 - n_coop

    # base scores
    max_coop = 25
    E_event_coop = {
        4:(max_coop-3) / n_events,
        3:(max_coop-6) / n_events,
        2:(max_coop-9) / n_events,
        1:(max_coop-12) / n_events
    }
    # the score is split across players
    E_event_coop = {k: v/k for k, v in E_event_coop.items()}
    E_event_coop[0] = 0
    
    E_risky = {1:(3/n_events),
               2:(6/n_events),
               3:(9/n_events),
               4:(12/n_events),}
    E_risky = {k : (v/k) for k, v in E_risky.items()}
    
    E_safe  = {1:(2/n_events) ,
               2:(5/n_events) ,
               3:(8/n_events) ,
               4:(11/n_events)}
    E_safe  = {k :  (v/k) for k, v in E_safe.items()}
    

    scenarios = [("safe","deflected"),("safe","unknown"),("safe","found"),
                 ("risky","deflected"),("risky","unknown"),("risky","found")]

    names = [f"{t}-{o}" for t,o in scenarios]
    evs   = [f"Event {i}" for i in range(1, n_events+1)]
    coop_tbl = pd.DataFrame(index=names, columns=evs, dtype=float)
    def_tbl  = coop_tbl.copy()

    for idx,(typ,outcome) in enumerate(scenarios):
        for e in range(1, n_events+1):
            # cooperators
            base_c = E_event_coop[n_coop]
            c = (e*base_c) + coop_mod[outcome]
            if e==5 :
                c += bonus_coop
            coop_tbl.iat[idx, e-1] = c

            # defectors
            base_d = (E_risky if typ=="risky" else E_safe)[n_def]
            d = (e*base_d) + def_mod[outcome] + def_starting_score
            if outcome!="found":
                if e < 5 or  (e==5 and typ=="risky"):
                    d += bonus_def
            def_tbl.iat[idx, e-1] = d

    return coop_tbl, def_tbl

def check_constraints(coop_tbl, def_tbl):
    fails = []

    # shorthand
    c = coop_tbl
    d = def_tbl
    ev5 = "Event 5"

    # defector ordering constraints
    for kind in ("risky","safe"):
        a, b, f = f"{kind}-deflected", f"{kind}-unknown", f"{kind}-found"
        if not (d.at[a,ev5]  >= d.at[b,ev5] >= d.at[f,ev5]):
            fails.append(f"Defector {kind}: {a} >= {b} >= {f} at {ev5}")

    # risky vs safe for each outcome
    for outcome in ("deflected","unknown","found"):
        r,s = f"risky-{outcome}", f"safe-{outcome}"
        if not (d.at[r,ev5] >= d.at[s,ev5]):
            fails.append(f"Defector risky vs safe for {outcome} at {ev5}")

    # cooperator ordering constraints
    for kind in ("risky","safe"):
        a, b, f = f"{kind}-deflected", f"{kind}-unknown", f"{kind}-found"
        if not (c.at[f,ev5] > c.at[b,ev5] > c.at[a,ev5]):
            fails.append(f"Cooperator {kind}: {f} > {b} > {a} at {ev5}")
            
    # deflected and unknown should always be negative for events 1,2,3,4
    for e in range(1, 5):
        for kind in ("risky","safe"):
            for outcome in ("deflected","unknown"):
                d_val = d.at[f"{kind}-{outcome}", f"Event {e}"]
                c_val = c.at[f"{kind}-{outcome}", f"Event {e}"]
                if c_val > d_val:
                    fails.append(f"Defector {kind}: {outcome} not negative at Event {e}")
           
    return fails

def validate_scores(starting_points_defector, sabotage_bonus, defector_accused, defector_unknown, cooperator_accused, verbose=False):

    coop_mod = {"deflected":-cooperator_accused, "unknown":defector_unknown, "found":defector_accused}
    def_mod  = {"deflected":0,  "unknown":0, "found":0}

    coop_event_finished = 0
    def_event_sabotage  = sabotage_bonus
    def_starting_score = starting_points_defector


    #loop over floor, round and ceil operators
    #for op in ("none", "floor", "round", "ceil"):
    any_errors = False
    for op in ("ceil", ):
        # main loop over different cooperator counts
        for n_coop in [2,3,4]:
            coop_tbl, def_tbl = make_tables(n_coop, coop_mod, def_mod, coop_event_finished, def_event_sabotage, def_starting_score)
            if op == "floor":
                coop_tbl = coop_tbl.apply(np.floor)
                def_tbl  = def_tbl.apply(np.floor)
            elif op == "round":
                coop_tbl = coop_tbl.apply(np.round)
                def_tbl  = def_tbl.apply(np.round)
            elif op == "ceil":
                coop_tbl = coop_tbl.apply(np.ceil)
                def_tbl  = def_tbl.apply(np.ceil)
            
            diff_tbl = coop_tbl - def_tbl

            errors = check_constraints(coop_tbl, def_tbl)

            if verbose:
                print(f"\n=== n_cooperators = {n_coop} ===")
                print("Cooperator table:\n", coop_tbl)
                print("\nDefector table:\n", def_tbl)
                
                print("\nDiff table:\n", diff_tbl)

                if errors:
                    print(f"\nConstraint failures ({op}):")
                    for e in errors:
                        print("  -", e)
                else:
                    print("\nAll constraints passed.")
            
            any_errors = any_errors or bool(errors)
            
    return not any_errors

def build_base_pmf():
    # prob that you draw a bad card twice
    p =  (2/5) * (2/5)  # = 0.16
    

    # 2. Scenario 1: exactly one compound attempt 
    # drew a good random card in the starting hand
    P1 = {
        0: 1 - p,  # fail the compound
        1: p,      # succeed exactly once
        2: 0                # impossible to get two successes in a single attempt
    }

    # 3. Scenario 2: two independent compound attempts
    # drew a bad random card in the starting hand
    P2 = {
        0: (1 - p) * (1 - p),         # both attempts fail
        1: 2 * p * (1 - p),           # exactly one success
        2: p * p                      # both attempts succeed
    }

    # 4. Mix with weights 0.6 and 0.4
    prob_draw_bad = 0.4  # probability of drawing a bad card in the starting hand
    prob_draw_good = 0.6  # probability of drawing a good card in the starting hand
    base_pmf = {}
    for k in (0, 1, 2):
        base_pmf[k] = (prob_draw_good * P1[k]) + (prob_draw_bad * P2[k])

    return base_pmf

def convolve_pmf(pmf1, pmf2):
    """
    Convolve two discrete PMFs pmf1 and pmf2.
    pmf1 and pmf2 are dicts mapping integer outcomes -> probability.
    Returns a new dict mapping sums -> probability.
    """
    out = defaultdict(float)
    for x1, prob1 in pmf1.items():
        for x2, prob2 in pmf2.items():
            out[x1 + x2] += prob1 * prob2
    return dict(out)

def compound_distribution_over_n(base_pmf, n_trials):
    """
    Starting from base_pmf (over outcomes {0,1,2}), convolve it with itself
    n_trials times to get the distribution of the total sum.
    """
    # Start with one copy of base_pmf
    current = dict(base_pmf)
    for _ in range(n_trials - 1):
        current = convolve_pmf(current, base_pmf)
    # Sort by outcome for readability
    return dict(sorted(current.items()))



def get_ev_score(sabotage_bonus, defector_accused, defector_unknown, cooperator_accused):
    B = - sabotage_bonus
    sD = defector_accused
    sN = defector_unknown
    sC = -cooperator_accused
    
    # Compute the base PMF automatically
    base_pmf = build_base_pmf()

    # Now get the total distribution after 5 independent trials
    total_pmf = compound_distribution_over_n(base_pmf, 5)
    p0 = total_pmf.get(0, 0)
    p1 = total_pmf.get(1, 0)
    p2 = total_pmf.get(2, 0)
    p3_plus = sum(prob for k, prob in total_pmf.items() if k >= 3)
    
    sabotage_fails = [0,1,2,3]
    sabotage_outcomes = ["D","N","C"]
    
    #assum D N C have equal probabilities, make a table of probabilities
    sabotage_pmf = defaultdict(float)
    #expected_values = defaultdict(float)
    for fail in sabotage_fails:
        for outcome in sabotage_outcomes:
            # P(fail, outcome) = P(fail) * P(outcome)
            # assuming equal probabilities for D, N, C
            if fail == 3 and (outcome == "D" or outcome == "C"):
                sabotage_pmf[(fail, outcome)] = 0
            elif fail == 3 and outcome == "N":
                sabotage_pmf[(fail, outcome)] = p3_plus
            else:
                sabotage_pmf[(fail, outcome)] = total_pmf[fail]
                

    pmf = {k: v for k, v in sabotage_pmf.items() if v > 0}
    
    EV = 0.0
    for (fail, outcome), p in pmf.items():
        if fail == 3 and outcome == "N":
            payoff = B + sN
        else:
            if outcome == "D":
                payoff = sD
            elif outcome == "N":
                payoff = B + sN
            else:  # "C"
                payoff = B + sC
        EV += payoff * p
    return EV

# satisfy the constraints and return the expected value
def check_score_valid_and_ev(starting_points_defector, sabotage_bonus, defector_accused, defector_unknown, cooperator_accused):
    is_valid = validate_scores(starting_points_defector, sabotage_bonus, defector_accused, defector_unknown, cooperator_accused)
    ev = get_ev_score(sabotage_bonus, defector_accused, defector_unknown, cooperator_accused)
    return is_valid, ev


def get_scores_and_ev():
    #results from looking at the filtered data when def_unknown = 0 and the accused = each other
    unusable = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (3, 0)]
    possible_starting_def_points = [1, 2, 3, 4]
    possible_sabotage_bonuses = [3, 4, 5]
    
    # Generate all possible combinations and filter out unusable ones
    valid_combinations = []
    for starting_points in possible_starting_def_points:
        for sabotage_bonus in possible_sabotage_bonuses:
            if (starting_points, sabotage_bonus) not in unusable:
                valid_combinations.append((starting_points, sabotage_bonus))
    
    # Sample from valid combinations
    starting_points_defector, sabotage_bonus = random.choice(valid_combinations)
    
    # Calculate the base score for defector_accused range
    base_score = starting_points_defector + sabotage_bonus

    # Select defector_accused within +/-1 of base_score
    min_accused = max(0, base_score - 1)  # Ensure non-negative
    max_accused = base_score + 1
    defector_accused = random.randint(min_accused, max_accused)
    
    # Set constraints as specified  
    defector_unknown = random.randint(0, min(possible_sabotage_bonuses) - 1)
    cooperator_accused = defector_accused
    
    # Get validation and expected value
    is_valid, ev = check_score_valid_and_ev(
        starting_points_defector, 
        sabotage_bonus, 
        defector_accused, 
        defector_unknown, 
        cooperator_accused
    )
    
    return {
        'starting_points_defector': starting_points_defector,
        'mission_sabotaged': sabotage_bonus,
        'defector_found': defector_accused,
        'defector_unknown': defector_unknown,
        'cooperator_found': cooperator_accused,
        'points_per_card': 1, 
        'is_valid': is_valid,
        'expected_value': ev
    }


def find_valid_bounds_for_param(param_idx, param_range, fixed_params):
   """Find min and max valid values for a parameter given fixed values for others"""
   valid_min = None
   valid_max = None
   
   # Test from minimum to find lower bound
   for val in param_range:
       test_params = fixed_params[:]
       test_params[param_idx] = val
       is_valid, _ = check_score_valid_and_ev(*test_params)
       if is_valid:
           valid_min = val
           break
   
   # Test from maximum to find upper bound  
   for val in reversed(param_range):
       test_params = fixed_params[:]
       test_params[param_idx] = val
       is_valid, _ = check_score_valid_and_ev(*test_params)
       if is_valid:
           valid_max = val
           break
   
   return valid_min, valid_max

def process_chunk(chunk_data):
    """Process a chunk of parameter combinations"""
    chunk, chunk_id = chunk_data
    valid_evs = []
    valid_combinations = []
    processed = 0
    
    for spd, b, sd, sn, sc in chunk:
        is_valid, ev = check_score_valid_and_ev(spd, b, sd, sn, sc)
        
        if is_valid:
            valid_evs.append(ev)
            valid_combinations.append((spd, b, sd, sn, sc))
        
        processed += 1
        
        # Progress indicator for this chunk
        if processed % 500 == 0:
            print(f"Chunk {chunk_id}: Processed {processed:,} combinations, found {len(valid_evs):,} valid results")
    
    return valid_evs, valid_combinations, processed


import pandas as pd

def filter_csv_results(csv_filename="payoff_combinations.csv"):
    """
    Load and filter the CSV file with the following conditions:
    1. EV < 0
    2. defector_accused = cooperator_accused
    3. starting_score < sabotage_bonus
    """
    try:
        # Load the CSV file
        df = pd.read_csv(csv_filename)
        print(f"Loaded {len(df)} combinations from {csv_filename}")
        
        # Apply filters
        filtered_df = df[
            (df['EV'] < 0) & 
            (df['defector_accused'] == df['cooperator_accused']) &
            (df['starting_score'] < df['sabotage_bonus']) &
            (df['defector_unknown'] == 0)
        ]
        
        # Display results
        print(f"Found {len(filtered_df)} combinations matching all filters:")
        print("\nFiltered combinations:")
        print(filtered_df.to_string(index=False))
        
        # Save filtered results to a new CSV
        output_filename = "filtered_payoff_combinations.csv"
        filtered_df.to_csv(output_filename, index=False)
        print(f"\nFiltered results saved to {output_filename}")
        
        return filtered_df
        
    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def generate_histogram_data(num_processes=None):
    """Generate all valid EV scores from the parameter combinations using multiprocessing"""
    # Define the ranges
    starting_points_defector = range(1, 11)
    B_range = range(1, 11)        # sabotage_bonus
    sD_range = range(1, 11)        # defector_accused
    sN_range = range(-5, 6)        # defector_unknown
    sC_range = range(1, 11)       # cooperator_accused
    
    #get_valid_score_and_ev(5,-5,5,0,5) = invalid and ev=10
    # Generate all combinations
    all_combinations = list(product(starting_points_defector, B_range, sD_range, sN_range, sC_range))
    total_combinations = len(all_combinations)
    
    print("Generating EV data from parameter combinations (parallel)...")
    print(f"Total combinations to test: {total_combinations:,}")
    
    # Determine number of processes
    if num_processes is None:
        num_processes = mp.cpu_count()
    print(f"Using {num_processes} processes")
    
    # Split combinations into chunks for each process
    chunk_size = max(1, total_combinations // num_processes)
    chunks = []
    for i in range(0, total_combinations, chunk_size):
        chunk = all_combinations[i:i + chunk_size]
        chunks.append((chunk, i // chunk_size))
    
    print(f"Split into {len(chunks)} chunks of approximately {chunk_size:,} combinations each")
    
    # Process chunks in parallel
    start_time = time.time()
    
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(process_chunk, chunks)
    
    # Combine results
    valid_evs = []
    valid_combinations = []
    total_processed = 0
    
    for chunk_evs, chunk_combinations, chunk_processed in results:
        valid_evs.extend(chunk_evs)
        valid_combinations.extend(chunk_combinations)
        total_processed += chunk_processed
    
    elapsed_time = time.time() - start_time
    print(f"Completed in {elapsed_time:.2f} seconds!")
    print(f"Found {len(valid_evs):,} valid results out of {total_processed:,} total combinations")
    
    # Print results
    print("starting_score, sabotage_bonus, defector_accused, defector_unknown, cooperator_accused, EV")
    for i, (spd, b, sd, sn, sc) in enumerate(valid_combinations):
        print(f"{spd:2d}, {b:3d}, {sd:2d}, {sn:2d}, {sc:2d}, {valid_evs[i]:.3f}")
    # Save to CSV
    csv_filename = "payoff_combinations.csv"
    import csv

    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['starting_score', 'sabotage_bonus', 'defector_accused', 
                        'defector_unknown', 'cooperator_accused', 'EV'])
        # Write data
        for i, (spd, b, sd, sn, sc) in enumerate(valid_combinations):
            writer.writerow([spd, b, sd, sn, sc, round(valid_evs[i], 3)])
    filtered = filter_csv_results(csv_filename)
    print(f"\nResults saved to {csv_filename}")
    return valid_evs

def create_histogram(valid_evs, n_bins, save_path=None):
   """Create bar chart with sorted EVs on y-axis and run index on x-axis"""
   if not valid_evs:
       print("No valid EV data to plot!")
       return
   
   import matplotlib.pyplot as plt
   
   # Sort the EVs
   sorted_evs = sorted(valid_evs)
   
   # Create x-axis as run indices
   x_indices = list(range(len(sorted_evs)))
   
   # Create the bar chart
   plt.figure(figsize=(12, 8))
   plt.bar(x_indices, sorted_evs, width=1.0, edgecolor='none', alpha=0.7)
   
   # Customize the plot
   plt.xlabel('Run Index', fontsize=12)
   plt.ylabel('Expected Value (EV)', fontsize=12)
   plt.title(f'Sorted Expected Values\n({len(valid_evs):,} valid results)', fontsize=14)
   plt.grid(True, alpha=0.3, axis='y')
   
   # Add statistics to the plot
   mean_ev = np.mean(valid_evs)
   std_ev = np.std(valid_evs)
   median_ev = np.median(valid_evs)
   min_ev = min(valid_evs)
   max_ev = max(valid_evs)
   
   stats_text = f'Mean: {mean_ev:.3f}\nStd: {std_ev:.3f}\nMedian: {median_ev:.3f}\nMin: {min_ev:.3f}\nMax: {max_ev:.3f}'
   plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
   
   # Add median line
   plt.axhline(y=median_ev, color='red', linestyle='--', alpha=0.7, label=f'Median: {median_ev:.3f}')
   plt.legend()
   
   plt.tight_layout()
   
   if save_path:
       plt.savefig(save_path, dpi=300, bbox_inches='tight')
       print(f"Bar chart saved to {save_path}")
   
   
   # Print summary statistics
   print(f"\nSummary for {len(valid_evs):,} valid EVs:")
   print(f"Min EV: {min_ev:.3f}")
   print(f"Max EV: {max_ev:.3f}")
   print(f"Mean EV: {mean_ev:.3f}")
   print(f"Median EV: {median_ev:.3f}")
   print(f"Std EV: {std_ev:.3f}")
       
       
def generate_all_histograms():
    """Generate histograms for all specified bin counts"""
    # Generate the data once
    valid_evs = generate_histogram_data()
    
    if not valid_evs:
        print("No valid data found! Check your validation function.")
        return
    
    # Create histograms for different bin counts
    bin_counts = [5, 10, 20, 50]
    
    for n_bins in bin_counts:
        print(f"\\n{'='*50}")
        print(f"Creating histogram with {n_bins} bins")
        print(f"{'='*50}")
        create_histogram(valid_evs, n_bins, f'ev_histogram_{n_bins}_bins.png')

def make_histograms():
    """Main function to run the histogram generation"""
    print("EV Histogram Generator")
    print("=" * 50)
    print("Parameter ranges:")
    print("- starting_points_defector: 0 to 9")
    print("- sabotage_bonus (B): -20 to 0") 
    print("- defector_accused (sD): 0 to 10")
    print("- defector_unknown (sN): -5 to 5")
    print("- cooperator_accused (sC): -10 to 0")
    print()
    print("IMPORTANT: Make sure to replace the placeholder functions:")
    print("- validate_scores()")
    print("- get_ev_score()")
    print("with your actual implementations!")
    print()

    
    generate_all_histograms()

if __name__ == "__main__":
    if False:
        make_histograms()
    # Compute the base PMF automatically
    base_pmf = build_base_pmf()
    print("Base PMF over {0,1,2}:")
    for k, v in base_pmf.items():
        print(f"  {k} → {v:.6f}")

    # Now get the total distribution after 5 independent trials
    total_pmf = compound_distribution_over_n(base_pmf, 5)
    print("\nTotal distribution over 5 trials (sums from 0 to 10):")
    for total_successes, prob in total_pmf.items():
        print(f"  {total_successes} successes: {prob * 100:.4f}%")
    p0 = total_pmf.get(0, 0)
    p1 = total_pmf.get(1, 0)
    p2 = total_pmf.get(2, 0)
    p3_plus = sum(prob for k, prob in total_pmf.items() if k >= 3)
    print(f"\nProbabilities: P(0)={p0:.4f}, P(1)={p1:.4f}, P(2)={p2:.4f}, P(3+)={p3_plus:.4f}")
    
    sabotage_fails = [0,1,2,3]
    sabotage_outcomes = ["D","N","C"]
    
    
    #assum D N C have equal probabilities, make a table of probabilities
    sabotage_pmf = defaultdict(float)
    #expected_values = defaultdict(float)
    for fail in sabotage_fails:
        for outcome in sabotage_outcomes:
            # P(fail, outcome) = P(fail) * P(outcome)
            # assuming equal probabilities for D, N, C
            
            if fail == 3 and (outcome == "D" or outcome == "C"):
                sabotage_pmf[(fail, outcome)] = 0
                #expected_values[(fail, outcome)] = 0
            elif fail == 3 and outcome == "N":
                sabotage_pmf[(fail, outcome)] = p3_plus
                #expected_values[(fail, outcome)] = (base_sabotage_score) + p3_plus * outcome_score_map[outcome]
            else:
                #hack_map = {"D": 10, "N": 4, "C": 6}
                #hack_map_sum = sum(hack_map.values())
                #hack_map = {k: v / hack_map_sum for k, v in hack_map.items()}  # normalize to sum to 1
                sabotage_pmf[(fail, outcome)] = total_pmf[fail] #* hack_map[outcome]
                #expected_values[(fail, outcome)] = ( bonus + outcome_score_map[outcome]) * sabotage_pmf[(fail, outcome)]
                
            
    print("\nSabotage PMF (fail, outcome):")
    for (fail, outcome), prob in sabotage_pmf.items():
        print(f"  {fail}, {outcome} → {prob:.6f}")

        
    from sympy import symbols, Eq, solve, simplify

    # 1. Declare the four unknown symbols:
    sD, sN, sC, B = symbols("sD sN sC B", real=True)

    pmf = {k: v for k, v in sabotage_pmf.items() if v > 0}

    # 3. Assemble the EV sum:
    EV = 0
    for (fail, outcome), p in pmf.items():
        if fail == 3 and outcome == "N":
            # payoff = B + sN
            EV += (B + sN) * p
        else:
            # for fail in {0,1,2} and outcome in {"D","N","C"}:
            if outcome == "D":
                payoff = sD
            elif outcome == "N":
                payoff = B + sN
            else:  # outcome == "C"
                payoff = B + sC
            EV += payoff * p

    EV = simplify(EV)  # clean up the symbolic expression
    print("\nSymbolic expected value (EV) expression:")
    print(EV)
    eq = Eq(EV, 0)

    # 6. Solve for B
    sol_for_B = solve(eq, B, dict=True)
    print(sol_for_B)


    # Search ranges for integer variables (adjust as desired)
    sD_range = range(0, 11)      # outcome_score_map["D"]
    sN_range = range(-5, 6)      # outcome_score_map["N"]
    sC_range = range(-10, 1)     # outcome_score_map["C"]
    B_range  = range(-20, 1)     # base_sabotage_score

    results = []  # to store (abs_EV, EV, sD, sN, sC, B)

    # Compute EV for each combination
    for sD in sD_range:
        for sN in sN_range:
            for sC in sC_range:
                for B in B_range:
                    EV = 0.0
                    for (fail, outcome), p in pmf.items():
                        if fail == 3 and outcome == "N":
                            payoff = B + sN
                        else:
                            if outcome == "D":
                                payoff = sD
                            elif outcome == "N":
                                payoff = B + sN
                            else:  # "C"
                                payoff = B + sC
                        EV += payoff * p
                    results.append((abs(EV), EV, sD, sN, sC, B))

    # Sort by absolute EV ascending
    results.sort(key=lambda x: x[0], reverse=False)

    # Take top 5
    k=20
    topk = results[k:k+10]

    # Build DataFrame
    df = pd.DataFrame(topk, columns=["|EV|", "EV", "sD", "sN", "sC", "B"])
    print(df.to_markdown(index=False))