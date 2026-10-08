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
selected = sys.argv[2:] or list(cases)
assert len(selected) == len(set(selected)) and all(name in {'compiler-gates', *cases} for name in selected)
states = [name for name in selected if name in cases]
watched = dict(prepared['inputs'])
assert watched == {path: describe(path) for path in watched}
modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
paths = [manifest_path, prepared_path, Path(manifest['renderer']), Path(__file__), runner,
         ROOT / 'tests/semantics/numeric_runner.ml', ROOT / '.tools/spectec/bin/p4spectec',
         ROOT / 'tests/semantics/error_handler_protocol.py']
paths.extend(Path(cases[name]['fixture']) for name in states)
watched.update({str(path): describe(path) for path in paths})
store = ROOT / '.tools/arrayaccess-generator-get'
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
                      and b'def $php_run' in emitted and b'def $access_generator_context' in emitted)
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
    for name in states:
        case = cases[name]
        compiler_stem = out / (name + '-compiler')
        compiler = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo',
                             *modules, case['fixture']], compiler_stem, 120)
        emitted = compiler_stem.with_suffix('.stdout').read_bytes()
        passed = (compiler['exit'] == 0 and not compiler['timeout'] and not compiler['group_after']
                  and not compiler_stem.with_suffix('.stderr').read_bytes()
                  and b'def $main' in emitted and b'def $access_generator_context' in emitted)
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
expected_rows = (3 if 'compiler-gates' in selected else 0) + 2 * len(states)
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
    'scope': 'Selected344 source-reached Generator Get creation, retained context and owner guards; no earlier source/state renewal'},
    indent=2) + '\n')
raise SystemExit(0 if passed else 1)
