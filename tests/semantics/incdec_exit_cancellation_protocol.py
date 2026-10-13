#!/usr/bin/env python3
"""Source-reached handler-local exit cancellation and pending-owner checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_exit_cancellation_cases as cases
import incdec_exit_protocol as exit_protocol
import incdec_warning_protocol as update_protocol
import integer_operator_warning_protocol as runner

CASES = ('cleanup-throw-int23', 'cleanup-throw-string-post',
         'cleanup-throw-kept-cell-rebind')
HELPERS = exit_protocol.HELPERS + r'''
def $update_exit_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (UPDATE_WARNING_EXIT perrorcall z) :: ptask_tail*
'''


def conditions(name, program, path, stdout):
    status = cases.EXIT_CODES.get(name, 0)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin = $update_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        '$update_warning_plan(S_begin) = (pupdatewarning)',
        'S_guard = $update_exit_seek(S_begin, 6, 2500)[.COMPLETION = NORMAL]',
        'S_guard.TODO = (THROW_SEARCH n_second) :: (UPDATE_WARNING_EXIT perrorcall z) :: ptask_tail*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'z = ' + str(status), 'S_guard.EXITSTATUS = ' + str(status),
        'S_guard.RESULT = KNOWN PNULL', 'S_guard.BASE = BASE_VALUE (KNOWN PNULL)',
        '$call_descriptors_valid(S_guard)', '$heap_valid($heap_graph(S_guard))',
        'pupdatewarning.PENDING = eps',
        '$update_warning_exit_named(S_guard, perrorcall)',
        '$update_warning_exit_cancel_safe(S_guard, perrorcall)',
        '$throwable_live(S_guard, n_second)',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$task_nodes(UPDATE_WARNING_EXIT perrorcall z) = eps',
        'S_global = $global_table_view(S_guard)',
        '$lookup(S_global.ENV, $ptascii("second")) = (n_second_cell)',
        'S_guard.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        'S_guard.STORE[n_value] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_guard)), HOBJECT n_second) = 2',
        '$throwable_previous_id(S_guard, n_second) = eps',
        '~$throwable_live(S_guard, |S_guard.OBJECTS|)',
        '~$call_task_valid(S_guard, UPDATE_WARNING_EXIT perrorcall 2147483648)',
        '~$call_task_valid(S_guard, UPDATE_WARNING_EXIT perrorcall[.MESSAGE = eps] z)',
        '~$call_task_valid(S_guard[.CODE = eps], UPDATE_WARNING_EXIT perrorcall z)',
        'PhpStep: S_guard ~> S_pending',
        'S_pending.TODO = (UPDATE_WARNING_DONE pupdatewarning_pending) :: ptask_tail*',
        'pupdatewarning_pending = pupdatewarning[.PENDING = (n_second)]',
        '$task_nodes(UPDATE_WARNING_DONE pupdatewarning_pending) = [HOBJECT n_second]',
        'S_pending.COMPLETION = NORMAL', 'S_pending.EXITSTATUS = S_guard.EXITSTATUS',
        'S_pending.RESULT = KNOWN PNULL', 'S_pending.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_pending.CURRENT = S_guard.CURRENT', 'S_pending.FRAMES = S_guard.FRAMES',
        'S_pending.ORIGIN = S_guard.ORIGIN', 'S_pending.EVENTS = S_guard.EVENTS',
        'S_pending.CODE = S_guard.CODE', 'S_pending.POOLS = S_guard.POOLS',
        'S_pending.STORE[n_value] = DEFINED (PINT 100)',
        'S_pending.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
        '$throwable_previous_id(S_pending, n_second) = eps',
        'PhpStep: S_pending ~> S_search',
        'S_search.TODO = (THROW_SEARCH n_second) :: ptask_tail*',
        'S_search.COMPLETION = NORMAL', 'S_search.EXITSTATUS = S_guard.EXITSTATUS',
        'S_search.STORE = S_pending.STORE', 'S_search.EVENTS = S_pending.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_search)), HOBJECT n_second) = 2',
        '$call_descriptors_valid(S_search)',
        '$drive_steps(S_guard, 0) = S_guard[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_guard, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_guard', 'S_pending') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_search, 2500)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = ' + str(status),
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if name == 'cleanup-throw-string-post':
        checks += [
            'pupdatewarning.POST',
            '$string_bytes(pupdatewarning.INPUT) = ($ptascii("foo"))',
            '~$update_warning_restores_throw(pupdatewarning.INPUT)',
            '$lookup(S_global.ENV, $ptascii("x")) = (n_x)',
            'S_guard.STORE[n_x] = DEFINED (PINT 41)',
            'S_pending.STORE = S_guard.STORE',
        ]
    else:
        checks += [
            'pupdatewarning.INPUT = PBOOL true', '~pupdatewarning.POST',
            '$update_warning_restores_throw(pupdatewarning.INPUT)',
        ]
        if name == 'cleanup-throw-kept-cell-rebind':
            checks += [
                'pupdatewarning.POINTER = UPDATE_CELL n_old',
                '$lookup(S_global.ENV, $ptascii("keep")) = (n_old)',
                '$lookup(S_global.ENV, $ptascii("x")) = (n_new)',
                '$lookup(S_global.ENV, $ptascii("peer")) = (n_new)', 'n_old =/= n_new',
                'S_guard.STORE[n_old] = DEFINED (PINT 41)',
                'S_guard.STORE[n_new] = DEFINED (PINT 73)',
                'S_pending.STORE[n_old] = DEFINED (PBOOL true)',
                'S_pending.STORE[n_new] = DEFINED (PINT 73)',
                '$heap_owners($heap_prune($heap_graph(S_guard)), HCELL n_old) = 1',
                '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_old) = 1',
            ]
        else:
            checks += [
                'pupdatewarning.POINTER = UPDATE_CV ($ptascii("x"))',
                '$lookup(S_global.ENV, $ptascii("x")) = (n_x)',
                'S_guard.STORE[n_x] = DEFINED (PINT 41)',
                'S_pending.STORE[n_x] = DEFINED (PBOOL true)',
            ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-exit-cancellation-', dir=runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(cases.__file__), Path(exit_protocol.__file__),
               Path(update_protocol.__file__), Path(runner.__file__)]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    before = {str(p): digest(p) for p in watched}
    runner.CASES, runner.HELPERS, runner.conditions = CASES, HELPERS, conditions
    runner.sources = cases
    runner.__file__ = __file__
    passed = runner.main()
    assert before == {str(p): digest(p) for p in watched}
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'] = before
    for row in report['rows']:
        assert row['native']['interruption'] is None and row['native']['group_after'] == []
        if 'model' in row:
            result = row['model']
            row['passed'] = row['passed'] and result['interruption'] is None and result['group_after'] == []
            row['passed'] = row['passed'] and (out / (row['id'] + '-model.stdout')).read_bytes() == b'true\n'
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed and all(row.get('passed', True) for row in report['rows'])


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
