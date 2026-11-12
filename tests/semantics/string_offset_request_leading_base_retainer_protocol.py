#!/usr/bin/env python3
"""REQUEST leading bases keep current owner proofs separate from saved history."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_leading_base_retainer_cases as cases
import string_offset_retained_carrier_protocol as shared

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = cases.OUTPUTS
PREFIX, lines, seek = shared.PREFIX, shared.lines, shared.seek


def watbytes(value):
    return '[' + ','.join(map(str, value)) + ']'


def conditions(program, path, thrown):
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S') + lines(r'''
$string_read_plan(S) = (pstringread)
pstringread.PHASE = STRING_LEADING 1 /\ pstringread.READ.LINE = 5
pstringread.READ.PHASE = KEY_NULL
pstringread.READ.INPUT = VARIABLE ($ptascii("key")) 5
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("abc"))
pstringread.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
$lookup(S.ENV, $ptascii("text")) = (n_text)
$lookup(S.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S.ENV, $ptascii("key")) = (n_key)
$lookup(S.ENV, $ptascii("got")) = (n_got)
n_keeper =/= n_text /\ n_key =/= n_text /\ n_got =/= n_keeper
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
n_keeper_cell? = (n_keeper)
~(n_text <- S.REFCELLS) /\ ~(n_keeper <- S.REFCELLS) /\ ~(n_key <- S.REFCELLS)
S.STORE[n_text] = DEFINED pstringread.READ.BASE
S.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S.STORE[n_got] = DEFINED (PINT 99)
S.STORE[n_key] = DEFINED pstringread.READ.VALUE
S.STRINGDATA[n_identity] = $ptascii("abc")
$string_read_capture(S, VARIABLE ($ptascii("keeper")) 5) = ((pstringread.READ.BASE, n_keeper_cell?))
$string_read_provider_ready(S, pstringread) /\ $string_read_source(S, pstringread)
$string_read_request_base_saved(S, pstringread) = (1)
$string_read_ready(S, pstringread)
$string_read_leading(pstringread.READ.BASE, pstringread.READ.VALUE) = eps
$string_read_request_saved(S, pstringread) = eps
$heap_owners($heap_graph(S), HCELL n_text) = 1 /\ $heap_owners($heap_graph(S), HCELL n_keeper) = 1
S.EVENTS = eps
PhpStep: S ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 5
perrorcall.MESSAGE = [73,108,108,101,103,97,108,32,115,116,114,105,110,103,32,111,102,102,115,101,116,32,34,49,120,34]
$error_call_valid(S_dispatch, perrorcall)
$task_nodes(STRING_READ_RESULT pstringread) = eps
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
''')
    if thrown:
        checks += lines(r'''
$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)
S.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    checks += seek('S_entered', 3 if thrown else 2, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps
S_after.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_after.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STRINGDATA = S.STRINGDATA
$string_read_capture(S_after, VARIABLE ($ptascii("text")) 5) = ((PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")), pstringread.BASECELL))
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
$lookup(S_after.ENV, $ptascii("key")) = eps
S_after.STORE[n_key] = DEFINED pstringread.READ.VALUE
$heap_owners($heap_graph(S_after), HCELL n_key) = 0
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
S_step.STORE[n_got] = DEFINED (PINT 99)
''')
    else:
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("key")) = (n_key)
S_after.STORE[n_key] = DEFINED (PINT 2)
$string_read_key_current(S_after, pstringread) = (PINT 2)
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*
S_after.ERRORHANDLER = S.ERRORHANDLER
PhpStep: S_after ~> S_step
S_step.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))
S_step.BASE = BASE_VALUE (KNOWN PNULL)
S_step.STORE = S_after.STORE /\ S_step.STRINGDATA = S_after.STRINGDATA
$heap_graph(S_step) = $heap_graph(S_after)
''')
    checks += lines(r'''
$drive_steps(S_after, 0) = S_after[.COMPLETION = BUDGET]
S_split = $drive_steps(S_after, 1)
S_split.COMPLETION = BUDGET
S_split.STORE = S_step.STORE /\ S_split.TODO = S_step.TODO /\ S_split.EVENTS = S_step.EVENTS
S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_text] = S_after.STORE[n_text] /\ S_done.STORE[n_keeper] = S_after.STORE[n_keeper]
$retained_outputs_only(S_done.EVENTS)
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
''')
    checks += ['$retained_outputs(S_done.EVENTS) = ' + watbytes(OUTPUTS[int(thrown)]),
               r'S_done.STRINGDATA = S.STRINGDATA ++ [$ptascii("99")] /\ S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE' if thrown else
               r'S_done.STRINGDATA = S.STRINGDATA /\ S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE',
               'S_done.STORE[n_got] = DEFINED (PINT 99)' if thrown else
               'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))']
    if thrown:
        checks += lines(r'''
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
''')

    reached = len(checks)
    checks += lines(r'''
S_lost = S_after[.ENV = $unbind(S_after.ENV, $ptascii("keeper"))]
S_lost.STRINGDATA[n_identity] = $ptascii("abc")
$string_read_request_base_saved(S_lost, pstringread) = (1)
$string_read_source(S_lost, pstringread)
~$string_read_cell(S_lost, n_keeper)
~$string_read_retained(S_lost, pstringread, S_lost.ENV)
~$string_read_provider_ready(S_lost, pstringread)
~$string_read_ready(S_lost, pstringread)
$string_read_resume(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
$string_read_discard(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_lost.STORE[n_got] = DEFINED (PINT 99)
''')
    if thrown:
        checks += lines(r'''
S_lost_popped = S_lost[.TODO = (THROW_SEARCH n_saved) :: ptask_pending*]
S_lost_restored = $error_handler_restore(S_lost_popped, perrorcall_pending.CALLBACK)
PhpStep: S_lost ~> S_lost_step
S_lost_step = S_lost_restored[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_lost_step.STORE[n_got] = DEFINED (PINT 99)
$throwable_previous_id(S_lost_step, n_saved) = eps
S_lost_step.EVENTS = S_lost.EVENTS
''')
    else:
        checks += lines(r'''
PhpStep: S_lost ~> S_lost_step
S_lost_step = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
~$string_read_source(S_after[.ORIGIN = eps], pstringread)
~$string_read_source(S_after, pstringread[.READ.LINE = 6])
S_shadow = S_after[.ENV = (BIND ($ptascii("keeper")) n_got) :: S_after.ENV]
~$string_read_retained(S_shadow, pstringread, S_shadow.ENV)
~$string_read_provider_ready(S_shadow, pstringread)
S_equal = S_after[.STRINGDATA = S_after.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii("abc")))]
$string_carrier_valid(S_equal, PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii("abc")))
~$string_read_retained(S_equal, pstringread, S_equal.ENV)
~$string_read_provider_ready(S_equal, pstringread)
~$string_read_provider_ready(S_after[.REFCELLS = n_keeper :: S_after.REFCELLS], pstringread)
~$string_read_provider_ready(S_after[.PROPREFS = [{CELL n_keeper, SOURCES eps}]], pstringread)
~$string_read_provider_ready(S_after[.REFCOERCIONS = [{CELL n_keeper, SITE pstringread.READ.SITE, LINE 5, VALUE $ptascii("abc")}]], pstringread)
~$string_read_provider_ready(S_after[.PARAMETERBACKINGS = [{FUNCTION pstringread.READ.SITE, INDEX 0, CELL n_keeper, LINE 5, VALUE $ptascii("abc")}]], pstringread)
~$string_read_provider_ready(S_after[.STORE[n_keeper] = UNDEFINED], pstringread)
$string_read_plan(S[.REFCELLS = n_text :: S.REFCELLS]) = eps
$string_read_plan(S[.REFCELLS = n_key :: S.REFCELLS]) = eps
$string_read_plan(S[.STRINGDATA = eps]) = eps
~$string_read_source(S_after[.STRINGDATA = eps], pstringread)
~$string_read_source(S_after, pstringread[.PHASE = STRING_LEADING 2])
~$string_read_source(S_after, pstringread[.KEYCELL = eps])
~$string_read_source(S_after, pstringread[.BASECELL = eps])
pstringread_nul = pstringread[.READ.BASE = PSTRING_CARRIER (REQUEST_STRING n_identity) ([97,0,99])]
S_nul = S_after[.STRINGDATA[n_identity] = [97,0,99]][.STORE[n_keeper] = DEFINED pstringread_nul.READ.BASE]
$string_carrier_valid(S_nul, pstringread_nul.READ.BASE)
~$string_read_source(S_nul, pstringread_nul)
~$string_read_provider_ready(S_nul, pstringread_nul)
S_alias = S_lost[.STORE[n_text] = DEFINED pstringread.READ.BASE][.ENV = (BIND ($ptascii("alias")) n_text) :: $unbind(S_lost.ENV, $ptascii("text"))][.REFCELLS = n_text :: S_lost.REFCELLS]
$lookup(S_alias.ENV, $ptascii("text")) = eps
$lookup(S_alias.ENV, $ptascii("keeper")) = eps
$lookup(S_alias.ENV, $ptascii("alias")) = (n_text)
$heap_owners($heap_graph(S_alias), HCELL n_text) = 1
$string_read_capture(S_alias, VARIABLE ($ptascii("alias")) 5) = eps
$string_read_base_capture(S_alias, VARIABLE ($ptascii("alias")) 5) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_retainer(S_alias, pstringread, BIND ($ptascii("alias")) n_text)
$string_read_source(S_alias, pstringread) /\ $string_read_ready(S_alias, pstringread)
$string_read_resume(S_alias, pstringread) = $key_read_done(S_alias, PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))
$heap_valid($heap_graph(S_alias))
pstringread_lost_far = pstringread[.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("3x"))][.PHASE = STRING_LEADING 3]
S_lost_far = S_lost[.TODO = (STRING_READ_RESULT pstringread_lost_far) :: ptask_after*]
$string_read_source(S_lost_far, pstringread_lost_far) /\ ~$string_read_ready(S_lost_far, pstringread_lost_far)
$string_read_resume(S_lost_far, pstringread_lost_far).COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"
$string_read_discard(S_lost_far, pstringread_lost_far).COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"
S_far = S[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("3x")))]
$string_read_plan(S_far) = (pstringread_far)
pstringread_far.PHASE = STRING_LEADING 3
PhpStep: S_far ~> S_far_dispatch
''') + seek('S_far_dispatch', 2, 'S_far_after') + lines(r'''
S_far_after.TODO = (STRING_READ_RESULT pstringread_far) :: ptask_far*
$string_read_ready(S_far_after, pstringread_far)
PhpStep: S_far_after ~> S_bounds
S_bounds.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_bounds*
perrorcall_bounds.RESUME = STRING_READ_RESULT (pstringread_far[.PHASE = STRING_BOUNDS 3])
S_bounds_lost = S_bounds[.ENV = $unbind(S_bounds.ENV, $ptascii("keeper"))]
$string_read_source(S_bounds_lost, pstringread_far[.PHASE = STRING_BOUNDS 3])
$string_read_ready(S_bounds_lost, pstringread_far[.PHASE = STRING_BOUNDS 3])
~$string_read_provider_ready(S_bounds_lost, pstringread_far[.PHASE = STRING_BOUNDS 3])
$string_read_resume(S_bounds_lost, pstringread_far[.PHASE = STRING_BOUNDS 3]) = $key_read_done(S_bounds_lost, PSTRING_CARRIER INTERNED_STRING eps)
$string_read_discard(S_bounds_lost, pstringread_far[.PHASE = STRING_BOUNDS 3]) = S_bounds_lost
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
        checks, derived = conditions(checked[name]['fixture'], source, index == 1)
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
