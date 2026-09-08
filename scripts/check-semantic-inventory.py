#!/usr/bin/env python3
"""Check semantic coverage bookkeeping; this does not execute PHP semantics."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--complete', action='store_true', help='also reject unfinished obligations')
args = parser.parse_args()
features = json.loads((ROOT / 'coverage/semantics/features.json').read_text())
schema = json.loads((ROOT / 'spec/schema.json').read_text())['nodes']
constructors = features['constructors']
obligations = features['runtime_obligations']
errors = []


def require(condition, message):
    if not condition:
        errors.append(message)


names = [entry['node'] for entry in constructors]
ids = [entry['id'] for entry in obligations]
require(len(names) == len(set(names)), 'duplicate syntax constructor entries')
require(set(names) == set(schema), 'syntax constructor membership differs from spec/schema.json')
require(len(ids) == len(set(ids)), 'duplicate runtime obligation IDs')
require(features['constructor_count'] == len(constructors), 'incorrect constructor_count')
require(features['runtime_obligation_count'] == len(obligations), 'incorrect runtime_obligation_count')
for entry in constructors:
    name = entry['node']
    if name in schema:
        require(entry['constructor'] == schema[name]['constructor'], f'{name}: incorrect SpecTec constructor')
    require(bool(entry['obligations']), f'{name}: missing runtime/contextual obligations')
    require(set(entry['obligations']) <= set(ids), f'{name}: unknown obligation reference')
for entry in obligations:
    name = entry['id']
    require(set(entry['dependencies']) <= set(ids), f'{name}: unknown dependency reference')
    require(name not in entry['dependencies'], f'{name}: self dependency')

finished = {'validated', 'compile-rejected', 'metadata'}
for entry in constructors + obligations:
    name = entry.get('id', entry.get('node'))
    status = entry['status']
    require(status in features['status_policy'], f'{name}: unknown status {status}')
    if status in finished:
        require(bool(entry['review']), f'{name}: missing independent review')
        require(bool(entry['source_tests']), f'{name}: missing source-level evidence')
        require(bool(entry['implementation']), f'{name}: missing implementation')
        if 'id' in entry and name.split('.')[0] in {'numeric', 'bytes', 'coercion'}:
            require(bool(entry['helper_tests']), f'{name}: missing helper-level evidence')
    if args.complete:
        require(status in finished, f'{name}: unfinished ({status})')

if errors:
    for error in errors:
        print(error)
    raise SystemExit(1)
print(f'Inventory consistent: {len(constructors)} constructors, {len(obligations)} runtime obligations; '
      f'{sum(entry["status"] in finished for entry in constructors)} constructors and '
      f'{sum(entry["status"] in finished for entry in obligations)} obligations closed.')
