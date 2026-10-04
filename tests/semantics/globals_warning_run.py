"""Fixed original ordinary/request sources and focused finite-state comparisons."""
from pathlib import Path
import argparse
import base64
import json
import resource
import struct
import sys
import tempfile
import time

import warning_consumer_run as family
from globals_warning_cases import CASES as SOURCES
from globals_warning_protocol import CASES
from error_handler_run import ROOT, ENV, describe, group, recorded
from warning_consumer_run import revision


def inputs():
    watched = family.inputs()
    for name in ('globals_warning_cases.py', 'globals_warning_protocol.py',
                 'globals_warning_prepare.py', 'globals_warning_run.py'):
        path = ROOT / 'tests/semantics' / name
        watched[str(path)] = describe(path)
    return watched


def facts(path):
    b64 = lambda value: base64.b64encode(value).decode()
    return {'env': [[b64(b'LC_ALL'), b64(b'C')], [b64(b'TZ'), b64(b'UTC')]],
            'argv': [b64(str(path).encode())], 'file': b64(str(path).encode()),
            'seconds': '1700000000', 'microseconds': 125000,
            'variables': b64(b'EGPCS'), 'jit': True, 'cwd': b64(str(ROOT).encode())}


# This transport only passes primitive request inputs before the original CLI
# starts. It computes no PHP globals or source execution results.
REQUEST_EXEC = '''import os,sys
fd=os.open(sys.argv[-1],os.O_RDONLY)
os.dup2(fd,198,inheritable=True)
if fd!=198: os.close(fd)
env=dict(os.environ,LD_PRELOAD=sys.argv[-2])
os.execve(sys.argv[1],sys.argv[1:-2],env)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepared', type=Path)
    parser.add_argument('--source', action='append')
    parser.add_argument('--finite', action='append')
    args = parser.parse_args()
    preparation = json.loads(args.prepared.read_bytes())
    assert preparation['passed'] and preparation['inputs'] == inputs()
    sources, finite = preparation['sources'], preparation['records']
    assert [r['id'] for r in sources] == [c[0] for c in SOURCES]
    assert [(r['id'], r['source_id'], r['assertions']) for r in finite] == [(c[0], c[1], len(c[3]) + 6) for c in CASES]
    expected = {c[0]: c for c in SOURCES}
    watched = dict(preparation['inputs'])
    for row in sources:
        assert Path(row['path']).read_bytes() == expected[row['id']][1]
        assert row['request'] == (facts(Path(row['path'])) if expected[row['id']][4] else None)
        watched[row['path']] = describe(row['path'])
    for row in finite:
        for key in ('fixture', 'al'):
            assert describe(row[key]) == row[key + '_descriptor']
            watched[row[key]] = describe(row[key])
    watched[str(args.prepared.resolve())] = describe(args.prepared)
    if args.source is not None:
        assert args.source and len(args.source) == len(set(args.source)) and set(args.source) <= set(expected)
        sources = [r for r in sources if r['id'] in args.source]
    if args.finite is not None:
        assert args.finite and len(args.finite) == len(set(args.finite)) and set(args.finite) <= {c[0] for c in CASES}
        finite = [r for r in finite if r['id'] in args.finite]
    head = revision()
    assert not head['status'], head
    out = Path(tempfile.mkdtemp(prefix='run-', dir=ROOT / '.tools/globals-warning'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    (out / 'context.json').write_text(json.dumps({'revision': head, 'inputs': watched, 'profile': profile,
        'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'], 'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
        'jobs': 1, 'caps': {'native': 45, 'model': 90, 'cli': 60, 'steps': 100000, 'finite': 300, 'source_phase': 1245, 'finite_phase': 930},
        'limits': {name: list(resource.getrlimit(getattr(resource, 'RLIMIT_' + name))) for name in ('AS', 'CPU', 'STACK', 'DATA', 'NOFILE', 'NPROC')},
        'selection': {'sources': [r['id'] for r in sources], 'finite': [r['id'] for r in finite]}}, indent=2) + '\n')
    print(out, flush=True)
    rows, failure = [], None
    try:
        deadline = time.monotonic() + 1245
        for source in sources:
            name = source['id']
            native_argv = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, source['path']]
            model_argv = [str(ROOT / 'bin/php-semantics'), source['path'], '--steps', '100000', '--timeout', '60']
            if source['request']:
                request = source['request']
                native_argv[2:2] = ['-d', 'variables_order=EGPCS']
                context = out / (name + '-request.json')
                context.write_text(json.dumps(request) + '\n')
                entries = [base64.b64decode(k) + b'=' + base64.b64decode(v) for k, v in request['env']]
                packet = b'PHPRQ001' + struct.pack('<qII', int(request['seconds']), request['microseconds'], len(entries)) + b''.join(struct.pack('<I', len(e)) + e for e in entries)
                payload = out / (name + '-input.bin')
                payload.write_bytes(packet)
                native_argv = [sys.executable, '-c', REQUEST_EXEC, *native_argv, str(ROOT / '.tools/request-clock.so'), str(payload)]
                model_argv += ['--request-context', str(context)]
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'source phase cap'
            native_stem, model_stem = out / (name + '-native'), out / (name + '-model')
            row = {'id': name, 'phase': 'source', 'request': source['request'], 'passed': False}
            rows.append(row)
            row['native'] = recorded(native_argv, native_stem, min(45, remaining))
            nout, nerr = native_stem.with_suffix('.stdout').read_bytes(), native_stem.with_suffix('.stderr').read_bytes()
            assert row['native']['exit'] == 0 and not row['native']['timeout'] and nout == expected[name][2] and not nerr, name
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'source phase cap'
            row['model'] = recorded(model_argv, model_stem, min(90, remaining))
            observed = json.loads(model_stem.with_suffix('.stdout').read_bytes())
            row['observation'] = observed
            row['passed'] = (row['model']['exit'] == 0 and not row['model']['timeout'] and not model_stem.with_suffix('.stderr').read_bytes()
                and observed.get('frontend') == 'accepted' and observed.get('checked') == 'program' and observed.get('status') == expected[name][3]
                and observed.get('exit_status') == 0 and observed.get('stdout') == base64.b64encode(nout).decode() and observed.get('stderr') == base64.b64encode(nerr).decode())
            print(name, row['passed'], flush=True)
            assert row['passed'], name
        deadline = time.monotonic() + 930
        for fixture in finite:
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'finite phase cap'
            stem = out / ('finite-' + fixture['id'])
            producer = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *modules, fixture['fixture']], stem, min(300, remaining))
            passed = producer['exit'] == 0 and not producer['timeout'] and stem.with_suffix('.stdout').read_bytes().strip() == b'true' and not stem.with_suffix('.stderr').read_bytes()
            rows.append({'id': fixture['id'], 'phase': 'finite', 'assertions': fixture['assertions'], 'producer': producer, 'passed': passed})
            print(fixture['id'], passed, flush=True)
            assert passed, fixture['id']
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    current = revision()
    stable = watched == {path: describe(path) for path in watched}
    groups = {str(p['pgid']): group(p['pgid']) for row in rows for p in (row.get('native'), row.get('model'), row.get('producer')) if p is not None}
    empty = all(not members for members in groups.values())
    passed = failure is None and stable and head == current and empty and len(rows) == len(sources) + len(finite)
    (out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': head, 'revision_after': current,
        'records': rows, 'failure': failure, 'inputs_stable': stable, 'groups_after': groups}, indent=2) + '\n')
    (out / 'RELEASE.json').write_text(json.dumps({'released': empty, 'passed': passed, 'groups_after': groups}) + '\n')
    print(json.dumps({'passed': passed, 'failure': failure}), flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
