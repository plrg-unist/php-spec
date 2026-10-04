"""Fixed source/finite handler gates with original producer streams and cleanup."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import signal
import stat
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
ENV = dict(os.environ, LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
ENV.pop('PHP_SPEC_SCRIPT_ENCODING', None)


def describe(path):
    path = Path(path)
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode), path
    return {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': s.st_size,
            'mode': stat.S_IMODE(s.st_mode), 'uid': s.st_uid, 'gid': s.st_gid}


def group(pgid):
    members = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():
            continue
        try:
            fields = (p / 'stat').read_text().rsplit(')', 1)[1].split()
            if int(fields[2]) == pgid:
                members.append({'pid': int(p.name), 'state': fields[0]})
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return members


def recorded(command, stem, cap):
    stem = Path(stem)
    start = time.time()
    p = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True)
    data = {'argv': command, 'cwd': str(ROOT), 'pid': p.pid, 'pgid': p.pid,
            'cap_seconds': cap, 'started': start}
    stem.with_suffix('.process.json').write_text(json.dumps(data) + '\n')
    interruption = None
    timeout = False
    try:
        stdout, stderr = p.communicate(timeout=cap)
    except BaseException as error:
        timeout = isinstance(error, subprocess.TimeoutExpired)
        if not timeout:
            interruption = error
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = p.communicate(timeout=10)
    finally:
        if group(p.pid):
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    for _ in range(50):
        if not group(p.pid):
            break
        time.sleep(.02)
    stem.with_suffix('.stdout').write_bytes(stdout)
    stem.with_suffix('.stderr').write_bytes(stderr)
    data.update({'exit': p.returncode, 'timeout': timeout, 'elapsed': time.time() - start,
                 'interruption': None if interruption is None else type(interruption).__name__,
                 'group_after': group(p.pid)})
    stem.with_suffix('.exit.json').write_text(json.dumps(data) + '\n')
    if interruption is not None:
        raise interruption
    assert not data['group_after'], data
    return data


def inputs():
    paths = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths += [ROOT / p for p in [
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'spec/nodes.json',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/profile.json', 'tests/semantics/static_types.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_cases.py',
        'tests/semantics/error_handler_protocol.py', 'tests/semantics/error_handler_prepare.py',
        'tests/semantics/reporting_cases.py', 'tests/semantics/reporting_protocol.py',
        'tests/semantics/reporting_diagnostics_cases.py', 'tests/semantics/reporting_diagnostics_protocol.py',
        'tests/semantics/reporting_diagnostics_current.php',
        'tests/semantics/error_handler_run.py', 'bin/php-semantics', '.tools/php/bin/php',
        '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec']]
    return {str(p): describe(p) for p in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepared', type=Path)
    parser.add_argument('--source', action='append')
    parser.add_argument('--finite', action='append')
    args = parser.parse_args()
    assert Path.cwd() == ROOT
    preparation = json.loads(args.prepared.read_text())
    assert preparation['passed'] and preparation['inputs'] == inputs()
    from error_handler_cases import CASES
    from error_handler_protocol import CASES as FIXED
    from reporting_cases import CASES as REPORTING_CASES, STDERR as REPORTING_STDERR
    from reporting_diagnostics_cases import CASES as DIAGNOSTICS_CASES, STDERR as DIAGNOSTICS_STDERR
    REPORTING_CASES = REPORTING_CASES + DIAGNOSTICS_CASES
    REPORTING_STDERR = REPORTING_STDERR | DIAGNOSTICS_STDERR
    reporting_ids = {case[0] for case in REPORTING_CASES}
    expected = {name: (source, stdout, status) for name, source, stdout, status in CASES}
    sources = preparation['sources']
    finite = preparation['records']
    assert [r['id'] for r in sources] == [c[0] for c in CASES]
    assert [(r['id'], r['source_id'], r['assertions']) for r in finite] == [
        (c[0], c[1], len(c[3]) + 5) for c in FIXED]
    assert all(r['passed'] for r in finite)
    if args.source is not None:
        assert len(args.source) == len(set(args.source))
        assert set(args.source) <= {r['id'] for r in sources}
        sources = [r for r in sources if r['id'] in args.source]
    if args.finite is not None:
        assert len(args.finite) == len(set(args.finite))
        assert set(args.finite) <= {r['id'] for r in finite}
        finite = [r for r in finite if r['id'] in args.finite]
    watched = dict(preparation['inputs'])
    for row in preparation['sources']:
        assert Path(row['path']).read_bytes() == expected[row['id']][0]
        watched[row['path']] = describe(row['path'])
    for row in preparation['records']:
        for key in ('fixture', 'al'):
            assert describe(row[key]) == row[key + '_descriptor']
            watched[row[key]] = describe(row[key])
    watched[str(args.prepared.resolve())] = describe(args.prepared)
    out = Path(tempfile.mkdtemp(prefix='run-', dir=ROOT / '.tools/error-handlers'))
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, env=ENV).decode().strip()
    status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, env=ENV).decode()
    assert not status, status
    (out / 'TAKE.json').write_text(json.dumps({'revision': head, 'inputs': watched,
        'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'],
                        'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
        'profile': json.loads((ROOT / 'tests/semantics/profile.json').read_text()),
        'selection': {'sources': [r['id'] for r in sources], 'finite': [r['id'] for r in finite]},
        'scope': 'serial source tuples then finite states'}, indent=2) + '\n')
    print(out, flush=True)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [flag for k, v in profile.items() for flag in ('-d', k + '=' + v)]
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    rows = []
    failure = None
    try:
        deadline = time.monotonic() + 2895
        for row in sources:
            stem = out / row['id']
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'source phase cap'
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, row['path']],
                              stem.with_name(stem.name + '-native'), min(45, remaining))
            nout = stem.with_name(stem.name + '-native').with_suffix('.stdout').read_bytes()
            nerr = stem.with_name(stem.name + '-native').with_suffix('.stderr').read_bytes()
            wanted = expected[row['id']]
            native_ok = (not native['timeout'] and nout == wanted[1]
                         and native['exit'] == (255 if wanted[2] == 'php_error' else 0)
                         and (wanted[2] != 'unsupported' or not nerr))
            if row['id'] in reporting_ids:
                native_ok = native_ok and nerr == REPORTING_STDERR.get(row['id'], b'').replace(b'{file}', os.fsencode(row['path']))
            result = {'id': row['id'], 'phase': 'source', 'native': native,
                      'agreement': wanted[2] != 'unsupported', 'passed': False}
            rows.append(result)
            assert native_ok, 'native expected tuple: ' + row['id']
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'source phase cap'
            model = recorded([str(ROOT / 'bin/php-semantics'), row['path'], '--steps', '100000', '--timeout', '60'],
                             stem.with_name(stem.name + '-model'), min(90, remaining))
            observed = json.loads(stem.with_name(stem.name + '-model').with_suffix('.stdout').read_bytes())
            result['model'] = model
            result['observation'] = observed
            result['passed'] = (model['exit'] == (1 if wanted[2] == 'unsupported' else 0) and not model['timeout']
                and not stem.with_name(stem.name + '-model').with_suffix('.stderr').read_bytes()
                and observed.get('frontend') == 'accepted' and observed.get('checked') == 'program'
                and observed.get('status') == wanted[2]
                and (wanted[2] == 'unsupported' or (
                    observed.get('stdout') == base64.b64encode(nout).decode()
                    and observed.get('stderr') == base64.b64encode(nerr).decode()
                    and observed.get('exit_status') == native['exit'])))
            if wanted[2] == 'unsupported':
                result['passed'] = result['passed'] and observed.get('reason') == 'error-handler ingress requires a producer continuation'
            print(row['id'], result['passed'], flush=True)
            assert result['passed'], row['id']
        deadline = time.monotonic() + 2430
        for row in finite:
            stem = out / row['id']
            remaining = deadline - time.monotonic()
            assert remaining > 0, 'finite phase cap'
            result = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                               *modules, row['fixture']], stem, min(300, remaining))
            passed = result['exit'] == 0 and not result['timeout'] and stem.with_suffix('.stdout').read_bytes().strip() == b'true' and not stem.with_suffix('.stderr').read_bytes()
            rows.append({'id': row['id'], 'phase': 'finite', 'assertions': row['assertions'], 'producer': result, 'passed': passed})
            print(row['id'], passed, flush=True)
            assert passed, row['id']
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    after = {path: describe(path) for path in watched}
    head_after = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, env=ENV).decode().strip()
    status_after = subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, env=ENV).decode()
    groups = {str(json.loads(p.read_text())['pgid']): group(json.loads(p.read_text())['pgid'])
              for p in out.glob('*.process.json')}
    groups_empty = all(not members for members in groups.values())
    passed = failure is None and not status_after and head_after == head and groups_empty and len(rows) == len(sources) + len(finite) and watched == after and all(r['passed'] for r in rows)
    (out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': head,
        'records': rows, 'failure': failure, 'inputs_stable': watched == after,
        'inputs_after': after, 'groups_after': groups, 'revision_after': head_after,
        'status_after': status_after}, indent=2) + '\n')
    (out / 'RELEASE.json').write_text(json.dumps({'released': groups_empty, 'passed': passed,
        'revision': head, 'inputs_stable': watched == after, 'groups_after': groups}) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
