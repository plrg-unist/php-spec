"""Held-PIPE source tuple and its reached truth state with original process records."""
from pathlib import Path
import argparse
import base64
import json
import subprocess
import tempfile
import time

from error_handler_run import ROOT, ENV, describe, group, recorded
from warning_truth_pipe import SOURCES, CASES
from warning_truth_run import inputs as base_inputs

SOURCE_CAP = 150
FINITE_CAP = 330


def inputs():
    watched = base_inputs()
    for name in ('warning_truth_pipe.py', 'warning_truth_pipe_prepare.py', 'warning_truth_pipe_run.py'):
        p = ROOT / 'tests/semantics' / name
        watched[str(p)] = describe(p)
    return watched


def revision():
    return {key: subprocess.check_output(command, cwd=ROOT, env=ENV).decode().strip()
            for key, command in (
                ('head', ['git', 'rev-parse', 'HEAD']),
                ('status', ['git', 'status', '--porcelain']),
                ('index_tree', ['git', 'write-tree']))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepared', type=Path)
    args = parser.parse_args()
    assert Path.cwd() == ROOT
    preparation = json.loads(args.prepared.read_text())
    assert preparation['passed'] and preparation['inputs'] == inputs()
    sources, finite = preparation['sources'], preparation['records']
    assert [r['id'] for r in sources] == [c[0] for c in SOURCES]
    assert [(r['id'], r['source_id'], r['assertions']) for r in finite] == [
        (c[0], c[1], len(c[3]) + 6) for c in CASES]
    assert all(r['passed'] for r in finite)
    expected = {name: (source, stdout, status) for name, source, stdout, status in SOURCES}
    watched = dict(preparation['inputs'])
    for row in sources:
        assert Path(row['path']).read_bytes() == expected[row['id']][0]
        watched[row['path']] = describe(row['path'])
    for row in finite:
        for key in ('fixture', 'al'):
            assert describe(row[key]) == row[key + '_descriptor']
            watched[row[key]] = describe(row[key])
    watched[str(args.prepared.resolve())] = describe(args.prepared)
    before = revision()
    assert not before['status'], before
    out = Path(tempfile.mkdtemp(prefix='run-', dir=ROOT / '.tools/warning-truth-pipe'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    assert len(profile) == 13 and 'include_path' not in profile
    profile['include_path'] = '.:'
    snapshot = out / 'snapshot.json'
    b64 = lambda data: base64.b64encode(data).decode()
    snapshot.write_text(json.dumps({'version': 2, 'main': b64(bytes(Path(sources[0]['path']))),
        'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'entries': [], 'chdir_entries': []}) + '\n')
    watched[str(snapshot)] = describe(snapshot)
    (out / 'TAKE.json').write_text(json.dumps({'revision': before, 'inputs': watched,
        'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'],
                        'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
        'profile': profile, 'producer_caps': {'native': 45, 'model': 90, 'finite': 300},
        'phase_caps': {'source': SOURCE_CAP, 'finite': FINITE_CAP},
        'selection': {'sources': [r['id'] for r in sources], 'finite': [r['id'] for r in finite]}}, indent=2) + '\n')
    print(out, flush=True)
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    rows, failure = [], None
    try:
        deadline = time.monotonic() + SOURCE_CAP
        for row in sources:
            stem = out / row['id']
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'source phase cap'
            native_stem = stem.with_name(stem.name + '-native')
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, row['path']],
                              native_stem, min(45, remaining))
            nout, nerr = native_stem.with_suffix('.stdout').read_bytes(), native_stem.with_suffix('.stderr').read_bytes()
            wanted = expected[row['id']]
            result = {'id': row['id'], 'phase': 'source', 'native': native,
                      'agreement': wanted[2] != 'unsupported', 'passed': False}
            rows.append(result)
            assert native['exit'] == 0 and not native['timeout'] and nout == wanted[1] and not nerr, row['id']
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'source phase cap'
            model_stem = stem.with_name(stem.name + '-model')
            model = recorded([str(ROOT / 'bin/php-semantics'), row['path'], '--steps', '100000', '--timeout', '60', '--file-snapshot', str(snapshot)],
                             model_stem, min(90, remaining))
            observed = json.loads(model_stem.with_suffix('.stdout').read_bytes())
            result.update({'model': model, 'observation': observed})
            passed = (not model['timeout'] and not model_stem.with_suffix('.stderr').read_bytes()
                      and observed.get('frontend') == 'accepted' and observed.get('checked') == 'program'
                      and observed.get('status') == wanted[2])
            passed = (passed and model['exit'] == 0 and observed.get('exit_status') == 0
                      and observed.get('stdout') == base64.b64encode(nout).decode()
                      and observed.get('stderr') == base64.b64encode(nerr).decode())
            result['passed'] = passed
            print(row['id'], passed, flush=True)
            assert passed, row['id']
        deadline = time.monotonic() + FINITE_CAP
        for row in finite:
            stem = out / row['id']
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'finite phase cap'
            producer = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *modules, row['fixture']], stem, min(300, remaining))
            passed = (producer['exit'] == 0 and not producer['timeout']
                      and stem.with_suffix('.stdout').read_bytes().strip() == b'true'
                      and not stem.with_suffix('.stderr').read_bytes())
            rows.append({'id': row['id'], 'phase': 'finite', 'assertions': row['assertions'],
                         'producer': producer, 'passed': passed})
            print(row['id'], passed, flush=True)
            assert passed, row['id']
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    after = {path: describe(path) for path in watched}
    current = revision()
    groups = {str(json.loads(p.read_text())['pgid']): group(json.loads(p.read_text())['pgid'])
              for p in out.glob('*.process.json')}
    empty = all(not members for members in groups.values())
    passed = (failure is None and len(rows) == len(sources) + len(finite)
              and all(r['passed'] for r in rows) and watched == after and before == current and empty)
    (out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before,
        'records': rows, 'failure': failure, 'inputs_stable': watched == after,
        'inputs_after': after, 'revision_after': current, 'groups_after': groups}, indent=2) + '\n')
    (out / 'RELEASE.json').write_text(json.dumps({'released': empty, 'passed': passed,
        'revision': current, 'inputs_stable': watched == after, 'groups_after': groups}) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
