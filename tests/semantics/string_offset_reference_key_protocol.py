#!/usr/bin/env python3
"""Same live primitive reference-key cells through cast return and throw."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_reference_key_cases as cases
import string_offset_retained_carrier_protocol as shared

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = (b'2|String offset cast occurred|5;c|2|2', b'2|String offset cast occurred|5;1|1|99|2|2')
PREFIX, lines, seek = shared.PREFIX, shared.lines, shared.seek


def conditions(program, path, thrown):
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S') + lines(r"""
$string_read_plan(S) = (pstringread)
pstringread.PHASE = STRING_CAST /\ pstringread.READ.LINE = 5
pstringread.READ.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pstringread.READ.VALUE = PFLOAT 4609434218613702656
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
pstringread.READ.INPUT = VARIABLE ($ptascii("key")) 5
$lookup(S.ENV, $ptascii("text")) = (n_text)
$lookup(S.ENV, $ptascii("key")) = (n_key)
$lookup(S.ENV, $ptascii("alias")) = (n_key)
$lookup(S.ENV, $ptascii("got")) = (n_got)
n_text =/= n_key /\ n_got =/= n_key
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
n_key <- S.REFCELLS /\ ~$string_read_cell(S, n_key)
S.STORE[n_key] = DEFINED pstringread.READ.VALUE
S.STORE[n_text] = DEFINED pstringread.READ.BASE
S.STORE[n_got] = DEFINED (PINT 99)
$string_read_capture(S, pstringread.READ.INPUT) = eps
$string_read_key_capture(S, pstringread.READ.INPUT, pstringread.READ.BASE) = ((pstringread.READ.VALUE, pstringread.KEYCELL))
$string_read_source(S, pstringread) /\ $string_read_ready(S, pstringread)
$string_read_provider_ready(S, pstringread)
$heap_owners($heap_graph(S), HCELL n_key) = 2
$task_nodes(STRING_READ_RESULT pstringread) = eps
S.EVENTS = eps /\ S.STRINGDATA = eps
PhpStep: S ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 5
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_dispatch, perrorcall)
S_dispatch.STORE = S.STORE /\ $heap_graph(S_dispatch) = $heap_graph(S)
""")
    if thrown:
        checks += lines(r"""
$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)
S.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
""")
    checks += seek('S_dispatch', 1, 'S_entered') + lines(r"""
S_entered.FRAMES = pframe :: pframe_tail*
pframe.LOCALS = eps
S_entered.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("alias")) = (n_key)
pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_entered*
perrorcall_entered.RESUME = STRING_READ_RESULT pstringread
""") + seek('S_entered', 3 if thrown else 2, 'S_after') + lines(r"""
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
$lookup(S_after.ENV, $ptascii("key")) = (n_key)
$lookup(S_after.ENV, $ptascii("alias")) = (n_key)
n_key <- S_after.REFCELLS
S_after.STORE[n_key] = DEFINED (PINT 2)
S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STORE[n_text] = S.STORE[n_text]
S_after.STRINGDATA = eps
$string_read_capture(S_after, pstringread.READ.INPUT) = eps
$string_read_key_current(S_after, pstringread) = (PINT 2)
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$heap_owners($heap_graph(S_after), HCELL n_key) = 2
$retained_outputs(S_after.EVENTS) = $ptascii("2|String offset cast occurred|5;")
$retained_outputs_only(S_after.EVENTS)
$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)
""")
    if thrown:
        checks += lines(r"""
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_pending) :: ptask_pending*
perrorcall_pending.RESUME = STRING_READ_RESULT pstringread
$throwable_previous_id(S_after, n_saved) = eps
S_popped = S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_pending*]
S_restored = $error_handler_restore(S_popped, perrorcall_pending.CALLBACK)
$string_read_key_current(S_restored, pstringread) = (PINT 2)
$error_read_discard(S_restored, STRING_READ_RESULT pstringread) = S_restored[.ERRORFATALTRACE = eps]
PhpStep: S_after ~> S_step
S_step = S_restored[.ERRORFATALTRACE = eps]
S_step.STORE[n_got] = DEFINED (PINT 99)
""")
    else:
        checks += lines(r"""
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*
PhpStep: S_after ~> S_step
S_step = S_after[.TODO = ptask_after*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))][.BASE = BASE_VALUE (KNOWN PNULL)]
$heap_graph(S_step) = $heap_graph(S_after)
""")
    checks += lines(r"""
