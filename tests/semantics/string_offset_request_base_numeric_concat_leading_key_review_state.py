#!/usr/bin/env python3
"""Independent numeric-CONCAT source, precision and borrowed-owner histories."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_base_numeric_concat_leading_key_cases as cases
import string_offset_request_base_literal_leading_key_review_state as prior

ROOT = Path(__file__).resolve().parents[2]
lines = prior.lines
ROUTES = (0, 0, 1, 2)


def conditions(program, path, index):
    route = ROUTES[index]
    checks, derived = prior.conditions(program, path, route)
    key, offset = ('3x', 3) if route == 2 else ('1x', 1)
    root = '$origin_node(S.SOURCES, porigin_key) = (NScalarString (BYTES text) metadata)'
    value = '$base64(text) = $ptascii("' + key + '")'
    assert checks.count(root) == checks.count(value) == 1
    checks[checks.index(root):checks.index(root) + 1] = lines(r'''
$origin_node(S.SOURCES, porigin_key) = (NExprBinaryOpConcat expression_1 expression_2 metadata_key)
$compiled_precision(S, (porigin_key)) = (14)
''')
    checks[checks.index(value)] = '$parser_literal_at(NExprBinaryOpConcat expression_1 expression_2 metadata_key, 14) = (PSTRING ($ptascii("' + key + '")))'
    if index < 2:
        ast = lines(r'''
expression_2 = NScalarString (BYTES text_suffix) metadata_suffix
$base64(text_suffix) = $ptascii("x")
S.PRECISIONINI = $ptascii("14") /\ $precision_value(S) = 14
''') + (['expression_1 = NScalarInt (INTEGER 1) metadata_numeric'] if index == 0 else lines(r'''
expression_1 = NScalarFloat (FLOAT text_numeric) metadata_numeric
$parser_literal_at(expression_1, 14) = (PFLOAT 4607182418800017408)
'''))
    else:
        ast = lines(r'''
expression_1 = NExprBinaryOpConcat expression_11 expression_12 metadata_left
expression_2 = NExprBinaryOpConcat expression_21 expression_22 metadata_right
expression_11 = NScalarFloat (FLOAT text_numeric) metadata_numeric
expression_12 = NScalarString (BYTES text_empty_left) metadata_empty_left
expression_21 = NScalarString (BYTES text_empty_right) metadata_empty_right
expression_22 = NScalarString (BYTES text_suffix) metadata_suffix
$base64(text_empty_left) = eps /\ $base64(text_empty_right) = eps
$base64(text_suffix) = $ptascii("x")
S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17
$parser_literal_at(NExprBinaryOpConcat expression_1 expression_2 metadata_key, 17) =/= (PSTRING ($ptascii("1x")))
$parser_literal_at(NExprBinaryOpConcat expression_1 expression_2 metadata_key, 17) =/= (PSTRING ($ptascii("3x")))
''')
    at = checks.index('$compiled_precision(S, (porigin_key)) = (14)') + 1
    checks[at:at] = ast + lines(r'''
$string_read_literal_bytes(NExprBinaryOpConcat expression_1 expression_2 metadata_key) = eps
''')
    # These are explicit derived receipt queries. They neither run another
    # original nor turn live INI bytes into compiler conversion authority.
    extra = lines(r'''
S_live_precision = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]
$precision_value(S_live_precision) = 9
$compiled_precision(S_live_precision, (porigin_key)) = (14)
S_no_precision = S_after[.POOLS = eps][.DECLARATIONS = eps]
$compiled_precision(S_no_precision, (porigin_key)) = eps
$string_read_request_base_saved(S_no_precision, pstringread) = eps
$parser_literal_at(NExprBinaryOpPlus expression_1 expression_2 metadata_key, 14) = eps
''') + [f'$string_read_request_base_saved(S_live_precision, pstringread) = ({offset})']
    checks += extra
    return checks, derived + len(extra)


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
    assert cases.OUTPUTS == tuple(prior.cases.OUTPUTS[index] for index in ROUTES)
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()}) for name, source in cases.CASES.items()}
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
    for index, (name, source_bytes) in enumerate(cases.CASES.items()):
        row = rows[name]
        native, outcome = row['native'], row['outcome']
        assert row['passed'] and outcome['status'] == 'normal' and outcome['exit_status'] == 0
        assert base64.b64decode(outcome['stdout']) == cases.OUTPUTS[index] and not base64.b64decode(outcome['stderr'])
        assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        source = Path(native['argv'][-1])
        stdout = Path(row['native_stdout'])
        stderr = Path(row['native_stderr'])
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        assert stdout.read_bytes() == cases.OUTPUTS[index] and not stderr.read_bytes()
        originals += [source, stdout, stderr]
        checks, derived = conditions(checked[name]['fixture'], source, index)
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
        print(row['id'], row['conditions'], row['passed'], process['elapsed'], flush=True)
        if not row['passed']:
            break
    passed = all(row.get('passed', False) for row in selections)
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'module_entries': len(modules), 'selection': list(cases.CASES), 'rows': selections, 'conditions': sum(row['conditions'] for row in selections), 'derived_conditions': sum(row['derived_conditions'] for row in selections), 'inputs': before, 'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING', 'LD_PRELOAD', 'PHP_SPEC_REQUEST_CLOCK')}, 'native_reused_from': str(report_path), 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
