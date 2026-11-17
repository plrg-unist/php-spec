#!/usr/bin/env python3
"""Independent saved-CV fronts and finite-FLOAT Warning resume checks."""
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
import string_offset_nested_unset_bool_cv_float_post_cases as cases

INDEX = 1
FRONT_ONLY = False
RANGE_ONLY = False
PENDING_ONLY = False
term = lambda data: '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'
PREFIX = seek.PREFIX + r'''
dec $float_post_output(pevent) : bool
def $float_post_output(OUTPUT n*) = true
def $float_post_output(pevent) = false -- otherwise
dec $float_post_diagnostics(pevent*) : pevent*
def $float_post_diagnostics(eps) = eps
def $float_post_diagnostics((OUTPUT n*) :: pevent_tail*) = $float_post_diagnostics(pevent_tail*)
def $float_post_diagnostics(pevent :: pevent_tail*) = pevent :: $float_post_diagnostics(pevent_tail*)
  -- if ~$float_post_output(pevent)
'''


def front(program, path):
    name = tuple(cases.CASES)[INDEX]
    throwing = INDEX == 1
    stage = 'discard' if throwing else 'resume'
    return [
        'S_float_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_float_I.COMPLETION = BUDGET',
        'S_float_E_found = $review_cv_seek(S_float_I, "entry", 1000)',
        '$review_cv_at(S_float_E_found, "entry")',
        'S_float_E = $review_cv_running(S_float_E_found)',
        '$string_unset_bool_cv_plan(S_float_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_float_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_float_E.ENV, n_key_name*) = (n_key)',
        'S_float_E.STORE[n_key] = DEFINED (PBOOL ' + str(not throwing).lower() + ')',
        '$string_unset_bool_cv_cell(S_float_E, n_key_name*, z_key, n_key)',
        'S_float_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$task_nodes(STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = eps',
        'PhpStep: S_float_E ~> S_float_A',
        'S_float_A.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_float_A, perrorcall)',
        'S_float_A.STORE = S_float_E.STORE',
        'S_float_A.HELD = S_float_E.HELD',
        '$heap_graph(S_float_A) = $heap_graph(S_float_E)',
        'S_float_P_found = $review_cv_seek(S_float_A, "' + stage + '", 1000)',
        '$review_cv_at(S_float_P_found, "' + stage + '")',
        'S_float_P = $review_cv_running(S_float_P_found)',
        '$lookup(S_float_P.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_float_P.STORE|)',
        '~$environment_blocked(S_float_P, n_key_name*)',
        '~(n_key <- S_float_P.REFCELLS)',
        '~$foreach_released_cell(S_float_P, n_key)',
        '~$typed_cv_string_released_cell(S_float_P, n_key)',
        '~$update_released_cell(S_float_P, n_key)',
        'pvalue_float = ' + cases.POST_VALUES[name],
        'S_float_P.STORE[n_key] = DEFINED pvalue_float',
        '$resolve_at(S_float_P, VARIABLE n_key_name* z_key, z_key) = S_float_P[.RESULT = KNOWN pvalue_float]',
        'pvalue_float = PFLOAT n_bits',
        '$(n_bits < 18446744073709551616)',
        '$float_decode(n_bits) = FINITE n_sign n_num n_den',
        'S_float_P.HELD = S_float_E.HELD',
        '$review_cv_outputs(S_float_P.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        '$float_post_diagnostics(S_float_P.EVENTS) = eps',
        *public('S_float_P'),
    ]


