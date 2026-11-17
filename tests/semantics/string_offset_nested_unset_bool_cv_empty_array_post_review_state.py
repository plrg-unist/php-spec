#!/usr/bin/env python3
"""Independent live empty-array ownership and saved-CV continuation checks."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as seek
import string_offset_nested_unset_bool_cv_empty_array_post_cases as cases

INDEX = 0
PRELAW = False


def conditions(program, path):
    facts = cases.FACTS[tuple(cases.CASES)[INDEX]]
    pending = facts['throwing']
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    checks = [
        'S_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_I.COMPLETION = BUDGET',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_E.ENV, n_key_name*) = (n_key)',
        'S_E.STORE[n_key] = DEFINED ' + facts['entry'],
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_E.ERRORHANDLER.LEVELS = 30719',
        '$task_nodes(' + resume + ') = eps',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_original_tail*',
        'perrorcall_first.RESUME = ' + resume,
        '$error_call_valid(S_A, perrorcall_first)',
        'S_A.STORE = S_E.STORE',
        'S_P_found = $review_cv_seek(S_A, "' + ('discard' if pending else 'resume') + '", 1000)',
        '$review_cv_at(S_P_found, "' + ('discard' if pending else 'resume') + '")',
        'S_P = $review_cv_running(S_P_found)',
    ]
    if pending:
        checks += [
            'S_P.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = ' + resume,
            'perrorcall_entered.CALLBACK = pvalue_callback',
            'S_P.ERRORHANDLER.CALLBACK = eps',
            'S_P.OBJECTS[n_exception] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            '$throwable_member(S_P, n_exception)',
            '$throwable_field(S_P, n_exception, "message") = PSTRING_CARRIER INTERNED_STRING ($ptascii("handler"))',
            '$throwable_field(S_P, n_exception, "line") = PINT 2',
            'S_cut = S_P[.TODO = (THROW_SEARCH n_exception) :: ptask_after*]',
            '$identity_read_discard(S_cut, ' + resume + ') = S_cut',
            'S_R = $error_handler_restore(S_cut, pvalue_callback)',
            'S_R = S_cut[.ERRORHANDLER.CALLBACK = (pvalue_callback)]',
        ]
    else:
        checks += ['S_R = S_P', 'S_R.TODO = (' + resume + ') :: ptask_after*']
    checks += [
        'ptask_after* = ptask_caller :: ptask_rest*',
        'S_R.COMPLETION = NORMAL',
        'S_R.ORIGIN = (porigin_site)',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        'porigin_key = PORIGIN 0 pcpath_key',
        '$origin_node(S_R.SOURCES, porigin_key) = (NExprVariable (BYTES text_key) metadata_key)',
        '$base64(text_key) = n_key_name*',
        '$source_line(metadata_key) = z_key',
        '$source_emission_cv(S_R, 0, pcpath_key, NExprVariable (BYTES text_key) metadata_key)',
        '$compiled_read(S_R, porigin_key) = eps',
        '$lookup(S_R.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_R.STORE|)',
        '~$environment_blocked(S_R, n_key_name*)',
        '~(n_key <- S_R.REFCELLS)',
        '~$foreach_released_cell(S_R, n_key)',
        '~$typed_cv_string_released_cell(S_R, n_key)',
        '~$update_released_cell(S_R, n_key)',
        'S_R.STORE[n_key] = DEFINED (PARRAY n_array)',
        '$(n_array < |S_R.ARRAYS|)',
        'parray_saved = S_R.ARRAYS[n_array]',
        'parray_saved.ITEMS = eps',
        '$entries_nodes(parray_saved.ITEMS) = eps',
        '$value_nodes(PARRAY n_array) = [HARRAY n_array]',
        '$resolve_at(S_R, VARIABLE n_key_name* z_key, z_key) = S_R[.RESULT = KNOWN (PARRAY n_array)]',
        'H_saved = $heap_graph(S_R)',
        '$heap_valid(H_saved)',
        '$heap_member(HCELL n_key, H_saved.NODES)',
        '$heap_member(HCELL n_key, H_saved.ROOTS)',
        '$heap_member(HARRAY n_array, H_saved.NODES)',
        '$node_children(S_R, HCELL n_key) = [HARRAY n_array]',
        '$node_children(S_R, HARRAY n_array) = eps',
        '(HEDGE (HCELL n_key) (HARRAY n_array)) <- H_saved.EDGES',
        '$heap_edge_owners(HARRAY n_array, H_saved.EDGES, [HCELL n_key]) = 1',
        '$($heap_owners(H_saved, HARRAY n_array) > 0)',
        '$heap_member(HARRAY n_array, $heap_reach(H_saved.ROOTS, eps, H_saved.EDGES))',
        '$call_task_valid(S_R, ' + resume + ')',
        'S_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_R.ERRORHANDLER.LEVELS = 30719',
        '$error_handler_eligible(S_R, 2)',
        r'S_R.REQUEST = eps /\ S_R.CURRENT = eps /\ S_R.FRAMES = eps /\ S_R.HELD = eps',
        r'S_R.SOURCEPENDING = eps /\ S_R.CONSTCONTEXT = eps',
        'S_R.RESULT = KNOWN PNULL',
        '$review_cv_outputs(S_R.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        *seek.public('S_R'),
    ]
    if not PRELAW:
        return postconditions(checks, pending, resume)
    checks += [
        '~$string_unset_bool_cv_post_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_plan(S_R) = eps',
    ]
    if pending:
        checks += [
            '$error_read_discard(S_R, ' + resume + ') = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
            'PhpStep: S_P ~> S_old',
            'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
        ]
    else:
        checks += ['PhpStep: S_R ~> S_old',
            'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    checks += [
        'S_old.STORE = S_R.STORE',
        'S_old.ARRAYS = S_R.ARRAYS',
        'S_old.ALLOCATIONS = S_R.ALLOCATIONS',
        'S_old.EVENTS = S_R.EVENTS',
    ]
    return checks, 0


def postconditions(checks, pending, resume):
    checks += [
        '~$string_unset_bool_cv_post_value(PARRAY n_array)',
        '~$string_unset_bool_cv_post_normal_value(PARRAY n_array)',
        '$string_unset_bool_cv_post_empty_array(S_R, n_key)',
        '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_plan(S_R) = eps',
        '~$string_unset_cv_range_discard(S_R, ' + resume + ')',
    ]
    if pending:
        checks += [
            '$error_read_discard(S_R, ' + resume + ') = S_R',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R',
            'PhpStep: S_P ~> S_next',
            'S_next = S_R',
            'S_next.TODO = (THROW_SEARCH n_exception) :: ptask_after*',
            'S_next.OBJECTS[n_exception] = S_P.OBJECTS[n_exception]',
            '$drive_steps(S_P, 1) = S_next[.COMPLETION = BUDGET]',
        ]
    else:
        checks += [
            'PhpStep: S_R ~> S_next',
            'S_next = S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
            'S_public = $drive_steps(S_R, 1)',
            'S_public.COMPLETION = BUDGET',
            'S_public.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            'S_public.OBJECTS[n_error] = THROWABLE pthrowable_error',
            'pthrowable_error.KIND = "Error"',
            '$throwable_field(S_public, n_error, "message") = PSTRING ($ptascii("Cannot use string offset as an array"))',
            '$throwable_field(S_public, n_error, "line") = PINT z',
            *seek.public('S_public'),
        ]
    checks += [
        '$heap_graph(S_next) = H_saved',
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
        'S_DONE.ARRAYS[n_array] = parray_saved',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + seek.term(cases.OUTPUTS[tuple(cases.CASES)[INDEX]]),
        *seek.public('S_DONE'),
        '$drive_steps(S_E, 5000) = S_DONE',
    ]
    if pending:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    else:
        checks += ['$drive_steps($review_cv_running(S_public), 3000) = S_DONE']
    reached = len(checks)
    for tag, changed in (
        ('dangling', 'S_R[.STORE[n_key] = DEFINED (PARRAY (|S_R.ARRAYS|))]'),
        ('missing_array', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HARRAY n_array)]'),
        ('missing_cell', 'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_key)]'),
        ('duplicate_cell', 'S_R[.ALLOCATIONS = S_R.ALLOCATIONS ++ [HCELL n_key]]'),
        ('nonempty', 'S_R[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]]'),
        ('unrooted', 'S_R[.ENV = eps][.GLOBALTABLE = eps][.TODO = eps]'),
    ):
        state = 'S_refuse_' + tag
        checks += [state + ' = ' + changed,
            '~$string_unset_bool_cv_post_empty_array(' + state + ', n_key)',
            '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(' + state + ', n_key_name*, z_key, n_key)']
    checks += [
        '~$string_unset_bool_cv_post_empty_array(S_R, (|S_R.STORE|))',
        '$string_unset_bool_cv_post_empty_array(S_R[.NATIVEEXCESS = S_R.NATIVEEXCESS ++ [HARRAY n_array, HARRAY n_array]], n_key)',
        '$call_task_valid(S_refuse_nonempty, ' + resume + ')',
    ]
    for changed in (
        'S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
        'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
        'S_R[.STORE[n_key] = UNDEFINED]',
    ):
        checks += ['~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(' + changed + ', n_key_name*, z_key, n_key)']
    for changed in ('S_R[.CODE = eps]', 'S_R[.SOURCES = eps]', 'S_R[.ORIGIN = eps]'):
        checks.append('~$call_task_valid(' + changed + ', ' + resume + ')')
    if pending:
        checks += ['$error_read_discard(S_refuse_nonempty, ' + resume + ') = S_refuse_nonempty[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    else:
        checks += ['PhpStep: S_refuse_nonempty ~> S_refuse_next',
            'S_refuse_next = S_refuse_nonempty[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
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
    watched = [Path(__file__), Path(seek.__file__), Path(sl.__file__),
               Path(cases.prior.__file__), *[runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions, runner.PREFIX, runner.recorded = cases, conditions, seek.PREFIX, sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent source-reached saved ordinary NULL/BOOL CV contains a live empty '
        'array with exact quiet compiled read, ENV-rooted HCELL/HARRAY edge and full heap/reachability '
        'before old Unsupported. Actual normal/pending caller tails and the genuine Exception remain '
        'separate; no new admission premise establishes reachability, source0/native0.' if PRELAW else
        'Independent source-reached saved ordinary NULL/BOOL CV retains its real empty array and '
        'full heap through the exact normal Error or same pending Exception/caller tail, public '
        'materialization, zero/one/split budgets and final state. Derived dangling, unallocated, '
        'duplicate, nonempty, unrooted, reference and source refusals stay separate; source0/native0.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
