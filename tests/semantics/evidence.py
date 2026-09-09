#!/usr/bin/env python3
"""Negative checks for the shared source campaign's implementation identity."""
import copy
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
import validate

ARCHIVES = ['coverage/semantics/comparison-phase-originals.json',
            'coverage/semantics/comparison-overflow-draft-disagreement.json']


def check_inventory_paths():
    with tempfile.TemporaryDirectory(prefix='php-inventory-') as directory:
        root = Path(directory) / 'project'
        features = json.loads((ROOT / 'coverage/semantics/features.json').read_text())
        for entry in features['constructors'] + features['runtime_obligations']:
            # This fixture isolates path checks; closure observations are tested
            # separately below, with real synthetic report contents.
            entry['status'] = 'pending'
            for field in ('implementation', 'source_tests', 'helper_tests'):
                for name in entry.get(field, []):
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
        for name in ('scripts/check-semantic-inventory.py', 'spec/schema.json'):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
        catalog = root / 'coverage/semantics/features.json'
        catalog.parent.mkdir(parents=True, exist_ok=True)
        def check(value):
            catalog.write_text(json.dumps(value))
            return subprocess.run([sys.executable, str(root / 'scripts/check-semantic-inventory.py')],
                                  capture_output=True, text=True, timeout=5)
        assert check(features).returncode == 0
        missing = copy.deepcopy(features)
        missing['constructors'][0]['implementation'] = ['missing.watsup']
        result = check(missing)
        assert result.returncode and 'missing or escaping implementation path' in result.stdout
        outside = Path(directory) / 'outside-evidence'
        outside.write_text('pass')
        (root / 'evidence-link').symlink_to(outside)
        escaping = copy.deepcopy(features)
        escaping['runtime_obligations'][0]['helper_tests'] = ['evidence-link']
        result = check(escaping)
        assert result.returncode and 'missing or escaping helper_tests path' in result.stdout
        unproved = copy.deepcopy(features)
        unproved['constructors'][0]['status'] = 'validated'
        unproved['constructors'][0]['source_tests'] = []
        result = check(unproved)
        assert result.returncode and 'missing source-level evidence' in result.stdout
        assert check(features).returncode == 0


