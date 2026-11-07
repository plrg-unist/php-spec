#!/usr/bin/env python3
"""AL checks of strict float diagnostics and silent quiet string access."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import string_offset_strict_float_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import seek
from error_handler_run import ENV, recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
NAME = 'string-offset-strict-float-infinite'
RANGE = 'The float INF is not representable as an int, cast occurred'
PRECISION = 'Implicit conversion from float INF to int loses precision'
HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 10) = true
  -- if S.TODO = (ISSET_RESULT false z) :: ptask_tail*
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ISSET_RESULT true z) :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (COALESCE_QUIET expression z_left z_right) :: ptask_tail*
'''


def conditions(program, path):
    filename = json.dumps(base64.b64encode(bytes(path)).decode())
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + filename + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        'S.TODO = (ISSET_RESULT false 2) :: ptask_after*',
        'S.ORIGIN = (PORIGIN 0 pcpath)', 'S.FILES = [SOURCEFILE 0 n_file*]',
        'n_file* = $base64(' + filename + ')',
        'S.REQUEST = eps', 'S.ERRORHANDLER.CALLBACK = eps', 'S.ERRORFATALTRACE = eps',
        'S.EVENTS = eps', 'S.STRINGDATA = eps',
        '$long_and(S.REPORTING, 8192) = 8192',
        '$lookup(S.ENV, $ptascii("s")) = (n_s)', '$lookup(S.ENV, $ptascii("k")) = (n_k)',
        'S.STORE[n_s] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")))',
        'S.STORE[n_k] = DEFINED (PFLOAT 9218868437227405312)',
        '~(n_s <- S.REFCELLS)', '~(n_k <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_s) = 1',
        '$heap_owners($heap_graph(S), HCELL n_k) = 1',
        '$float_long(9218868437227405312, true) = (0, [RANGEWARNING])',
        '$float_long(9218868437227405312, false) = (0, [RANGEWARNING])',
        'pevent_warning = DIAGNOSTIC "Warning" ($ptascii("' + RANGE + '")) 2',
        'pevent_precision = DIAGNOSTIC "Deprecated" ($ptascii("' + PRECISION + '")) 2',
        '$quiet_string(S, $ptascii("ab"), PFLOAT 9218868437227405312, 2) = S[.RESULT = KNOWN (PSTRING ($ptascii("a")))]',
        'PhpStep: S ~> S_set',
        'S_set = S[.RESULT = KNOWN (PBOOL true)][.TODO = ptask_after*][.BASE = BASE_VALUE (KNOWN PNULL)][.EVENTS = [pevent_warning, pevent_precision]]',
        '$drive(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive(S, 1) = S_set[.COMPLETION = BUDGET]',
        '$call_descriptors_valid(S_set)', '$heap_valid($heap_graph(S_set))',
    ] + seek('S_set', 11, 'S_empty') + [
        'S_empty.TODO = (ISSET_RESULT true 2) :: ptask_empty*',
        'PhpStep: S_empty ~> S_emptied',
        'S_emptied = S_empty[.RESULT = KNOWN (PBOOL false)][.TODO = ptask_empty*][.BASE = BASE_VALUE (KNOWN PNULL)][.EVENTS = S_empty.EVENTS ++ [pevent_warning, pevent_precision]]',
    ] + seek('S_emptied', 12, 'S_coalesce') + [
        'S_coalesce.TODO = (COALESCE_QUIET expression 2 2) :: ptask_coalesce*',
        'S_coalesce.CONSTCONTEXT = eps', 'PhpStep: S_coalesce ~> S_coalesced',
        'S_coalesced = S_coalesce[.RESULT = KNOWN (PSTRING ($ptascii("a")))][.TODO = ptask_coalesce*][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_done = $drive_steps(S_coalesced, 1000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE = S.STORE', 'S_done.STRINGDATA = eps', 'S_done.POOLS = S.POOLS',
        'S_done.CODE = S.CODE',
        'S_done.EVENTS = [pevent_warning, pevent_precision, OUTPUT ($ptascii("1")), OUTPUT ($ptascii("|")), pevent_warning, pevent_precision, OUTPUT ($ptascii("0")), OUTPUT ($ptascii("|")), OUTPUT ($ptascii("a"))]',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$drive_steps(S, 1000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    source_report = json.loads(report_path.read_bytes())
    row = next(row for row in source_report['rows'] if row['id'] == NAME)
    native = row['native']
    assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
    path = Path(native['argv'][-1])
    if not path.is_absolute():
        path = Path(native['cwd']) / path
    assert path.read_bytes() == cases.CASES[NAME]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(path) == row['source_sha256']
    stdout, stderr = path.parent / 'native.stdout', path.parent / 'native.stderr'
    expected = ''.join(level + ': ' + message + ' in ' + str(path) + ' on line 2\n'
        for level, message in [('Warning', RANGE), ('Deprecated', PRECISION)] * 2).encode()
    assert stdout.read_bytes() == b'1|0|a' and stderr.read_bytes() == expected
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source_report['profile'] == profile
    hashes = [v for p, v in source_report['inputs'].items() if p == '.tools/php/bin/php' or p.endswith('/.tools/php/bin/php')]
    assert hashes == [digest(ROOT / '.tools/php/bin/php')]
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(cases.CASES[NAME]).decode()})
        assert parsed['accepted']
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        program = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
    finally:
        adapter.close()
    checks = conditions(program, path)
    fixture = out / 'test.watsup'
    fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json',
        Path(__file__), Path(cases.__file__), Path(shared.__file__),
        ROOT / 'tests/semantics/array_literal_float_array_cv_state_review.py',
        ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/profile.json', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
        ROOT / '_build/default/adapter/main.exe', runner, report_path, path, stdout, stderr, fixture]
    before = {str(p): digest(p) for p in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    process = recorded([str(runner), *map(str, modules), str(fixture)], out / 'model', 180)
    passed = (process['exit'] == 0 and not process['timeout'] and process['interruption'] is None
        and process['group_after'] == [] and (out / 'model.stdout').read_bytes() == b'true\n'
        and not (out / 'model.stderr').read_bytes())
    assert before == {str(p): digest(p) for p in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL',
        'selection': [NAME], 'conditions': len(checks), 'raw_query_steps': 3,
        'inputs': before, 'native_reused_from': str(report_path),
        'source_sha256': row['source_sha256'], 'process': process, 'passed': passed,
        'source_credit': 0}, indent=2) + '\n')
    print(NAME, len(checks), passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
