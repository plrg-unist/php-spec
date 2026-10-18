#!/usr/bin/env python3
"""Source-reached missing-list-key callbacks, saved owners and cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import list_missing_warning_cases as cases

ROOT = Path(__file__).resolve().parents[2]
HELPERS = r'''
dec $list_warning_task(ptask) : bool
def $list_warning_task(LIST_MISSING_RESULT poperand n expression phpType13* z pkey) = true
def $list_warning_task(ERROR_HANDLER_INVOKE perrorcall) = $list_warning_task(perrorcall.RESUME)
def $list_warning_task(ERROR_HANDLER_RESULT perrorcall) = $list_warning_task(perrorcall.RESUME)
def $list_warning_task(ERROR_HANDLER_CLEAN perrorcall) = $list_warning_task(perrorcall.RESUME)
def $list_warning_task(AT porigin ptask) = $list_warning_task(ptask)
def $list_warning_task(ptask) = false -- otherwise
dec $list_warning_tasks(ptask*) : bool
def $list_warning_tasks(eps) = false
def $list_warning_tasks(ptask :: ptask_tail*) = ($list_warning_task(ptask) \/ $list_warning_tasks(ptask_tail*))
dec $list_warning_frontier(pstate, nat) : bool
def $list_warning_frontier(S, 0) = ($list_missing_plan(S) =/= eps)
def $list_warning_frontier(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if $list_warning_task(perrorcall.RESUME)
def $list_warning_frontier(S, 2) = true
  -- if S.TODO = (LIST_MISSING_RESULT poperand n expression phpType13* z pkey) :: ptask_tail*
def $list_warning_frontier(S, 3) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $list_warning_task(perrorcall.RESUME)
def $list_warning_frontier(S, 4) = true
  -- if S.TODO = (LIST_FETCH poperand n expression false phpType13* z) :: ptask_tail*
  -- if $(n > 0)
def $list_warning_frontier(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if S.FRAMES = eps
  -- if ~$list_warning_tasks(S.TODO)
def $list_warning_frontier(S, n) = false -- otherwise
dec $list_warning_seek(pstate, nat, nat) : pstate
def $list_warning_seek(S, n_stage, n) = S -- if $list_warning_frontier(S, n_stage)
def $list_warning_seek(S, n_stage, n) = S
  -- if ~$list_warning_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $list_warning_seek(S, n_stage, 0) = S
  -- if ~$list_warning_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $list_warning_seek(S, n_stage, n) = $list_warning_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$list_warning_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $list_warning_outputs(pevent*) : ptbytes
dec $list_warning_is_output(pevent) : bool
def $list_warning_outputs(eps) = eps
def $list_warning_outputs((OUTPUT n*) :: pevent_tail*) = n* ++ $list_warning_outputs(pevent_tail*)
def $list_warning_outputs(pevent :: pevent_tail*) = $list_warning_outputs(pevent_tail*) -- if ~$list_warning_is_output(pevent)
def $list_warning_is_output(OUTPUT n*) = true
def $list_warning_is_output(pevent) = false -- otherwise
'''


def conditions(name, program, path, stdout):
    shared = name != 'list-missing-rebind-snapshot'
    thrown = name == 'list-missing-throw-targets'
    marker = 'LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 0 expression phpType13* z (KINT 0)'
    args = 'KNOWN (PARRAY n_array), 0, expression, phpType13*, z, KINT 0'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$list_warning_frontier(S, 0)',
        'S.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 0 expression false phpType13* z) :: ptask_tail*',
        'S.RESULT = KNOWN (PINT 0)', 'S.ORIGIN = (porigin)',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 0) = eps',
        '$list_missing_source(S, ' + args + ')',
        '~$list_missing_source(S, KNOWN (PARRAY n_array), 0, expression, phpType13*, $(z + 1), KINT 0)',
        '~$list_missing_source(S, KNOWN (PARRAY n_array), 1, expression, phpType13*, z, KINT 0)',
        '~$list_missing_source(S, KNOWN (PARRAY n_array), 0, expression, eps, z, KINT 0)',
        '~$list_missing_source(S, KNOWN (PARRAY n_array), 0, expression, phpType13*, z, KINT 9)',
        '~$list_missing_source(S[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '~$list_missing_source(S, KNOWN (PARRAY (|S.ARRAYS|)), 0, expression, phpType13*, z, KINT 0)',
        '$list_missing_plan(S[.RESULT = KNOWN (PINT 9)]) = eps',
        '$task_nodes(LIST_FETCH (KNOWN (PARRAY n_array)) 0 expression false phpType13* z) = [HARRAY n_array]',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = $(2 + $heap_count(HARRAY n_array, $pools_nodes(S.POOLS)))',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', '$list_warning_frontier(S_dispatch, 1)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker,
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $ptascii("Undefined array key 0")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 512])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.SITE = PORIGIN 9 eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE z])',
        '~$call_task_valid(S_dispatch, LIST_MISSING_RESULT (KNOWN (PARRAY n_array)) 0 expression phpType13* z (KINT 9))',
        '$task_nodes(' + marker + ') = [HARRAY n_array]',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HARRAY n_array]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$list_warning_frontier(S_entered, 3)',
        'S_entered.ERRORHANDLER.CALLBACK = eps', 'S_entered.CURRENT = (pcallcontext)',
        'S_entered.FRAMES = pframe :: eps',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ' + marker,
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if shared:
        checks += [
            '$lookup(S.ENV, $ptascii("q")) = (n_q)',
            '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 1) = (ALIAS n_q)',
            'S.STORE[n_q] = DEFINED (PINT 2)',
            '$heap_count(HARRAY n_array, $pools_nodes(S.POOLS)) = 0',
            '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entered)), HARRAY n_array) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entered)), HCELL n_q) = 2',
        ]
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("v")) = (n_v)',
            'S_pending_found = $list_warning_seek(S_entered, 5, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]', '$list_warning_frontier(S_pending, 5)',
            'S_pending.TODO = (THROW_SEARCH n_second) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            '~((HARRAY n_array) <- S_pending.ALLOCATIONS)', '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            '$lookup(S_pending.ENV, $ptascii("a")) = eps', '$lookup(S_pending.ENV, $ptascii("q")) = eps',
            'S_pending.STORE[n_x] = DEFINED (PINT 99)', 'S_pending.STORE[n_y] = DEFINED (PINT 8)',
            'S_pending.STORE[n_v] = DEFINED (PINT 100)', '$throwable_previous_id(S_pending, n_second) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $list_warning_seek(S_entered, 2, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$list_warning_frontier(S_return, 2)',
            'S_return.TODO = (' + marker + ') :: ptask_tail*',
            'S_return.ERRORHANDLER = S.ERRORHANDLER', '$list_missing_source(S_return, ' + args + ')',
            'S_return.STORE[n_x] = DEFINED (PINT 7)', 'S_return.STORE[n_y] = DEFINED (PINT 8)',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'PhpStep: S_return ~> S_store',
            'S_store.TODO = (AT porigin_target (LIST_STORE expression (KNOWN PNULL) false z_target)) :: (LIST_NEXT (KNOWN (PARRAY n_array)) 1 phpType13* z_next) :: ptask_tail*',
            'S_store.STORE = S_return.STORE', 'S_store.ARRAYS = S_return.ARRAYS',
            'S_store.ALLOCATIONS = S_return.ALLOCATIONS', 'S_store.RESULT = KNOWN PNULL',
            '$call_descriptors_valid(S_store)', '$heap_valid($heap_graph(S_store))',
            'S_next_found = $list_warning_seek(S_store, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
            'S_next = S_next_found[.COMPLETION = NORMAL]', '$list_warning_frontier(S_next, 4)',
            'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_array)) 1 expression_next false eps z_next) :: ptask_tail*',
            'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.STORE[n_y] = DEFINED (PINT 8)',
            'S_next.RESULT = KNOWN (PINT 1)',
            '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))',
        ]
        if shared:
            checks += [
                '$lookup(S_return.ENV, $ptascii("a")) = eps', '$lookup(S_return.ENV, $ptascii("q")) = eps',
                'S_return.STORE[n_q] = DEFINED (PINT 33)',
                '$entry_lookup(S_return.ARRAYS[n_array].ITEMS, KINT 0) = eps',
                '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 1',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 1',
                'S_done = $drive_steps(S_next, 2000)',
                '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)',
                'S_done.STORE[n_y] = DEFINED (PINT 33)',
            ]
        else:
            checks += [
                'S_return.STORE[n_a] = DEFINED (PARRAY n_rebound)', 'n_array =/= n_rebound',
                '$entry_lookup(S_return.ARRAYS[n_array].ITEMS, KINT 0) = eps',
                '$entry_lookup(S_return.ARRAYS[n_array].ITEMS, KINT 1) = (DIRECT (PINT 2))',
                '$entry_lookup(S_return.ARRAYS[n_rebound].ITEMS, KINT 0) = (DIRECT (PINT 11))',
                '$entry_lookup(S_return.ARRAYS[n_rebound].ITEMS, KINT 1) = (DIRECT (PINT 22))',
                'S_done = $drive_steps(S_next, 2000)',
                'S_done.STORE[n_y] = DEFINED (PINT 2)',
                '$lookup(S_done.ENV, $ptascii("v")) = (n_v)', 'S_done.STORE[n_v] = DEFINED (PARRAY n_array)',
            ]
        checks += ['S_done.STORE[n_x] = DEFINED PNULL']
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '~$list_warning_tasks(S_done.TODO)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done', '$drive_steps(S_dispatch, 2000) = S_done',
    ]


def run(source_cases, make_conditions, helpers=HELPERS, expected_stderr=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, action='append', required=True)
    parser.add_argument('--case', choices=tuple(source_cases.CASES))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    source_reports = [path.resolve() for path in args.source_report]
    source_rows = {row['id']: (row, report) for report in source_reports
                   for row in json.loads(report.read_bytes())['rows']}
    selected = (args.case,) if args.case else tuple(source_cases.CASES)
    flags = [arg for key, value in json.loads((ROOT / 'tests/semantics/profile.json').read_bytes()).items()
             for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(source_cases.CASES[name]).decode()})
                  for name in selected}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        programs = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True})['fixture']
                    for name, row in parsed.items()}
    finally:
        adapter.close()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    rows, originals = [], []
    for name in selected:
        source_row, source_report = source_rows[name]
        native = source_row['native']
        assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
        path = Path(native['argv'][-1])
        if not path.is_absolute():
            path = Path(native['cwd']) / path
        assert path.read_bytes() == source_cases.CASES[name]
        assert digest(path) == source_row['source_sha256']
        stdout_path, stderr_path = path.parent / 'native.stdout', path.parent / 'native.stderr'
        assert stderr_path.read_bytes() == (expected_stderr(name, path) if expected_stderr else b'')
        checks = make_conditions(name, programs[name], path, stdout_path.read_bytes())
        fixture = out / (name + '.watsup')
        fixture.write_text(helpers + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks))
        rows.append({'id': name, 'conditions': len(checks), 'raw_steps': sum(check.startswith('PhpStep:') for check in checks),
                     'native_reused_from': str(source_report), 'native': native, 'source_sha256': digest(path)})
        originals += [path, stdout_path, stderr_path]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', runner, Path(__file__), Path(source_cases.__file__),
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
               ROOT / 'tests/semantics/recorded_worker.py', *source_reports, *originals,
               *[out / (name + '.watsup') for name in selected]]
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if not args.prepare_only:
        for row in rows:
            result = recorded([str(runner), '--sl', *map(str, modules), str(out / (row['id'] + '.watsup'))],
                              out / (row['id'] + '-model'), 180)
            row['model'] = result
            row['passed'] = (result['exit'] == 0 and not result['timeout'] and result['interruption'] is None
                and result['group_after'] == [] and (out / (row['id'] + '-model.stdout')).read_bytes() == b'true\n'
                and not (out / (row['id'] + '-model.stderr')).read_bytes())
            print(row['id'], row['passed'], flush=True)
            if not row['passed']:
                break
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'selection': selected, 'rows': rows, 'inputs': before,
        'scope': 'checked syntax preparation only' if args.prepare_only else 'source-reached SL premises with preserved native originals',
        'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')}}, indent=2) + '\n')
    return args.prepare_only or all(row.get('passed', False) for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if run(cases, conditions) else 1)