def check_closure_bindings():
    # A synthetic one-entry inventory exercises --complete without
    # relabeling any unfinished production obligation or invoking the oracle.
    with tempfile.TemporaryDirectory(prefix='php-closure-') as directory:
        root = Path(directory)
        for name in ('scripts/check-semantic-inventory.py', 'tests/validate.py',
                     'tests/corpus.py', 'frontend/wire.py', 'tests/semantics/profile.json'):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        for name in ('Makefile', 'dune-project', '.tools/php/bin/php', '.tools/php-file.so',
                     '_build/default/adapter/main.exe', 'coverage/encoding-spellings.json',
                     'spec/rule.watsup', *ARCHIVES):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'fixture')
        (root / 'spec/schema.json').write_text(json.dumps({'nodes': {'Stmt_Nop': {'constructor': 'NStmtNop'}}}))
        closure = {'scope': 'fixture no-op', 'branches': [{'name': 'normal', 'case_ids': ['empty']}],
                   'source_report': 'coverage/source.json', 'independent_review': 'coverage/review.json',
                   'divergences': []}
        entry = {'status': 'validated', 'implementation': ['spec/rule.watsup'],
                 'source_tests': ['coverage/source.json'], 'helper_tests': [],
                 'review': 'fixture independent review', 'closure': closure}
        catalog = {'constructors': [{'node': 'Stmt_Nop', 'constructor': 'NStmtNop',
                                    'obligations': ['fixture.no-op'], **copy.deepcopy(entry)}],
                   'runtime_obligations': [{'id': 'fixture.no-op', 'dependencies': [], **entry}],
                   'constructor_count': 1, 'runtime_obligation_count': 1,
                   'status_policy': {'validated': 'fixture'}, 'intentional_divergences': []}
        # Give the constructor its own independently bound review artifact.
        catalog['constructors'][0]['closure']['independent_review'] = 'coverage/constructor-review.json'
        source = b'<?php ;'
        digest = hashlib.sha256(source).hexdigest()
        raw = {'id': 'empty', 'source_sha256': digest,
               'source_base64': base64.b64encode(source).decode(),
               'semantic': {'status': 'normal', 'stdout': '', 'stderr': '', 'exit_status': 0},
               'oracle': {'stdout': '', 'stderr': '', 'exit_status': 0}, 'comparison': 'pass'}
        row = {'id': 'empty', 'source_sha256': digest, 'semantic_status': 'normal', 'comparison': 'pass'}
        previous = validate.ROOT
        validate.ROOT = root
        try:
            fingerprint = validate.implementation_fingerprint()
        finally:
            validate.ROOT = previous
        report = {'fingerprints': fingerprint, 'results': [row],
                  'profile': json.loads((root / 'tests/semantics/profile.json').read_text()),
                  'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
                  'oracle': {'version': '8.5.10', 'sapi': 'cli', 'int_size': 8, 'zts': False,
                             'source_commit': '34308a6666b2d489c509541ea9befea9e2b42348',
                             'binary_sha256': hashlib.sha256(b'fixture').hexdigest()}}
        def save(value=catalog, result=report, observation=raw):
            raw_path = root / 'coverage/raw.jsonl'
            raw_path.write_text(json.dumps(observation) + '\n')
            result = copy.deepcopy(result)
            result['raw_results'] = {'path': 'coverage/raw.jsonl', 'records': 1,
                                    'sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest()}
            report_path = root / 'coverage/source.json'
            report_path.write_text(json.dumps(result))
            for item in value['constructors'] + value['runtime_obligations']:
                c = item['closure']
                review = {'entry': item.get('id', item.get('node')), 'scope': c['scope'],
                          'branches': c['branches'], 'divergences': c['divergences'],
                          'source_report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
                          'implementation_sha256': result['fingerprints']['sha256'],
                          'reviewer': 'independent fixture reviewer', 'decision': 'accepted'}
                (root / c['independent_review']).write_text(json.dumps(review))
            target = root / 'coverage/semantics/features.json'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(value))
        def check(expected=None, optimized=False):
            result = subprocess.run([sys.executable, *(['-O'] if optimized else []), str(root / 'scripts/check-semantic-inventory.py'), '--complete'],
                                    capture_output=True, text=True, timeout=5)
            assert (result.returncode == 0) if expected is None else (result.returncode and expected in result.stdout), result.stdout + result.stderr
        save(); check()
        for field, value, expected in [('profile', {}, 'wrong oracle profile'),
                                      ('environment', {}, 'wrong oracle environment')]:
            changed = copy.deepcopy(report); changed[field] = value
            save(result=changed); check(expected)
        changed = copy.deepcopy(report); changed['oracle']['version'] = '8.4.0'
        save(result=changed); check('wrong oracle target')
        changed = copy.deepcopy(report); changed['fingerprints']['sha256'] = 'claimed-current'
        save(result=changed); check('invalid implementation digest')
        for field, value, expected in [('source_sha256', 'wrong', 'original source hash mismatch'),
                                      ('semantic_status', 'unsupported', 'semantic status mismatch'),
                                      ('comparison', 'fail', 'comparison classification mismatch')]:
            changed = copy.deepcopy(report); changed['results'][0][field] = value
            save(result=changed); check(expected)
        changed = copy.deepcopy(catalog)
        changed['runtime_obligations'][0]['closure']['branches'][0]['case_ids'] = ['missing']
        save(value=changed); check('missing selected source case')
        changed = copy.deepcopy(raw); changed['semantic']['stdout'] = 'eA=='
        save(observation=changed); check('false differential pass')
        check('false differential pass', optimized=True)
        changed = copy.deepcopy(raw); changed['semantic']['status'] = 'unsupported'
        changed_report = copy.deepcopy(report); changed_report['results'][0]['semantic_status'] = 'unsupported'
        save(result=changed_report, observation=changed); check('nonsemantic outcome')
        save(); (root / 'coverage/raw.jsonl').write_text('{}\n'); check('raw report hash mismatch')
        save(); review_path = root / 'coverage/review.json'
        changed = json.loads(review_path.read_text()); changed['branches'] = []
        review_path.write_text(json.dumps(changed)); check('independent review binding mismatch')
        save(); review_path.unlink(); check('missing or escaping evidence path')
        save(); (root / 'spec/rule.watsup').write_bytes(b'changed'); check('stale source implementation fingerprint')
        (root / 'spec/rule.watsup').write_bytes(b'fixture')
        # Intentional differences require original-source integration and a
        # separate expected semantic outcome; a helper-only ledger cannot close.
        changed = copy.deepcopy(catalog)
        changed['intentional_divergences'] = [{'id': 'fixture-divergence', 'source_integration': 'pending'}]
        for item in changed['constructors'] + changed['runtime_obligations']:
            item['closure']['divergences'] = ['fixture-divergence']
        different_raw = copy.deepcopy(raw); different_raw.update(comparison='intentional-divergence', divergence='fixture-divergence')
        different_raw['semantic']['stdout'] = 'eA=='
        different_raw['expected_semantic'] = {'stdout': 'eA==', 'stderr': '', 'exit_status': 0}
        different_report = copy.deepcopy(report)
        different_report['results'][0].update(comparison='intentional-divergence', divergence='fixture-divergence')
        save(changed, different_report, different_raw); check('missing divergence source integration')
        changed['intentional_divergences'][0]['source_integration'] = {'report': 'coverage/source.json', 'case_ids': ['empty']}
        save(changed, different_report, different_raw); check()
        different_raw['comparison'] = 'pass'; different_report['results'][0]['comparison'] = 'pass'
        different_raw['oracle'] = different_raw['expected_semantic']
        save(changed, different_report, different_raw); check('divergence counted as differential pass')
        save(); check()


