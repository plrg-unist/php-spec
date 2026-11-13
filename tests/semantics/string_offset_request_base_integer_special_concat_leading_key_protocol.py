#!/usr/bin/env python3
"""Integer and special-CONCAT keys preserve real callback and borrowed-base history."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_base_integer_special_concat_leading_key_cases as cases
import string_offset_request_base_concat_leading_key_protocol as prior

ROOT = Path(__file__).resolve().parents[2]
PREFIX = prior.PREFIX
OUTPUTS = cases.OUTPUTS


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    key = '3x' if index == 2 else '1x'
    authority = '$string_read_literal_bytes(NExprBinaryOpConcat expression_1 expression_2 metadata_key) = ($ptascii("' + key + '"))'
    at = checks.index(authority)
    checks[at:at + 1] = [
        '$string_read_literal_bytes(NExprBinaryOpConcat expression_1 expression_2 metadata_key) = eps',
        '$compiled_precision(S, (porigin_key)) = (14)',
        '$parser_literal_at(NExprBinaryOpConcat expression_1 expression_2 metadata_key, 14) = eps',
        '$compiled_special_concat_bytes(S, porigin_key) = ($ptascii("' + key + '"))']
    checks = [check.replace('PSTRING_CARRIER (REQUEST_STRING 0)', 'PSTRING_CARRIER (REQUEST_STRING n_base_identity)')
              .replace('S.STRINGDATA = [$ptascii("abc")]', 'S.STRINGDATA[n_base_identity] = $ptascii("abc")') for check in checks]
    special_path = '[PCFIELD 0, PCFIELD 1]'
    value = ('PNULL', 'PBOOL false', 'PNULL')[index]
    extra = [
        '$origin_child((porigin_key), ' + special_path + ') = (porigin_special)',
        '$origin_node(S.SOURCES, porigin_special) = (NExprConstFetch name metadata_special)',
        '$compiled_read(S, porigin_special) = (' + value + ')',
        '$parser_literal_at(NExprConstFetch name metadata_special, 14) = eps']
    integer = 3 if index == 2 else 1
    extra += [
        '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_integer)',
        '$origin_node(S.SOURCES, porigin_integer) = (NScalarInt (INTEGER ' + str(integer) + ') metadata_integer)',
        '$compiled_read(S, porigin_integer) = (PINT ' + str(integer) + ')',
        '$compiled_special_concat_bytes(S, porigin_integer) = ($ptascii("' + str(integer) + '"))']
    checks[at + 4:at + 4] = extra
    extra = prior.lines(r'''
S_no_code = S_after[.CODE = eps]
$compiled_special_concat_bytes(S_no_code, porigin_key) = eps
$string_read_request_base_saved(S_no_code, pstringread) = eps
S_no_pools = S_after[.POOLS = eps]
$compiled_special_concat_bytes(S_no_pools, porigin_key) = eps
$string_read_request_base_saved(S_no_pools, pstringread) = eps
S_no_source = S_after[.SOURCES = eps]
$compiled_special_concat_bytes(S_no_source, porigin_key) = eps
$string_read_request_base_saved(S_no_source, pstringread) = eps
$compiled_special_concat_bytes(S_after, PORIGIN 999999 eps) = eps
''') + [
        '$compiled_string_value(S_after, porigin_key, PSTRING ($ptascii("wrong"))) = PSTRING ($ptascii("wrong"))',
        '$compiled_string_value(S_no_pools, porigin_key, PSTRING ($ptascii("' + key + '"))) = PSTRING ($ptascii("' + key + '"))']
    checks += extra
    return checks, derived + len(extra)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sl', action='store_true')
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    source_report = json.loads(report_path.read_bytes())
    rows = {row['id']: row for row in source_report['rows']}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source_report['profile'] == profile and all(rows[name]['passed'] for name in cases.CASES)
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
    originals, counts, fixtures = [], [], []
    for index, (name, source_bytes) in enumerate(cases.CASES.items()):
        row = rows[name]
        native = row['native']
        assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        source = Path(native['argv'][-1])
        native_stdout, native_stderr = Path(row['native_stdout']), Path(row['native_stderr'])
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        assert native_stdout.read_bytes() == OUTPUTS[index] and not native_stderr.read_bytes()
        checks, derived = conditions(checked[name]['fixture'], source, index)
        fixture = out / (name + '.watsup')
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        counts.append({'id': name, 'conditions': len(checks), 'derived_guard_conditions': derived, 'raw_steps': sum(check.startswith('PhpStep:') for check in checks)})
        originals += [source, native_stdout, native_stderr]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), Path(prior.__file__), Path(prior.cases.__file__), Path(prior.shared.__file__), report_path, *originals, *fixtures, *[ROOT / name for name in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in source_report['inputs'].items() if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')] == [digest(ROOT / '.tools/php/bin/php')]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for row, fixture in zip(counts, fixtures):
        stem = out / (row['id'] + '-model')
        process = recorded([str(runner), *(['--sl'] if args.sl else []), *map(str, modules), str(fixture)], stem, 180)
        row['process'] = process
        row['passed'] = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and stem.with_suffix('.stdout').read_bytes() == b'true\n' and not stem.with_suffix('.stderr').read_bytes()
        print(row['id'], row['conditions'], row['passed'], flush=True)
        if not row['passed']:
            break
    passed = all(row.get('passed', False) for row in counts)
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'fixture SL' if args.sl else 'AL', 'selection': list(cases.CASES), 'rows': counts, 'conditions': sum(row['conditions'] for row in counts), 'derived_guard_conditions': sum(row['derived_guard_conditions'] for row in counts), 'inputs': before, 'native_reused_from': str(report_path), 'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING', 'LD_PRELOAD', 'PHP_SPEC_REQUEST_CLOCK')}, 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
