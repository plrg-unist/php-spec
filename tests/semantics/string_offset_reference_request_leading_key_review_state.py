#!/usr/bin/env python3
"""Independent marked REQUEST acquisition, retired-key history and CAST fences."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_reference_request_leading_key_cases as cases
import string_offset_request_leading_key_review_state as prior

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = (b'2|Illegal string offset "1x"|5;b|XYZ|2|2',
           b'2|Illegal string offset "1x"|5;1|1|99|XYZ|0|0')
HELPERS, lines, seek, outputs = prior.HELPERS, prior.lines, prior.seek, prior.outputs


def conditions(program, source, thrown):
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_entry') + lines(r'''
$string_read_plan(S_entry) = (pstringread)
pstringread.PHASE = STRING_LEADING 1 /\ pstringread.READ.LINE = 5
pstringread.READ.PHASE = KEY_NULL
pstringread.READ.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pstringread.READ.VALUE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("1x"))
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
pstringread.READ.INPUT = VARIABLE ($ptascii("key")) 5
$lookup(S_entry.ENV, $ptascii("text")) = (n_text)
$lookup(S_entry.ENV, $ptascii("key")) = (n_key)
$lookup(S_entry.ENV, $ptascii("key_alias")) = (n_key)
$lookup(S_entry.ENV, $ptascii("got")) = (n_got)
pstringread.BASECELL = (n_text) /\ pstringread.KEYCELL = (n_key)
~(n_text <- S_entry.REFCELLS) /\ n_key <- S_entry.REFCELLS
S_entry.STORE[n_text] = DEFINED pstringread.READ.BASE
S_entry.STORE[n_key] = DEFINED pstringread.READ.VALUE
S_entry.STORE[n_got] = DEFINED (PINT 99)
S_entry.STRINGDATA = [$ptascii("1x")] /\ S_entry.EVENTS = eps
$string_carrier_valid(S_entry, pstringread.READ.VALUE)
$string_read_capture(S_entry, pstringread.READ.INPUT) = eps
$string_read_key_capture(S_entry, pstringread.READ.INPUT, pstringread.READ.BASE) = ((pstringread.READ.VALUE, pstringread.KEYCELL))
$string_read_leading(pstringread.READ.BASE, pstringread.READ.VALUE) = eps
$string_read_phase(pstringread.READ.BASE, pstringread.READ.VALUE) = eps
$string_read_request_saved(S_entry, pstringread) = (1)
$string_read_key_current(S_entry, pstringread) = eps
$string_read_source(S_entry, pstringread) /\ $string_read_ready(S_entry, pstringread)
$heap_owners($heap_graph(S_entry), HCELL n_text) = 1
$heap_owners($heap_graph(S_entry), HCELL n_key) = 2
$task_nodes(STRING_READ_RESULT pstringread) = eps
PhpStep: S_entry ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_entry) :: ptask_dispatch*
perrorcall_entry.RESUME = STRING_READ_RESULT pstringread
perrorcall_entry.LEVEL = 2 /\ perrorcall_entry.LINE = 5
perrorcall_entry.MESSAGE = $ptascii("Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34]
$error_call_valid(S_dispatch, perrorcall_entry)
S_dispatch.STORE = S_entry.STORE /\ $heap_graph(S_dispatch) = $heap_graph(S_entry)
''')
    if thrown:
        checks += lines(r'''
$lookup(S_entry.ENV, $ptascii("saved")) = (n_saved_cell)
S_entry.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    checks += seek('S_dispatch', 2 if thrown else 1, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps /\ S_after.GLOBALTABLE = eps
S_after.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STRINGDATA = S_entry.STRINGDATA
$string_read_request_saved(S_after, pstringread) = (1)
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$heap_valid($heap_graph(S_after)) /\ $call_descriptors_valid(S_after)
$task_nodes(STRING_READ_RESULT pstringread) = eps
''')
    chunks = ('2', '|', 'Illegal string offset "1x"', '|', '5', ';')
    checks.append('S_after.EVENTS = ' + outputs(chunks))
    if thrown:
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("key")) = eps
$lookup(S_after.ENV, $ptascii("key_alias")) = eps
S_after.STORE[n_key] = DEFINED pstringread.READ.VALUE
$heap_owners($heap_graph(S_after), HCELL n_key) = 0
~((HCELL n_key) <- $heap_prune($heap_graph(S_after)).NODES)
$string_read_capture(S_after, pstringread.READ.INPUT) = eps
$string_read_key_current(S_after, pstringread) = eps
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
PhpStep: S_after ~> S_raw
S_raw = S_after[.TODO = (THROW_SEARCH n_saved) :: ptask_tail*][.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)][.ERRORFATALTRACE = eps]
$throwable_previous_id(S_raw, n_saved) = eps
''')
    else:
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("key")) = (n_key)
$lookup(S_after.ENV, $ptascii("key_alias")) = (n_key)
S_after.STORE[n_key] = DEFINED (PINT 2)
n_key <- S_after.REFCELLS
$heap_owners($heap_graph(S_after), HCELL n_key) = 2
$string_read_key_current(S_after, pstringread) = (PINT 2)
S_after.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
PhpStep: S_after ~> S_raw
S_raw = $key_read_done(S_after, PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))
''')
    checks += lines(r'''
S_raw.STORE[n_got] = DEFINED (PINT 99)
$drive_steps(S_after, 0) = S_after[.COMPLETION = BUDGET]
S_one = $drive_steps(S_after, 1)
S_one.COMPLETION = BUDGET
S_one.STORE = S_raw.STORE /\ S_one.TODO = S_raw.TODO /\ S_one.EVENTS = S_raw.EVENTS
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.STORE[n_text] = S_after.STORE[n_text]
S_done.CODE = S_entry.CODE /\ S_done.POOLS = S_entry.POOLS
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
''')
    chunks += ('1', '|', '1', '|', '99', '|', 'XYZ', '|', '0', '|', '0') if thrown else ('b', '|', 'XYZ', '|', '2', '|', '2')
    checks.append('S_done.EVENTS = ' + outputs(chunks))
    checks.append('S_done.STRINGDATA = [$ptascii("1x"), $ptascii("99")]' if thrown else 'S_done.STRINGDATA = S_entry.STRINGDATA')
    if thrown:
        checks += lines(r'''
S_done.STORE[n_got] = DEFINED (PINT 99)
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$lookup(S_done.ENV, $ptascii("key")) = eps
$lookup(S_done.ENV, $ptascii("key_alias")) = eps
$throwable_previous_id(S_done, n_saved) = eps
''')
    else:
        checks += lines(r'''
S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))
S_done.STORE[n_key] = DEFINED (PINT 2)
''')
    reached = len(checks)
    if not thrown:
        checks += lines(r'''
$string_read_key_capture(S_entry, REFERENCE n_key, pstringread.READ.BASE) = eps
$string_read_key_capture(S_entry, BORROWED (ROOT n_key), pstringread.READ.BASE) = eps
$string_read_key_capture(S_entry[.PROPREFS = [{CELL n_key, SOURCES eps}]], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_key_capture(S_entry[.REFCOERCIONS = [{CELL n_key, SITE pstringread.READ.SITE, LINE 5, VALUE $ptascii("1x")}]], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_key_capture(S_entry[.PARAMETERBACKINGS = [{FUNCTION pstringread.READ.SITE, INDEX 0, CELL n_key, LINE 5, VALUE $ptascii("1x")}]], pstringread.READ.INPUT, pstringread.READ.BASE) = eps
S_dead = S_entry[.ENV = $unbind($unbind(S_entry.ENV, $ptascii("key")), $ptascii("key_alias"))]
~((HCELL n_key) <- $heap_prune($heap_graph(S_dead)).NODES)
$string_read_key_capture(S_dead, pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_plan(S_dead) = eps
$string_read_plan(S_entry[.STRINGDATA = eps]) = eps
$string_read_plan(S_entry[.STRINGDATA[0] = $ptascii("2x")]) = eps
S_unknown = S_entry[.STORE[n_key] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("1x")))]
$string_read_key_capture(S_unknown, pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_plan(S_unknown) = eps
S_numeric = S_entry[.STRINGDATA = [$ptascii("1")]][.STORE[n_key] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("1")))]
$string_carrier_valid(S_numeric, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("1")))
$string_read_key_capture(S_numeric, pstringread.READ.INPUT, pstringread.READ.BASE) = eps
$string_read_plan(S_numeric) = eps
S_nul = S_entry[.STRINGDATA = [[49,0,120]]][.STORE[n_key] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) ([49,0,120]))]
$string_carrier_valid(S_nul, PSTRING_CARRIER (REQUEST_STRING 0) ([49,0,120]))
$string_read_plan(S_nul) = eps
S_request_base = S_entry[.STRINGDATA = S_entry.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_text] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))]
$string_carrier_valid(S_request_base, PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))
$string_read_plan(S_request_base) = eps
$string_read_request_saved(S_after, pstringread[.KEYCELL = eps]) = eps
$string_read_request_saved(S_after, pstringread[.READ.INPUT = KNOWN pstringread.READ.VALUE]) = eps
$string_read_request_saved(S_after, pstringread[.READ.INPUT = REFERENCE n_key]) = eps
$string_read_request_saved(S_after, pstringread[.READ.PHASE = KEY_CV]) = eps
~$string_read_source(S_after, pstringread[.READ.PHASE = KEY_CV][.KEYCELL = eps])
~$string_read_source(S_after, pstringread[.READ.LINE = 6])
~$string_read_source(S_after[.ORIGIN = eps], pstringread)
~$string_read_source(S_after, pstringread[.PHASE = STRING_LEADING 2])
~$string_read_ready(S_after, pstringread[.PHASE = STRING_LEADING 2])
~$string_read_source(S_after[.STRINGDATA = eps], pstringread)
~$string_read_ready(S_after[.STRINGDATA = eps], pstringread)
pstringread_forged = pstringread[.READ.VALUE = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("1x"))]
~$string_read_source(S_after, pstringread_forged)
S_rebound = S_after[.ENV = (BIND ($ptascii("key")) n_got) :: S_after.ENV]
$string_read_key_current(S_rebound, pstringread) = eps
$string_read_source(S_rebound, pstringread) /\ $string_read_ready(S_rebound, pstringread)
$string_read_resume(S_rebound, pstringread) = $key_read_done(S_rebound, PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))
S_retired = S_after[.ENV = $unbind($unbind(S_after.ENV, $ptascii("key")), $ptascii("key_alias"))]
$heap_owners($heap_graph(S_retired), HCELL n_key) = 0
~((HCELL n_key) <- $heap_prune($heap_graph(S_retired)).NODES)
$string_read_key_current(S_retired, pstringread) = eps
$string_read_source(S_retired, pstringread) /\ $string_read_ready(S_retired, pstringread)
$string_read_resume(S_retired, pstringread) = $key_read_done(S_retired, PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))
S_float = S_entry[.STORE[n_key] = DEFINED (PFLOAT 4609434218613702656)]
$string_read_plan(S_float) = (pstringread_cast)
pstringread_cast.PHASE = STRING_CAST
S_cast = S_after[.STORE[n_key] = DEFINED pstringread.READ.VALUE][.TODO = (STRING_READ_RESULT pstringread_cast) :: ptask_tail*]
$string_read_key_capture(S_cast, pstringread_cast.READ.INPUT, pstringread_cast.READ.BASE) = ((pstringread.READ.VALUE, pstringread.KEYCELL))
$string_read_key_current(S_cast, pstringread_cast) = eps
$string_read_source(S_cast, pstringread_cast) /\ ~$string_read_ready(S_cast, pstringread_cast)
$string_read_resume(S_cast, pstringread_cast).COMPLETION = UNSUPPORTED "string offset changed key locator after callback"
S_three = S_retired[.STRINGDATA = S_retired.STRINGDATA ++ [$ptascii("3x")]]
pstringread_three = pstringread[.READ.VALUE = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("3x"))][.PHASE = STRING_LEADING 3]
$string_read_request_saved(S_three, pstringread_three) = (3)
$string_read_source(S_three, pstringread_three) /\ $string_read_ready(S_three, pstringread_three)
S_bounds_dispatch = $string_read_resume(S_three, pstringread_three)
S_bounds_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_bounds*
perrorcall_bounds.RESUME = STRING_READ_RESULT (pstringread_three[.PHASE = STRING_BOUNDS 3])
perrorcall_bounds.MESSAGE = $ptascii("Uninitialized string offset 3")
$error_call_valid(S_bounds_dispatch, perrorcall_bounds)
$string_read_source(S_bounds_dispatch, pstringread_three[.PHASE = STRING_BOUNDS 3])
~$string_read_source(S_bounds_dispatch, pstringread_three[.PHASE = STRING_BOUNDS 4])
$task_nodes(perrorcall_bounds.RESUME) = eps
S_bounds = S_three[.TODO = (STRING_READ_RESULT (pstringread_three[.PHASE = STRING_BOUNDS 3])) :: ptask_tail*]
PhpStep: S_bounds ~> S_empty
S_empty = $key_read_done(S_bounds, PSTRING_CARRIER INTERNED_STRING eps)
''')
    return checks, len(checks) - reached


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    report = json.loads(report_path.read_bytes())
    rows = {row['id']: row for row in report['rows']}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert report['profile'] == profile and cases.OUTPUTS == OUTPUTS
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
        row, expected = rows[name], OUTPUTS[index]
        native, outcome = row['native'], row['outcome']
        assert row['passed'] and outcome['status'] == 'normal' and outcome['exit_status'] == 0
        assert base64.b64decode(outcome['stdout']) == expected and not base64.b64decode(outcome['stderr'])
        assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        source = Path(native['argv'][-1])
        assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
        assert source.with_name('native.stdout').read_bytes() == expected and not source.with_name('native.stderr').read_bytes()
        checks, derived = conditions(checked[name]['fixture'], source, index == 1)
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        selections.append({'id': name, 'conditions': len(checks), 'derived_conditions': derived,
            'raw_steps': sum(check.startswith('PhpStep:') for check in checks), 'source_credit': 0})
        originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner,
               Path(__file__), Path(cases.__file__), Path(prior.__file__), report_path, *originals, *fixtures,
               *[ROOT / path for path in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
                 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
                 'tests/semantics/profile.json', 'tests/semantics/static_types.py',
                 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in report['inputs'].items() if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')] == [digest(ROOT / '.tools/php/bin/php')]
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
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL',
        'selection': list(cases.CASES), 'rows': selections, 'conditions': sum(row['conditions'] for row in selections),
        'derived_conditions': sum(row['derived_conditions'] for row in selections), 'inputs': before,
        'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING', 'LD_PRELOAD', 'PHP_SPEC_REQUEST_CLOCK')},
        'native_reused_from': str(report_path), 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
