#!/usr/bin/env python3
"""Independent FLOAT-CV Warning checks after real unset and object mutation."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from encoding_declare_protocol import public
import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_bool_cv_warning_review_state as seek
import string_offset_nested_unset_float_cv_warning_cases as cases

INDEX = 4
term = lambda data: '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'
PREFIX = seek.PREFIX.replace('$review_cv_', '$review_float_').replace(
    '$string_unset_bool_cv_plan', '$string_unset_float_cv_plan').replace(
    'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin z n_cell',
    'STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin z') + r'''
dec $review_float_other_events(pevent*) : pevent*
def $review_float_other_events(eps) = eps
def $review_float_other_events((OUTPUT n*) :: pevent_tail*) = $review_float_other_events(pevent_tail*)
def $review_float_other_events(pevent :: pevent_tail*) = pevent :: $review_float_other_events(pevent_tail*)
  -- if $review_float_output(pevent) = eps
  -- if pevent =/= OUTPUT eps
'''


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    throwing = INDEX == 5
    checks = [
        'S_float_I = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')',
        'S_float_I.COMPLETION = BUDGET',
        'S_float_E_found = $review_float_seek(S_float_I, "entry", 1000)',
        '$review_float_at(S_float_E_found, "entry")',
        'S_float_E = $review_float_running(S_float_E_found)',
        '$string_unset_float_cv_plan(S_float_E) = ((porigin_site, z))',
        '$string_unset_bool_cv_source(S_float_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        'S_float_E.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base_name* z_base)) (VARIABLE n_key_name* z_key) z) (KNOWN (PINT 7)) z_outer',
        '$lookup(S_float_E.ENV, n_key_name*) = (n_key)',
        'S_float_E.STORE[n_key] = DEFINED (PFLOAT ' + str(cases.KEY_BITS[name]) + ')',
        '$string_unset_float_cv_cell(S_float_E, n_key_name*, z_key, n_key)',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        'porigin_key = PORIGIN 0 pcpath_key',
        '$origin_node(S_float_E.SOURCES, porigin_key) = (NExprVariable (BYTES text_key) metadata_key)',
        '$base64(text_key) = n_key_name*',
        '$variable_line(BYTES text_key, metadata_key) = z_key',
        '$compiled_read(S_float_E, porigin_key) = eps',
        '$code_at(S_float_E.CODE, 0) = (pcode_key)',
        '$code_expression(pcode_key.EXPRESSIONS, pcpath_key) = ((z_code_key, false))',
        '~(pcpath_key <- pcode_key.GLOBALS)',
        'S_float_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_float_E.HELD = eps',
        '$task_nodes(STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z) = eps',
        '$string_unset_warning_pending(S_float_E)',
        *public('S_float_E'),
        '$drive_steps(S_float_E, 0) = S_float_E[.COMPLETION = BUDGET]',
        'PhpStep: S_float_E ~> S_float_A',
        'S_float_A.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z',
        'S_float_A.RESULT = KNOWN PNULL',
        'S_float_A.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_float_A.LOCATION = NOWHERE',
        'S_float_A.STORE = S_float_E.STORE',
        'S_float_A.ALLOCATIONS = S_float_E.ALLOCATIONS',
        'S_float_A.HELD = S_float_E.HELD',
        'S_float_A.EVENTS = S_float_E.EVENTS',
        '$heap_graph(S_float_A) = $heap_graph(S_float_E)',
        '$drive_steps(S_float_E, 1) = S_float_A[.COMPLETION = BUDGET]',
        '$error_call_valid(S_float_A, perrorcall)',
        '$call_task_valid(S_float_A, perrorcall.RESUME)',
        '~$error_call_valid(S_float_A[.ORIGIN = eps], perrorcall)',
        '~$error_call_valid(S_float_A, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_float_A, perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_float_A, perrorcall[.MESSAGE = $ptascii("forged")])',
        '~$call_task_valid(S_float_A[.SOURCES = eps], perrorcall.RESUME)',
        '~$call_task_valid(S_float_A[.CODE = eps], perrorcall.RESUME)',
        '~$call_task_valid(S_float_A, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site $(z + 1))',
        *public('S_float_A'),
    ]
    controls = [
        '$string_unset_float_cv_plan(S_float_E[.ENV = $unbind(S_float_E.ENV, n_key_name*)]) = eps',
        '$string_unset_float_cv_plan(S_float_E[.REFCELLS = S_float_E.REFCELLS ++ [n_key]]) = eps',
        '$string_unset_float_cv_plan(S_float_E[.STORE[n_key] = UNDEFINED]) = eps',
        '$string_unset_float_cv_plan(S_float_E[.HELD = [HCELL n_key]]) = eps',
        '$string_unset_float_cv_plan(S_float_E[.ERRORHANDLER.CALLBACK = eps]) = eps',
        'S_float_phase = S_float_E[.CODE = (pcode_key[.EXPRESSIONS = (CODEEXPR pcpath_key z_code_key true) :: pcode_key.EXPRESSIONS]) :: eps]',
        '$string_unset_float_cv_plan(S_float_phase) = eps',
        'S_float_global = S_float_E[.CODE = (pcode_key[.GLOBALS = pcpath_key :: pcode_key.GLOBALS]) :: eps]',
        '$string_unset_float_cv_plan(S_float_global) = eps',
    ]
    for value in ('PNULL', '(PBOOL true)', '(PINT 1)', '(PFLOAT 18446744073709551616)',
                  '(PFLOAT 9221120237041090560)', '(PFLOAT 9218868437227405313)'):
        controls.append('~$string_unset_float_cv_cell(S_float_E[.STORE[n_key] = DEFINED '
                        + value + '], n_key_name*, z_key, n_key)')
    for bits in (0, 1 << 63, 1, 0x000fffffffffffff, 0x0010000000000000,
                 0x7ff0000000000000, 0xfff0000000000000):
        controls.append('$string_unset_float_cv_cell(S_float_E[.STORE[n_key] = DEFINED (PFLOAT '
                        + str(bits) + ')], n_key_name*, z_key, n_key)')
    checks += controls
    derived = len(controls)
    if throwing:
        checks += [
            'S_float_D_found = $review_float_seek(S_float_A, "discard", 1000)',
            '$review_float_at(S_float_D_found, "discard")',
            'S_float_D = $review_float_running(S_float_D_found)',
            'S_float_D.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_discard_tail*',
            'perrorcall_entered.RESUME = STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z',
            'S_float_D.ERRORHANDLER.CALLBACK = eps',
            'S_float_D.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            '$lookup(S_float_D.ENV, n_key_name*) = (n_object_cell)',
            'S_float_D.STORE[n_object_cell] = DEFINED (POBJECT n_object)',
            'n_object =/= n_throwable',
            '$heap_member(HOBJECT n_object, S_float_D.ALLOCATIONS)',
            '~$string_unset_float_cv_cell(S_float_D, n_key_name*, z_key, n_key)',
            '$call_task_valid(S_float_D, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z)',
            '$error_read_discard(S_float_D, perrorcall_entered.RESUME) = S_float_D',
            'PhpStep: S_float_D ~> S_float_D_next',
            'S_float_D_next.TODO = (THROW_SEARCH n_throwable) :: ptask_discard_tail*',
            'S_float_D_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'S_float_D_next.OBJECTS[n_throwable] = S_float_D.OBJECTS[n_throwable]',
            'S_float_D_next.STORE = S_float_D.STORE',
            'S_float_D_next.HELD = S_float_D.HELD',
            'S_float_D_next.EVENTS = S_float_D.EVENTS',
            *public('S_float_D_next'),
            'S_float_DONE = $drive_steps(S_float_D_next, 2000)',
        ]
    else:
        checks += [
            'S_float_R_found = $review_float_seek(S_float_A, "resume", 1000)',
            '$review_float_at(S_float_R_found, "resume")',
            'S_float_R = $review_float_running(S_float_R_found)',
            'S_float_R.TODO = (STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z) :: ptask_resume_tail*',
            'S_float_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            '$lookup(S_float_R.ENV, n_key_name*) = eps',
            '~$string_unset_float_cv_cell(S_float_R, n_key_name*, z_key, n_key)',
            '$call_task_valid(S_float_R, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z)',
            '$task_nodes(STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z) = eps',
            *public('S_float_R'),
            'PhpStep: S_float_R ~> S_float_R_error',
            'S_float_R_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            'S_float_R_error.STORE = S_float_R.STORE',
            'S_float_R_error.ENV = S_float_R.ENV',
            'S_float_R_error.EVENTS = S_float_R.EVENTS',
            'S_float_R_error.TODO = ptask_resume_tail*',
        ]
        mutations = [
            'S_float_gone = S_float_R[.ENV = eps]',
            '$call_task_valid(S_float_gone, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z)',
            'PhpStep: S_float_gone ~> S_float_gone_error',
            'S_float_gone_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            'S_float_gone_error.ENV = eps',
            'S_float_gone_error.STORE = S_float_gone.STORE',
            'S_float_gone_error.EVENTS = S_float_gone.EVENTS',
            'n_rebound = |S_float_R.STORE|',
            'S_float_rebound = S_float_R[.ENV = (BIND n_key_name* n_rebound) :: S_float_R.ENV][.STORE = S_float_R.STORE ++ [DEFINED (PBOOL true)]][.ALLOCATIONS = S_float_R.ALLOCATIONS ++ [HCELL n_rebound]]',
            '$heap_valid($heap_graph(S_float_rebound))',
            '$call_task_valid(S_float_rebound, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site z)',
            'PhpStep: S_float_rebound ~> S_float_rebound_error',
            'S_float_rebound_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
            'S_float_rebound_error.STORE = S_float_rebound.STORE',
            'S_float_rebound_error.EVENTS = S_float_rebound.EVENTS',
        ]
        derived += len(mutations)
        checks += mutations + ['S_float_DONE = $drive_steps(S_float_R, 2000)']
    checks += [
        'S_float_DONE.COMPLETION = NORMAL',
        'S_float_DONE.TODO = eps',
        'S_float_DONE.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$review_float_outputs(S_float_DONE.EVENTS) = ' + term(cases.OUTPUTS[name]),
        '$review_float_other_events(S_float_DONE.EVENTS) = eps',
        *public('S_float_DONE'),
        '$drive_steps(S_float_E, 2000) = S_float_DONE',
        '$drive_steps(S_float_A, 2000) = S_float_DONE',
    ]
    return checks, derived


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(seek.__file__), Path(cases.null.__file__),
               Path(sys.modules[public.__module__].__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (4, 5)
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions, runner.PREFIX = cases, conditions, PREFIX
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'AL', 1
    report['scope'] = ('Independent actual GLOBALS-key unset and object-mutating throwing handler fronts: '
        'ordinary nonNaN FLOAT CV entry/source/CODE fences, borrowed fixed-slot Warning dispatch without '
        'roots, source-only completion after real removal/type mutation, no secondary diagnostics, '
        'same-Exception discard, restored callback and whole/split equality. Fixture source0/native0; '
        'fresh native originals reused without execution.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
