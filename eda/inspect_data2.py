import json

for f in ['level-stats', 'votes', 'player-profiles', 'trajectories']:
    with open(f'eda/data_23_03/pcg-arena-{f}-2026-03-23.json') as fh:
        data = json.load(fh)
        total = data.get('total', '?')
        records = data.get('data', [])
        print(f'{f}: total={total}, fetched={len(records)}')
        if len(records) > 0:
            print(f'  keys: {list(records[0].keys())[:25]}')
            print(f'  sample: {json.dumps(records[0], indent=2)[:500]}')
        print()
