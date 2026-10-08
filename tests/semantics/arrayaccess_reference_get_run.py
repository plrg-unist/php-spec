from pathlib import Path
import base64
import json
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from error_handler_run import ENV, describe, group, recorded


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
            for key, command in [('head', ['rev-parse', 'HEAD']),
                                 ('tree', ['rev-parse', 'HEAD^{tree}']),
                                 ('status', ['status', '--porcelain'])]}


prepared_path = Path(sys.argv[1]).resolve()
prepared = json.loads(prepared_path.read_text())
assert prepared['passed']
before = revision()
assert before == prepared['revision'] and not before['status']
cases = {case['id']: case for case in prepared['records']}
selected = sys.argv[2:] or list(cases)
assert len(selected) == len(set(selected)) and all(name in cases for name in selected)
watched = dict(prepared['inputs'])
assert watched == {name: describe(name) for name in watched}
for path in (prepared_path, Path(__file__), ROOT / '.tools/spectec/bin/p4spectec', ROOT / 'bin/php-semantics',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
             ROOT / 'tests/semantics/numeric_runner.ml'):
    watched[str(path)] = describe(path)
store = ROOT / '.tools/arrayaccess-reference-get'
store.mkdir(exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='run-', dir=store))
print(out, flush=True)
modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
rows, failure = [], None
try:
    for stage in ('algo', 'struct'):
        producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), stage, *modules], out / stage, 120)
        emitted = (out / (stage + '.stdout')).read_bytes()
        markers = {name: ('def $' + name).encode() in emitted for name in
            ('php_run', 'access_reference_signature', 'access_reference_get',
             'access_reference_result_pending', 'access_reference_fetch', 'access_reference_cell',
             'access_reference_compound', 'access_reference_binary', 'reference_callback_used')}
        passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
                  and not (out / (stage + '.stderr')).read_bytes() and all(markers.values()))
        rows.append({'id': stage, 'producer': producer, 'markers': markers,
                     'emitted_bytes': len(emitted), 'passed': passed})
        print(stage, passed, len(emitted), flush=True)
        assert passed, stage
    loader = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
        '--sl', *modules, prepared['loader']], out / 'initial', 120)
    passed = (loader['exit'] == 0 and not loader['timeout'] and not loader['group_after']
              and (out / 'initial.stdout').read_bytes().strip() == b'true'
              and not (out / 'initial.stderr').read_bytes())
    rows.append({'id': 'strict_SL_initial', 'producer': loader, 'premises': 6, 'passed': passed})
    print('strict_SL_initial', passed, loader['elapsed'], flush=True)
    assert passed, 'strict SL initial'
    started = time.monotonic()
    for name in selected:
        assert time.monotonic() - started < 390, 'source phase480 cap before next outer90 producer'
        case = cases[name]
        native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, case['source']], out / (name + '-native'), 45)
        stdout = (out / (name + '-native.stdout')).read_bytes()
        stderr = (out / (name + '-native.stderr')).read_bytes()
        passed = (native['exit'] == 0 and not native['timeout'] and not native['group_after']
                  and stdout == case['expected_stdout'].encode() and not stderr)
        rows.append({'id': name + ':native', 'producer': native, 'passed': passed})
        print(name, 'native', passed, flush=True)
        assert passed, name + ' native'
        assert time.monotonic() - started < 390, 'source phase480 cap before outer90 model'
        model = recorded([str(ROOT / 'bin/php-semantics'), case['source'],
                          '--steps', '100000', '--timeout', '60'], out / (name + '-model'), 90)
        raw = (out / (name + '-model.stdout')).read_bytes()
        observed = json.loads(raw) if raw else None
        passed = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
                  and not (out / (name + '-model.stderr')).read_bytes() and observed
                  and observed.get('frontend') == 'accepted' and observed.get('checked') == 'program'
                  and observed.get('status') == 'normal' and observed.get('exit_status') == 0
                  and observed.get('stdout') == base64.b64encode(stdout).decode()
                  and observed.get('stderr') == base64.b64encode(stderr).decode())
        rows.append({'id': name + ':model', 'producer': model, 'passed': bool(passed), 'observation': observed})
        print(name, 'model', bool(passed), observed and observed.get('status'), model['elapsed'], flush=True)
        assert passed, name + ' exact model'
except BaseException as error:
    failure = {'type': type(error).__name__, 'message': str(error)}
after = revision()
stable = before == after and watched == {name: describe(name) for name in watched}
groups = {str(row['producer']['pgid']): group(row['producer']['pgid']) for row in rows}
passed = (failure is None and len(rows) == 3 + 2 * len(selected) and all(row['passed'] for row in rows)
          and stable and all(not members for members in groups.values()))
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before,
    'revision_after': after, 'modules': len(modules), 'preparation': str(prepared_path),
    'selection': selected, 'inputs': watched, 'inputs_stable': stable, 'profile': profile,
    'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'], 'cwd': str(ROOT),
        'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
    'records': rows, 'failure': failure, 'groups_after': groups, 'jobs': 1,
    'caps': {'compiler': 120, 'strict_SL_initial': 120, 'native': 45, 'CLI': 60, 'outer': 90, 'steps': 100000, 'source_phase': 480},
    'scope': 'Current319 compiler and selected original source comparisons; no historical renewal'}, indent=2) + '\n')
raise SystemExit(0 if passed else 1)
