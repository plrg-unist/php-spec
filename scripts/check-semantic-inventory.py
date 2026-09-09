#!/usr/bin/env python3
"""Check semantic coverage bookkeeping; this does not execute PHP semantics."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--complete', action='store_true', help='also reject unfinished obligations')
args = parser.parse_args()
features = json.loads((ROOT / 'coverage/semantics/features.json').read_text())
schema = json.loads((ROOT / 'spec/schema.json').read_text())['nodes']
constructors = features['constructors']
obligations = features['runtime_obligations']
errors = []
covered_divergences = set()


def require(condition, message):
    if not condition:
        errors.append(message)


def evidence_file(reference):
    path = ROOT / reference
    if not path.is_file() or not path.resolve().is_relative_to(ROOT):
        raise ValueError(f'missing or escaping evidence path {reference}')
    return path


def evidence_require(condition, message):
    if not condition:
        raise ValueError(message)


def check_closure(entry):
    """Bind reviewed scope to original-source observations, not report totals."""
    name = entry.get('id', entry.get('node'))
    try:
        closure = entry['closure']
        scope, branches = closure['scope'], closure['branches']
        evidence_require(isinstance(scope, str) and scope.strip(), 'missing closure scope')
        evidence_require(isinstance(branches, list) and branches and all(
            isinstance(b['name'], str) and b['name'].strip() and
            isinstance(b['case_ids'], list) and b['case_ids'] for b in branches), 'missing branch cases')
        evidence_require(len({b['name'] for b in branches}) == len(branches), 'duplicate closure branch')
        case_ids = {case for branch in branches for case in branch['case_ids']}
        evidence_require(all(isinstance(case, str) and case for case in case_ids), 'invalid case IDs')
        report_path = evidence_file(closure['source_report'])
        evidence_require(closure['source_report'] in entry['source_tests'], 'unlisted source report')
        report = json.loads(report_path.read_text())
        fingerprint = report['fingerprints']['sha256']
        evidence_require(isinstance(fingerprint, str) and re.fullmatch('[0-9a-f]{64}', fingerprint), 'invalid implementation digest')
        evidence_require(report['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_text()), 'wrong oracle profile')
        evidence_require(report['environment'] == {'LC_ALL': 'C', 'TZ': 'UTC'}, 'wrong oracle environment')
        oracle = report['oracle']
        evidence_require((oracle['version'], oracle['sapi'], oracle['int_size'], oracle['zts'], oracle['source_commit']) ==
                         ('8.5.10', 'cli', 8, False, '34308a6666b2d489c509541ea9befea9e2b42348'), 'wrong oracle target')
        evidence_require(isinstance(oracle['binary_sha256'], str) and re.fullmatch('[0-9a-f]{64}', oracle['binary_sha256']), 'invalid oracle digest')
        rows = report['results']
        evidence_require(len({row['id'] for row in rows}) == len(rows), 'duplicate source case IDs')
        rows = {row['id']: row for row in rows}
        evidence_require(case_ids <= rows.keys(), 'missing selected source case')
        raw_info = report['raw_results']
        raw_path = evidence_file(raw_info['path'])
        evidence_require(hashlib.sha256(raw_path.read_bytes()).hexdigest() == raw_info['sha256'], 'raw report hash mismatch')
        raw = [json.loads(line) for line in raw_path.read_text().splitlines()]
        evidence_require(len(raw) == raw_info['records'] == len(rows), 'raw record count mismatch')
        evidence_require(len({row['id'] for row in raw}) == len(raw), 'duplicate raw case IDs')
        raw = {row['id']: row for row in raw}
        evidence_require(raw.keys() == rows.keys(), 'raw/source membership mismatch')
        declared = {item['id']: item for item in features['intentional_divergences']}
        used_divergences = set()
        for case in case_ids:
            row, observation = rows[case], raw[case]
            source_hash = hashlib.sha256(base64.b64decode(observation['source_base64'], validate=True)).hexdigest()
            evidence_require(source_hash == row['source_sha256'] == observation['source_sha256'], 'original source hash mismatch')
            semantic = observation['semantic']
            evidence_require(semantic['status'] == row['semantic_status'], 'semantic status mismatch')
            evidence_require(semantic['status'] in {'normal', 'php_error', 'static_rejection'}, 'nonsemantic outcome cannot close an obligation')
            if entry['status'] == 'compile-rejected':
                evidence_require(semantic['status'] == 'static_rejection', 'compile rejection lacks a static outcome')
            actual = {key: semantic[key] for key in ('stdout', 'stderr', 'exit_status')}
            for stream in ('stdout', 'stderr'):
                base64.b64decode(actual[stream], validate=True)
                base64.b64decode(observation['oracle'][stream], validate=True)
            evidence_require(type(actual['exit_status']) is int and type(observation['oracle']['exit_status']) is int, 'missing process outcome')
            evidence_require(row['comparison'] == observation['comparison'], 'comparison classification mismatch')
            if row['comparison'] == 'pass':
                evidence_require(actual == observation['oracle'], 'false differential pass')
                evidence_require(not row.get('divergence') and not observation.get('divergence'), 'divergence counted as differential pass')
            else:
                evidence_require(row['comparison'] == 'intentional-divergence', 'failed source comparison')
                divergence = row['divergence']
                evidence_require(observation['divergence'] == divergence and divergence in declared, 'undeclared divergence')
                binding = declared[divergence]['source_integration']
                evidence_require(isinstance(binding, dict) and binding['report'] == closure['source_report'] and case in binding['case_ids'], 'missing divergence source integration')
                evidence_require(actual != observation['oracle'] and actual == observation['expected_semantic'], 'invalid intended-divergence observation')
                used_divergences.add(divergence)
        evidence_require(set(closure['divergences']) == used_divergences, 'divergence accounting mismatch')
        review = json.loads(evidence_file(closure['independent_review']).read_text())
        evidence_require(review['decision'] == 'accepted' and review['reviewer'].strip(), 'missing independent acceptance')
        expected = {'entry': name, 'scope': scope, 'branches': branches,
                    'source_report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
                    'implementation_sha256': fingerprint, 'divergences': closure['divergences']}
        evidence_require(all(review.get(key) == value for key, value in expected.items()), 'independent review binding mismatch')
        if args.complete:
            sys.path.insert(0, str(ROOT / 'tests'))
            import validate
            evidence_require(validate.implementation_fingerprint()['sha256'] == fingerprint, 'stale source implementation fingerprint')
            evidence_require(hashlib.sha256((ROOT / '.tools/php/bin/php').read_bytes()).hexdigest() == oracle['binary_sha256'], 'stale oracle binary fingerprint')
        covered_divergences.update(used_divergences)
    except (AttributeError, KeyError, TypeError, ValueError, OSError) as error:
        errors.append(f'{name}: invalid closure evidence: {error}')


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
    for field in ('implementation', 'source_tests', 'helper_tests'):
        for reference in entry.get(field, []):
            path = ROOT / reference
            require(path.is_file() and path.resolve().is_relative_to(ROOT),
                    f'{name}: missing or escaping {field} path {reference}')
    if status in finished:
        require(bool(entry['review']), f'{name}: missing independent review')
        require(bool(entry['source_tests']), f'{name}: missing source-level evidence')
        require(bool(entry['implementation']), f'{name}: missing implementation')
        if 'id' in entry and name.split('.')[0] in {'numeric', 'bytes', 'coercion'}:
            require(bool(entry['helper_tests']), f'{name}: missing helper-level evidence')
        check_closure(entry)
    if args.complete:
        require(status in finished, f'{name}: unfinished ({status})')

if args.complete:
    for divergence in features['intentional_divergences']:
        require(divergence['id'] in covered_divergences,
                f'{divergence["id"]}: missing intentional-divergence source integration')

if errors:
    for error in errors:
        print(error)
    raise SystemExit(1)
print(f'Inventory consistent: {len(constructors)} constructors, {len(obligations)} runtime obligations; '
      f'{sum(entry["status"] in finished for entry in constructors)} constructors and '
      f'{sum(entry["status"] in finished for entry in obligations)} obligations closed.')
