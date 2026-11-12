#!/usr/bin/env python3
"""Reached same-cell alias retention after selected-name removal."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_reference_alias_keeper_cases as cases
import string_offset_retained_carrier_protocol as shared

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = cases.OUTPUTS
PREFIX, lines, seek = shared.PREFIX, shared.lines, shared.seek


def conditions(program, path, thrown):
    encoded = json.dumps(base64.b64encode(bytes(path)).decode())
    checks = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S') + lines(r'''
$string_read_plan(S) = (pstringread)
pstringread.PHASE = STRING_CAST /\ pstringread.READ.LINE = 5
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("abc"))
pstringread.READ.VALUE = PFLOAT 4609434218613702656
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
pstringread.READ.INPUT = VARIABLE ($ptascii("key")) 5
$lookup(S.ENV, $ptascii("text")) = (n_text)
$lookup(S.ENV, $ptascii("base_alias")) = (n_text)
$lookup(S.ENV, $ptascii("key")) = (n_key)
$lookup(S.ENV, $ptascii("got")) = (n_got)
$lookup(S.ENV, $ptascii("left")) = (n_left)
n_text =/= n_key /\ n_text =/= n_got /\ n_text =/= n_left
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
n_text <- S.REFCELLS /\ ~(n_key <- S.REFCELLS) /\ ~(n_left <- S.REFCELLS)
S.STORE[n_text] = DEFINED pstringread.READ.BASE
S.STORE[n_key] = DEFINED pstringread.READ.VALUE
S.STORE[n_got] = DEFINED (PINT 99)
$string_read_capture(S, S.RESULT) = eps
$string_read_base_capture(S, S.RESULT) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_retainer(S, pstringread, BIND ($ptascii("base_alias")) n_text)
$string_read_source(S, pstringread) /\ $string_read_ready(S, pstringread)
$heap_owners($heap_graph(S), HCELL n_text) = 2
$task_nodes(STRING_READ_RESULT pstringread) = eps
S.STRINGDATA = [$ptascii("abc")] /\ n_identity = 0 /\ S.EVENTS = eps
PhpStep: S ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 5
$error_call_valid(S_dispatch, perrorcall)
S_dispatch.STORE = S.STORE /\ $heap_graph(S_dispatch) = $heap_graph(S)
''')
    if thrown:
        checks += lines(r'''
$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)
S.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    checks += seek('S_dispatch', 1, 'S_entered') + lines(r'''
S_entered.FRAMES = pframe :: pframe_tail*
pframe.LOCALS = eps
S_entered.GLOBALTABLE = (psymboltable_caller)
$lookup(psymboltable_caller.ENV, $ptascii("base_alias")) = (n_text)
pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_entered*
perrorcall_entered.RESUME = STRING_READ_RESULT pstringread
''') + seek('S_entered', 3 if thrown else 2, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
$lookup(S_after.ENV, $ptascii("text")) = eps
$lookup(S_after.ENV, $ptascii("base_alias")) = (n_text)
$lookup(S_after.ENV, $ptascii("key")) = (n_key)
n_text <- S_after.REFCELLS
S_after.STORE[n_text] = DEFINED pstringread.READ.BASE
S_after.STORE[n_key] = DEFINED (PINT 2)
S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STRINGDATA = S.STRINGDATA
$heap_owners($heap_graph(S_after), HCELL n_text) = 1
(HCELL n_text) <- $heap_prune($heap_graph(S_after)).NODES
$string_read_capture(S_after, VARIABLE ($ptascii("base_alias")) 5) = eps
$string_read_base_capture(S_after, VARIABLE ($ptascii("text")) 5) = eps
$string_read_base_capture(S_after, VARIABLE ($ptascii("base_alias")) 5) = ((pstringread.READ.BASE, pstringread.BASECELL))
$string_read_retainer(S_after, pstringread, BIND ($ptascii("base_alias")) n_text)
$string_read_retained(S_after, pstringread, S_after.ENV)
$string_read_provider_ready(S_after, pstringread)
$string_read_key_current(S_after, pstringread) = (PINT 2)
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$retained_outputs(S_after.EVENTS) = $ptascii("2|String offset cast occurred|5;")
$retained_outputs_only(S_after.EVENTS)
$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)
''')
    if thrown:
        checks += lines(r'''
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
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*
PhpStep: S_after ~> S_step
S_step = $key_read_done(S_after, PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))
S_step.STORE[n_got] = DEFINED (PINT 99)
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
$lookup(S_done.ENV, $ptascii("text")) = eps
$lookup(S_done.ENV, $ptascii("base_alias")) = (n_text)
S_done.STORE[n_text] = S_after.STORE[n_text] /\ n_text <- S_done.REFCELLS
S_done.STORE[n_key] = DEFINED (PINT 2)
S_done.CODE = S.CODE /\ S_done.POOLS = S.POOLS
$retained_outputs_only(S_done.EVENTS)
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
''') + [f'$retained_outputs(S_done.EVENTS) = $ptascii("{OUTPUTS[int(thrown)].decode()}")',
        'S_done.STRINGDATA = S.STRINGDATA ++ [$ptascii("99")]' if thrown else 'S_done.STRINGDATA = S.STRINGDATA',
        'S_done.STORE[n_got] = DEFINED (PINT 99)' if thrown else
        'S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))']
    if thrown:
        checks += lines(r'''
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
''')
    reached = len(checks)
    if not thrown:
        checks += lines(r'''
S_lost = S_after[.ENV = $unbind(S_after.ENV, $ptascii("base_alias"))]
S_lost.STORE[n_text] = DEFINED pstringread.READ.BASE /\ S_lost.STRINGDATA = S.STRINGDATA
~((HCELL n_text) <- $heap_prune($heap_graph(S_lost)).NODES)
~$string_read_retainer(S_lost, pstringread, BIND ($ptascii("base_alias")) n_text)
~$string_read_retained(S_lost, pstringread, S_lost.ENV)
~$string_read_provider_ready(S_lost, pstringread)
$string_read_source(S_lost, pstringread)
$string_read_resume(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
$error_read_discard(S_lost, STRING_READ_RESULT pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_shadow = S_after[.ENV = (BIND ($ptascii("base_alias")) n_got) :: S_after.ENV]
~$string_read_retained(S_shadow, pstringread, S_shadow.ENV)
~$string_read_provider_ready(S_shadow, pstringread)
~$string_read_retainer(S_after, pstringread, BIND ($ptascii("text")) n_text)
~$string_read_retainer(S_after, pstringread, BIND ($ptascii("base_alias")) n_left)
S_outside = S_lost[.STORE[n_left] = DEFINED pstringread.READ.BASE][.REFCELLS = n_left :: S_lost.REFCELLS]
n_left_cell? = (n_left)
$string_read_base_capture(S_outside, VARIABLE ($ptascii("left")) 5) = ((pstringread.READ.BASE, n_left_cell?))
~$string_read_retainer(S_outside, pstringread, BIND ($ptascii("left")) n_left)
~$string_read_retained(S_outside, pstringread, S_outside.ENV)
~$string_read_provider_ready(S_outside, pstringread)
S_equal = S_after[.STRINGDATA = S_after.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_text] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii("abc")))]
$string_carrier_valid(S_equal, PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii("abc")))
~$string_read_retained(S_equal, pstringread, S_equal.ENV)
~$string_read_provider_ready(S_equal, pstringread)
~$string_read_retained(S_after[.STRINGDATA = eps], pstringread, S_after.ENV)
~$string_read_provider_ready(S_after[.PROPREFS = [{CELL n_text, SOURCES eps}]], pstringread)
~$string_read_provider_ready(S_after[.REFCOERCIONS = [{CELL n_text, SITE pstringread.READ.SITE, LINE 5, VALUE $ptascii("abc")}]], pstringread)
~$string_read_provider_ready(S_after[.PARAMETERBACKINGS = [{FUNCTION pstringread.READ.SITE, INDEX 0, CELL n_text, LINE 5, VALUE $ptascii("abc")}]], pstringread)
pstringread_nul = pstringread[.READ.BASE = PSTRING_CARRIER (REQUEST_STRING n_identity) ([97,0,99])]
S_nul = S_after[.STRINGDATA[n_identity] = [97,0,99]][.STORE[n_text] = DEFINED pstringread_nul.READ.BASE]
$string_carrier_valid(S_nul, pstringread_nul.READ.BASE)
~$string_read_retained(S_nul, pstringread_nul, S_nul.ENV)
~$string_read_provider_ready(S_nul, pstringread_nul)
~$string_read_source(S_after[.ORIGIN = eps], pstringread)
~$string_read_source(S_after, pstringread[.READ.LINE = 6])
$task_nodes(STRING_READ_RESULT pstringread) = eps
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
