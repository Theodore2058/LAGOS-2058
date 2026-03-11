"""Run a full 12-turn campaign with actions for all 14 parties, spending nearly all PC each turn."""
import urllib.request
import json

BASE = 'http://127.0.0.1:8000/api'

def get(path):
    return json.loads(urllib.request.urlopen(f'{BASE}{path}').read())

def post(path, data):
    req = urllib.request.Request(f'{BASE}{path}', data=json.dumps(data).encode(),
                                headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=120).read())

party_names = [p['name'] for p in get('/parties')['parties']]
print(f'Loaded {len(party_names)} parties: {party_names}')

# Start new campaign
state = post('/campaign/new', {
    'parties': get('/parties')['parties'],
    'params': {
        'q': 0.5, 'beta_s': 3.0, 'alpha_e': 3.0, 'alpha_r': 2.0, 'scale': 1.5,
        'tau_0': 3.0, 'tau_1': 0.3, 'tau_2': 0.5, 'beta_econ': 0.3,
        'kappa': 200, 'sigma_national': 0.10, 'sigma_regional': 0.15,
        'sigma_turnout': 0.0, 'sigma_turnout_regional': 0.0,
    },
    'n_monte_carlo': 5,
    'seed': 42,
    'n_turns': 12,
})
print(f'Campaign started: Turn {state["turn"]}/{state["n_turns"]}, Phase: {state["phase"]}')

def get_azs(party_idx):
    if party_idx % 3 == 0: return [1, 4, 5]
    elif party_idx % 3 == 1: return [6, 7, 8]
    else: return [2, 3, 6]

# Action plans per turn (costs must total ~7 PC per party, max 3 actions/party/turn)
TURN_PLANS = {
    1: [
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
        {'action_type': 'advertising', 'parameters': {'medium': 'radio', 'budget': 1.0, 'language': 'english'}},
        {'action_type': 'media', 'parameters': {'tone': 'positive', 'narrative': 'Vision for 2058'}},
    ],  # 2+2+1=5
    2: [
        {'action_type': 'ground_game', 'parameters': {'intensity': 1.0, 'language': 'english'}},
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
    ],  # 3+2=5
    3: [
        {'action_type': 'manifesto', 'parameters': {}},
        {'action_type': 'advertising', 'parameters': {'medium': 'tv', 'budget': 1.0, 'language': 'english'}},
        {'action_type': 'media', 'parameters': {'tone': 'positive', 'narrative': 'Policy agenda'}},
    ],  # 3+2+1=6
    4: [
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
        {'action_type': 'endorsement', 'parameters': {'endorser_type': 'Traditional ruler', 'endorser_name': 'Chief'}},
        {'action_type': 'ground_game', 'parameters': {'intensity': 1.0, 'language': 'english'}},
    ],  # 2+2+3=7
    5: [
        {'action_type': 'advertising', 'parameters': {'medium': 'internet', 'budget': 1.0, 'language': 'english'}},
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
        {'action_type': 'media', 'parameters': {'tone': 'contrast', 'narrative': 'Better choice'}},
    ],  # 2+2+1=5
    6: [
        {'action_type': 'ground_game', 'parameters': {'intensity': 1.0, 'language': 'english'}},
        {'action_type': 'endorsement', 'parameters': {'endorser_type': 'Celebrity', 'endorser_name': 'Popular figure'}},
    ],  # 3+2=5
    7: [
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
        {'action_type': 'ground_game', 'parameters': {'intensity': 1.0, 'language': 'english'}},
        {'action_type': 'endorsement', 'parameters': {'endorser_type': 'Religious leader', 'endorser_name': 'Cleric'}},
    ],  # 2+3+2=7
    8: [
        {'action_type': 'advertising', 'parameters': {'medium': 'tv', 'budget': 1.0, 'language': 'english'}},
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
        {'action_type': 'media', 'parameters': {'tone': 'negative', 'narrative': 'Opposition failures'}},
    ],  # 2+2+1=5
    9: [
        {'action_type': 'ground_game', 'parameters': {'intensity': 1.0, 'language': 'english'}},
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
    ],  # 3+2=5
    10: [
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
        {'action_type': 'advertising', 'parameters': {'medium': 'radio', 'budget': 1.0, 'language': 'english'}},
        {'action_type': 'ground_game', 'parameters': {'intensity': 1.0, 'language': 'english'}},
    ],  # 2+2+3=7
    11: [
        {'action_type': 'advertising', 'parameters': {'medium': 'tv', 'budget': 1.0, 'language': 'english'}},
        {'action_type': 'ground_game', 'parameters': {'intensity': 1.0, 'language': 'english'}},
        {'action_type': 'media', 'parameters': {'tone': 'positive', 'narrative': 'Final vision'}},
    ],  # 2+3+1=6
    12: [
        {'action_type': 'rally', 'parameters': {'language': 'english'}},
        {'action_type': 'ground_game', 'parameters': {'intensity': 1.0, 'language': 'english'}},
    ],  # 2+3=5
}

for turn in range(1, 13):
    plan = TURN_PLANS[turn]
    actions = []
    for i, pname in enumerate(party_names):
        azs = get_azs(i)
        for tmpl in plan:
            a = {
                'party': pname,
                'action_type': tmpl['action_type'],
                'target_lgas': None,
                'target_azs': azs if tmpl['action_type'] not in ['manifesto', 'fundraising', 'opposition_research'] else None,
                'target_party': None,
                'parameters': dict(tmpl['parameters']),
            }
            actions.append(a)

    print(f'\n=== Turn {turn} === ({len(actions)} actions for {len(party_names)} parties)')
    result = post('/campaign/advance', {'actions': actions, 'crises': []})

    shares = result['national_vote_shares']
    sorted_shares = sorted(shares.items(), key=lambda x: -x[1])
    print(f'  Turnout: {result["national_turnout"]*100:.1f}%')
    print(f'  Top 5: {", ".join(f"{n}={v*100:.1f}%" for n,v in sorted_shares[:5])}')
    seats = result['seat_counts']
    print(f'  Seats: {", ".join(f"{n}={seats[n]:.0f}" for n,_ in sorted_shares[:5])}')
    if result['synergies']:
        print(f'  Synergies: {len(result["synergies"])}')
    if result['scandals']:
        print(f'  SCANDALS: {[s.get("party","?") for s in result["scandals"]]}')

print('\n=== FINAL RESULTS ===')
sorted_final = sorted(result['national_vote_shares'].items(), key=lambda x: -x[1])
print(f'Turnout: {result["national_turnout"]*100:.1f}%')
for name, share in sorted_final:
    s = result['seat_counts'][name]
    print(f'  {name:5s}: {share*100:5.1f}%  Seats: {s:5.0f}')
print(f'\nWinner: {sorted_final[0][0]} with {sorted_final[0][1]*100:.1f}% and {result["seat_counts"][sorted_final[0][0]]:.0f} seats')
