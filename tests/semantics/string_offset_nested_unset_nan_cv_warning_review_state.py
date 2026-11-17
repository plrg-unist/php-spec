#!/usr/bin/env python3
"""Independent reached arithmetic/negated NaN-CV Warning and throw checks."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from encoding_declare_protocol import public
import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_float_cv_warning_review_state as seek
import string_offset_nested_unset_nan_cv_warning_cases as cases

INDEX = 2
PREFIX = seek.PREFIX
term = lambda data: '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    checks = [
        'S_nan_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_nan_I.COMPLETION = BUDGET',
        'S_nan_E_found = $review_float_seek(S_nan_I, "entry", 1000)',
        '$review_float_at(S_nan_E_found, "entry")',
        'S_nan_E = $review_float_running(S_nan_E_found)',
        '$string_unset_float_cv_plan(S_nan_E) = ((porigin_site, z))',
        '$string_unset_bool_cv_plan(S_nan_E) = eps',
        '$string_unset_bool_cv_source(S_nan_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        'S_nan_E.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base_name* z_base)) (VARIABLE n_key_name* z_key) z) (KNOWN (PINT 7)) z_outer',
        '$lookup(S_nan_E.ENV, n_key_name*) = (n_key)',
        'S_nan_E.STORE[n_key] = DEFINED (PFLOAT n_nan)',
        '$(n_nan < 18446744073709551616)',
        '$fparts_nan($float_decode(n_nan))',
        '$string_unset_float_cv_cell(S_nan_E, n_key_name*, z_key, n_key)',
        '$resolve_at(S_nan_E, VARIABLE n_key_name* z_key, z_key) = S_nan_E[.RESULT = KNOWN (PFLOAT n_nan)]',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        '$compiled_read(S_nan_E, porigin_key) = eps',
        '$review_float_outputs(S_nan_E.EVENTS) = $ptascii("N:1;")',
        '$review_float_other_events(S_nan_E.EVENTS) = eps',
        'S_nan_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_nan_E.HELD = eps',
        '$task_nodes(STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z) = eps',
        *public('S_nan_E'),
        '$drive_steps(S_nan_E, 0) = S_nan_E[.COMPLETION = BUDGET]',
        'PhpStep: S_nan_E ~> S_nan_A',
        'S_nan_A.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z',
        'S_nan_A.EVENTS = S_nan_E.EVENTS',
        'S_nan_A.STORE = S_nan_E.STORE',
        'S_nan_A.HELD = S_nan_E.HELD',
        '$heap_graph(S_nan_A) = $heap_graph(S_nan_E)',
        '$error_call_valid(S_nan_A, perrorcall)',
        '$call_task_valid(S_nan_A, perrorcall.RESUME)',
        '~$call_task_valid(S_nan_A[.ORIGIN = eps], perrorcall.RESUME)',
        '~$call_task_valid(S_nan_A[.SOURCES = eps], perrorcall.RESUME)',
        '~$call_task_valid(S_nan_A[.CODE = eps], perrorcall.RESUME)',
        '~$call_task_valid(S_nan_A, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site $(z + 1))',
        *public('S_nan_A'),
    ]
    guards = [
        '$string_unset_float_cv_plan(S_nan_E[.REFCELLS = S_nan_E.REFCELLS ++ [n_key]]) = eps',
        '$string_unset_float_cv_plan(S_nan_E[.STORE[n_key] = UNDEFINED]) = eps',
        '$string_unset_float_cv_plan(S_nan_E[.HELD = [HCELL n_key]]) = eps',
    ]
    for bits in (0x7ff8000000000000, 0xfff8000000000000,
                 0x7ff0000000000001, 0xfff0000000000001):
        guards.append('$string_unset_float_cv_cell(S_nan_E[.STORE[n_key] = DEFINED (PFLOAT '
                      + str(bits) + ')], n_key_name*, z_key, n_key)')
    for value in ('PNULL', '(PBOOL true)', '(PINT 0)', '(PFLOAT 18446744073709551616)'):
        guards.append('~$string_unset_float_cv_cell(S_nan_E[.STORE[n_key] = DEFINED '
                      + value + '], n_key_name*, z_key, n_key)')
    checks += guards
    if INDEX == 1:
        checks += [
            'S_nan_D_found = $review_float_seek(S_nan_A, "discard", 1000)',
            '$review_float_at(S_nan_D_found, "discard")',
            'S_nan_D = $review_float_running(S_nan_D_found)',
            'S_nan_D.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_discard_tail*',
            'perrorcall_entered.RESUME = STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z',
            'S_nan_D.STORE[n_key] = DEFINED (PFLOAT n_nan)',
            '$string_unset_float_cv_cell(S_nan_D, n_key_name*, z_key, n_key)',
            'S_nan_D.ERRORHANDLER.CALLBACK = eps',
            'S_nan_D.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            '$error_read_discard(S_nan_D, perrorcall_entered.RESUME) = S_nan_D',
            'PhpStep: S_nan_D ~> S_nan_D_next',
            'S_nan_D_next.TODO = (THROW_SEARCH n_throwable) :: ptask_discard_tail*',
            'S_nan_D_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'S_nan_D_next.OBJECTS[n_throwable] = S_nan_D.OBJECTS[n_throwable]',
            'S_nan_D_next.STORE = S_nan_D.STORE',
            'S_nan_D_next.EVENTS = S_nan_D.EVENTS',
            'S_nan_D_next.HELD = S_nan_D.HELD',
            *public('S_nan_D_next'),
            'S_nan_DONE = $drive_steps(S_nan_D_next, 2000)',
        ]
    else:
        checks += [
            'S_nan_R_found = $review_float_seek(S_nan_A, "resume", 1000)',
            '$review_float_at(S_nan_R_found, "resume")',
            'S_nan_R = $review_float_running(S_nan_R_found)',
            'S_nan_R.TODO = (STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z) :: ptask_resume_tail*',
            'S_nan_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            '$lookup(S_nan_R.ENV, n_key_name*) = (n_key)',
            'S_nan_R.STORE[n_key] = DEFINED (PFLOAT n_nan)',
            '$string_unset_float_cv_cell(S_nan_R, n_key_name*, z_key, n_key)',
            '$call_task_valid(S_nan_R, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z)',
            *public('S_nan_R'),
            'PhpStep: S_nan_R ~> S_nan_R_error',
            'S_nan_R_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            'S_nan_R_error.STORE = S_nan_R.STORE',
            'S_nan_R_error.EVENTS = S_nan_R.EVENTS',
            'S_nan_R_error.TODO = ptask_resume_tail*',
            'S_nan_DONE = $drive_steps(S_nan_R, 2000)',
        ]
    checks += [
        'S_nan_DONE.COMPLETION = NORMAL',
        'S_nan_DONE.TODO = eps',
        'S_nan_DONE.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$review_float_outputs(S_nan_DONE.EVENTS) = ' + term(cases.OUTPUTS[name]),
        '$review_float_other_events(S_nan_DONE.EVENTS) = eps',
        *public('S_nan_DONE'),
        '$drive_steps(S_nan_E, 2000) = S_nan_DONE',
        '$drive_steps(S_nan_A, 2000) = S_nan_DONE',
    ]
    return checks, len(guards)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(seek.__file__), Path(seek.seek.__file__),
               Path(cases.null.__file__), Path(cases.floating.__file__),
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
    report['scope'] = ('Independent fresh arithmetic/negated NaN CV fronts assert reached PFLOAT, range, '
        'fparts_nan and the core N:1 observer without assuming NaN payload sign. Source-only FLOAT Warning '
        'dispatch, no new owners, unchanged cell/tail, normal Error or same-Exception discard, restored '
        'callback, no extra diagnostics and whole/split are source0/native0; saved native4 reused only.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
