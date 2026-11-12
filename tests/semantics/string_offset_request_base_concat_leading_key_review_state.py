#!/usr/bin/env python3
"""Independent string-CONCAT histories and genuine numeric-leaf entries."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_base_concat_leading_key_cases as cases
import string_offset_request_base_literal_leading_key_review_state as prior

ROOT = Path(__file__).resolve().parents[2]
lines = prior.lines


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    key = '3x' if index == 2 else '1x'
    root = '$origin_node(S.SOURCES, porigin_key) = (NScalarString (BYTES text) metadata)'
    value = '$base64(text) = $ptascii("' + key + '")'
    assert checks.count(root) == checks.count(value) == 1
    checks[checks.index(root):checks.index(root) + 1] = lines(r'''
$origin_node(S.SOURCES, porigin_key) = (NExprBinaryOpConcat expression_1 expression_2 metadata_key)
$compiled_precision(S, (porigin_key)) = (14)
''')
    checks[checks.index(value)] = '$parser_literal_at(NExprBinaryOpConcat expression_1 expression_2 metadata_key, 14) = (PSTRING ($ptascii("' + key + '")))'
    ast = lines(r'''
expression_1 = NExprBinaryOpConcat expression_11 expression_12 metadata_left
expression_2 = NExprBinaryOpConcat expression_21 expression_22 metadata_right
expression_11 = NScalarString (BYTES text_11) metadata_11
expression_12 = NScalarString (BYTES text_12) metadata_12
expression_21 = NScalarString (BYTES text_21) metadata_21
expression_22 = NScalarString (BYTES text_22) metadata_22
$base64(text_11) = $ptascii("1") /\ $base64(text_12) = eps
$base64(text_21) = eps /\ $base64(text_22) = $ptascii("x")
''') if index == 1 else lines(r'''
expression_1 = NScalarString (BYTES text_left) metadata_left
expression_2 = NScalarString (BYTES text_right) metadata_right
$base64(text_right) = $ptascii("x")
''') + ['$base64(text_left) = $ptascii("' + ('3' if index == 2 else '1') + '")']
    insert = checks.index('$compiled_precision(S, (porigin_key)) = (14)') + 1
    checks[insert:insert] = ast
    checks.append('$string_read_literal_bytes(NExprBinaryOpConcat expression_1 expression_2 metadata_key) = ($ptascii("' + key + '"))')
    # The maintained literal-family CONCAT control is promoted at this same
    # genuine source frontier; fresh normal coverage checks its changed premises.
    if index == 0:
        checks += lines(r'''
S_dispatch.EVENTS = eps /\ S_dispatch.STORE = S.STORE
''')
    return checks, derived


def numeric_conditions(program, path, floating):
    checks = prior.concat_conditions(program, path)
    root = '$origin_node(S.SOURCES, porigin_key) = (NExprBinaryOpConcat expression_1 expression_2 metadata)'
    at = checks.index(root) + 1
    checks[at:at] = [
        'expression_1 = NScalarFloat (FLOAT text_float) metadata_float' if floating else
        'expression_1 = NScalarInt (INTEGER 1) metadata_integer',
        '$string_read_literal_bytes(NExprBinaryOpConcat expression_1 expression_2 metadata) = eps']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    report = json.loads(report_path.read_bytes())
    rows = {row['id']: row for row in report['rows']}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert report['profile'] == profile and report['selection'] == list(cases.CASES)
    assert cases.OUTPUTS == prior.cases.OUTPUTS
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = dict(cases.CASES)
    normal = next(iter(sources.values()))
    assert normal.count(b"$got=$text['1'.'x'];") == 1
    sources['integer-concat-key-entry'] = normal.replace(b"$got=$text['1'.'x'];", b"$got=$text[1 . 'x'];")
    sources['float-concat-key-entry'] = normal.replace(b"$got=$text['1'.'x'];", b"$got=$text[1.0 . 'x'];")
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()}) for name, source in sources.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        checked = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for name, row in parsed.items()}
        assert all(row['ok'] for row in checked.values())
    finally:
        adapter.close()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    fixtures, originals, selections = [], [], []
    for index, (name, source_bytes) in enumerate(sources.items()):
        if index < 3:
            row = rows[name]
            native, outcome = row['native'], row['outcome']
            assert row['passed'] and outcome['status'] == 'normal' and outcome['exit_status'] == 0
            assert base64.b64decode(outcome['stdout']) == cases.OUTPUTS[index] and not base64.b64decode(outcome['stderr'])
            assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
            source = Path(native['argv'][-1])
            assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
            assert source.with_name('native.stdout').read_bytes() == cases.OUTPUTS[index] and not source.with_name('native.stderr').read_bytes()
            originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
            checks, derived = conditions(checked[name]['fixture'], source, index)
        else:
            source = out / (name + '.php')
            source.write_bytes(source_bytes)
            originals.append(source)
            checks = numeric_conditions(checked[name]['fixture'], source, index == 4)
            derived = len(checks)
        fixture = out / (name + '.watsup')
        fixture.write_text(prior.HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        selections.append({'id': name, 'conditions': len(checks), 'derived_conditions': derived, 'source_credit': 0})
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), Path(prior.__file__), Path(prior.cases.__file__), Path(prior.shared.__file__), report_path, *originals, *fixtures, *[ROOT / name for name in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in report['inputs'].items() if path.endswith('/.tools/php/bin/php') or path == '.tools/php/bin/php'] == [digest(ROOT / '.tools/php/bin/php')]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for row, fixture in zip(selections, fixtures):
        prefix = out / (row['id'] + '-model')
        process = recorded([str(runner), *map(str, modules), str(fixture)], prefix, 180)
        row['model'] = process
        row['passed'] = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and prefix.with_suffix('.stdout').read_bytes() == b'true\n' and not prefix.with_suffix('.stderr').read_bytes()
        print(row['id'], row['conditions'], row['passed'], flush=True)
        if not row['passed']:
            break
    passed = all(row.get('passed', False) for row in selections)
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'module_entries': len(modules), 'selection': list(sources), 'rows': selections, 'conditions': sum(row['conditions'] for row in selections), 'derived_conditions': sum(row['derived_conditions'] for row in selections), 'inputs': before, 'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING', 'LD_PRELOAD', 'PHP_SPEC_REQUEST_CLOCK')}, 'native_reused_from': str(report_path), 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