$drive_steps(S_after, 0) = S_after[.COMPLETION = BUDGET]
S_split = $drive_steps(S_after, 1)
S_split.COMPLETION = BUDGET
S_split.STORE = S_step.STORE /\ S_split.TODO = S_step.TODO /\ S_split.EVENTS = S_step.EVENTS
S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
$lookup(S_done.ENV, $ptascii("key")) = (n_key)
$lookup(S_done.ENV, $ptascii("alias")) = (n_key)
S_done.STORE[n_key] = DEFINED (PINT 2) /\ n_key <- S_done.REFCELLS
S_done.STORE[n_text] = S.STORE[n_text]
S_done.CODE = S.CODE /\ S_done.POOLS = S.POOLS
$retained_outputs_only(S_done.EVENTS)
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
$drive_steps(S_after, 2000) = S_done
""") + [f'$retained_outputs(S_done.EVENTS) = $ptascii("{OUTPUTS[int(thrown)].decode()}")',
        'S_done.STRINGDATA = [$ptascii("99")]' if thrown else 'S_done.STRINGDATA = eps',
        'S_done.STORE[n_got] = DEFINED (PINT 99)' if thrown else
        'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))']
    if thrown:
        checks += lines(r"""
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
""")
    reached = len(checks)
    if not thrown:
        checks += lines(r"""
$string_read_key_quiet(PFLOAT 4609434218613702656)
~$string_read_key_quiet(PFLOAT 9218868437227405312)
$string_read_key_quiet(PNULL) /\ $string_read_key_quiet(PBOOL true) /\ $string_read_key_quiet(PINT 2)
S_range = S_after[.STORE[n_key] = DEFINED (PFLOAT 9218868437227405312)]
$string_read_key_current(S_range, pstringread) = eps
$string_read_resume(S_range, pstringread).COMPLETION = UNSUPPORTED "string offset changed key locator after callback"
$string_read_plan(S[.STORE[n_key] = DEFINED (PFLOAT 9218868437227405312)]) = eps
S_plain = S_after[.STORE[n_got] = DEFINED (PFLOAT 9218868437227405312)]
$string_read_key_capture(S_plain, VARIABLE ($ptascii("got")) 5, pstringread.READ.BASE) = $string_read_capture(S_plain, VARIABLE ($ptascii("got")) 5)
$string_read_key_capture(S_after, REFERENCE n_key, pstringread.READ.BASE) = eps
$string_read_key_capture(S_after, BORROWED (ROOT n_key), pstringread.READ.BASE) = eps
$string_read_plan(S[.REFCELLS = n_text :: S.REFCELLS]) = eps
$string_read_key_capture(S_after, pstringread.READ.INPUT, PSTRING_CARRIER INTERNED_STRING ([97,0,99])) = eps
$string_read_key_capture(S_after, pstringread.READ.INPUT, PSTRING_CARRIER INTERNED_STRING ([256])) = eps
$string_read_key_capture(S_after, pstringread.READ.INPUT, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))) = eps
$string_read_key_capture(S_after[.PROPREFS = [{CELL n_key, SOURCES eps}]], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_key_capture(S_after[.REFCOERCIONS = [{CELL n_key, SITE pstringread.READ.SITE, LINE 5, VALUE $ptascii("2")}]], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_key_capture(S_after[.PARAMETERBACKINGS = [{FUNCTION pstringread.READ.SITE, INDEX 0, CELL n_key, LINE 5, VALUE $ptascii("2")}]], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_key_capture(S_after[.STORE[n_key] = UNDEFINED], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_key_capture(S_after[.STORE[n_key] = DEFINED (PARRAY 0)], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_key_capture(S_after[.STORE[n_key] = DEFINED (PFLOAT 18446744073709551616)], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_key_capture(S_after[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1x")))], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
S_rebound = S_after[.ENV = (BIND ($ptascii("key")) n_got) :: S_after.ENV]
$string_read_key_current(S_rebound, pstringread) = eps
$string_read_key_current(S_after[.ENV = $unbind(S_after.ENV, $ptascii("key"))], pstringread) = eps
S_far = S_after[.STORE[n_key] = DEFINED (PINT 9)]
S_bounds = $string_read_resume(S_far, pstringread)
S_bounds.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_bounds*
perrorcall_bounds.RESUME = STRING_READ_RESULT (pstringread[.PHASE = STRING_BOUNDS 9])
$error_call_valid(S_bounds, perrorcall_bounds)
""")
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
    assert source_report['profile'] == profile
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
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), Path(shared.__file__), Path(shared.cases.__file__), report_path, *originals, *fixtures, *[ROOT / name for name in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in source_report['inputs'].items() if path.endswith('/.tools/php/bin/php')] == [digest(ROOT / '.tools/php/bin/php')]
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
    print('reference-key', sum(row['conditions'] for row in counts), 'derived', sum(row['derived_guard_conditions'] for row in counts), passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
