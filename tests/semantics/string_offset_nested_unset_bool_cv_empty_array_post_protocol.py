#!/usr/bin/env python3
"""Source-reached live empty-array ownership and saved-CV completion."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as shared
import string_offset_nested_unset_bool_cv_empty_array_post_cases as cases

INDEX = 0
PRELAW = False
PREFIX = shared.PREFIX


def front(program, path):
    name = tuple(cases.CASES)[INDEX]
    facts = cases.FACTS[name]
    stage = 'discard' if facts['throwing'] else 'resume'
    checks = [
        'S_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_I.COMPLETION = BUDGET',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        'S_E.STORE[n_key] = DEFINED ' + facts['entry'],
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_E.ERRORHANDLER.LEVELS = 30719',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_after*',
        'perrorcall_first.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_A, perrorcall_first)',
        'S_P_found = $review_cv_seek(S_A, "' + stage + '", 1000)',
        '$review_cv_at(S_P_found, "' + stage + '")',
        'S_P = $review_cv_running(S_P_found)',
    ]
    if facts['throwing']:
        checks += ['S_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = perrorcall_first.RESUME',
            'S_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            '$throwable_field(S_P, n_throwable, "message") = PSTRING_CARRIER INTERNED_STRING ($ptascii("handler"))',
            '$throwable_field(S_P, n_throwable, "line") = PINT 2',
            'S_cut = S_P[.TODO = (THROW_SEARCH n_throwable) :: ptask_after*]',
            '$identity_read_discard(S_cut, perrorcall_entered.RESUME) = S_cut',
            'S_R = $error_handler_restore(S_cut, pvalue_callback)',
            'S_R.TODO = (THROW_SEARCH n_throwable) :: ptask_after*']
    else:
        checks += ['S_R = S_P',
            'S_R.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*']
    checks += [
        'S_R.COMPLETION = NORMAL',
        'ptask_after* = ptask_caller :: ptask_rest*',
        'S_R.ORIGIN = (porigin_site)',
        '$lookup(S_R.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_R.STORE|)',
        '~$environment_blocked(S_R, n_key_name*)',
        '~(n_key <- S_R.REFCELLS)',
        '~$foreach_released_cell(S_R, n_key)',
        '~$typed_cv_string_released_cell(S_R, n_key)',
        '~$update_released_cell(S_R, n_key)',
        'S_R.STORE[n_key] = DEFINED (PARRAY n_array)',
        '$(n_array < |S_R.ARRAYS|)',
        'parray_key = S_R.ARRAYS[n_array]',
        'parray_key.ITEMS = eps',
        '$resolve_at(S_R, VARIABLE n_key_name* z_key, z_key) = S_R[.RESULT = KNOWN (PARRAY n_array)]',
        'H_R = $heap_graph(S_R)',
        '$heap_valid(H_R)',
        '$heap_member(HCELL n_key, H_R.NODES)',
        '$heap_member(HCELL n_key, H_R.ROOTS)',
        '$heap_member(HARRAY n_array, H_R.NODES)',
        '$node_children(S_R, HCELL n_key) = [HARRAY n_array]',
        '$node_children(S_R, HARRAY n_array) = eps',
        '$heap_edge_owners(HARRAY n_array, H_R.EDGES, [HCELL n_key]) = 1',
        '$($heap_owners(H_R, HARRAY n_array) > 0)',
        '$value_nodes(PARRAY n_array) = [HARRAY n_array]',
        '$task_nodes(perrorcall_first.RESUME) = eps',
        '$call_task_valid(S_R, perrorcall_first.RESUME)',
        'S_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_R.ERRORHANDLER.LEVELS = 30719',
        r'S_R.REQUEST = eps /\ S_R.CURRENT = eps /\ S_R.FRAMES = eps /\ S_R.HELD = eps',
        r'S_R.SOURCEPENDING = eps /\ S_R.CONSTCONTEXT = eps',
        'S_R.RESULT = KNOWN PNULL',
        '$review_cv_outputs(S_R.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        *shared.public('S_R'),
    ]
    return checks


def conditions(program, path):
    checks = front(program, path)
    pending = cases.FACTS[tuple(cases.CASES)[INDEX]]['throwing']
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    if PRELAW:
        checks += ['~$string_unset_bool_cv_post_value(PARRAY n_array)',
            '~$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
            '$string_unset_cv_range_plan(S_R) = eps']
        if pending:
            checks += ['PhpStep: S_P ~> S_old',
                'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        else:
            checks += ['PhpStep: S_R ~> S_old',
                'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        return checks, 0
    checks += ['~$string_unset_bool_cv_post_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_normal_value(PARRAY n_array)',
        '$string_unset_bool_cv_post_empty_array(S_R, n_key)',
        '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_plan(S_R) = eps',
        '~$string_unset_cv_range_discard(S_R, ' + resume + ')']
    if pending:
        checks += ['$error_read_discard(S_R, ' + resume + ') = S_R',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R',
            'PhpStep: S_P ~> S_next',
            'S_next = S_R',
            'S_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]',
            '$drive_steps(S_P, 1) = S_next[.COMPLETION = BUDGET]']
    else:
        checks += ['PhpStep: S_R ~> S_next',
            'S_next = S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
            'S_public = $drive_steps(S_R, 1)',
            'S_public.COMPLETION = BUDGET',
            'S_public.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            'S_public.OBJECTS[n_error] = THROWABLE pthrowable_error',
            'pthrowable_error.KIND = "Error"',
            '$throwable_field(S_public, n_error, "message") = PSTRING ($ptascii("Cannot use string offset as an array"))',
            '$throwable_field(S_public, n_error, "line") = PINT z',
            '$heap_valid($heap_graph(S_public))']
    name = tuple(cases.CASES)[INDEX]
    checks += ['$heap_graph(S_next) = $heap_graph(S_R)',
        'S_next.STORE = S_R.STORE',
        'S_next.ARRAYS = S_R.ARRAYS',
        'S_next.ALLOCATIONS = S_R.ALLOCATIONS',
        'S_next.EVENTS = S_R.EVENTS',
        '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]',
        'S_DONE = $drive_steps(S_P, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        'S_DONE.STORE[n_key] = DEFINED (PARRAY n_array)',
        'S_DONE.ARRAYS[n_array] = parray_key',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + shared.term(cases.OUTPUTS[name]),
        *shared.public('S_DONE'),
        '$drive_steps(S_E, 5000) = S_DONE']
    if pending:
        checks += ['S_DONE.OBJECTS[n_throwable] = S_R.OBJECTS[n_throwable]']
    else:
        checks += ['$drive_steps($review_cv_running(S_public), 3000) = S_DONE']
    reached = len(checks)
    for tag, changed in (
        ('no_array', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_array)]'),
        ('no_cell', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_key)]'),
        ('duplicate', 'S_R[.ALLOCATIONS = S_R.ALLOCATIONS ++ [HARRAY n_array]]'),
        ('nonempty', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]]'),
        ('alias', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_key)]]'),
        ('oob', 'S_R[.STORE[n_key] = DEFINED (PARRAY (|S_R.ARRAYS|))]'),
        ('undefined', 'S_R[.STORE[n_key] = UNDEFINED]'),
    ):
        state = 'S_bad_' + tag
        refusal = '' if tag == 'nonempty' else '~'
        checks += [state + ' = ' + changed,
            '~$string_unset_bool_cv_post_empty_array(' + state + ', n_key)',
            refusal + '$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
            refusal + '$string_unset_bool_cv_post_normal_cell(' + state + ', n_key_name*, z_key, n_key)']
        if tag == 'nonempty':
            checks += ['$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['n_rebound = |S_R.STORE|']
    for changed in (
        'S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
        'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
        'S_R[.ENV = (BIND n_key_name* n_rebound) :: $unbind(S_R.ENV, n_key_name*)][.STORE = S_R.STORE ++ [DEFINED (PARRAY n_array)]][.ALLOCATIONS = S_R.ALLOCATIONS ++ [HCELL n_rebound]]',
    ):
        checks += ['~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(' + changed + ', n_key_name*, z_key, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks.append('~$call_task_valid(' + changed + ', ' + resume + ')')
    checks += ['~$string_unset_bool_cv_post_empty_array(S_R, (|S_R.STORE|))',
        '$call_task_valid(S_bad_nonempty, ' + resume + ')']
    if pending:
        checks += ['$error_read_discard(S_bad_nonempty, ' + resume + ') = S_bad_nonempty']
    else:
        checks += ['PhpStep: S_bad_nonempty ~> S_bad_next',
            'S_bad_next = S_bad_nonempty[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]']
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    name = tuple(cases.CASES)[INDEX]
    watched = [Path(__file__), Path(shared.__file__), Path(sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions, runner.PREFIX, runner.recorded = cases, conditions, PREFIX, sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Source-reached live empty-array ownership before old Unsupported; source0/native0.' if PRELAW else
        'Source-reached saved ordinary NULL/BOOL CV retains its real empty array, full heap and exact normal fixed Error or pending Throwable/caller tail. Budgets, final outputs and derived storage/owner/source refusals are separate; source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
