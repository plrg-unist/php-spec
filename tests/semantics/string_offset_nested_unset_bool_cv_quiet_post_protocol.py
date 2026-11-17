#!/usr/bin/env python3
"""Reached quiet post-handler values keep the captured ordinary Boolean CV slot."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from encoding_declare_protocol import public
import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as seek
import string_offset_nested_unset_bool_cv_quiet_post_cases as cases

INDEX = 0
term = lambda data: '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def front_checks(program, path):
    name = tuple(cases.CASES)[INDEX]
    throwing = INDEX >= 2
    post = cases.POST_VALUES[name]
    stage = 'discard' if throwing else 'resume'
    return [
        'S_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_I.COMPLETION = BUDGET',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_E.ENV, n_key_name*) = (n_key)',
        'S_E.STORE[n_key] = DEFINED (PBOOL ' + str(not throwing).lower() + ')',
        '$string_unset_bool_cv_cell(S_E, n_key_name*, z_key, n_key)',
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$task_nodes(STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = eps',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_A, perrorcall)',
        'S_P_found = $review_cv_seek(S_A, "' + stage + '", 1000)',
        '$review_cv_at(S_P_found, "' + stage + '")',
        'S_P = $review_cv_running(S_P_found)',
        '$string_unset_bool_cv_source(S_P, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_P.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_P.STORE|)',
        '~$environment_blocked(S_P, n_key_name*)',
        '~(n_key <- S_P.REFCELLS)',
        '~$foreach_released_cell(S_P, n_key)',
        '~$typed_cv_string_released_cell(S_P, n_key)',
        '~$update_released_cell(S_P, n_key)',
        'pvalue_post = ' + post,
        'S_P.STORE[n_key] = DEFINED pvalue_post',
        '$resolve_at(S_P, VARIABLE n_key_name* z_key, z_key) = S_P[.RESULT = KNOWN pvalue_post]',
        'S_P.HELD = S_E.HELD',
        *public('S_P'),
    ]


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    throwing = INDEX >= 2
    checks = front_checks(program, path) + [
        '~$string_unset_bool_cv_cell(S_P, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_cell(S_P, n_key_name*, z_key, n_key)',
        '$call_task_valid(S_P, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
    ]
    if throwing:
        checks += [
            'S_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
            'S_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_P.ERRORHANDLER.CALLBACK = eps',
            '$error_read_discard(S_P, perrorcall_entered.RESUME) = S_P',
            'S_next_budget = $drive_steps(S_P, 1)',
            'S_next_budget.COMPLETION = BUDGET',
            'S_next = $review_cv_running(S_next_budget)',
            'S_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'S_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]',
            'S_next.STORE = S_P.STORE',
            'S_next.EVENTS = S_P.EVENTS',
            'S_next.HELD = S_P.HELD',
        ]
    else:
        checks += [
            'S_P.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
            'S_P.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'PhpStep: S_P ~> S_error',
            'S_error = S_P[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
        ]
    checks += [
        'S_DONE = $drive_steps(S_P, 2000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps',
        'S_DONE.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + term(cases.OUTPUTS[name]),
        *public('S_DONE'),
        '$drive_steps(S_E, 2000) = S_DONE',
        '$drive_steps(S_A, 2000) = S_DONE',
    ]
    reached = len(checks)
    for tag, value in (('null', 'PNULL'), ('false', '(PBOOL false)'),
                       ('true', '(PBOOL true)'), ('minimum', '(PINT (-9223372036854775808))'),
                       ('zero', '(PINT 0)'), ('maximum', '(PINT 9223372036854775807)')):
        state = 'S_post_' + tag
        checks += [state + ' = S_P[.STORE[n_key] = DEFINED ' + value + ']',
            '$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)']
        if throwing:
            checks += ['$error_read_discard(' + state + ', perrorcall_entered.RESUME) = ' + state]
        else:
            checks += ['PhpStep: ' + state + ' ~> ' + state + '_error',
                state + '_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
                state + '_error.EVENTS = ' + state + '.EVENTS']
    checks += ['n_rebound = |S_P.STORE|']
    for tag, changed in (
        ('absent', 'S_P[.ENV = $unbind(S_P.ENV, n_key_name*)]'),
        ('undefined', 'S_P[.STORE[n_key] = UNDEFINED]'),
        ('reference', 'S_P[.REFCELLS = S_P.REFCELLS ++ [n_key]]'),
        ('overflow', 'S_P[.STORE[n_key] = DEFINED (PINT 9223372036854775808)]'),
        ('underflow', 'S_P[.STORE[n_key] = DEFINED (PINT (-9223372036854775809))]'),
        ('float', 'S_P[.STORE[n_key] = DEFINED (PFLOAT 4607182418800017408)]'),
        ('string', 'S_P[.STORE[n_key] = DEFINED (PSTRING ($ptascii("7")))]'),
        ('array', 'S_P[.STORE[n_key] = DEFINED (PARRAY 0)]'),
        ('object', 'S_P[.STORE[n_key] = DEFINED (POBJECT 0)]'),
        ('rebound', 'S_P[.ENV = (BIND n_key_name* n_rebound) :: $unbind(S_P.ENV, n_key_name*)][.STORE = S_P.STORE ++ [DEFINED pvalue_post]][.ALLOCATIONS = S_P.ALLOCATIONS ++ [HCELL n_rebound]]'),
    ):
        state = 'S_unsafe_' + tag
        checks += [state + ' = ' + changed,
            '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
            '$call_task_valid(' + state + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
            'PhpStep: ' + state + ' ~> ' + state + '_next',
            state + '_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
            state + '_next.EVENTS = ' + state + '.EVENTS',
            state + '_next.STORE = ' + state + '.STORE',
            state + '_next.HELD = ' + state + '.HELD',
            state + '_next.ENV = ' + state + '.ENV']
        if throwing:
            checks += [state + '_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
                state + '_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]']
        if tag == 'rebound':
            checks += ['$heap_valid($heap_graph(' + state + '))',
                '$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_rebound)']
    return checks, len(checks) - reached


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(seek.__file__), Path(sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1, 2, 3)
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = seek.PREFIX, sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Actual post-handler NULL/INT retains the saved ordinary cell, no reference/released marker, '
        'and a whole-state quiet read; exact Error or same pending Exception, restored callback, whole/split '
        'equality and bounded quiet-value/cell refusals. Fixture source0/native0, saved originals reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