def normal_range_checks():
    checks = []
    for bits in (4890909195324358656, 14114281232179134465, 9218868437227405311):
        state = 'S_float_range_' + str(bits)
        checks += [state + ' = S_float_P[.STORE[n_key] = DEFINED (PFLOAT ' + str(bits) + ')]',
            '$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_value(PFLOAT ' + str(bits) + ')',
            '~$string_unset_bool_cv_post_normal_cell(' + state + ', n_key_name*, z_key, n_key)',
            '$string_unset_cv_range_plan(' + state + ') = ((porigin_site, z, n_key, ' + str(bits) + '))',
            'PhpStep: ' + state + ' ~> ' + state + '_next',
            state + '_next.TODO = (ERROR_HANDLER_INVOKE perrorcall_range_' + str(bits) + ') :: ptask_after*',
            'perrorcall_range_' + str(bits) + '.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key ' + str(bits),
            '$error_call_valid(' + state + '_next, perrorcall_range_' + str(bits) + ')',
            state + '_next.STORE = ' + state + '.STORE',
            state + '_next.EVENTS = ' + state + '.EVENTS',
            state + '_next.HELD = ' + state + '.HELD']
    return checks


def pending_mask_checks():
    checks = ['$integer_float_notices([RANGEWARNING], 4906019910204099648) = [(2, n_range_message*)]',
        'pevent_pending_range = DIAGNOSTIC "Warning" n_range_message* z']
    for mask in (0, 512):
        state = 'S_float_range_mask_' + str(mask)
        checks += [state + ' = S_float_R[.ERRORHANDLER.LEVELS = ' + str(mask) + ']',
            '~$string_unset_bool_cv_post_discard_cell(' + state + ', n_key_name*, z_key, n_key)',
            '$string_unset_cv_range_discard(' + state + ', perrorcall_entered.RESUME)',
            '$error_read_discard(' + state + ', perrorcall_entered.RESUME) = ' + state + '[.EVENTS = ' + state + '.EVENTS ++ [pevent_pending_range]]']
    return checks


