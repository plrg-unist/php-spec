#!/usr/bin/env python3
"""Independent NULL-unset Warning ownership, restoration, and resume checks."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from encoding_declare_protocol import public
import string_offset_terminal_unset_protocol as prior
import string_offset_nested_unset_null_warning_cases as cases

INDEX = 0
term = lambda data: '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'
PREFIX = r'''
dec $review_null_running(pstate) : pstate
def $review_null_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $review_null_running(S) = S -- otherwise
dec $review_null_at(pstate, text) : bool
def $review_null_at(S, "entry") = true
  -- if $string_unset_warning_plan($review_null_running(S)) =/= eps
def $review_null_at(S, "returned") = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_WARNING_RESULT porigin z
def $review_null_at(S, "resume") = true
  -- if S.TODO = (STRING_UNSET_WARNING_RESULT porigin z) :: ptask_tail*
def $review_null_at(S, "discard") = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_WARNING_RESULT porigin z
def $review_null_at(S, text) = false -- otherwise
dec $review_null_seek(pstate, text, nat) : pstate
def $review_null_seek(S, text, 0) = S
def $review_null_seek(S, text, n) = S
  -- if $(n > 0)
  -- if $review_null_at(S, text) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_null_seek(S, text, n) = $review_null_seek($drive_steps($review_null_running(S), 1), text, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$review_null_at(S, text)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $review_null_outputs(pevent*) : nat*
dec $review_null_output(pevent) : nat*
def $review_null_output(OUTPUT n*) = n*
def $review_null_output(pevent) = eps -- otherwise
def $review_null_outputs(eps) = eps
def $review_null_outputs(pevent :: pevent_tail*) = $review_null_output(pevent) ++ $review_null_outputs(pevent_tail*)
'''


def assertions(unit, path, output, throwing):
    checks = [
        'S_review_I = $php_run(' + unit + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_review_I.COMPLETION = BUDGET',
        'S_review_E_found = $review_null_seek(S_review_I, "entry", 1000)',
        '$review_null_at(S_review_E_found, "entry")',
        'S_review_E = $review_null_running(S_review_E_found)',
        '$string_unset_warning_plan(S_review_E) = ((porigin_site, z))',
        'S_review_E.TODO = UNSET_ARRAY :: ptask_tail*',
        'S_review_E.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base* z_base)) (KNOWN PNULL) z) (KNOWN (PINT 7)) z_outer',
        '$lookup(S_review_E.ENV, n_base*) = (n_cell)',
        'S_review_E.STORE[n_cell] = DEFINED pvalue_base',
        'S_review_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_review_E.HELD = eps',
        '$hold_task_inputs(S_review_E).HELD = S_review_E.HELD',
        '$task_nodes(STRING_UNSET_WARNING_RESULT porigin_site z) = eps',
        '$string_unset_warning_pending(S_review_E)',
        *public('S_review_E'),
        'S_review_Z = $drive_steps(S_review_E, 0)',
        'S_review_Z = S_review_E[.COMPLETION = BUDGET]',
        'S_review_A_budget = $drive_steps(S_review_E, 1)',
        'S_review_A_budget.COMPLETION = BUDGET',
        'S_review_A = $review_null_running(S_review_A_budget)',
        'S_review_A.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = STRING_UNSET_WARNING_RESULT porigin_site z',
        'perrorcall.LEVEL = 2',
        'perrorcall.LINE = z',
        'perrorcall.MESSAGE = $ptascii("String offset cast occurred")',
        'S_review_A.HELD = S_review_E.HELD',
        'S_review_A.STORE = S_review_E.STORE',
        'S_review_A.EVENTS = S_review_E.EVENTS',
        'S_review_A.RESULT = KNOWN PNULL',
        'S_review_A.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_review_A.LOCATION = NOWHERE',
        '$error_call_valid(S_review_A, perrorcall)',
        '$call_task_valid(S_review_A, perrorcall.RESUME)',
        '~$error_call_valid(S_review_A[.ORIGIN = eps], perrorcall)',
        '~$call_task_valid(S_review_A[.ORIGIN = eps], perrorcall.RESUME)',
        '~$error_call_valid(S_review_A[.SOURCES = eps], perrorcall)',
        '~$call_task_valid(S_review_A[.CODE = eps], perrorcall.RESUME)',
        '~$call_task_valid(S_review_A, STRING_UNSET_WARNING_RESULT porigin_site $(z + 1))',
        *public('S_review_A'),
    ]
    for changed in (
        'S_review_E[.ORIGIN = eps]', 'S_review_E[.CODE = eps]', 'S_review_E[.SOURCES = eps]',
        'S_review_E[.REFCELLS = S_review_E.REFCELLS ++ [n_cell]]',
        'S_review_E[.STORE[n_cell] = DEFINED (PSTRING ($ptascii("ab")))]',
        'S_review_E[.STORE[n_cell] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([97, 0, 98]))]',
        'S_review_E[.STORE[n_cell] = DEFINED PNULL]',
        'S_review_E[.ERRORHANDLER.CALLBACK = eps]', 'S_review_E[.ERRORHANDLER.LEVELS = 0]',
        'S_review_E[.HELD = [HCELL n_cell]]',
        'S_review_E[.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base* z_base)) (KNOWN (PBOOL false)) z) (KNOWN (PINT 7)) z_outer]',
    ):
        checks.append('$string_unset_warning_plan(' + changed + ') = eps')
    if throwing:
        checks += [
            'S_review_D_found = $review_null_seek(S_review_A, "discard", 1000)',
            '$review_null_at(S_review_D_found, "discard")',
            'S_review_D = $review_null_running(S_review_D_found)',
            'S_review_D.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_discard_tail*',
            'perrorcall_entered.RESUME = STRING_UNSET_WARNING_RESULT porigin_site z',
            'S_review_D.ERRORHANDLER.CALLBACK = eps',
            'S_review_D.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_review_D_after_budget = $drive_steps(S_review_D, 1)',
            'S_review_D_after_budget.COMPLETION = BUDGET',
            'S_review_D_after = $review_null_running(S_review_D_after_budget)',
            'S_review_D_after.TODO = (THROW_SEARCH n_throwable) :: ptask_discard_tail*',
            'S_review_D_after.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'S_review_D_after.HELD = S_review_D.HELD',
            'S_review_D_after.OBJECTS[n_throwable] = S_review_D.OBJECTS[n_throwable]',
            'S_review_DONE = $drive_steps(S_review_D_after, 2000)',
        ]
    else:
        checks += [
            'S_review_H_found = $review_null_seek(S_review_A, "returned", 1000)',
            '$review_null_at(S_review_H_found, "returned")',
            'S_review_H = $review_null_running(S_review_H_found)',
            'S_review_H.RESULT = KNOWN (PBOOL true)',
            'S_review_H.ERRORHANDLER.CALLBACK = eps',
            'S_review_R_found = $review_null_seek(S_review_H, "resume", 1000)',
            '$review_null_at(S_review_R_found, "resume")',
            'S_review_R = $review_null_running(S_review_R_found)',
            'S_review_R.TODO = (STRING_UNSET_WARNING_RESULT porigin_site z) :: ptask_tail*',
            'S_review_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'S_review_R.HELD = S_review_E.HELD',
            '$call_task_valid(S_review_R, STRING_UNSET_WARNING_RESULT porigin_site z)',
            'S_review_R_changed = S_review_R[.STORE[n_cell] = DEFINED (PINT 9)]',
            '$call_task_valid(S_review_R_changed, STRING_UNSET_WARNING_RESULT porigin_site z)',
            '$string_unset_warning_plan(S_review_R_changed) = eps',
            'PhpStep: S_review_R_changed ~> S_review_R_changed_error',
            'S_review_R_changed_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            'S_review_R_changed_error.STORE = S_review_R_changed.STORE',
            'S_review_R_changed_error.EVENTS = S_review_R_changed.EVENTS',
            'S_review_R_changed_error.TODO = ptask_tail*',
            'S_review_R_deleted = S_review_R[.ENV = eps]',
            '$call_task_valid(S_review_R_deleted, STRING_UNSET_WARNING_RESULT porigin_site z)',
            'PhpStep: S_review_R_deleted ~> S_review_R_deleted_error',
            'S_review_R_deleted_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            'S_review_R_deleted_error.ENV = eps',
            'S_review_R_deleted_error.TODO = ptask_tail*',
            *public('S_review_R'),
            'S_review_DONE = $drive_steps(S_review_R, 2000)',
        ]
    return checks + [
        'S_review_DONE.COMPLETION = NORMAL', 'S_review_DONE.TODO = eps',
        '$review_null_outputs(S_review_DONE.EVENTS) = ' + term(output),
        'S_review_DONE.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        *public('S_review_DONE'),
        'S_review_WHOLE = $drive_steps(S_review_E, 2000)', 'S_review_WHOLE = S_review_DONE',
        'S_review_SPLIT = $drive_steps(S_review_A, 2000)', 'S_review_SPLIT = S_review_DONE',
    ]



def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    checks = assertions(program, path, cases.OUTPUTS[name], INDEX == 1)
    return checks, (30, 16)[INDEX]


if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    prior.NAME = tuple(cases.CASES)[INDEX]
    prior.OUTPUT = cases.OUTPUTS[prior.NAME]
    prior.cases, prior.conditions, prior.PREFIX = cases, conditions, PREFIX
    passed = prior.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'][str(own)] = before
    report['mode'] = 'AL'
    report['raw_unset_steps'] = 1
    report['scope'] = ('Independent source-reached NULL inner string-unset Warning: exact task tail and '
        'no extra HELD or resume roots; source/origin/line and entry-domain refusals; callback restoration, '
        'normal resume after base rebind/removal, and actual throw-marker discard preserving the same '
        'Throwable; whole/split equality. Fixture source0/native0; original observations reused once.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
