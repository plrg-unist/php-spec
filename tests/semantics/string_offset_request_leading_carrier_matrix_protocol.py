#!/usr/bin/env python3
"""REQUEST leading carriers preserve physical acquisitions and saved reads."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_leading_carrier_matrix_cases as cases
import string_offset_retained_carrier_protocol as shared

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = cases.OUTPUTS
PREFIX, lines, seek = shared.PREFIX, shared.lines, shared.seek


def watbytes(value):
    return '[' + ','.join(map(str, value)) + ']'


def conditions(program, path, index):
    shared_cell, thrown = index == 3, index == 2
    base_bytes = '1x' if shared_cell else 'abc'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S') + lines(r'''
$string_read_plan(S) = (pstringread)
pstringread.PHASE = STRING_LEADING 1 /\ pstringread.READ.LINE = 5
pstringread.READ.PHASE = KEY_NULL
pstringread.READ.INPUT = VARIABLE ($ptascii("key")) 5
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
$lookup(S.ENV, $ptascii("text")) = (n_text)
$lookup(S.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S.ENV, $ptascii("key")) = (n_key)
$lookup(S.ENV, $ptascii("got")) = (n_got)
n_keeper =/= n_text /\ n_keeper =/= n_key /\ n_got =/= n_keeper
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
n_keeper_cell? = (n_keeper)
~(n_keeper <- S.REFCELLS)
S.STORE[n_text] = DEFINED pstringread.READ.BASE
S.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S.STORE[n_got] = DEFINED (PINT 99)
S.STORE[n_key] = DEFINED pstringread.READ.VALUE
$string_read_capture(S, VARIABLE ($ptascii("keeper")) 5) = ((pstringread.READ.BASE, n_keeper_cell?))
$string_read_base_capture(S, VARIABLE ($ptascii("text")) 5) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_key_capture(S, pstringread.READ.INPUT, pstringread.READ.BASE) = ((pstringread.READ.VALUE, pstringread.KEYCELL))
$string_read_provider_ready(S, pstringread) /\ $string_read_source(S, pstringread)
$string_read_request_base_saved(S, pstringread) = (1)
$string_read_ready(S, pstringread)
$string_read_leading(pstringread.READ.BASE, pstringread.READ.VALUE) = eps
$string_read_request_saved(S, pstringread) = eps
$heap_owners($heap_graph(S), HCELL n_keeper) = 1
$task_nodes(STRING_READ_RESULT pstringread) = eps
S.EVENTS = eps
''')
    key_identity = 'INTERNED_STRING' if index == 0 else '(REQUEST_STRING ' + ('0' if shared_cell else '1') + ')'
    registry = ['1x'] if shared_cell else ['abc'] if index == 0 else ['abc', '1x']
    checks += ['pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("' + base_bytes + '"))',
               'pstringread.READ.VALUE = PSTRING_CARRIER ' + key_identity + ' ($ptascii("1x"))',
               'S.STRINGDATA = [' + ', '.join('$ptascii(' + json.dumps(value) + ')' for value in registry) + ']']
    if index == 1:
        checks += lines(r'''
n_text =/= n_key
~(n_text <- S.REFCELLS) /\ ~(n_key <- S.REFCELLS)
$heap_owners($heap_graph(S), HCELL n_text) = 1
$heap_owners($heap_graph(S), HCELL n_key) = 1
$string_read_capture(S, S.RESULT) = ((pstringread.READ.BASE, pstringread.BASECELL))
''')
    else:
        checks += lines(r'''
$lookup(S.ENV, $ptascii("base_alias")) = (n_text)
$lookup(S.ENV, $ptascii("key_alias")) = (n_key)
n_text <- S.REFCELLS /\ n_key <- S.REFCELLS
$string_read_capture(S, S.RESULT) = eps
$string_read_capture(S, pstringread.READ.INPUT) = eps
''') + [r'n_text = n_key /\ pstringread.READ.BASE = pstringread.READ.VALUE' if shared_cell else 'n_text =/= n_key',
        '$heap_owners($heap_graph(S), HCELL n_text) = ' + ('4' if shared_cell else '2'),
        '$heap_owners($heap_graph(S), HCELL n_key) = ' + ('4' if shared_cell else '2')]
    if index < 2:
        reached = len(checks)
        checks += lines(r'''
$string_read_plan(S[.PROPREFS = [{CELL n_text, SOURCES eps}]]) = eps
$string_read_plan(S[.REFCOERCIONS = [{CELL n_key, SITE pstringread.READ.SITE, LINE 5, VALUE $ptascii("1x")} ]]) = eps
$string_read_plan(S[.PARAMETERBACKINGS = [{FUNCTION pstringread.READ.SITE, INDEX 0, CELL n_key, LINE 5, VALUE $ptascii("1x")} ]]) = eps
$string_read_plan(S[.STRINGDATA = eps]) = eps
''')
        return checks, len(checks) - reached
    if thrown:
        checks += lines(r'''
$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)
S.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S, n_saved) = eps
''')
    checks += lines(r'''
PhpStep: S ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 5
perrorcall.MESSAGE = $ptascii("Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34]
$error_call_valid(S_dispatch, perrorcall)
$heap_graph(S_dispatch) = $heap_graph(S)
S_dispatch.STORE = S.STORE /\ S_dispatch.STRINGDATA = S.STRINGDATA
''') + seek('S_dispatch', 1, 'S_entered') + lines(r'''
S_entered.FRAMES = pframe :: pframe_tail*
pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_entered*
perrorcall_entered.RESUME = STRING_READ_RESULT pstringread
pframe.LOCALS = eps
S_entered.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("keeper")) = (n_keeper)
$task_nodes(perrorcall_entered.RESUME) = eps
''') + seek('S_entered', 3 if thrown else 2, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
S_after.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STRINGDATA = S.STRINGDATA
$string_read_capture(S_after, VARIABLE ($ptascii("keeper")) 5) = ((pstringread.READ.BASE, n_keeper_cell?))
$string_read_retainer(S_after, pstringread, BIND ($ptascii("keeper")) n_keeper)
$string_read_retained(S_after, pstringread, S_after.ENV)
$string_read_provider_ready(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$string_read_source(S_after, pstringread)
$retained_outputs(S_after.EVENTS) = [50,124,73,108,108,101,103,97,108,32,115,116,114,105,110,103,32,111,102,102,115,101,116,32,34,49,120,34,124,53,59] /\ $retained_outputs_only(S_after.EVENTS)
$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)
''')
    if thrown:
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("text")) = eps
$lookup(S_after.ENV, $ptascii("base_alias")) = eps
$lookup(S_after.ENV, $ptascii("key")) = eps
$lookup(S_after.ENV, $ptascii("key_alias")) = eps
$heap_owners($heap_graph(S_after), HCELL n_text) = 0
$heap_owners($heap_graph(S_after), HCELL n_key) = 0
~((HCELL n_text) <- $heap_prune($heap_graph(S_after)).NODES)
~((HCELL n_key) <- $heap_prune($heap_graph(S_after)).NODES)
$string_read_key_current(S_after, pstringread) = eps
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_pending) :: ptask_pending*
perrorcall_pending.RESUME = STRING_READ_RESULT pstringread
$throwable_previous_id(S_after, n_saved) = eps
S_popped = S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_pending*]
S_restored = $error_handler_restore(S_popped, perrorcall_pending.CALLBACK)
$error_read_discard(S_restored, STRING_READ_RESULT pstringread) = S_restored[.ERRORFATALTRACE = eps]
PhpStep: S_after ~> S_step
S_step = S_restored[.ERRORFATALTRACE = eps]
''')
    else:
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("text")) = (n_text)
$lookup(S_after.ENV, $ptascii("base_alias")) = (n_text)
$lookup(S_after.ENV, $ptascii("key")) = (n_text)
$lookup(S_after.ENV, $ptascii("key_alias")) = (n_text)
S_after.STORE[n_text] = DEFINED (PINT 2)
$heap_owners($heap_graph(S_after), HCELL n_text) = 4
$string_read_key_current(S_after, pstringread) = (PINT 2)
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*
PhpStep: S_after ~> S_step
S_step = $key_read_done(S_after, PSTRING_CARRIER INTERNED_STRING ($ptascii("x")))
S_step.STORE = S_after.STORE /\ S_step.STRINGDATA = S_after.STRINGDATA
$heap_graph(S_step) = $heap_graph(S_after)
''')
    checks += lines(r'''
S_step.STORE[n_got] = DEFINED (PINT 99)
$drive_steps(S_after, 0) = S_after[.COMPLETION = BUDGET]
S_split = $drive_steps(S_after, 1)
S_split.COMPLETION = BUDGET
S_split.STORE = S_step.STORE /\ S_split.TODO = S_step.TODO /\ S_split.EVENTS = S_step.EVENTS
S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_keeper] = S_after.STORE[n_keeper]
$retained_outputs_only(S_done.EVENTS)
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE
''') + ['$retained_outputs(S_done.EVENTS) = ' + watbytes(OUTPUTS[index]),
         'S_done.STRINGDATA = S.STRINGDATA ++ [$ptascii("99")]' if thrown else 'S_done.STRINGDATA = S.STRINGDATA',
         'S_done.STORE[n_got] = DEFINED (PINT 99)' if thrown else 'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("x")))']
    if thrown:
        checks += lines(r'''
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
''')
    reached = len(checks)
    checks += lines(r'''
S_lost = S_after[.ENV = $unbind(S_after.ENV, $ptascii("keeper"))]
$string_read_request_base_saved(S_lost, pstringread) = (1)
$string_read_source(S_lost, pstringread)
~$string_read_provider_ready(S_lost, pstringread) /\ ~$string_read_ready(S_lost, pstringread)
$string_read_resume(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
$string_read_discard(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_lost.STORE[n_got] = DEFINED (PINT 99)
''')
    if thrown:
        checks += lines(r'''
S_lost_restored = $error_handler_restore(S_lost[.TODO = (THROW_SEARCH n_saved) :: ptask_pending*], perrorcall_pending.CALLBACK)
PhpStep: S_lost ~> S_lost_step
S_lost_step = S_lost_restored[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
$throwable_previous_id(S_lost_step, n_saved) = eps
''')
    else:
        checks += lines(r'''
PhpStep: S_lost ~> S_lost_step
S_lost_step = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_equal = S_after[.STRINGDATA = S_after.STRINGDATA ++ [$ptascii("1x")]][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("1x")))]
$string_carrier_valid(S_equal, PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("1x")))
~$string_read_provider_ready(S_equal, pstringread)
~$string_read_provider_ready(S_after[.REFCELLS = n_keeper :: S_after.REFCELLS], pstringread)
~$string_read_provider_ready(S_after[.PROPREFS = [{CELL n_keeper, SOURCES eps}]], pstringread)
$string_read_request_base_saved(S_after, pstringread[.READ.PHASE = KEY_CV]) = eps
~$string_read_source(S_after, pstringread[.READ.PHASE = KEY_CV])
$string_read_request_base_saved(S_after, pstringread[.KEYCELL = eps]) = eps
$string_read_plan(S[.RESULT = KNOWN pstringread.READ.BASE]) = eps
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
