"""Fixed warning-consumer sources and reached states with original process records."""
from pathlib import Path
import argparse
import base64
import json
import subprocess
import tempfile
import time

from error_handler_run import ROOT, ENV, describe, group, recorded
from warning_consumer_cases import CASES as SOURCES
from warning_consumer_protocol import CASES

SOURCE_CAP = 1650
FINITE_CAP = 1230


def inputs():
    paths = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths += [ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'spec/nodes.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py',
        'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py',
        'tests/semantics/error_handler_protocol.py', 'tests/semantics/error_handler_cases.py',
        'tests/semantics/warning_consumer_cases.py', 'tests/semantics/warning_consumer_protocol.py',
        'tests/semantics/warning_consumer_prepare.py', 'tests/semantics/warning_consumer_run.py',
        'tests/semantics/warning_truth_cases.py',
        'bin/php-semantics', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        '.tools/spectec/bin/p4spectec', '.tools/request-clock.so')]
    return {str(p): describe(p) for p in paths}


def revision():
    return {key: subprocess.check_output(command, cwd=ROOT, env=ENV).decode().strip()
            for key, command in (
                ('head', ['git', 'rev-parse', 'HEAD']),
                ('status', ['git', 'status', '--porcelain']),
                ('index_tree', ['git', 'write-tree']))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepared', type=Path)
    parser.add_argument('--source', action='append')
    parser.add_argument('--finite', action='append')
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
    if args.source is not None:
        assert args.source and len(args.source) == len(set(args.source))
        assert set(args.source) <= set(expected)
        sources = [r for r in sources if r['id'] in args.source]
    if args.finite is not None:
        assert args.finite and len(args.finite) == len(set(args.finite))
        assert set(args.finite) <= {c[0] for c in CASES}
        finite = [r for r in finite if r['id'] in args.finite]
    before = revision()
    assert not before['status'], before
    out = Path(tempfile.mkdtemp(prefix='run-', dir=ROOT / '.tools/warning-consumers'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
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
            stem = out / ('source-' + row['id'])
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
            model = recorded([str(ROOT / 'bin/php-semantics'), row['path'], '--steps', '100000', '--timeout', '60'],
                             model_stem, min(90, remaining))
            observed = json.loads(model_stem.with_suffix('.stdout').read_bytes())
            result.update({'model': model, 'observation': observed})
            passed = (not model['timeout'] and not model_stem.with_suffix('.stderr').read_bytes()
                      and observed.get('frontend') == 'accepted' and observed.get('checked') == 'program'
                      and observed.get('status') == wanted[2])
            if wanted[2] == 'unsupported':
                passed = passed and model['exit'] == 1 and observed.get('reason') == 'error-handler throw with rejected constrained assignment'
            else:
                passed = (passed and model['exit'] == 0 and observed.get('exit_status') == 0
                          and observed.get('stdout') == base64.b64encode(nout).decode()
                          and observed.get('stderr') == base64.b64encode(nerr).decode())
            result['passed'] = passed
            print(row['id'], passed, flush=True)
            assert passed, row['id']
        deadline = time.monotonic() + FINITE_CAP
        for row in finite:
            stem = out / ('finite-' + row['id'])
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
