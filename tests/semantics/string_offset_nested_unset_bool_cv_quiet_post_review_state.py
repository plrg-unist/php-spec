#!/usr/bin/env python3
"""Independent quiet NULL/INT post-Warning reads keep the saved physical CV."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from encoding_declare_protocol import public
import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_bool_cv_warning_review_state as seek
import string_offset_nested_unset_bool_cv_quiet_post_cases as cases

INDEX = 1
term = lambda data: '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'
PREFIX = seek.PREFIX + r'''
dec $quiet_post_output_event(pevent) : bool
def $quiet_post_output_event(OUTPUT n*) = true
def $quiet_post_output_event(pevent) = false -- otherwise
dec $quiet_post_diagnostics(pevent*) : pevent*
def $quiet_post_diagnostics(eps) = eps
def $quiet_post_diagnostics((OUTPUT n*) :: pevent_tail*) = $quiet_post_diagnostics(pevent_tail*)
def $quiet_post_diagnostics(pevent :: pevent_tail*) = pevent :: $quiet_post_diagnostics(pevent_tail*)
  -- if ~$quiet_post_output_event(pevent)
'''


def refusals(state, throwing):
    checks = ['n_rebound = |' + state + '.STORE|']
    for tag, changed in (
        ('absent', state + '[.ENV = $unbind(' + state + '.ENV, n_key_name*)]'),
        ('undefined', state + '[.STORE[n_key] = UNDEFINED]'),
        ('reference', state + '[.REFCELLS = ' + state + '.REFCELLS ++ [n_key]]'),
        ('rebound', state + '[.ENV = (BIND n_key_name* n_rebound) :: $unbind(' + state + '.ENV, n_key_name*)][.STORE = ' + state + '.STORE ++ [DEFINED pvalue_post]][.ALLOCATIONS = ' + state + '.ALLOCATIONS ++ [HCELL n_rebound]]'),
    ):
        name = 'S_quiet_' + tag
        checks += [name + ' = ' + changed,
            '~$string_unset_bool_cv_post_cell(' + name + ', n_key_name*, z_key, n_key)',
            '$call_task_valid(' + name + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)']
        if tag == 'rebound':
            checks += ['$heap_valid($heap_graph(' + name + '))',
                '$lookup(' + name + '.ENV, n_key_name*) = (n_rebound)',
                '$string_unset_bool_cv_post_cell(' + name + ', n_key_name*, z_key, n_rebound)']
        checks += ['PhpStep: ' + name + ' ~> ' + name + '_next',
            name + '_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
            name + '_next.STORE = ' + name + '.STORE',
            name + '_next.ENV = ' + name + '.ENV',
            name + '_next.EVENTS = ' + name + '.EVENTS',
            name + '_next.HELD = ' + name + '.HELD']
        if throwing:
            checks += [name + '_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
                name + '_next.OBJECTS[n_throwable] = ' + state + '.OBJECTS[n_throwable]']
    return checks


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    throwing = INDEX == 2
    stage = 'discard' if throwing else 'resume'
    checks = [
        'S_quiet_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_quiet_I.COMPLETION = BUDGET',
        'S_quiet_E_found = $review_cv_seek(S_quiet_I, "entry", 1000)',
        '$review_cv_at(S_quiet_E_found, "entry")',
        'S_quiet_E = $review_cv_running(S_quiet_E_found)',
        '$string_unset_bool_cv_plan(S_quiet_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_quiet_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_quiet_E.ENV, n_key_name*) = (n_key)',
        'S_quiet_E.STORE[n_key] = DEFINED (PBOOL ' + str(not throwing).lower() + ')',
        '$string_unset_bool_cv_cell(S_quiet_E, n_key_name*, z_key, n_key)',
        'S_quiet_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$task_nodes(STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = eps',
        *public('S_quiet_E'),
        '$drive_steps(S_quiet_E, 0) = S_quiet_E[.COMPLETION = BUDGET]',
        'PhpStep: S_quiet_E ~> S_quiet_A',
        'S_quiet_A.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_quiet_A, perrorcall)',
        'S_quiet_A.STORE = S_quiet_E.STORE',
        'S_quiet_A.HELD = S_quiet_E.HELD',
        'S_quiet_A.EVENTS = S_quiet_E.EVENTS',
        '$heap_graph(S_quiet_A) = $heap_graph(S_quiet_E)',
        '$drive_steps(S_quiet_E, 1) = S_quiet_A[.COMPLETION = BUDGET]',
        'S_quiet_P_found = $review_cv_seek(S_quiet_A, "' + stage + '", 1000)',
        '$review_cv_at(S_quiet_P_found, "' + stage + '")',
        'S_quiet_P = $review_cv_running(S_quiet_P_found)',
        '$lookup(S_quiet_P.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_quiet_P.STORE|)',
        '~(n_key <- S_quiet_P.REFCELLS)',
        '~$foreach_released_cell(S_quiet_P, n_key)',
        '~$typed_cv_string_released_cell(S_quiet_P, n_key)',
        '~$update_released_cell(S_quiet_P, n_key)',
        'pvalue_post = ' + cases.POST_VALUES[name],
        'S_quiet_P.STORE[n_key] = DEFINED pvalue_post',
        '$resolve_at(S_quiet_P, VARIABLE n_key_name* z_key, z_key) = S_quiet_P[.RESULT = KNOWN pvalue_post]',
        '~$string_unset_bool_cv_cell(S_quiet_P, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_value(pvalue_post)',
        '$string_unset_bool_cv_post_cell(S_quiet_P, n_key_name*, z_key, n_key)',
        '$call_task_valid(S_quiet_P, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
        'S_quiet_P.HELD = S_quiet_E.HELD',
        '$review_cv_outputs(S_quiet_P.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        '$quiet_post_diagnostics(S_quiet_P.EVENTS) = eps',
        *public('S_quiet_P'),
    ]
    derived = []
    for value in ('PNULL', '(PBOOL true)', '(PBOOL false)', '(PFLOAT 0)', '(PINT (-9223372036854775808))',
                  '(PINT 0)', '(PINT 9223372036854775807)'):
        derived += ['$string_unset_bool_cv_post_value(' + value + ')',
            '$string_unset_bool_cv_post_cell(S_quiet_P[.STORE[n_key] = DEFINED ' + value + '], n_key_name*, z_key, n_key)']
    for value in ('(PINT 9223372036854775808)', '(PINT (-9223372036854775809))',
                  '(PSTRING ($ptascii("7")))', '(PARRAY 0)', '(POBJECT 0)'):
        derived.append('~$string_unset_bool_cv_post_value(' + value + ')')
    for value in ('PNULL', '(PINT 7)'):
        derived += ['$string_unset_bool_cv_plan(S_quiet_E[.STORE[n_key] = DEFINED ' + value + ']) = eps',
            '$string_unset_bool_cv_post_cell(S_quiet_E[.STORE[n_key] = DEFINED ' + value + '], n_key_name*, z_key, n_key)']
    if throwing:
        checks += [
            'S_quiet_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
            'S_quiet_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_quiet_P.ERRORHANDLER.CALLBACK = eps',
            '$error_read_discard(S_quiet_P, perrorcall_entered.RESUME) = S_quiet_P',
            'PhpStep: S_quiet_P ~> S_quiet_next',
            'S_quiet_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_quiet_next.ERRORHANDLER = S_quiet_E.ERRORHANDLER',
            'S_quiet_next.OBJECTS[n_throwable] = S_quiet_P.OBJECTS[n_throwable]',
            'S_quiet_next.STORE = S_quiet_P.STORE',
            'S_quiet_next.EVENTS = S_quiet_P.EVENTS',
            'S_quiet_next.HELD = S_quiet_P.HELD',
            *public('S_quiet_next'),
            'S_quiet_DONE = $drive_steps(S_quiet_next, 2000)',
        ]
    else:
        checks += [
            'S_quiet_P.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
            'S_quiet_P.ERRORHANDLER = S_quiet_E.ERRORHANDLER',
            'PhpStep: S_quiet_P ~> S_quiet_error',
            'S_quiet_error = S_quiet_P[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
            'S_quiet_DONE = $drive_steps(S_quiet_P, 2000)',
        ]
        derived += [
            'S_quiet_no_base = S_quiet_P[.ENV = $unbind(S_quiet_P.ENV, n_base_name*)]',
            '$call_task_valid(S_quiet_no_base, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
            'PhpStep: S_quiet_no_base ~> S_quiet_no_base_error',
            'S_quiet_no_base_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            'S_quiet_no_base_error.ENV = S_quiet_no_base.ENV',
            'S_quiet_no_base_error.STORE = S_quiet_no_base.STORE',
        ]
    derived += refusals('S_quiet_P', throwing)
    checks += derived + [
        'S_quiet_DONE.COMPLETION = NORMAL',
        'S_quiet_DONE.TODO = eps',
        'S_quiet_DONE.ERRORHANDLER = S_quiet_E.ERRORHANDLER',
        '$review_cv_outputs(S_quiet_DONE.EVENTS) = ' + term(cases.OUTPUTS[name]),
        '$quiet_post_diagnostics(S_quiet_DONE.EVENTS) = eps',
        *public('S_quiet_DONE'),
        '$drive_steps(S_quiet_E, 2000) = S_quiet_DONE',
        '$drive_steps(S_quiet_A, 2000) = S_quiet_DONE',
    ]
    return checks, len(derived)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(seek.__file__), Path(cases.prior.__file__), Path(cases.prior.null.__file__),
               Path(sys.modules[public.__module__].__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 2)
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions, runner.PREFIX = cases, conditions, PREFIX
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'AL', 1
    report['scope'] = ('Independent fresh NULL-return/INT-throw source fronts retain current ENV-to-saved-cell '
        'identity, no reference/released marker and exact quiet read. BOOL-only entry and bounded post-value '
        'domains stay distinct; actual normal Error or same Exception, callback restoration, no extra owners, '
        'no second diagnostic, genuinely allocated rebinding refusal and whole/split retain source0/native0. '
        'Saved fresh native4 are reused only; no older BOOL/FLOAT/NaN renewal.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
