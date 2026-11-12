#!/usr/bin/env python3
"""String-leaf CONCAT keys retain REQUEST-base history without a key cell."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_base_concat_leading_key_cases as cases
import string_offset_retained_carrier_protocol as shared

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = cases.OUTPUTS
PREFIX, lines, seek = shared.PREFIX, shared.lines, shared.seek


def watbytes(value):
    return '[' + ','.join(map(str, value)) + ']'


def conditions(program, path, index):
    thrown, bounds = index == 1, index == 2
    offset, key = (3, '3x') if bounds else (1, '1x')
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S') + lines(r'''
$string_read_plan(S) = (pstringread)
pstringread.READ.PHASE = KEY_NULL
pstringread.READ.INPUT = KNOWN pstringread.READ.VALUE
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
pstringread.READ.LINE = 5 /\ pstringread.KEYCELL = eps
$lookup(S.ENV, $ptascii("text")) = (n_text)
$lookup(S.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S.ENV, $ptascii("got")) = (n_got)
$lookup(S.ENV, $ptascii("key")) = eps
n_text =/= n_keeper
pstringread.BASECELL = (n_text)
S.STORE[n_text] = DEFINED pstringread.READ.BASE
S.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S.STORE[n_got] = DEFINED (PINT 99)
S.STRINGDATA = [$ptascii("abc")] /\ S.EVENTS = eps
$origin_child((pstringread.READ.SITE), [PCFIELD 1]) = (porigin_key)
$origin_node(S.SOURCES, porigin_key) = (NExprBinaryOpConcat expression_1 expression_2 metadata_key)
$key_read_input_source(S, pstringread.READ)
$key_value_selected(pstringread.READ.INPUT, pstringread.READ.VALUE)
$string_read_base_capture(S, S.RESULT) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_key_capture(S, pstringread.READ.INPUT, pstringread.READ.BASE) = ((pstringread.READ.VALUE, eps))
$string_read_source(S, pstringread) /\ $string_read_ready(S, pstringread)
$string_read_provider_ready(S, pstringread)
$heap_owners($heap_graph(S), HCELL n_keeper) = 1
~(n_keeper <- S.REFCELLS)
$task_nodes(STRING_READ_RESULT pstringread) = eps
''') + ['pstringread.PHASE = STRING_LEADING ' + str(offset),
        'pstringread.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("' + key + '"))',
        '$string_read_literal_bytes(NExprBinaryOpConcat expression_1 expression_2 metadata_key) = ($ptascii("' + key + '"))',
        '$compiled_read(S, porigin_key) = (PSTRING ($ptascii("' + key + '")))',
        '$compiled_string_value(S, porigin_key, PSTRING ($ptascii("' + key + '"))) = pstringread.READ.VALUE',
        '$string_read_request_base_saved(S, pstringread) = (' + str(offset) + ')']
    if thrown:
        checks += lines(r'''
$lookup(S.ENV, $ptascii("base_alias")) = (n_text)
n_text <- S.REFCELLS
$heap_owners($heap_graph(S), HCELL n_text) = 2
$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)
S.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    else:
        checks += lines(r'''
~(n_text <- S.REFCELLS)
$heap_owners($heap_graph(S), HCELL n_text) = 1
''')
    checks += lines(r'''
PhpStep: S ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 5
$error_call_valid(S_dispatch, perrorcall)
S_dispatch.STORE = S.STORE /\ S_dispatch.STRINGDATA = S.STRINGDATA
$heap_graph(S_dispatch) = $heap_graph(S)
''') + ['perrorcall.MESSAGE = ' + watbytes(('Illegal string offset "' + key + '"').encode())]
    checks += seek('S_dispatch', 3 if thrown else 2, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
S_after.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STRINGDATA = S.STRINGDATA
$string_read_retainer(S_after, pstringread, BIND ($ptascii("keeper")) n_keeper)
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$string_read_provider_ready(S_after, pstringread)
$string_read_key_current(S_after, pstringread) = eps
$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)
''') + ['$retained_outputs(S_after.EVENTS) = ' + watbytes(('2|Illegal string offset "' + key + '"|5;').encode())]
    if thrown:
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("text")) = eps
$lookup(S_after.ENV, $ptascii("base_alias")) = eps
$heap_owners($heap_graph(S_after), HCELL n_text) = 0
~((HCELL n_text) <- $heap_prune($heap_graph(S_after)).NODES)
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_pending) :: ptask_pending*
perrorcall_pending.RESUME = STRING_READ_RESULT pstringread
S_restored = $error_handler_restore(S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_pending*], perrorcall_pending.CALLBACK)
PhpStep: S_after ~> S_step
S_step = S_restored[.ERRORFATALTRACE = eps]
$throwable_previous_id(S_step, n_saved) = eps
S_finish = S_after
''')
    else:
        checks += lines(r'''
S_after.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*
PhpStep: S_after ~> S_step
''')
        if bounds:
            checks += lines(r'''
S_step.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_bounds*
pstringread_bounds = pstringread[.PHASE = STRING_BOUNDS 3]
perrorcall_bounds.RESUME = STRING_READ_RESULT pstringread_bounds
perrorcall_bounds.MESSAGE = $ptascii("Uninitialized string offset 3")
$error_call_valid(S_step, perrorcall_bounds)
''') + seek('S_step', 2, 'S_bounds_after') + lines(r'''
S_bounds_after.TODO = (STRING_READ_RESULT pstringread_bounds) :: ptask_bounds_after*
S_bounds_after.CURRENT = eps /\ S_bounds_after.FRAMES = eps
$lookup(S_bounds_after.ENV, $ptascii("text")) = eps
$lookup(S_bounds_after.ENV, $ptascii("keeper")) = eps
$heap_owners($heap_graph(S_bounds_after), HCELL n_text) = 0
$heap_owners($heap_graph(S_bounds_after), HCELL n_keeper) = 0
$string_read_source(S_bounds_after, pstringread_bounds)
$string_read_ready(S_bounds_after, pstringread_bounds)
~$string_read_provider_ready(S_bounds_after, pstringread_bounds)
S_bounds_after.STORE[n_got] = DEFINED (PINT 99)
PhpStep: S_bounds_after ~> S_empty
S_empty = $key_read_done(S_bounds_after, PSTRING_CARRIER INTERNED_STRING eps)
S_finish = S_bounds_after
S_step = $string_read_resume(S_after, pstringread)
''')
        else:
            checks += lines(r'''
S_step = $key_read_done(S_after, PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))
S_step.STORE = S_after.STORE /\ $heap_graph(S_step) = $heap_graph(S_after)
S_finish = S_after
''')
    checks += lines(r'''
S_finish.STORE[n_got] = DEFINED (PINT 99)
$drive_steps(S_finish, 0) = S_finish[.COMPLETION = BUDGET]
S_one = $drive_steps(S_finish, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.CODE = S.CODE /\ S_done.POOLS = S.POOLS
$retained_outputs_only(S_done.EVENTS)
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
''') + ['$retained_outputs(S_done.EVENTS) = ' + watbytes(OUTPUTS[index]),
        'S_done.STORE[n_got] = DEFINED (PINT 99)' if thrown else
        'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING eps)' if bounds else
        'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))']
    if thrown:
        checks += lines(r'''
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
''')
    reached = len(checks)
    wrong = '1x' if bounds else '3x'
    checks += ['pstringread_wrong = pstringread[.READ.INPUT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("' + wrong + '")))][.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("' + wrong + '"))]',
        r'~$string_read_source(S_after, pstringread_wrong)',
        r'$string_read_request_base_saved(S_after, pstringread_wrong) = eps']
    checks += lines(r'''
$string_read_request_base_saved(S_after, pstringread[.KEYCELL = (n_got)]) = eps
$string_read_request_base_saved(S_after, pstringread[.BASECELL = eps]) = eps
$string_read_request_base_saved(S_after, pstringread[.READ.PHASE = KEY_CV]) = eps
S_lost = S_after[.ENV = $unbind(S_after.ENV, $ptascii("keeper"))]
$string_read_source(S_lost, pstringread)
~$string_read_ready(S_lost, pstringread)
$string_read_resume(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
$string_read_discard(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
''')
    if thrown:
        checks += lines(r'''
S_lost_restored = $error_handler_restore(S_lost[.TODO = (THROW_SEARCH n_saved) :: ptask_pending*], perrorcall_pending.CALLBACK)
PhpStep: S_lost ~> S_lost_step
S_lost_step = S_lost_restored[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
''')
    else:
        checks += lines(r'''
PhpStep: S_lost ~> S_lost_step
S_lost_step = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
''')
    if bounds:
        checks += lines(r'''
S_longer = S_after[.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZlong")))]
$string_read_source(S_longer, pstringread) /\ $string_read_ready(S_longer, pstringread)
$string_read_resume(S_longer, pstringread).TODO = S_step.TODO
$string_read_discard(S_bounds_after, pstringread_bounds) = S_bounds_after
''')
    return checks, len(checks) - reached


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
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
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        assert source.with_name('native.stdout').read_bytes() == OUTPUTS[index] and not source.with_name('native.stderr').read_bytes()
        checks, derived = conditions(checked[name]['fixture'], source, index)
        fixture = out / (name + '.watsup')
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        counts.append({'id': name, 'conditions': len(checks), 'derived_guard_conditions': derived, 'raw_steps': sum(check.startswith('PhpStep:') for check in checks)})
        originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), Path(shared.__file__), report_path, *originals, *fixtures, *[ROOT / name for name in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in source_report['inputs'].items() if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')] == [digest(ROOT / '.tools/php/bin/php')]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for row, fixture in zip(counts, fixtures):
        stem = out / (row['id'] + '-model')
        process = recorded([str(runner), *map(str, modules), str(fixture)], stem, 180)
        row['process'] = process
        row['passed'] = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and stem.with_suffix('.stdout').read_bytes() == b'true\n' and not stem.with_suffix('.stderr').read_bytes()
        print(row['id'], row['conditions'], row['passed'], flush=True)
        if not row['passed']:
            break
    passed = all(row.get('passed', False) for row in counts)
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'selection': list(cases.CASES), 'rows': counts, 'conditions': sum(row['conditions'] for row in counts), 'derived_guard_conditions': sum(row['derived_guard_conditions'] for row in counts), 'inputs': before, 'native_reused_from': str(report_path), 'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING', 'LD_PRELOAD', 'PHP_SPEC_REQUEST_CLOCK')}, 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