def conditions(program, path):
    checks = front(program, path)
    if FRONT_ONLY:
        return checks, 0
    if PENDING_ONLY:
        assert INDEX == 1
        checks += [
            'S_float_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
            'S_float_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_float_P.ERRORHANDLER.CALLBACK = eps',
            'PhpStep: S_float_P ~> S_float_next',
            'S_float_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_float_next.ERRORHANDLER = S_float_E.ERRORHANDLER',
            'S_float_next.OBJECTS[n_throwable] = S_float_P.OBJECTS[n_throwable]',
            'S_float_next.EVENTS = S_float_P.EVENTS',
            'S_float_R = S_float_next[.STORE[n_key] = DEFINED (PFLOAT 4906019910204099648)]',
            'S_float_R.RESULT = KNOWN PNULL',
        ]
        changed = pending_mask_checks()
        return checks + changed, len(changed)
    if RANGE_ONLY:
        assert INDEX == 2
        changed = normal_range_checks()
        return checks + [
            'S_float_P.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
            'S_float_P.ERRORHANDLER = S_float_E.ERRORHANDLER',
        ] + changed, len(changed)
    name = tuple(cases.CASES)[INDEX]
    throwing = INDEX == 1
    checks += [
        '~$string_unset_bool_cv_cell(S_float_P, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_value(pvalue_float)',
        '$string_unset_bool_cv_post_cell(S_float_P, n_key_name*, z_key, n_key)',
        '$call_task_valid(S_float_P, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
    ]
    if throwing:
        checks += [
            'S_float_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
            'S_float_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_float_P.ERRORHANDLER.CALLBACK = eps',
            '$error_read_discard(S_float_P, perrorcall_entered.RESUME) = S_float_P',
            'PhpStep: S_float_P ~> S_float_next',
            'S_float_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_float_next.ERRORHANDLER = S_float_E.ERRORHANDLER',
            'S_float_next.OBJECTS[n_throwable] = S_float_P.OBJECTS[n_throwable]',
            'S_float_next.STORE = S_float_P.STORE',
            'S_float_next.EVENTS = S_float_P.EVENTS',
            'S_float_next.HELD = S_float_P.HELD',
            *public('S_float_next'),
        ]
    else:
        checks += [
            'S_float_P.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
            'S_float_P.ERRORHANDLER = S_float_E.ERRORHANDLER',
            'PhpStep: S_float_P ~> S_float_error',
            'S_float_error = S_float_P[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
        ]
    reached = len(checks)
    checks += ['$string_unset_bool_cv_post_normal_cell(S_float_P, n_key_name*, z_key, n_key)']
    for bits in (4890909195324358655, 14114281232179134464):
        checks += ['$string_unset_bool_cv_post_normal_value(PFLOAT ' + str(bits) + ')',
            '$string_unset_bool_cv_post_normal_cell(S_float_P[.STORE[n_key] = DEFINED (PFLOAT ' + str(bits) + ')], n_key_name*, z_key, n_key)']
    if throwing:
        checks += [
            'S_float_fit_mask = S_float_P[.ERRORHANDLER.LEVELS = 0]',
            '$string_unset_bool_cv_post_discard_cell(S_float_fit_mask, n_key_name*, z_key, n_key)',
            'PhpStep: S_float_fit_mask ~> S_float_fit_mask_next',
            'S_float_fit_mask_next = S_float_next[.ERRORHANDLER.LEVELS = 0]',
            'S_float_R = S_float_next[.STORE[n_key] = DEFINED (PFLOAT 4906019910204099648)]',
            '$string_unset_bool_cv_post_cell(S_float_R, n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(S_float_R, n_key_name*, z_key, n_key)',
            '$string_unset_bool_cv_post_discard_cell(S_float_R, n_key_name*, z_key, n_key)',
            '$error_read_discard(S_float_R, perrorcall_entered.RESUME) = S_float_R',
            'n_no_throwable = |S_float_R.OBJECTS|',
        ]
        checks += pending_mask_checks()
        for tag, changed in (
            ('no_callback', 'S_float_R[.ERRORHANDLER.CALLBACK = eps]'),
            ('budget', 'S_float_R[.COMPLETION = BUDGET]'),
            ('no_throw', 'S_float_R[.TODO = eps]'),
            ('object_bound', 'S_float_R[.TODO = [THROW_SEARCH n_no_throwable]]'),
            ('object_kind', 'S_float_R[.OBJECTS[n_throwable] = THROWABLE pthrowable[.KIND = "stdClass"]]'),
        ):
            state = 'S_float_range_' + tag
            checks += [state + ' = ' + changed,
                '~$string_unset_bool_cv_post_discard_cell(' + state + ', n_key_name*, z_key, n_key)',
                '$error_read_discard(' + state + ', perrorcall_entered.RESUME) = ' + state + '[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    else:
        checks += normal_range_checks()
    for bits in (0, 1, 9223372036854775808, 9223372036854775809,
                 9218868437227405311, 18442240474082181119):
        checks += ['$string_unset_bool_cv_post_value(PFLOAT ' + str(bits) + ')',
            '$string_unset_bool_cv_post_cell(S_float_P[.STORE[n_key] = DEFINED (PFLOAT ' + str(bits) + ')], n_key_name*, z_key, n_key)']
    changes = [
        ('nonfinite_' + str(bits), 'S_float_P[.STORE[n_key] = DEFINED (PFLOAT ' + str(bits) + ')]')
        for bits in (9218868437227405312, 18442240474082181120,
                     9218868437227405313, 18444492273895866368, 18446744073709551616)
    ]
    checks += ['n_rebound = |S_float_P.STORE|']
    changes += [
        ('absent', 'S_float_P[.ENV = $unbind(S_float_P.ENV, n_key_name*)]'),
        ('undefined', 'S_float_P[.STORE[n_key] = UNDEFINED]'),
        ('reference', 'S_float_P[.REFCELLS = S_float_P.REFCELLS ++ [n_key]]'),
        ('owning', 'S_float_P[.STORE[n_key] = DEFINED (POBJECT 0)]'),
        ('rebound', 'S_float_P[.ENV = (BIND n_key_name* n_rebound) :: $unbind(S_float_P.ENV, n_key_name*)][.STORE = S_float_P.STORE ++ [DEFINED pvalue_float]][.ALLOCATIONS = S_float_P.ALLOCATIONS ++ [HCELL n_rebound]]'),
    ]
    for tag, changed in changes:
        state = 'S_float_bad_' + tag
        checks += [state + ' = ' + changed,
            '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
            '$call_task_valid(' + state + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)']
        if tag == 'rebound':
            checks += ['$heap_valid($heap_graph(' + state + '))',
                '$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_rebound)']
        checks += ['PhpStep: ' + state + ' ~> ' + state + '_next',
            state + '_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
            state + '_next.STORE = ' + state + '.STORE',
            state + '_next.ENV = ' + state + '.ENV',
            state + '_next.EVENTS = ' + state + '.EVENTS',
            state + '_next.HELD = ' + state + '.HELD']
        if throwing:
            checks += [state + '_next.ERRORHANDLER = S_float_E.ERRORHANDLER',
                state + '_next.OBJECTS[n_throwable] = S_float_P.OBJECTS[n_throwable]']
    derived = len(checks) - reached
    checks += [
        'S_float_DONE = $drive_steps(S_float_P, 2000)',
        'S_float_DONE.COMPLETION = NORMAL',
        'S_float_DONE.TODO = eps',
        'S_float_DONE.ERRORHANDLER = S_float_E.ERRORHANDLER',
        '$review_cv_outputs(S_float_DONE.EVENTS) = ' + term(cases.OUTPUTS[name]),
        '$float_post_diagnostics(S_float_DONE.EVENTS) = eps',
        *public('S_float_DONE'),
        '$drive_steps(S_float_E, 2000) = S_float_DONE',
        '$drive_steps(S_float_A, 2000) = S_float_DONE',
    ]
    return checks, derived


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(seek.__file__), Path(sl.__file__), Path(cases.prior.__file__),
               Path(cases.prior.prior.__file__), Path(cases.prior.prior.null.__file__),
               Path(sys.modules[public.__module__].__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 2)
    FRONT_ONLY = '--front-only' in sys.argv
    if FRONT_ONLY:
        sys.argv.remove('--front-only')
    RANGE_ONLY = '--range-only' in sys.argv
    if RANGE_ONLY:
        sys.argv.remove('--range-only')
        assert INDEX == 2 and not FRONT_ONLY
    PENDING_ONLY = '--pending-only' in sys.argv
    if PENDING_ONLY:
        sys.argv.remove('--pending-only')
        assert INDEX == 1 and not FRONT_ONLY and not RANGE_ONLY
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions, runner.PREFIX = cases, conditions, PREFIX
    runner.recorded = sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent actual saved-cell identity, in-bounds ordinary unreferenced/unreleased '
        'CV and unchanged-state PFLOAT read with exact finite bits, before any finite law.' if FRONT_ONLY else
        'Only two prior pending finite-OOB mask controls now use existing default Warning reporting '
        'without changing their real Throwable or complete pending tail. No closed whole/discard '
        'campaign is renewed. Source0/native0; saved native reused.' if PENDING_ONLY else
        'Only three formerly refused normal finite-OOB controls from the peer negative-zero return '
        'front dispatch copied range Warning tasks with their entire original caller tail. '
        'Closed fitting/discard/whole campaigns are not renewed. Source0/native0; saved native reused.' if RANGE_ONLY else
        'Independent fitting normal PFLOAT resume and finite OOB discard only under a genuine pending '
        'Throwable and restored eligible Warning handler. Exact Error or same Exception, callback/mask '
        'priority, no extra owners/diagnostics and whole/split; eligible normal OOB starts the new '
        'secondary Warning with copied bits and the complete caller tail; pending mask0/512 controls '
        'use default reporting, while forged '
        'pending object/context and nonfinite/out-of-bits/ref/rebind/owning forms refused. Source0/native0.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
