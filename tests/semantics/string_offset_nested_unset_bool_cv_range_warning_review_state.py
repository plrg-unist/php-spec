#!/usr/bin/env python3
"""Independent copied-range Warning dispatch and secondary-throw continuation."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_float_post_review_state as shared
import string_offset_nested_unset_bool_cv_range_warning_cases as cases

FRONT_ONLY = False
DEFAULT_ONLY = False
PREFIX = shared.PREFIX + r'''
dec $review_range_at(pstate, text) : bool
def $review_range_at(S, "entered") = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin z n_cell n_bits
def $review_range_at(S, "discard") = true
  -- if S.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin z n_cell n_bits
def $review_range_at(S, text) = false -- otherwise
dec $review_range_seek(pstate, text, nat) : pstate
def $review_range_seek(S, text, 0) = S
def $review_range_seek(S, text, n) = S
  -- if $(n > 0)
  -- if $review_range_at(S, text) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $review_range_seek(S, text, n) = $review_range_seek($drive_steps($review_cv_running(S), 1), text, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$review_range_at(S, text)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def default_checks():
    checks = ['S_P.DISPLAYINIT = ($ptascii("stderr"))',
        'S_P.DISPLAYINI = S_P.DISPLAYINIT', '$display_state_mode(S_P) = 2']
    for mask in (0, 512):
        state = 'S_range_normal_mask_' + str(mask)
        checks += [state + ' = S_P[.ERRORHANDLER.LEVELS = ' + str(mask) + ']',
            '$string_unset_cv_range_plan(' + state + ') = ((porigin_site, z, n_key, n_bits))',
            'PhpStep: ' + state + ' ~> ' + state + '_next',
            state + '_next.TODO = (STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits) :: ptask_after*',
            state + '_next = ' + state + '[.TODO = (STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits) :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps][.EVENTS = ' + state + '.EVENTS ++ [DIAGNOSTIC "Warning" n_message* z]]',
            '$call_task_valid(' + state + '_next, STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits)']
    return checks


def conditions(program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    checks = [
        'S_I = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_I.COMPLETION = BUDGET',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_E.ENV, n_key_name*) = (n_key)',
        'S_E.STORE[n_key] = DEFINED (PBOOL true)',
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_after*',
        'perrorcall_first.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_A, perrorcall_first)',
        'S_A.STORE = S_E.STORE',
        '$heap_graph(S_A) = $heap_graph(S_E)',
        'S_P_found = $review_cv_seek(S_A, "resume", 1000)',
        '$review_cv_at(S_P_found, "resume")',
        'S_P = $review_cv_running(S_P_found)',
        'S_P.COMPLETION = NORMAL',
        'S_P.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
        'S_P.ORIGIN = (porigin_site)',
        '$call_task_valid(S_P, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
        '$string_unset_bool_cv_source(S_P, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        'porigin_key = PORIGIN 0 pcpath_key',
        '$origin_node(S_P.SOURCES, porigin_key) = (NExprVariable (BYTES text_key) metadata_key)',
        '$base64(text_key) = n_key_name*',
        '$source_line(metadata_key) = z_key',
        '$source_emission_cv(S_P, 0, pcpath_key, NExprVariable (BYTES text_key) metadata_key)',
        '$compiled_read(S_P, porigin_key) = eps',
        '$lookup(S_P.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_P.STORE|)',
        '~$environment_blocked(S_P, n_key_name*)',
        '~(n_key <- S_P.REFCELLS)',
        '~$foreach_released_cell(S_P, n_key)',
        '~$typed_cv_string_released_cell(S_P, n_key)',
        '~$update_released_cell(S_P, n_key)',
        'n_bits = ' + str(cases.BITS),
        'S_P.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$resolve_at(S_P, VARIABLE n_key_name* z_key, z_key) = S_P[.RESULT = KNOWN (PFLOAT n_bits)]',
        '$(n_bits < 18446744073709551616)',
        '$float_decode(n_bits) = FINITE n_sign n_num n_den',
        '~$fparts_fits(FINITE n_sign n_num n_den)',
        '$string_unset_bool_cv_post_cell(S_P, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_P, n_key_name*, z_key, n_key)',
        'S_P.ERRORHANDLER = S_E.ERRORHANDLER',
        '$error_handler_eligible(S_P, 2)',
        'S_P.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$type_bytes(pvalue_callback) = $ptascii("string")',
        r'S_P.CURRENT = eps /\ S_P.FRAMES = eps /\ S_P.HELD = eps /\ S_P.REQUEST = eps',
        '$task_nodes(STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = eps',
        '$integer_float_notices([RANGEWARNING], n_bits) = [(2, n_message*)]',
        'n_message* = $ptascii("The float 1.0E+20 is not representable as an int, cast occurred")',
        '$review_cv_outputs(S_P.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        '$float_post_diagnostics(S_P.EVENTS) = eps',
        *shared.public('S_P'),
    ]
    if FRONT_ONLY:
        return checks + [
            'PhpStep: S_P ~> S_unsupported',
            'S_unsupported = S_P[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
        ], 0
    if DEFAULT_ONLY:
        changed = default_checks()
        return checks + changed, len(changed)
    checks += [
        'S_P.RESULT = KNOWN PNULL',
        r'S_P.SOURCEPENDING = eps /\ S_P.CONSTCONTEXT = eps',
        '~$eval_compile_recorded_error(S_P, 2)',
        '~$recorded_runtime_pending(S_P, 2)',
        '$arithmetic_add_named(S_P)',
        'ptask_after* = ptask_first :: ptask_rest*',
        '$string_unset_cv_range_plan(S_P) = ((porigin_site, z, n_key, n_bits))',
        '$string_unset_cv_range_snapshot(S_P, porigin_site, z, n_key, n_bits)',
        'ptask_range = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits',
        '$call_task_valid(S_P, ptask_range)',
        '$task_nodes(ptask_range) = eps',
        'PhpStep: S_P ~> S_range_A',
        'S_range_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_range) :: ptask_after*',
        'S_range_A = S_P[.TODO = (ERROR_HANDLER_INVOKE perrorcall_range) :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps]',
        'perrorcall_range.RESUME = ptask_range',
        r'perrorcall_range.SITE = porigin_site /\ perrorcall_range.LINE = z /\ perrorcall_range.LEVEL = 2',
        'perrorcall_range.MESSAGE = n_message*',
        'perrorcall_range.EVENT = DIAGNOSTIC "Warning" n_message* z',
        'perrorcall_range.CALLBACK = pvalue_callback',
        'perrorcall_range.TARGET = eps',
        '$error_call_valid(S_range_A, perrorcall_range)',
        '$call_task_valid(S_range_A, ERROR_HANDLER_INVOKE perrorcall_range)',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall_range) = eps',
        '$heap_graph(S_range_A) = $heap_graph(S_P)',
        '$drive_steps(S_P, 0) = S_P[.COMPLETION = BUDGET]',
        '$drive_steps(S_P, 1) = S_range_A[.COMPLETION = BUDGET]',
        *shared.public('S_range_A'),
        'S_range_E_found = $review_range_seek(S_range_A, "entered", 1000)',
        '$review_range_at(S_range_E_found, "entered")',
        'S_range_E = $review_cv_running(S_range_E_found)',
        'S_range_E.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
        'perrorcall_entered.TARGET = (pcalltarget)',
        'perrorcall_entered = perrorcall_range[.TARGET = (pcalltarget)]',
        'S_range_E.ERRORHANDLER.CALLBACK = eps',
        'S_range_E.CURRENT = (pcallcontext)',
        '$error_context_anchor(S_range_E, pcallcontext, (pcallcontext), S_range_E.FRAMES)',
        '$task_nodes(ptask_range) = eps',
        'S_range_D_found = $review_range_seek(S_range_E, "discard", 1000)',
        '$review_range_at(S_range_D_found, "discard")',
        'S_range_D = $review_cv_running(S_range_D_found)',
        'S_range_D.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
        r'S_range_D.CURRENT = eps /\ S_range_D.FRAMES = eps /\ S_range_D.HELD = eps',
        'S_range_D.ORIGIN = (porigin_site)',
        'S_range_D.ERRORHANDLER.CALLBACK = eps',
        '$lookup(S_range_D.ENV, n_key_name*) = (n_key)',
        'S_range_D.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("done")))',
        '~$string_unset_cv_range_snapshot(S_range_D, porigin_site, z, n_key, n_bits)',
        '$call_task_valid(S_range_D, ptask_range)',
        '$error_call_valid(S_range_D, perrorcall_entered)',
        '~$error_call_valid(S_range_D, perrorcall_entered[.TARGET = eps])',
        '$call_task_valid(S_range_D, ERROR_HANDLER_RESULT perrorcall_entered)',
        '$task_nodes(ERROR_HANDLER_RESULT perrorcall_entered) = eps',
        'S_range_D.OBJECTS[n_exception] = THROWABLE pthrowable',
        'pthrowable.KIND = "Exception"',
        '$throwable_field(S_range_D, n_exception, "message") = PSTRING_CARRIER INTERNED_STRING ($ptascii("range"))',
        '$throwable_field(S_range_D, n_exception, "line") = PINT 2',
        '$review_cv_outputs(S_range_D.EVENTS) = $ptascii("H:2:String offset cast occurred;H:2:The float 1.0E+20 is not representable as an int, cast occurred;")',
        '$float_post_diagnostics(S_range_D.EVENTS) = eps',
        '$error_read_discard(S_range_D, ptask_range) = S_range_D',
        '$string_unset_cv_range_plan(S_range_D) = eps',
        'PhpStep: S_range_D ~> S_range_next',
        'S_range_next.TODO = (THROW_SEARCH n_exception) :: ptask_after*',
        'S_range_next.ERRORHANDLER = S_E.ERRORHANDLER',
        'S_range_next.OBJECTS = S_range_D.OBJECTS',
        'S_range_next.STORE = S_range_D.STORE',
        'S_range_next.EVENTS = S_range_D.EVENTS',
        'S_range_next.HELD = S_range_D.HELD',
        '$drive_steps(S_range_D, 1) = S_range_next[.COMPLETION = BUDGET]',
        *shared.public('S_range_D'),
        *shared.public('S_range_next'),
    ]
    reached = len(checks)
    for tag, changed in (
        ('site', 'perrorcall_range[.SITE = PORIGIN 99 eps]'),
        ('line', 'perrorcall_range[.LINE = $(z + 1)]'),
        ('level', 'perrorcall_range[.LEVEL = 512]'),
        ('message', 'perrorcall_range[.MESSAGE = $ptascii("forged")]'),
        ('event', 'perrorcall_range[.EVENT = DIAGNOSTIC "Warning" ($ptascii("forged")) z]'),
        ('bits', 'perrorcall_range[.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key 0]'),
    ):
        checks += ['~$error_call_valid(S_range_A, ' + changed + ')']
    for tag, changed in (
        ('snapshot', 'S_range_A[.STORE[n_key] = DEFINED (PINT 7)]'),
        ('bits', 'S_range_A[.STORE[n_key] = DEFINED (PFLOAT 14129391947058875456)]'),
        ('source', 'S_range_A[.SOURCES = eps]'),
        ('origin', 'S_range_A[.ORIGIN = eps]'),
    ):
        checks += ['~$error_call_valid(' + changed + ', perrorcall_range)']
    for tag, changed in (
        ('default', 'S_P[.ERRORHANDLER.CALLBACK = eps]'),
        ('reference', 'S_P[.REFCELLS = S_P.REFCELLS ++ [n_key]]'),
    ):
        state = 'S_range_bad_' + tag
        checks += [state + ' = ' + changed,
            '$string_unset_cv_range_plan(' + state + ') = eps',
            'PhpStep: ' + state + ' ~> ' + state + '_next',
            state + '_next = ' + state + '[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    checks += default_checks() + [
        '$string_unset_cv_range_plan(S_P[.COMPLETION = BUDGET]) = eps',
        '$string_unset_cv_range_plan(S_P[.RESULT = KNOWN (PINT 7)]) = eps',
        '$string_unset_cv_range_plan(S_P[.STORE[n_key] = DEFINED (PFLOAT 0)]) = eps',
        'S_first_pending = S_range_next[.STORE[n_key] = DEFINED (PFLOAT n_bits)]',
        '$string_unset_cv_range_plan(S_first_pending) = eps',
        '$string_unset_bool_cv_post_discard_cell(S_first_pending, n_key_name*, z_key, n_key)',
        '$error_read_discard(S_first_pending, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = S_first_pending',
    ]
    derived = len(checks) - reached
    checks += [
        'S_done = $drive_steps(S_range_next, 2000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.EXITSTATUS = 0',
        r'S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
        'S_done.ERRORHANDLER = S_E.ERRORHANDLER',
        'S_done.STORE[n_key] = S_range_D.STORE[n_key]',
        '$review_cv_outputs(S_done.EVENTS) = ' + shared.term(cases.OUTPUTS[cases.THROW]),
        '$float_post_diagnostics(S_done.EVENTS) = eps',
        *shared.public('S_done'),
        '$drive_steps(S_range_D, 2000) = S_done',
        '$drive_steps(S_range_A, 2000) = S_done',
        '$drive_steps(S_P, 2000) = S_done',
        '$drive_steps(S_E, 2000) = S_done',
    ]
    return checks, derived


if __name__ == '__main__':
    FRONT_ONLY = '--front-only' in sys.argv
    if FRONT_ONLY:
        sys.argv.remove('--front-only')
    DEFAULT_ONLY = '--default-only' in sys.argv
    if DEFAULT_ONLY:
        sys.argv.remove('--default-only')
        assert not FRONT_ONLY
    own = Path(__file__).resolve()
    watched = [own, Path(shared.__file__), Path(shared.seek.__file__), Path(shared.sl.__file__),
               Path(cases.prior.__file__), Path(cases.prior.prior.__file__),
               Path(sys.modules[shared.public.__module__].__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = shared.runner
    runner.NAME, runner.OUTPUT = cases.THROW, cases.OUTPUTS[cases.THROW]
    runner.cases, runner.conditions, runner.PREFIX = cases, conditions, PREFIX
    runner.recorded = shared.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('New secondary-throw source reaches the old NORMAL BOOL-CV resume after its first '
        'handler returns. Actual source/CODE/saved n/finite nonfitting bits/full quiet read, restored '
        'eligible callback and existing pure range formatter precede the current exact Unsupported step. '
        'No new range-plan/task premise establishes reachability. Source0/native0; exact native reused.' if FRONT_ONLY else
        'Only two formerly refused normal Warning-excluding mask controls now use the existing stderr '
        'default renderer and copied range task with the exact original caller tail. The old fixture '
        'display profile stays literal; closed full secondThrow/whole campaigns are not renewed. '
        'Source0/native0; exact saved native reused.' if DEFAULT_ONLY else
        'Independent secondary Warning preserves the entire actual caller tail and copied finite OOB '
        'bits/source/saved-cell authority. Actual second callback overwrites the old CV with INTERNED '
        'done; selected task remains valid without snapshot reread, generic discard preserves the same '
        'range Exception and raw callback, no task roots and exact whole/split equality. Forged '
        'source/line/level/message/event/snapshot/bits and absent/ref guards refuse; normal '
        'Warning-excluding masks use existing default reporting. '
        'First pending finite-OOB discard stays separate. Source0/native0; exact native reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