def main():
    # A disposable project exercises the actual fingerprint function; no live
    # specification, binary or retained acceptance report is mutated.
    with tempfile.TemporaryDirectory(prefix='php-evidence-') as directory:
        root = Path(directory)
        fixed = ['Makefile', 'dune-project', '.tools/php/bin/php',
                 '.tools/php-file.so', '.tools/request-clock.so', '_build/default/adapter/main.exe',
                 'coverage/encoding-spellings.json']
        helper_name = 'tests/semantics/_build/default/numeric_runner.exe'
        for name in fixed + ARCHIVES + [helper_name, 'spec/semantics/rules.watsup', 'tests/fixture.php',
                             'tests/semantics/dune', 'tests/semantics/data.json']:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'original')
        original_root = validate.ROOT
        validate.ROOT = root
        try:
            before = validate.implementation_fingerprint()
            assert before == validate.implementation_fingerprint()
            source = root / 'spec/semantics/rules.watsup'
            stamp = source.stat()
            source.write_bytes(b'modified')  # Same size and restored mtime.
            os.utime(source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            assert before != validate.implementation_fingerprint(), 'stale source bytes accepted'
            source.write_bytes(b'original')
            assert before == validate.implementation_fingerprint()

            added = root / 'spec/semantics/new.watsup'
            added.write_bytes(b'original')
            assert before != validate.implementation_fingerprint(), 'added source path ignored'
            added.unlink()
            moved = source.with_name('renamed.watsup')
            source.rename(moved)
            assert before != validate.implementation_fingerprint(), 'renamed source path ignored'
            moved.rename(source)
            source.unlink()
            assert before != validate.implementation_fingerprint(), 'deleted source path ignored'
            source.write_bytes(b'original')

            binary = root / '.tools/php/bin/php'
            binary.write_bytes(b'modified')
            assert before != validate.implementation_fingerprint(), 'changed oracle binary ignored'
            binary.unlink()
            try:
                validate.implementation_fingerprint()
            except FileNotFoundError:
                pass
            else:
                raise AssertionError('missing pinned oracle accepted')
            binary.write_bytes(b'original')
            assert before == validate.implementation_fingerprint(), 'restored fixture differs'

            # Concurrent dune runs may rewrite these without changing any input
            # or executable. Their presence, contents and deletion are irrelevant.
            for name in ('.lock', 'trace.csexp', '.filesystem-clock'):
                log = root / 'tests/semantics/_build' / name
                log.write_bytes(b'first build')
                assert before == validate.implementation_fingerprint(), 'build log addition changed identity'
                log.write_bytes(b'next build')
                assert before == validate.implementation_fingerprint(), 'build log churn changed identity'
                log.unlink()
                assert before == validate.implementation_fingerprint(), 'build log removal changed identity'
            for name in ('tests/semantics/dune', 'tests/semantics/data.json',
                         '_build/default/adapter/main.exe', helper_name, *ARCHIVES):
                artifact = root / name
                artifact.write_bytes(b'modified')
                assert before != validate.implementation_fingerprint(), f'changed input ignored: {name}'
                artifact.write_bytes(b'original')
            for name in ARCHIVES:
                archive = root / name
                archive.unlink()
                try:
                    validate.implementation_fingerprint()
                except FileNotFoundError:
                    pass
                else:
                    raise AssertionError(f'missing mandatory archive accepted: {name}')
                archive.write_bytes(b'original')
            helper = root / helper_name
            helper.unlink()
            assert before != validate.implementation_fingerprint(), 'deleted helper binary ignored'
            helper.write_bytes(b'original')
            provider = root / '.tools/request-clock.so'
            provider.write_bytes(b'modified')
            assert before != validate.implementation_fingerprint(), 'changed request provider ignored'
            provider.unlink()
            assert before != validate.implementation_fingerprint(), 'deleted request provider ignored'
            provider.write_bytes(b'original')
            assert before == validate.implementation_fingerprint(), 'restored artifacts differ'
        finally:
            validate.ROOT = original_root
    check_inventory_paths()
    check_closure_bindings()
    print('17 stale-identity, 3 invalid-path and 17 invalid-closure checks rejected; valid source/divergence bindings passed; 9 build-log changes ignored')


if __name__ == '__main__':
    main()
