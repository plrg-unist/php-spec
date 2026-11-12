#!/usr/bin/env python3
"""Independent literal-key histories and a genuine folded-CONCAT refusal."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_request_base_literal_leading_key_cases as cases
import string_offset_retained_carrier_protocol as shared

ROOT = Path(__file__).resolve().parents[2]
lines, seek = shared.lines, shared.seek
HELPERS = shared.PREFIX + r'''
dec $literal_key_front(pstate) : bool
def $literal_key_front(S) = true
  -- if S.TODO = (KEY_READ_DIM poperand 5 KEY_R) :: ptask_tail*
  -- if S.RESULT = VARIABLE ($ptascii("text")) 5
def $literal_key_front(S) = false -- otherwise
dec $literal_key_seek(pstate, nat) : pstate
def $literal_key_seek(S, n) = S -- if $literal_key_front(S)
def $literal_key_seek(S, n) = S
  -- if ~$literal_key_front(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $literal_key_seek(S, 0) = S
  -- if ~$literal_key_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $literal_key_seek(S, n) = $literal_key_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$literal_key_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def conditions(program, path, index):
    thrown, bounds = index == 1, index == 2
    offset, key = (3, '3x') if bounds else (1, '1x')
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S') + lines(r'''
$string_read_plan(S) = (pstringread)
pstringread.READ.INPUT = KNOWN pstringread.READ.VALUE
pstringread.READ.PHASE = KEY_NULL /\ pstringread.KEYCELL = eps
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("text")) 5)
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
$lookup(S.ENV, $ptascii("text")) = (n_text)
$lookup(S.ENV, $ptascii("keeper")) = (n_keeper)
$lookup(S.ENV, $ptascii("got")) = (n_got)
$lookup(S.ENV, $ptascii("key")) = eps
pstringread.BASECELL = (n_text) /\ n_text =/= n_keeper
S.STORE[n_keeper] = DEFINED pstringread.READ.BASE
$heap_owners($heap_graph(S), HCELL n_keeper) = 1
~(n_keeper <- S.REFCELLS)
$origin_child((pstringread.READ.SITE), [PCFIELD 1]) = (porigin_key)
$origin_node(S.SOURCES, porigin_key) = (NScalarString (BYTES text) metadata)
$key_read_input_source(S, pstringread.READ) /\ $key_read_owners_source(S, pstringread.READ)
$string_read_source(S, pstringread) /\ $string_read_ready(S, pstringread)
$task_nodes(STRING_READ_RESULT pstringread) = eps
S.EVENTS = eps
''') + [f'pstringread.PHASE = STRING_LEADING {offset}',
        f'pstringread.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("{key}"))',
        f'$base64(text) = $ptascii("{key}")',
        f'$compiled_read(S, porigin_key) = (PSTRING ($ptascii("{key}")))',
        f'$string_read_request_base_saved(S, pstringread) = ({offset})']
    if thrown:
        checks += lines(r'''
$lookup(S.ENV, $ptascii("base_alias")) = (n_text)
n_text <- S.REFCELLS /\ $heap_owners($heap_graph(S), HCELL n_text) = 2
$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)
S.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)
''')
    else:
        checks += lines(r'''
~(n_text <- S.REFCELLS) /\ $heap_owners($heap_graph(S), HCELL n_text) = 1
''')
    checks += lines(r'''
PhpStep: S ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
$error_call_valid(S_dispatch, perrorcall)
S_dispatch.STORE = S.STORE /\ S_dispatch.STRINGDATA = S.STRINGDATA
$heap_graph(S_dispatch) = $heap_graph(S)
''') + seek('S_dispatch', 3 if thrown else 2, 'S_after') + lines(r'''
S_after.CURRENT = eps /\ S_after.FRAMES = eps
S_after.STORE[n_keeper] = DEFINED pstringread.READ.BASE
S_after.STORE[n_got] = DEFINED (PINT 99)
S_after.STRINGDATA = S.STRINGDATA
$string_read_source(S_after, pstringread) /\ $string_read_ready(S_after, pstringread)
$string_read_retainer(S_after, pstringread, BIND ($ptascii("keeper")) n_keeper)
$string_read_provider_ready(S_after, pstringread)
$string_read_key_current(S_after, pstringread) = eps
''')
    if thrown:
        checks += lines(r'''
$lookup(S_after.ENV, $ptascii("text")) = eps
$lookup(S_after.ENV, $ptascii("base_alias")) = eps
$heap_owners($heap_graph(S_after), HCELL n_text) = 0
S_after.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_pending) :: ptask_pending*
perrorcall_pending.RESUME = STRING_READ_RESULT pstringread
PhpStep: S_after ~> S_step
$throwable_previous_id(S_step, n_saved) = eps
S_finish = S_after
''')
    else:
        checks += lines(r'''
S_after.STORE[n_text] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
PhpStep: S_after ~> S_step
''')
        if bounds:
            checks += lines(r'''
S_step.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_bounds*
pstringread_bounds = pstringread[.PHASE = STRING_BOUNDS 3]
perrorcall_bounds.RESUME = STRING_READ_RESULT pstringread_bounds
perrorcall_bounds.MESSAGE = $ptascii("Uninitialized string offset 3")
$error_call_valid(S_step, perrorcall_bounds)
''') + seek('S_step', 2, 'S_bounds') + lines(r'''
$lookup(S_bounds.ENV, $ptascii("text")) = eps /\ $lookup(S_bounds.ENV, $ptascii("keeper")) = eps
$heap_owners($heap_graph(S_bounds), HCELL n_text) = 0
$heap_owners($heap_graph(S_bounds), HCELL n_keeper) = 0
$string_read_source(S_bounds, pstringread_bounds) /\ $string_read_ready(S_bounds, pstringread_bounds)
~$string_read_provider_ready(S_bounds, pstringread_bounds)
PhpStep: S_bounds ~> S_empty
S_empty = $key_read_done(S_bounds, PSTRING_CARRIER INTERNED_STRING eps)
S_finish = S_bounds
''')
        else:
            checks += lines(r'''
S_step = $key_read_done(S_after, PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))
$heap_graph(S_step) = $heap_graph(S_after)
S_finish = S_after
''')
    checks += lines(r'''
$drive_steps(S_finish, 0) = S_finish[.COMPLETION = BUDGET]
S_one = $drive_steps(S_finish, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps
S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.CODE = S.CODE /\ S_done.POOLS = S.POOLS
$retained_outputs_only(S_done.EVENTS)
$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)
''') + ['$retained_outputs(S_done.EVENTS) = [' + ','.join(map(str, cases.OUTPUTS[index])) + ']']
    if thrown:
        checks += lines(r'''
$lookup(S_done.ENV, $ptascii("caught")) = (n_caught)
S_done.STORE[n_caught] = DEFINED (POBJECT n_saved)
$throwable_previous_id(S_done, n_saved) = eps
S_done.STORE[n_got] = DEFINED (PINT 99)
''')
    reached = len(checks)
    wrong = '1x' if bounds else '3x'
    checks += [f'pstringread_wrong = pstringread[.READ.INPUT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("{wrong}")))][.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("{wrong}"))]',
        '$string_read_request_base_saved(S_after, pstringread_wrong) = eps',
        '~$string_read_source(S_after, pstringread_wrong)'] + lines(r'''
$string_read_request_base_saved(S_after, pstringread[.KEYCELL = (n_got)]) = eps
$string_read_request_base_saved(S_after, pstringread[.BASECELL = eps]) = eps
$string_read_request_base_saved(S_after, pstringread[.READ.PHASE = KEY_CV]) = eps
$string_read_request_base_saved(S_after, pstringread[.READ.INPUT = VARIABLE ($ptascii("key")) 5]) = eps
~$string_read_source(S_after[.ORIGIN = eps], pstringread)
~$string_read_source(S_after, pstringread[.READ.LINE = 6])
$string_read_plan(S[.PROPREFS = [{CELL n_text, SOURCES eps}]]) = eps
S_nul = S[.STRINGDATA = [[97,0,99]]][.STORE[n_text] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) ([97,0,99]))][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) ([97,0,99]))]
$string_carrier_valid(S_nul, PSTRING_CARRIER (REQUEST_STRING 0) ([97,0,99]))
$string_read_plan(S_nul) = eps
S_lost = S_after[.ENV = $unbind(S_after.ENV, $ptascii("keeper"))]
$string_read_source(S_lost, pstringread) /\ ~$string_read_ready(S_lost, pstringread)
$string_read_resume(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
$string_read_discard(S_lost, pstringread) = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_equal = S_after[.STRINGDATA = S_after.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))]
$string_read_source(S_equal, pstringread) /\ ~$string_read_ready(S_equal, pstringread)
~$string_read_ready(S_after[.REFCELLS = n_keeper :: S_after.REFCELLS], pstringread)
''')
    return checks, len(checks) - reached


def concat_conditions(program, path):
    return ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET'] + lines(r'''
S_found = $literal_key_seek(S_initial, 2000)
S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
S = S_found[.COMPLETION = NORMAL]
$literal_key_front(S)
S.TODO = (KEY_READ_DIM (KNOWN pvalue_key) 5 KEY_R) :: ptask_tail*
pvalue_key = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))
$lookup(S.ENV, $ptascii("text")) = (n_text)
$lookup(S.ENV, $ptascii("keeper")) = (n_keeper)
S.STORE[n_text] = DEFINED pvalue_base
S.STORE[n_keeper] = DEFINED pvalue_base
pvalue_base = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
S.ORIGIN = (porigin)
$origin_child((porigin), [PCFIELD 1]) = (porigin_key)
$origin_node(S.SOURCES, porigin_key) = (NExprBinaryOpConcat expression_1 expression_2 metadata)
$parser_literal_at(NExprBinaryOpConcat expression_1 expression_2 metadata, 14) = (PSTRING ($ptascii("1x")))
$compiled_read(S, porigin_key) = (PSTRING ($ptascii("1x")))
$compiled_string_value(S, porigin_key, PSTRING ($ptascii("1x"))) = pvalue_key
$string_read_request_base_leading(S, pvalue_base, pvalue_key) = (1)
$string_read_key_capture(S, KNOWN pvalue_key, pvalue_base) = ((pvalue_key, eps))
$error_handler_eligible(S, 2)
$string_read_plan(S) = eps
S.EVENTS = eps
PhpStep: S ~> S_refused
S_refused.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_refused.EVENTS = eps /\ S_refused.STORE = S.STORE
''')


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
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = dict(cases.CASES)
    first_source = next(iter(sources.values()))
    assert first_source.count(b"$got=$text['1x'];") == 1
    sources['folded-concat-literal-key-refusal'] = first_source.replace(b"$got=$text['1x'];", b"$got=$text['1'.'x'];")
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()}) for name, source in sources.items()}
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
    for index, (name, source_bytes) in enumerate(sources.items()):
        if index < 3:
            row = rows[name]
            native, outcome = row['native'], row['outcome']
            assert row['passed'] and outcome['status'] == 'normal' and outcome['exit_status'] == 0
            assert base64.b64decode(outcome['stdout']) == cases.OUTPUTS[index] and not base64.b64decode(outcome['stderr'])
            assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
            source = Path(native['argv'][-1])
            assert source.is_absolute() and source.read_bytes() == source_bytes and digest(source) == row['source_sha256']
            assert source.with_name('native.stdout').read_bytes() == cases.OUTPUTS[index] and not source.with_name('native.stderr').read_bytes()
            originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
            checks, derived = conditions(checked[name]['fixture'], source, index)
        else:
            source = out / (name + '.php')
            source.write_bytes(source_bytes)
            originals.append(source)
            checks = concat_conditions(checked[name]['fixture'], source)
            derived = len(checks)
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
        fixtures.append(fixture)
        selections.append({'id': name, 'conditions': len(checks), 'derived_conditions': derived, 'source_credit': 0})
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner, Path(__file__), Path(cases.__file__), Path(shared.__file__), report_path, *originals, *fixtures, *[ROOT / name for name in ('_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py')]]
    before = {str(path): digest(path) for path in watched}
    assert [value for path, value in report['inputs'].items() if path.endswith('/.tools/php/bin/php') or path == '.tools/php/bin/php'] == [digest(ROOT / '.tools/php/bin/php')]
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
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL', 'module_entries': len(modules), 'selection': list(sources), 'rows': selections, 'conditions': sum(row['conditions'] for row in selections), 'derived_conditions': sum(row['derived_conditions'] for row in selections), 'inputs': before, 'profile': profile, 'native_reused_from': str(report_path), 'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
