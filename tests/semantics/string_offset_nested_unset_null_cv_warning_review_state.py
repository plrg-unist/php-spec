#!/usr/bin/env python3
"""Independent raw NULL-CV entry, callback restoration and saved-cell checks."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_float_post_review_state as shared
import string_offset_nested_unset_null_cv_warning_cases as cases

INDEX = 1
FRONT_ONLY = False
PREFIX = shared.PREFIX + r'''
dec $null_cv_raw(pstate) : bool
def $null_cv_raw(S) = true -- if S.TODO = UNSET_ARRAY :: ptask_tail*
def $null_cv_raw(S) = false -- otherwise
dec $null_cv_seek(pstate, nat) : pstate
def $null_cv_seek(S, 0) = S
def $null_cv_seek(S, n) = S
  -- if $(n > 0)
  -- if $null_cv_raw(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $null_cv_seek(S, n) = $null_cv_seek($drive_steps($review_cv_running(S), 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$null_cv_raw(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    checks = [
        'S_I = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_I.COMPLETION = BUDGET',
        'S_E_found = $null_cv_seek(S_I, 1000)',
        '$null_cv_raw(S_E_found)',
        'S_E = $review_cv_running(S_E_found)',
        'S_E.COMPLETION = NORMAL',
        'S_E.TODO = UNSET_ARRAY :: ptask_entry*',
        'S_E.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_base_name* z_base)) (VARIABLE n_key_name* z_key) z) (KNOWN (PINT 7)) z_outer',
        'S_E.ORIGIN = (porigin_site)',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_E.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_E.STORE|)',
        '~$environment_blocked(S_E, n_key_name*)',
        '~(n_key <- S_E.REFCELLS)',
        '~$foreach_released_cell(S_E, n_key)',
        '~$typed_cv_string_released_cell(S_E, n_key)',
        '~$update_released_cell(S_E, n_key)',
        'S_E.STORE[n_key] = DEFINED PNULL',
        '$resolve_at(S_E, VARIABLE n_key_name* z_key, z_key) = S_E[.RESULT = KNOWN PNULL]',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        'porigin_key = PORIGIN 0 pcpath_key',
        '$origin_node(S_E.SOURCES, porigin_key) = (NExprVariable (BYTES text_key) metadata_key)',
        '$base64(text_key) = n_key_name*',
        '$source_line(metadata_key) = z_key',
        '$source_emission_cv(S_E, 0, pcpath_key, NExprVariable (BYTES text_key) metadata_key)',
        '$compiled_read(S_E, porigin_key) = eps',
        '$compiled_effects(S_E, porigin_key) = eps',
        '$code_at(S_E.CODE, 0) = (pcode_entry)',
        '$code_expression(pcode_entry.EXPRESSIONS, pcpath_key) = ((z_code_key, false))',
        '$lookup(S_E.ENV, n_base_name*) = (n_base)',
        'S_E.STORE[n_base] = DEFINED pvalue_base',
        '$hold_task_inputs(S_E) = S_E[.TODO = ptask_entry*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        r'S_E.REQUEST = eps /\ S_E.CURRENT = eps /\ S_E.FRAMES = eps /\ S_E.HELD = eps',
        'S_E.EVENTS = eps',
        '$error_handler_eligible(S_E, 2)',
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$task_nodes(STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = eps',
        *shared.public('S_E'),
    ]
    if FRONT_ONLY:
        return checks + [
            '~$string_unset_bool_cv_cell(S_E, n_key_name*, z_key, n_key)',
            '$string_unset_bool_cv_plan(S_E) = eps',
        ], 0
    checks += [
        '$string_unset_bool_cv_cell(S_E, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_warning_pending(S_E)',
    ]
    derived = []
    for changed in (
        'S_E[.ORIGIN = eps]', 'S_E[.CODE = eps]', 'S_E[.SOURCES = eps]',
        'S_E[.ENV = $unbind(S_E.ENV, n_key_name*)]',
        'S_E[.REFCELLS = S_E.REFCELLS ++ [n_key]]',
        'S_E[.STORE[n_key] = UNDEFINED]',
        'S_E[.STORE[n_key] = DEFINED (PINT 7)]',
        'S_E[.STORE[n_key] = DEFINED (PFLOAT 4609434218613702656)]',
        'S_E[.ERRORHANDLER.CALLBACK = eps]',
        'S_E[.HELD = [HCELL n_key]]',
    ):
        derived.append('$string_unset_bool_cv_plan(' + changed + ') = eps')
    for value in ('true', 'false'):
        derived += ['$string_unset_bool_cv_cell(S_E[.STORE[n_key] = DEFINED (PBOOL ' + value + ')], n_key_name*, z_key, n_key)']
    derived += [
        'n_oob = |S_E.STORE|',
        '~$string_unset_bool_cv_cell(S_E, n_key_name*, z_key, n_oob)',
        'S_bad_code = S_E[.CODE = (pcode_entry[.EXPRESSIONS = (CODEEXPR pcpath_key z_code_key true) :: pcode_entry.EXPRESSIONS]) :: eps]',
        '$string_unset_bool_cv_source(S_bad_code, porigin_site, z) = eps',
        '$string_unset_bool_cv_plan(S_bad_code) = eps',
        'S_bad_global = S_E[.CODE = (pcode_entry[.GLOBALS = pcpath_key :: pcode_entry.GLOBALS]) :: eps]',
        '$string_unset_bool_cv_source(S_bad_global, porigin_site, z) = eps',
        '$string_unset_bool_cv_plan(S_bad_global) = eps',
    ]
    stage = 'discard' if INDEX == 1 else 'resume'
    checks += [
        '$drive_steps(S_E, 0) = S_E[.COMPLETION = BUDGET]',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_entry*',
        'perrorcall.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        r'perrorcall.LEVEL = 2 /\ perrorcall.LINE = z',
        'perrorcall.MESSAGE = $ptascii("String offset cast occurred")',
        '$error_call_valid(S_A, perrorcall)',
        r'S_A.STORE = S_E.STORE /\ S_A.EVENTS = S_E.EVENTS /\ S_A.HELD = S_E.HELD',
        '$heap_graph(S_A) = $heap_graph(S_E)',
        '$drive_steps(S_E, 1) = S_A[.COMPLETION = BUDGET]',
        'S_P_found = $review_cv_seek(S_A, "' + stage + '", 1000)',
        '$review_cv_at(S_P_found, "' + stage + '")',
        'S_P = $review_cv_running(S_P_found)',
        '$lookup(S_P.ENV, n_key_name*) = (n_key)',
        'pvalue_post = ' + cases.POST_VALUES[name],
        'S_P.STORE[n_key] = DEFINED pvalue_post',
        '$resolve_at(S_P, VARIABLE n_key_name* z_key, z_key) = S_P[.RESULT = KNOWN pvalue_post]',
        ('' if INDEX == 1 else '~') + '$string_unset_bool_cv_cell(S_P, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_cell(S_P, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_normal_cell(S_P, n_key_name*, z_key, n_key)',
        '$call_task_valid(S_P, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
        'S_P.HELD = S_E.HELD',
        '$review_cv_outputs(S_P.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        '$float_post_diagnostics(S_P.EVENTS) = eps',
        *shared.public('S_P'),
    ]
    if INDEX == 1:
        checks += [
            'S_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
            'S_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_P.ERRORHANDLER.CALLBACK = eps',
            '$error_read_discard(S_P, perrorcall_entered.RESUME) = S_P',
            'PhpStep: S_P ~> S_next',
            'S_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_next.ERRORHANDLER = S_E.ERRORHANDLER',
            'S_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]',
            r'S_next.STORE = S_P.STORE /\ S_next.ENV = S_P.ENV',
            r'S_next.EVENTS = S_P.EVENTS /\ S_next.HELD = S_P.HELD',
            *shared.public('S_next'),
        ]
    else:
        checks += [
            'S_P.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
            'S_P.ERRORHANDLER = S_E.ERRORHANDLER',
            'PhpStep: S_P ~> S_error',
            'S_error = S_P[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
        ]
    for changed in (
        'S_P[.ENV = $unbind(S_P.ENV, n_key_name*)]',
        'S_P[.STORE[n_key] = UNDEFINED]',
        'S_P[.REFCELLS = S_P.REFCELLS ++ [n_key]]',
    ):
        derived += ['~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)']
    checks += derived + [
        'S_DONE = $drive_steps(S_P, 2000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.EXITSTATUS = 0 /\ S_DONE.TODO = eps',
        'S_DONE.ERRORHANDLER = S_E.ERRORHANDLER',
        'S_DONE.STORE[n_key] = DEFINED pvalue_post',
        'S_DONE.STORE[n_base] = S_E.STORE[n_base]',
        r'S_DONE.CODE = S_E.CODE /\ S_DONE.POOLS = S_E.POOLS',
        'S_DONE.HELD = eps',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + shared.term(cases.OUTPUTS[name]),
        '$float_post_diagnostics(S_DONE.EVENTS) = eps',
        *shared.public('S_DONE'),
        '$drive_steps(S_E, 2000) = S_DONE',
        '$drive_steps(S_A, 2000) = S_DONE',
    ]
    return checks, len(derived)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(shared.__file__), Path(shared.seek.__file__), Path(shared.sl.__file__),
               Path(cases.boolean.__file__), Path(cases.floating.__file__),
               Path(cases.floating.prior.__file__), Path(cases.boolean.null.__file__),
               Path(sys.modules[shared.public.__module__].__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 2)
    FRONT_ONLY = '--front-only' in sys.argv
    if FRONT_ONLY:
        sys.argv.remove('--front-only')
    runner = shared.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions, runner.PREFIX = cases, conditions, PREFIX
    runner.recorded = shared.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent raw UNSET_ARRAY/source/CODE/PNULL saved ordinary cell and exact quiet '
        'read before NULL entry admission; BOOL-only helper/plan refusal is separate from reachability.'
        if FRONT_ONLY else 'New initialized NULL entry retains original source/CODE/read/cell/owner '
        'guards, value-free Warning dispatch, actual unchanged-NULL throw or fitting-FLOAT normal '
        'return, callback restoration, same Error/Exception and whole/split equality. Ref/undefined/'
        'FLOAT entry and source/lookup/owner forgeries remain refused. Source0/native0; no old source renewal.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
