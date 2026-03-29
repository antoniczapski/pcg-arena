import json

for f in ['level-stats', 'votes', 'player-profiles', 'trajectories']:
    with open(f'eda/data_23_03/pcg-arena-{f}-2026-03-23.json') as fh:
        data = json.load(fh)
        if isinstance(data, list):
            print(f'{f}: {len(data)} records (list)')
            if len(data) > 0:
                print(f'  keys: {list(data[0].keys())[:20]}')
        elif isinstance(data, dict):
            print(f'{f}: dict with {len(data)} top-level keys: {list(data.keys())[:10]}')
            first_key = list(data.keys())[0]
            val = data[first_key]
            if isinstance(val, list):
                print(f'  first key "{first_key}": {len(val)} records')
                if len(val) > 0 and isinstance(val[0], dict):
                    print(f'    sub-keys: {list(val[0].keys())[:20]}')
            elif isinstance(val, dict):
                print(f'  first key "{first_key}": dict with keys {list(val.keys())[:20]}')
