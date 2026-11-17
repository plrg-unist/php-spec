#!/usr/bin/env python3
"""Independent live-CV identity, Warning restoration and pending-throw checks."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from encoding_declare_protocol import public
import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_bool_cv_warning_cases as cases

INDEX = 0
term = lambda data: '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'
PREFIX = r'''
dec $review_cv_running(pstate) : pstate
def $review_cv_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $review_cv_running(S) = S -- otherwise
dec $review_cv_at(pstate, text) : bool
def $review_cv_at(S, "entry") = true
  -- if $string_unset_bool_cv_plan($review_cv_running(S)) =/= eps
def $review_cv_at(S, "resume") = true
  -- if S.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin z n_cell) :: ptask_tail*
def $review_cv_at(S, "discard") = true
  -- if S.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin z n_cell
def $review_cv_at(S, text) = false -- otherwise
dec $review_cv_seek(pstate, text, nat) : pstate
def $review_cv_seek(S, text, 0) = S
def $review_cv_seek(S, text, n) = S
  -- if $(n > 0)
  -- if $review_cv_at(S, text) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_cv_seek(S, text, n) = $review_cv_seek($drive_steps($review_cv_running(S), 1), text, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$review_cv_at(S, text)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $review_cv_outputs(pevent*) : nat*
dec $review_cv_output(pevent) : nat*
def $review_cv_output(OUTPUT n*) = n*
def $review_cv_output(pevent) = eps -- otherwise
def $review_cv_outputs(eps) = eps
def $review_cv_outputs(pevent :: pevent_tail*) = $review_cv_output(pevent) ++ $review_cv_outputs(pevent_tail*)
'''


def unsafe_checks(state, throwing):
    checks = ['n_rebound = |' + state + '.STORE|']
    for tag, changed in (
        ('absent', state + '[.ENV = $unbind(' + state + '.ENV, n_key_name*)]'),
        ('undefined', state + '[.STORE[n_key] = UNDEFINED]'),
        ('integer', state + '[.STORE[n_key] = DEFINED (PINT 7)]'),
        ('reference', state + '[.REFCELLS = ' + state + '.REFCELLS ++ [n_key]]'),
        ('rebound', state + '[.ENV = (BIND n_key_name* n_rebound) :: $unbind(' + state + '.ENV, n_key_name*)][.STORE = ' + state + '.STORE ++ [DEFINED (PBOOL true)]][.ALLOCATIONS = ' + state + '.ALLOCATIONS ++ [HCELL n_rebound]]'),
    ):
        name = 'S_cv_' + tag
        checks += [name + ' = ' + changed,
            '~$string_unset_bool_cv_cell(' + name + ', n_key_name*, z_key, n_key)',
            '$call_task_valid(' + name + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)']
        if tag == 'rebound':
            checks += ['$lookup(' + name + '.ENV, n_key_name*) = (n_rebound)',
                '$heap_valid($heap_graph(' + name + '))',
                '$string_unset_bool_cv_cell(' + name + ', n_key_name*, z_key, n_rebound)']
        if throwing:
            checks += ['PhpStep: ' + name + ' ~> ' + name + '_next',
                name + '_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
                name + '_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
                name + '_next.OBJECTS[n_throwable] = ' + state + '.OBJECTS[n_throwable]']
        else:
            checks += ['PhpStep: ' + name + ' ~> ' + name + '_next',
                name + '_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"']
        checks += [name + '_next.EVENTS = ' + name + '.EVENTS',
            name + '_next.STORE = ' + name + '.STORE',
            name + '_next.HELD = ' + name + '.HELD',
            name + '_next.ENV = ' + name + '.ENV']
    return checks


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    throwing = INDEX == 1
    checks = [
        'S_cv_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_cv_I.COMPLETION = BUDGET',
        'S_cv_E_found = $review_cv_seek(S_cv_I, "entry", 1000)',
        '$review_cv_at(S_cv_E_found, "entry")',
        'S_cv_E = $review_cv_running(S_cv_E_found)',
        '$string_unset_bool_cv_plan(S_cv_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_cv_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        'S_cv_E.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base_name* z_base)) (VARIABLE n_key_name* z_key) z) (KNOWN (PINT 7)) z_outer',
        '$lookup(S_cv_E.ENV, n_key_name*) = (n_key)',
        'S_cv_E.STORE[n_key] = DEFINED (PBOOL ' + str(not throwing).lower() + ')',
        '$lookup(S_cv_E.ENV, n_base_name*) = (n_base)',
        '$string_unset_bool_cv_cell(S_cv_E, n_key_name*, z_key, n_key)',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        'porigin_key = PORIGIN 0 pcpath_key',
        '$origin_node(S_cv_E.SOURCES, porigin_key) = (NExprVariable (BYTES text_key) metadata_key)',
        '$base64(text_key) = n_key_name*',
        '$source_line(metadata_key) = z_key',
        '$source_emission_cv(S_cv_E, 0, pcpath_key, NExprVariable (BYTES text_key) metadata_key)',
        '$compiled_read(S_cv_E, porigin_key) = eps',
        '$code_at(S_cv_E.CODE, 0) = (pcode_entry)',
        '$code_expression(pcode_entry.EXPRESSIONS, pcpath_key) = ((z_code_key, false))',
        '$compiled_effects(S_cv_E, porigin_key) = eps',
        'S_cv_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_cv_E.HELD = eps',
        '$task_nodes(STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = eps',
        '$string_unset_warning_pending(S_cv_E)',
        *public('S_cv_E'),
        '$drive_steps(S_cv_E, 0) = S_cv_E[.COMPLETION = BUDGET]',
        'PhpStep: S_cv_E ~> S_cv_A',
        'S_cv_A.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        r'perrorcall.LEVEL = 2 /\ perrorcall.LINE = z',
        'perrorcall.MESSAGE = $ptascii("String offset cast occurred")',
        'S_cv_A.RESULT = KNOWN PNULL',
        'S_cv_A.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_cv_A.LOCATION = NOWHERE',
        r'S_cv_A.STORE = S_cv_E.STORE /\ S_cv_A.HELD = S_cv_E.HELD',
        'S_cv_A.EVENTS = S_cv_E.EVENTS',
        '$heap_graph(S_cv_A) = $heap_graph(S_cv_E)',
        '$drive_steps(S_cv_E, 1) = S_cv_A[.COMPLETION = BUDGET]',
        '$error_call_valid(S_cv_A, perrorcall)',
        '$call_task_valid(S_cv_A, perrorcall.RESUME)',
        '~$error_call_valid(S_cv_A[.ORIGIN = eps], perrorcall)',
        '~$error_call_valid(S_cv_A, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_cv_A, perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_cv_A, perrorcall[.MESSAGE = $ptascii("forged")])',
        '~$call_task_valid(S_cv_A[.CODE = eps], perrorcall.RESUME)',
        '~$call_task_valid(S_cv_A[.SOURCES = eps], perrorcall.RESUME)',
        '~$call_task_valid(S_cv_A, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site $(z + 1) n_key)',
        'n_oob = |S_cv_A.STORE|',
        '~$call_task_valid(S_cv_A, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_oob)',
        *public('S_cv_A'),
    ]
    derived = len(checks)
    for changed in (
        'S_cv_E[.ORIGIN = eps]', 'S_cv_E[.CODE = eps]', 'S_cv_E[.SOURCES = eps]',
        'S_cv_E[.ENV = $unbind(S_cv_E.ENV, n_key_name*)]',
        'S_cv_E[.REFCELLS = S_cv_E.REFCELLS ++ [n_key]]',
        'S_cv_E[.STORE[n_key] = UNDEFINED]',
        'S_cv_E[.STORE[n_key] = DEFINED (PINT 7)]',
        'S_cv_E[.ERRORHANDLER.CALLBACK = eps]',
        'S_cv_E[.HELD = [HCELL n_key]]',
        'S_cv_E[.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base_name* z_base)) (KNOWN (PBOOL true)) z) (KNOWN (PINT 7)) z_outer]',
        'S_cv_E[.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base_name* z_base)) (VARIABLE n_key_name* $(z_key + 1)) z) (KNOWN (PINT 7)) z_outer]',
    ):
        checks.append('$string_unset_bool_cv_plan(' + changed + ') = eps')
    checks += [
        'S_cv_phase = S_cv_E[.CODE = (pcode_entry[.EXPRESSIONS = (CODEEXPR pcpath_key z_code_key true) :: pcode_entry.EXPRESSIONS]) :: eps]',
        '$string_unset_bool_cv_source(S_cv_phase, porigin_site, z) = eps',
        '$string_unset_bool_cv_plan(S_cv_phase) = eps',
        'S_cv_globals = S_cv_E[.CODE = (pcode_entry[.GLOBALS = pcpath_key :: pcode_entry.GLOBALS]) :: eps]',
        '$string_unset_bool_cv_source(S_cv_globals, porigin_site, z) = eps',
        '$string_unset_bool_cv_plan(S_cv_globals) = eps',
        '~$call_task_valid(S_cv_globals, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
        '~$string_unset_bool_cv_cell(S_cv_E, n_key_name*, z_key, n_oob)',
    ]
    derived = len(checks) - derived
    if throwing:
        unsafe = unsafe_checks('S_cv_D', True)
        derived += len(unsafe)
        checks += [
            'S_cv_D_found = $review_cv_seek(S_cv_A, "discard", 1000)',
            '$review_cv_at(S_cv_D_found, "discard")',
            'S_cv_D = $review_cv_running(S_cv_D_found)',
            'S_cv_D.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_discard_tail*',
            'perrorcall_entered.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
            'S_cv_D.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_cv_D.ERRORHANDLER.CALLBACK = eps',
            '$string_unset_bool_cv_cell(S_cv_D, n_key_name*, z_key, n_key)',
            'S_cv_D_next_budget = $drive_steps(S_cv_D, 1)',
            'S_cv_D_next = $review_cv_running(S_cv_D_next_budget)',
            'S_cv_D_next.TODO = (THROW_SEARCH n_throwable) :: ptask_discard_tail*',
            'S_cv_D_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'S_cv_D_next.OBJECTS[n_throwable] = S_cv_D.OBJECTS[n_throwable]',
            'S_cv_D_next.HELD = S_cv_D.HELD',
            'S_cv_D_next.EVENTS = S_cv_D.EVENTS',
            *public('S_cv_D_next'),
            *unsafe,
            'S_cv_DONE = $drive_steps(S_cv_D_next, 2000)',
        ]
    else:
        checks += [
            'S_cv_R_found = $review_cv_seek(S_cv_A, "resume", 1000)',
            '$review_cv_at(S_cv_R_found, "resume")',
            'S_cv_R = $review_cv_running(S_cv_R_found)',
            'S_cv_R.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_resume_tail*',
            'S_cv_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'S_cv_R.HELD = S_cv_E.HELD',
            '$string_unset_bool_cv_cell(S_cv_R, n_key_name*, z_key, n_key)',
            '$call_task_valid(S_cv_R, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
            *public('S_cv_R'),
        ]
        mutations = [
            'S_cv_flip = S_cv_R[.STORE[n_key] = DEFINED (PBOOL false)]',
            '$string_unset_bool_cv_cell(S_cv_flip, n_key_name*, z_key, n_key)',
            'PhpStep: S_cv_flip ~> S_cv_flip_error',
            'S_cv_flip_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            r'S_cv_flip_error.STORE = S_cv_flip.STORE /\ S_cv_flip_error.EVENTS = S_cv_flip.EVENTS',
            'S_cv_flip_error.TODO = ptask_resume_tail*',
            'S_cv_no_base = S_cv_R[.ENV = $unbind(S_cv_R.ENV, n_base_name*)]',
            '$call_task_valid(S_cv_no_base, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
            'PhpStep: S_cv_no_base ~> S_cv_no_base_error',
            'S_cv_no_base_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            'S_cv_no_base_error.ENV = S_cv_no_base.ENV',
            'S_cv_forged = S_cv_R[.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_base) :: ptask_resume_tail*]',
            '$call_task_valid(S_cv_forged, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_base)',
            'PhpStep: S_cv_forged ~> S_cv_forged_next',
            'S_cv_forged_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
            r'S_cv_forged_next.STORE = S_cv_forged.STORE /\ S_cv_forged_next.EVENTS = S_cv_forged.EVENTS',
            *unsafe_checks('S_cv_R', False),
        ]
        derived += len(mutations)
        checks += mutations + ['S_cv_DONE = $drive_steps(S_cv_R, 2000)']
    checks += [
        r'S_cv_DONE.COMPLETION = NORMAL /\ S_cv_DONE.TODO = eps',
        'S_cv_DONE.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$review_cv_outputs(S_cv_DONE.EVENTS) = ' + term(cases.OUTPUTS[name]),
        *public('S_cv_DONE'),
        '$drive_steps(S_cv_E, 2000) = S_cv_DONE',
        '$drive_steps(S_cv_A, 2000) = S_cv_DONE',
    ]
    return checks, derived


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(cases.null.__file__), Path(sys.modules[public.__module__].__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions, runner.PREFIX = cases, conditions, PREFIX
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'] = 'AL'
    report['raw_unset_steps'] = 1
    report['scope'] = ('Independent genuine Boolean-CV nested-unset Warning fronts: exact source/CODE '
        'and raw variable-line authority, captured physical cell, no metadata roots, callback restoration, '
        'same-cell BOOL flips and base removal, wrong-cell/absent/rebound/reference/value refusals, '
        'normal and pending-throw postguards, preserved Throwable and whole/split equality. '
        'Fixture source0/native0; saved originals reused without execution.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
