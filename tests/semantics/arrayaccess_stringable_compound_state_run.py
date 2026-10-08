from pathlib import Path
import base64
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from error_handler_run import ENV, describe, group, recorded


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
            for key, command in [('head', ['rev-parse', 'HEAD']),
                                 ('tree', ['rev-parse', 'HEAD^{tree}']),
                                 ('status', ['status', '--porcelain'])]}


manifest_path = Path(sys.argv[1]).resolve()
manifest = json.loads(manifest_path.read_text())
prepared_path = Path(manifest['preparation'])
prepared = json.loads(prepared_path.read_text())
before = revision()
assert prepared['passed'] and before == prepared['revision'] == manifest['revision']
assert not before['status']
cases = {row['id']: row for row in manifest['records']}
controls = {row['id']: row for row in manifest['compiler_controls']}
selected = sys.argv[2:] or ['compiler-gates', *controls, *cases]
assert len(selected) == len(set(selected)) and all(name in {'compiler-gates', *controls, *cases} for name in selected)
states = [name for name in selected if name in cases]
watched = dict(prepared['inputs'])
assert watched == {path: describe(path) for path in watched}
modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
paths = [manifest_path, prepared_path, Path(manifest['renderer']), Path(__file__), runner,
         ROOT / 'tests/semantics/numeric_runner.ml', ROOT / '.tools/spectec/bin/p4spectec',
         ROOT / 'tests/semantics/error_handler_protocol.py']
paths.extend(Path(cases[name]['fixture']) for name in states)
paths.extend(Path(row['source']) for row in manifest['compiler_controls'])
watched.update({str(path): describe(path) for path in paths})
store = ROOT / '.tools/arrayaccess-stringable-compound'
store.mkdir(exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='reached-run-', dir=store))
print(out, flush=True)
rows, failure = [], None
try:
    if 'compiler-gates' in selected:
        for stage in ('algo', 'struct'):
            stem = out / stage
            producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), stage, *modules], stem, 120)
            emitted = stem.with_suffix('.stdout').read_bytes()
            passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
                      and not stem.with_suffix('.stderr').read_bytes()
                      and b'def $php_run' in emitted and b'def $access_string_source' in emitted)
            rows.append({'id': stage, 'producer': producer, 'emitted_bytes': len(emitted), 'passed': passed})
            print(stage, passed, len(emitted), flush=True)
            assert passed, stage
        stem = out / 'strict-SL-initial'
        producer = recorded([str(runner), '--sl', *modules, prepared['loader']], stem, 120)
        passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
                  and stem.with_suffix('.stdout').read_bytes().strip() == b'true'
                  and not stem.with_suffix('.stderr').read_bytes())
        rows.append({'id': 'strict-SL-initial', 'producer': producer, 'assertions': 6, 'passed': passed})
        print('strict-SL-initial', passed, producer['elapsed'], flush=True)
        assert passed, 'strict SL initialization'
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    for case in (controls[name] for name in selected if name in controls):
        name = case['id']
        native_stem = out / (name + '-native')
        native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, case['source']], native_stem, 45)
        stdout = native_stem.with_suffix('.stdout').read_bytes()
        stderr = native_stem.with_suffix('.stderr').read_bytes()
        expected = ('Fatal error: ' + case['message'] + ' in ' + case['source']
                    + ' on line 1\nStack trace:\n#0 {main}\n').encode()
        passed = (native['exit'] == 255 and not native['timeout'] and not native['group_after']
                  and not stdout and stderr == expected)
        rows.append({'id': name + ':native', 'producer': native, 'passed': passed})
        print(name, 'native', passed, flush=True)
        assert passed, name + ' native compile error'
        model_stem = out / (name + '-model')
        model = recorded([str(ROOT / 'bin/php-semantics'), case['source'],
                          '--steps', '100000', '--timeout', '60'], model_stem, 90)
        raw = model_stem.with_suffix('.stdout').read_bytes()
        observed = json.loads(raw) if raw else None
        passed = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
                  and not model_stem.with_suffix('.stderr').read_bytes() and observed
                  and observed.get('frontend') == 'accepted' and observed.get('checked') == 'program'
                  and observed.get('status') == 'static_rejection' and observed.get('exit_status') == 255
                  and observed.get('stdout') == base64.b64encode(stdout).decode()
                  and observed.get('stderr') == base64.b64encode(stderr).decode())
        rows.append({'id': name + ':model', 'producer': model, 'passed': bool(passed),
                     'observation': observed})
        print(name, 'model', bool(passed), flush=True)
        assert passed, name + ' exact model compile error'
    for name in states:
        case = cases[name]
        compiler_stem = out / (name + '-compiler')
        compiler = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo',
                             *modules, case['fixture']], compiler_stem, 120)
        emitted = compiler_stem.with_suffix('.stdout').read_bytes()
        passed = (compiler['exit'] == 0 and not compiler['timeout'] and not compiler['group_after']
                  and not compiler_stem.with_suffix('.stderr').read_bytes()
                  and b'def $main' in emitted and b'def $access_string_source' in emitted)
        rows.append({'id': name + ':compiler', 'producer': compiler,
                     'emitted_bytes': len(emitted), 'passed': passed})
        print(name, 'compiler', passed, len(emitted), flush=True)
        assert passed, name + ' compiler'
        stem = out / name
        producer = recorded([str(runner), '--sl', *modules, case['fixture']], stem, 300)
        passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
                  and stem.with_suffix('.stdout').read_bytes().strip() == b'true'
                  and not stem.with_suffix('.stderr').read_bytes())
        rows.append({'id': name, 'source_id': case['source_id'], 'assertions': case['assertions'],
                     'fixture': case['fixture'], 'producer': producer, 'passed': passed})
        print(name, 'strict_SL', passed, producer['elapsed'], flush=True)
        assert passed, name + ' strict SL'
except BaseException as error:
    failure = {'type': type(error).__name__, 'message': str(error)}
after = revision()
stable = before == after and watched == {path: describe(path) for path in watched}
groups = {str(row['producer']['pgid']): group(row['producer']['pgid']) for row in rows}
expected_rows = (3 if 'compiler-gates' in selected else 0) + 2 * sum(name in controls or name in cases for name in selected)
passed = (failure is None and len(rows) == expected_rows
          and all(row['passed'] for row in rows)
          and stable and all(not members for members in groups.values()))
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before,
    'revision_after': after, 'manifest': str(manifest_path), 'preparation': str(prepared_path),
    'modules': len(modules), 'selection': selected, 'inputs': watched, 'inputs_stable': stable,
    'records': rows, 'failure': failure, 'groups_after': groups, 'jobs': 1, 'mode': 'strict SL',
    'cache': False, 'deterministic': True,
    'caps': {'compiler': 120, 'strict_SL': 300, 'native': 45, 'CLI': 60, 'outer': 90, 'steps': 100000},
    'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'], 'cwd': str(ROOT),
        'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
    'scope': 'Selected current334 original-source-reached Stringable conversion, raw RV and owner-order guards; no319/326/329 renewal'},
    indent=2) + '\n')
raise SystemExit(0 if passed else 1)
