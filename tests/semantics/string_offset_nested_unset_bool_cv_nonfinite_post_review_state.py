#!/usr/bin/env python3
"""Independent reached nonfinite normal and pending conversion frontiers."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as seek
import string_offset_nested_unset_bool_cv_range_warning_review_state as range_peer
import string_offset_nested_unset_bool_cv_nonfinite_post_cases as cases

INDEX = 1
PRELAW = False


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    facts = cases.FACTS[name]
    pending = facts['mode'] == 'first-throw'
    stage = 'discard' if pending else 'resume'
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    checks = [
        'S_I = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_I.COMPLETION = BUDGET',
        'S_I.DISPLAYINIT = ($ptascii("stderr"))',
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
        'S_P_found = $review_cv_seek(S_A, "' + stage + '", 1000)',
        '$review_cv_at(S_P_found, "' + stage + '")',
        'S_P = $review_cv_running(S_P_found)',
    ]
    if pending:
        checks += [
            'S_P.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = ' + resume,
            'perrorcall_entered.CALLBACK = pvalue_callback',
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
        'ptask_after* = ptask_first :: ptask_rest*',
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
        'n_bits = ' + str(facts['bits']),
        'S_R.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$(n_bits < 18446744073709551616)',
        '$float_decode(n_bits) = INFINITE 1',
        '~$fparts_fits($float_decode(n_bits))',
        '$value_nodes(PFLOAT n_bits) = eps',
        '$resolve_at(S_R, VARIABLE n_key_name* z_key, z_key) = S_R[.RESULT = KNOWN (PFLOAT n_bits)]',
        '$call_task_valid(S_R, ' + resume + ')',
        'S_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_R.ERRORHANDLER.LEVELS = ' + ('512' if facts['masked'] else '30719'),
        ('~' if facts['masked'] else '') + '$error_handler_eligible(S_R, 2)',
        r'S_R.REQUEST = eps /\ S_R.CURRENT = eps /\ S_R.FRAMES = eps /\ S_R.HELD = eps',
        r'S_R.SOURCEPENDING = eps /\ S_R.CONSTCONTEXT = eps',
        'S_R.RESULT = KNOWN PNULL',
        'S_R.REPORTING = 30719',
        '$display_state_mode(S_R) = 2',
        'S_R.OUTPUTBUFFERS = eps',
        'S_R.ERRORFATALTRACE = eps',
        '$arithmetic_add_named(S_R)',
        '~$eval_compile_recorded_error(S_R, 2)',
        '~$recorded_runtime_pending(S_R, 2)',
        '$integer_float_notices([RANGEWARNING], n_bits) = [(2, n_message*)]',
        'n_message* = ' + seek.term(facts['message']),
        '$review_cv_outputs(S_R.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        *seek.public('S_R'),
    ]
    if not PRELAW:
        return postconditions(checks, pending, resume)
    checks += [
        '~$string_unset_bool_cv_post_value(PFLOAT n_bits)',
        '~$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_cv_range_bits(n_bits)',
        '~$string_unset_cv_range_snapshot(S_R, porigin_site, z, n_key, n_bits)',
        '$string_unset_cv_range_plan(S_R) = eps',
        '~$string_unset_cv_range_discard(S_R, ' + resume + ')',
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
    return checks, 0


def postconditions(checks, pending, resume):
    checks += [
        '$string_unset_bool_cv_post_value(PFLOAT n_bits)',
        '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_bits(n_bits)',
        '$string_unset_cv_range_snapshot(S_R, porigin_site, z, n_key, n_bits)',
        'ptask_range = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits',
        '$task_nodes(ptask_range) = eps',
        '$call_task_valid(S_R, ptask_range)',
        'pevent_range = DIAGNOSTIC "Warning" n_message* z',
    ]
    if pending:
        checks += [
            '~$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
            '$string_unset_cv_range_discard(S_R, ' + resume + ')',
            '$string_unset_cv_range_plan(S_R) = eps',
            'S_next = S_R[.EVENTS = S_R.EVENTS ++ [pevent_range]]',
            '$error_read_discard(S_R, ' + resume + ') = S_next',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_next',
            'PhpStep: S_P ~> S_next',
            'S_next.TODO = (THROW_SEARCH n_exception) :: ptask_after*',
            'S_next.OBJECTS[n_exception] = S_P.OBJECTS[n_exception]',
            '$drive_steps(S_P, 1) = S_next[.COMPLETION = BUDGET]',
        ]
    else:
        checks += [
            '$string_unset_cv_range_plan(S_R) = ((porigin_site, z, n_key, n_bits))',
            'PhpStep: S_R ~> S_next',
            'S_next.TODO = (ERROR_HANDLER_INVOKE perrorcall_range) :: ptask_after*',
            'S_next = S_R[.TODO = (ERROR_HANDLER_INVOKE perrorcall_range) :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps]',
            'perrorcall_range.SITE = porigin_site',
            'perrorcall_range.LINE = z',
            'perrorcall_range.LEVEL = 2',
            'perrorcall_range.MESSAGE = n_message*',
            'perrorcall_range.EVENT = pevent_range',
            'perrorcall_range.CALLBACK = pvalue_callback',
            'perrorcall_range.RESUME = ptask_range',
            'perrorcall_range.TARGET = eps',
            '$error_call_valid(S_next, perrorcall_range)',
            '$drive_steps(S_R, 1) = S_next[.COMPLETION = BUDGET]',
            'S_D_found = $review_range_seek(S_next, "discard", 1000)',
            '$review_range_at(S_D_found, "discard")',
            'S_D = $review_cv_running(S_D_found)',
            'S_D.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_second) :: ptask_after*',
            'perrorcall_second.RESUME = ptask_range',
            'perrorcall_second.TARGET = (pcalltarget)',
            'S_D.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("done")))',
            '~$string_unset_cv_range_snapshot(S_D, porigin_site, z, n_key, n_bits)',
            '$error_call_valid(S_D, perrorcall_second)',
            '$call_task_valid(S_D, ptask_range)',
            'S_D.OBJECTS[n_second] = THROWABLE pthrowable_second',
            'pthrowable_second.KIND = "Exception"',
            '$throwable_field(S_D, n_second, "message") = PSTRING_CARRIER INTERNED_STRING ($ptascii("range"))',
            '$throwable_field(S_D, n_second, "line") = PINT 2',
            'PhpStep: S_D ~> S_second_next',
            'S_second_next = S_D[.TODO = (THROW_SEARCH n_second) :: ptask_after*][.ERRORHANDLER.CALLBACK = (pvalue_callback)]',
            '$heap_graph(S_second_next) = $heap_graph(S_D)',
            '$drive_steps(S_D, 1) = S_second_next[.COMPLETION = BUDGET]',
            '$drive_steps(S_second_next, 2000) = $drive_steps(S_next, 3000)',
        ]
    checks += [
        '$heap_graph(S_next) = $heap_graph(S_R)',
        *seek.public('S_next'),
        '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]',
        'S_DONE = $drive_steps(S_next, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        r'S_DONE.CODE = S_R.CODE /\ S_DONE.POOLS = S_R.POOLS',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + seek.term(cases.OUTPUTS[tuple(cases.CASES)[INDEX]]),
        *seek.public('S_DONE'),
        '$drive_steps(S_E, 5000) = S_DONE',
    ]
    if pending:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    reached = len(checks)
    for bits in (9218868437227405312, 18442240474082181120,
                 9218868437227405313, 9221120237041090560,
                 18444492273895866368, 18446744073709551615):
        checks += ['$string_unset_bool_cv_post_value(PFLOAT ' + str(bits) + ')',
            '~$string_unset_bool_cv_post_normal_value(PFLOAT ' + str(bits) + ')',
            '$string_unset_cv_range_bits(' + str(bits) + ')']
    for changed in ('S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
                    'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
                    'S_R[.STORE[n_key] = UNDEFINED]',
                    'S_R[.STORE[n_key] = DEFINED (PFLOAT 18446744073709551616)]',
                    'S_R[.CODE = eps]'):
        checks.append('~$string_unset_cv_range_snapshot(' + changed + ', porigin_site, z, n_key, n_bits)')
    checks += ['~$string_unset_bool_cv_post_value(PFLOAT 18446744073709551616)',
        '~$string_unset_cv_range_bits(18446744073709551616)']
    if pending:
        checks += ['S_eligible = S_R[.ERRORHANDLER.LEVELS = 30719]',
            '$string_unset_bool_cv_post_discard_cell(S_eligible, n_key_name*, z_key, n_key)',
            '~$string_unset_cv_range_discard(S_eligible, ' + resume + ')',
            '$error_read_discard(S_eligible, ' + resume + ') = S_eligible']
    else:
        checks += ['~$error_call_valid(S_next, perrorcall_range[.LINE = $(z + 1)])',
            '~$error_call_valid(S_next, perrorcall_range[.MESSAGE = $ptascii("forged")])',
            '~$error_call_valid(S_next[.STORE[n_key] = DEFINED (PINT 7)], perrorcall_range)',
            '~$error_call_valid(S_D, perrorcall_second[.TARGET = eps])']
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 5)
    name = tuple(cases.CASES)[INDEX]
    watched = [Path(__file__), Path(seek.__file__), Path(sl.__file__),
               Path(range_peer.__file__), Path(range_peer.shared.__file__),
               *[runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions, runner.PREFIX, runner.recorded = cases, conditions, range_peer.PREFIX, sl.recorded
    passed = runner.main(expected_stderr=lambda path: cases.stderr(name, path))
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent actual nonfinite ordinary CV, exact compiled source/read, zero owners, '
        'raw negative-infinity bits and genuine normal or masked pending continuation precede old Unsupported. '
        'No new admission guard establishes reachability; source0/native0.' if PRELAW else
        'Independent source-reached copied nonfinite Warning with selected secondary throw or masked '
        'pending Exception. Exact full states, original caller tails, raw-bit/source/cell/task guard '
        'controls and whole/split budget checks retain source0/native0.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
