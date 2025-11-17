import pandas as pd
import numpy as np

def calculate_base_score():
    pmf = build_base_pmf()
    


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

exit_early = True
sD=5     
sN=0    
sC=-(sD-sN)    
B = -5 #-sN
#sD=0     
#sN=0    
#sC=-0    
#B =-0


coop_mod = {"deflected":sC, "unknown":sN, "found":sD}
def_mod  = {"deflected":0,  "unknown":0, "found":0}

coop_event_finished = 0
def_event_sabotage  = -B
def_starting_score = 1

#loop over floor, round and ceil operators
#for op in ("none", "floor", "round", "ceil"):
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

        print(f"\n=== n_cooperators = {n_coop} ===")
        print("Cooperator table:\n", coop_tbl)
        print("\nDefector table:\n", def_tbl)
        
        print("\nDiff table:\n", diff_tbl)

        errors = check_constraints(coop_tbl, def_tbl)
        if errors:
            print(f"\nConstraint failures ({op}):")
            for e in errors:
                print("  -", e)
        else:
            print("\nAll constraints passed.")

if exit_early:
    exit()
from collections import defaultdict

def build_base_pmf():
    # 1. Probability of two consecutive rolls both being in {1,2}:
    # prob that you draw a bad card twice
    p =  (2/5) * (2/5)  # = 0.16
    

    # 2. Scenario 1: exactly one compound attempt (2 rolls)
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

if __name__ == "__main__":
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
    
    outcome_score_map = {
        "D": 5,  # Defector found
        "N": 0,   # No defector found
        "C": -5    # Cooperator found
    }
    base_sabotage_score = -10
    
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
                bonus = 0 if outcome == "D" else base_sabotage_score
                #expected_values[(fail, outcome)] = ( bonus + outcome_score_map[outcome]) * sabotage_pmf[(fail, outcome)]
                
            
    print("\nSabotage PMF (fail, outcome):")
    for (fail, outcome), prob in sabotage_pmf.items():
        print(f"  {fail}, {outcome} → {prob:.6f}")
        
  
    '''print("\nExpected values for each fail-outcome pair:")
    for (fail, outcome), ev in expected_values.items():
        print(f"  {fail}, {outcome} → {ev:.6f}")
        
    print("\nTotal expected value of sabotage outcomes:")
    total_ev = sum(expected_values.values())
    print(f"  Total EV: {total_ev:.6f}")'''
        
    from sympy import symbols, Eq, solve, simplify

    # 1. Declare the four unknown symbols:
    sD, sN, sC, B = symbols("sD sN sC B", real=True)

    # 2. Build a dict of all nonzero PMF entries:
    '''pmf = {
        (0, "D"): 0.100151,
        (0, "N"): 0.100151,
        (0, "C"): 0.100151,
        (1, "D"): 0.129621,
        (1, "N"): 0.129621,
        (1, "C"): 0.129621,
        (2, "D"): 0.073627,
        (2, "N"): 0.073627,
        (2, "C"): 0.073627,
        (3, "N"): 0.089802,
    }'''
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