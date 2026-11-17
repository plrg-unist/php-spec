#!/usr/bin/env python3
"""Source-reached nonfinite CV conversion, copied bits and pending exception."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as shared
import string_offset_nested_unset_bool_cv_range_warning_protocol as normal
import string_offset_nested_unset_bool_cv_range_warning_review_state as second
import string_offset_nested_unset_bool_cv_nonfinite_post_cases as cases

INDEX = 0
PRELAW = False
PREFIX = normal.PREFIX + second.PREFIX[len(second.shared.PREFIX):]


def front(program, path):
    name = tuple(cases.CASES)[INDEX]
    facts = cases.FACTS[name]
    pending = facts['mode'] == 'first-throw'
    stage = 'discard' if pending else 'resume'
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
    if pending:
        checks += [
            'S_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = perrorcall_first.RESUME',
            'S_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            '$throwable_field(S_P, n_throwable, "message") = PSTRING_CARRIER INTERNED_STRING ($ptascii("handler"))',
            '$throwable_field(S_P, n_throwable, "line") = PINT 2',
            'S_cut = S_P[.TODO = (THROW_SEARCH n_throwable) :: ptask_after*]',
            '$identity_read_discard(S_cut, perrorcall_entered.RESUME) = S_cut',
            'S_R = $error_handler_restore(S_cut, pvalue_callback)',
            'S_R.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
        ]
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
        'n_bits = ' + str(facts['bits']),
        'S_R.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$(n_bits < 18446744073709551616)',
        '~$fparts_fits($float_decode(n_bits))',
        '$float_decode(n_bits) = ' + ('NOTNUMBER n_bits' if b'NAN' in facts['message'] else 'INFINITE ' + str(facts['bits'] >> 63)),
        '$resolve_at(S_R, VARIABLE n_key_name* z_key, z_key) = S_R[.RESULT = KNOWN (PFLOAT n_bits)]',
        '$call_task_valid(S_R, perrorcall_first.RESUME)',
        'S_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_R.ERRORHANDLER.LEVELS = ' + ('512' if facts['masked'] else '30719'),
        ('$error_handler_eligible' if not facts['masked'] else '~$error_handler_eligible') + '(S_R, 2)',
        r'S_R.REQUEST = eps /\ S_R.CURRENT = eps /\ S_R.FRAMES = eps /\ S_R.HELD = eps',
        r'S_R.SOURCEPENDING = eps /\ S_R.CONSTCONTEXT = eps',
        'S_R.RESULT = KNOWN PNULL',
        'S_R.DISPLAYINI = ($ptascii("stderr"))',
        'S_R.REPORTING = 30719',
        'S_R.OUTPUTBUFFERS = eps',
        'S_R.ERRORFATALTRACE = eps',
        '$arithmetic_add_named(S_R)',
        '~$eval_compile_recorded_error(S_R, 2)',
        '~$recorded_runtime_pending(S_R, 2)',
        '$integer_float_notices([RANGEWARNING], n_bits) = [(2, n_message*)]',
        'n_message* = ' + shared.term(facts['message']),
        'pevent_range = DIAGNOSTIC "Warning" n_message* z',
        '$review_cv_outputs(S_R.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        *shared.public('S_R'),
    ]
    return checks


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    facts = cases.FACTS[name]
    pending = facts['mode'] == 'first-throw'
    checks = front(program, path)
    if PRELAW:
        checks += ['~$string_unset_bool_cv_post_value(PFLOAT n_bits)',
            '~$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
            '$string_unset_cv_range_plan(S_R) = eps']
        if pending:
            checks += ['~$string_unset_cv_range_discard(S_R, perrorcall_first.RESUME)',
                'PhpStep: S_P ~> S_old',
                'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        else:
            checks += ['PhpStep: S_R ~> S_old',
                'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        return checks, 0
    checks += ['$string_unset_bool_cv_post_value(PFLOAT n_bits)',
        '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_bits(n_bits)',
        '$string_unset_cv_range_snapshot(S_R, porigin_site, z, n_key, n_bits)']
    if pending:
        checks += [
            ('$string_unset_bool_cv_post_discard_cell' if not facts['masked'] else '~$string_unset_bool_cv_post_discard_cell') + '(S_R, n_key_name*, z_key, n_key)',
            ('$string_unset_cv_range_discard' if facts['masked'] else '~$string_unset_cv_range_discard') + '(S_R, perrorcall_first.RESUME)',
            'S_next = S_R' + ('[.EVENTS = S_R.EVENTS ++ [pevent_range]]' if facts['masked'] else ''),
            '$error_read_discard(S_R, perrorcall_first.RESUME) = S_next',
            'PhpStep: S_P ~> S_next',
            'S_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]',
            '$heap_graph(S_next) = $heap_graph(S_R)',
            '$drive_steps(S_P, 1) = S_next[.COMPLETION = BUDGET]',
        ]
    else:
        checks += ['$string_unset_cv_range_plan(S_R) = ((porigin_site, z, n_key, n_bits))',
            'ptask_range = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits',
            '$task_nodes(ptask_range) = eps',
            'PhpStep: S_R ~> S_next']
        if facts['masked']:
            checks += ['S_next = S_R[.TODO = ptask_range :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps][.EVENTS = S_R.EVENTS ++ [pevent_range]]']
        else:
            checks += ['S_next.TODO = (ERROR_HANDLER_INVOKE perrorcall_range) :: ptask_after*',
                'S_next = S_R[.TODO = (ERROR_HANDLER_INVOKE perrorcall_range) :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps]',
                'perrorcall_range.RESUME = ptask_range',
                r'perrorcall_range.SITE = porigin_site /\ perrorcall_range.LINE = z /\ perrorcall_range.LEVEL = 2',
                'perrorcall_range.MESSAGE = n_message*',
                'perrorcall_range.EVENT = pevent_range',
                'perrorcall_range.CALLBACK = pvalue_callback',
                'perrorcall_range.TARGET = eps',
                '$error_call_valid(S_next, perrorcall_range)',
                '~$error_call_valid(S_next[.STORE[n_key] = DEFINED (PINT 7)], perrorcall_range)',
                '~$error_call_valid(S_next, perrorcall_range[.LINE = $(z + 1)])',
                '~$error_call_valid(S_next, perrorcall_range[.MESSAGE = $ptascii("forged")])']
        checks += ['$heap_graph(S_next) = $heap_graph(S_R)',
            '$drive_steps(S_R, 1) = S_next[.COMPLETION = BUDGET]']
        if facts['mode'] == 'second-throw':
            checks += ['S_D_found = $review_range_seek(S_next, "discard", 1000)',
                '$review_range_at(S_D_found, "discard")',
                'S_D = $review_cv_running(S_D_found)',
                'S_D.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_second) :: ptask_after*',
                'perrorcall_second.RESUME = ptask_range',
                'perrorcall_second.TARGET = (pcalltarget)',
                'S_D.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("done")))',
                '~$string_unset_cv_range_snapshot(S_D, porigin_site, z, n_key, n_bits)',
                '$error_call_valid(S_D, perrorcall_second)',
                '~$error_call_valid(S_D, perrorcall_second[.TARGET = eps])',
                '$call_task_valid(S_D, ptask_range)',
                'S_D.OBJECTS[n_second] = THROWABLE pthrowable_second',
                'pthrowable_second.KIND = "Exception"',
                '$throwable_field(S_D, n_second, "message") = PSTRING_CARRIER INTERNED_STRING ($ptascii("range"))',
                'PhpStep: S_D ~> S_second_next',
                'S_second_next = S_D[.TODO = (THROW_SEARCH n_second) :: ptask_after*][.ERRORHANDLER.CALLBACK = (pvalue_callback)]',
                '$drive_steps(S_second_next, 2000) = $drive_steps(S_next, 3000)']
    checks += [*shared.public('S_next'),
        '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]',
        'S_DONE = $drive_steps(S_next, 3000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        r'S_DONE.CODE = S_R.CODE /\ S_DONE.POOLS = S_R.POOLS',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + shared.term(cases.OUTPUTS[name]),
        *shared.public('S_DONE'),
        '$drive_steps(S_E, 5000) = S_DONE']
    if pending:
        checks += ['S_DONE.OBJECTS[n_throwable] = S_R.OBJECTS[n_throwable]']
    reached = len(checks)
    if facts['mode'] == 'second-throw':
        checks += ['S_unbound = $unset_name(S_D, n_key_name*)',
            '$lookup(S_unbound.ENV, n_key_name*) = eps',
            '$heap_valid($heap_graph(S_unbound))',
            '$call_task_valid(S_unbound, ptask_range)',
            '$error_call_valid(S_unbound, perrorcall_second)',
            '$error_call_valid(S_D[.STORE[n_key] = UNDEFINED], perrorcall_second)',
            '~$error_call_valid(S_unbound, perrorcall_second[.TARGET = eps])']
    for bits in (9218868437227405312, 18442240474082181120, 9218868437227405313,
                 9221120237041090560, 18444492273895866368, 18446744073709551615):
        checks += ['$string_unset_bool_cv_post_value(PFLOAT ' + str(bits) + ')',
            '~$string_unset_bool_cv_post_normal_value(PFLOAT ' + str(bits) + ')',
            '$string_unset_cv_range_bits(' + str(bits) + ')']
    for changed in ('S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
                    'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
                    'S_R[.STORE[n_key] = UNDEFINED]',
                    'S_R[.STORE[n_key] = DEFINED (POBJECT 0)]',
                    'S_R[.STORE[n_key] = DEFINED (PFLOAT 18446744073709551616)]'):
        checks.append('~$string_unset_cv_range_snapshot(' + changed + ', porigin_site, z, n_key, n_bits)')
    checks += ['~$string_unset_bool_cv_post_value(PFLOAT 18446744073709551616)',
        '~$string_unset_cv_range_bits(18446744073709551616)']
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    name = tuple(cases.CASES)[INDEX]
    watched = [Path(__file__), Path(shared.__file__), Path(sl.__file__), Path(normal.__file__), Path(second.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions, runner.PREFIX, runner.recorded = cases, conditions, PREFIX, sl.recorded
    passed = runner.main(expected_stderr=lambda path: cases.stderr(name, path))
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Source-reached saved ordinary nonfinite CV, exact bits/read/source and actual normal or pending continuation precede old Unsupported. Source0/native0.' if PRELAW else
        'Source-reached nonfinite range Warning retains copied bits, saved ordinary cell and whole caller tail. Actual normal/secondary throw and eligible/masked first throw remain separate; raw bit and source/cell/task forgeries have source0/native0.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
