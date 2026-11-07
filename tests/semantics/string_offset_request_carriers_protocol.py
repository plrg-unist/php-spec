#!/usr/bin/env python3
"""AL fixtures for source-reached concatenated quiet string-offset carriers."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import string_offset_request_carriers_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import seek
from error_handler_run import ENV, recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = true
  -- if S.TODO = (ISSET_RESULT false z) :: ptask_tail*
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ISSET_RESULT true z) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (COALESCE_QUIET expression z_left z_right) :: ptask_tail*
'''


def conditions(name, program, path, stdout):
    string_key = name.endswith('-key')
    base = 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("a0"))'
    key = 'PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("-1"))' if string_key else 'PINT 0'
    byte = '0' if string_key else 'a'
    empty = 'true' if string_key else 'false'
    registry = '[($ptascii("a0")), ($ptascii("-1"))]' if string_key else '[($ptascii("a0"))]'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        'S.TODO = (ISSET_RESULT false 2) :: ptask_after*',
        'S.BASE = BASE_DIM pbase poperand 2', 'S.REQUEST = eps',
        'S.STRINGDATA = ' + registry,
        '$lookup(S.ENV, $ptascii("s")) = (n_s)', 'S.STORE[n_s] = DEFINED (' + base + ')',
        '~(n_s <- S.REFCELLS)', '$heap_owners($heap_graph(S), HCELL n_s) = 1',
        '$string_carrier_valid(S, ' + base + ')', '$value_nodes(' + base + ') = eps',
        'S_base = $quiet_base(S, pbase, 2)', 'S_base.RESULT = KNOWN (' + base + ')',
        'S_key = $quiet_operand(S_base, poperand)', 'S_key.RESULT = KNOWN (' + key + ')',
        '$quiet_dimension_value(S, ' + base + ', ' + key + ', 2) = S[.RESULT = KNOWN (PSTRING ($ptascii("' + byte + '")))]',
        '$isset_dimension_value(S, ' + base + ', ' + key + ', false, 2) = S[.RESULT = KNOWN (PBOOL true)]',
        '$isset_dimension_value(S, ' + base + ', ' + key + ', true, 2) = S[.RESULT = KNOWN (PBOOL ' + empty + ')]',
        'PhpStep: S ~> S_step',
        'S_step = S[.RESULT = KNOWN (PBOOL true)][.TODO = ptask_after*][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$drive_steps(S, 1) = S_step[.COMPLETION = BUDGET]',
    ]
    if string_key:
        checks += [
            '$lookup(S.ENV, $ptascii("key")) = (n_key)',
            'S.STORE[n_key] = DEFINED (' + key + ')', '~(n_key <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_key) = 1', '$string_carrier_valid(S, ' + key + ')',
            '$quiet_string(S, $ptascii("a0"), ' + key + ', 2) = $quiet_string(S, $ptascii("a0"), PSTRING ($ptascii("-1")), 2)',
            '$isset_string(S, $ptascii("a0"), ' + key + ', true, 2) = $isset_string(S, $ptascii("a0"), PSTRING ($ptascii("-1")), true, 2)',
        ]
    checks += seek('S_step', 11, 'S_empty') + [
        'S_empty.TODO = (ISSET_RESULT true 2) :: ptask_empty*', 'PhpStep: S_empty ~> S_emptied',
        'S_emptied = S_empty[.RESULT = KNOWN (PBOOL ' + empty + ')][.TODO = ptask_empty*][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ] + seek('S_emptied', 12, 'S_coalesce') + [
        'S_coalesce.TODO = (COALESCE_QUIET expression 2 2) :: ptask_coalesce*',
        'S_coalesce.CONSTCONTEXT = eps', 'PhpStep: S_coalesce ~> S_coalesced',
        'S_coalesced = S_coalesce[.RESULT = KNOWN (PSTRING ($ptascii("' + byte + '")))][.TODO = ptask_coalesce*][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_done = $drive_steps(S_coalesced, 1000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_s] = DEFINED (' + base + ')', 'S_done.STRINGDATA = S.STRINGDATA',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 1000) = S_done',
    ]
    if not string_key:
        checks += [
            'S_missing = S[.STRINGDATA = eps]',
            'S_invalid = S[.STRINGDATA = S.STRINGDATA ++ [([256])]]',
            'S_nul = S[.STRINGDATA = S.STRINGDATA ++ [([97,0])]]',
            'S_nul_key = S[.STRINGDATA = S.STRINGDATA ++ [([48,0])]]',
        ]
        bad_bases = [
            ('S_missing', base, False),
            ('S', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("a0"))', False),
            ('S', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("z0"))', False),
            ('S_invalid', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([256])', False),
            ('S_nul', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([97,0])', True),
        ]
        for state, value, valid in bad_bases:
            checks += [
                ('' if valid else '~') + '$string_carrier_valid(' + state + ', ' + value + ')',
                '$quiet_dimension_value(' + state + ', ' + value + ', PINT 0, 2) = ' + state + '[.RESULT = KNOWN PNULL]',
                '$isset_dimension_value(' + state + ', ' + value + ', PINT 0, false, 2) = ' + state + '[.RESULT = KNOWN (PBOOL false)]',
            ]
        for state, key_value in [
            ('S_missing', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("0"))'),
            ('S', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))'),
            ('S', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("0"))'),
            ('S_invalid', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([256])'),
            ('S_nul_key', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([48,0])'),
        ]:
            checks += ['$isset_string(' + state + ', $ptascii("a0"), ' + key_value + ', false, 2) = ' + state + '[.RESULT = KNOWN (PBOOL false)]']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, action='append', required=True)
    parser.add_argument('--case', choices=tuple(cases.CASES))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    reports = [path.resolve() for path in args.source_report]
    source_rows = {row['id']: (row, report) for report in reports for row in json.loads(report.read_bytes())['rows']}
    names = (args.case,) if args.case else tuple(cases.CASES)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(cases.CASES[name]).decode()}) for name in names}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        programs = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True})['fixture'] for name, row in parsed.items()}
    finally:
        adapter.close()
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    rows, originals = [], []
    for name in names:
        source_row, source_report = source_rows[name]
        native = source_row['native']
        assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        path = Path(native['argv'][-1])
        assert path.is_absolute() and path.read_bytes() == cases.CASES[name] and digest(path) == source_row['source_sha256']
        stdout, stderr = path.parent / 'native.stdout', path.parent / 'native.stderr'
        assert stderr.read_bytes() == b''
        checks = conditions(name, programs[name], path, stdout.read_bytes())
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks))
        rows.append({'id': name, 'conditions': len(checks), 'raw_steps': sum(check.startswith('PhpStep:') for check in checks),
            'native_reused_from': str(source_report), 'source_sha256': digest(path), 'native': native})
        originals += [path, stdout, stderr, fixture]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__),
        Path(cases.__file__), Path(shared.__file__), ROOT / 'tests/semantics/array_literal_float_array_cv_state_review.py',
        ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/profile.json', ROOT / '_build/default/adapter/main.exe',
        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', *reports, *originals]
    before = {str(p): digest(p) for p in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for row in rows:
        stem = out / (row['id'] + '-model')
        result = recorded([str(runner), *map(str, modules), str(out / (row['id'] + '.watsup'))], stem, 180)
        row['model'] = result
        row['passed'] = (result['exit'] == 0 and not result['timeout'] and result['interruption'] is None
            and result['group_after'] == [] and stem.with_suffix('.stdout').read_bytes() == b'true\n'
            and not stem.with_suffix('.stderr').read_bytes())
        print(row['id'], row['passed'], flush=True)
        if not row['passed']:
            break
    assert before == {str(p): digest(p) for p in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'selection': names, 'inputs': before,
        'rows': rows, 'profile': profile, 'scope': 'source-reached AL fixtures; preserved ordinary native originals',
        'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')}}, indent=2) + '\n')
    return all(row.get('passed', False) for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
