#!/usr/bin/env python3
"""Actual pending finite-range state before default Warning admission."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as shared
import string_offset_nested_unset_bool_cv_pending_range_cases as cases

PRELAW = False


def front(program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    return [
        'S_I = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_I.COMPLETION = BUDGET',
        'S_I.DISPLAYINI = ($ptascii("stderr"))',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        'S_E.STORE[n_key] = DEFINED (PBOOL false)',
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_E.ERRORHANDLER.LEVELS = 30719',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_original_tail*',
        'perrorcall_first.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_A, perrorcall_first)',
        'S_D_found = $review_cv_seek(S_A, "discard", 1000)',
        '$review_cv_at(S_D_found, "discard")',
        'S_D = $review_cv_running(S_D_found)',
        'S_D.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
        'perrorcall_entered.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        'perrorcall_entered.CALLBACK = pvalue_callback',
        'S_D.OBJECTS[n_throwable] = THROWABLE pthrowable',
        'pthrowable.KIND = "Exception"',
        'S_D.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_D.ERRORHANDLER.LEVELS = 512',
        'S_cut = S_D[.TODO = (THROW_SEARCH n_throwable) :: ptask_after*]',
        '$identity_read_discard(S_cut, perrorcall_entered.RESUME) = S_cut',
        'S_R = $error_handler_restore(S_cut, pvalue_callback)',
        'S_R = S_cut[.ERRORHANDLER.CALLBACK = (pvalue_callback)]',
        'S_R.COMPLETION = NORMAL',
        'S_R.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
        'ptask_after* = ptask_first :: ptask_rest*',
        r'S_R.REQUEST = eps /\ S_R.CURRENT = eps /\ S_R.FRAMES = eps /\ S_R.HELD = eps',
        r'S_R.SOURCEPENDING = eps /\ S_R.CONSTCONTEXT = eps',
        'S_R.RESULT = KNOWN PNULL',
        '$lookup(S_R.ENV, n_key_name*) = (n_key)',
        '~(n_key <- S_R.REFCELLS)',
        '~$foreach_released_cell(S_R, n_key)',
        '~$typed_cv_string_released_cell(S_R, n_key)',
        '~$update_released_cell(S_R, n_key)',
        'n_bits = ' + str(cases.BITS),
        'S_R.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$float_decode(n_bits) = FINITE n_sign n_num n_den',
        '~$fparts_fits($float_decode(n_bits))',
        '$resolve_at(S_R, VARIABLE n_key_name* z_key, z_key) = S_R[.RESULT = KNOWN (PFLOAT n_bits)]',
        '$string_unset_cv_range_snapshot(S_R, porigin_site, z, n_key, n_bits)',
        '$call_task_valid(S_R, perrorcall_entered.RESUME)',
        '$throwable_member(S_R, n_throwable)',
        '$arithmetic_add_named(S_R)',
        '~$error_handler_eligible(S_R, 2)',
        '~$eval_compile_recorded_error(S_R, 2)',
        '~$recorded_runtime_pending(S_R, 2)',
        '$review_cv_outputs(S_R.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        'S_R.ERRORFATALTRACE = eps',
        '$display_mode(S_R.DISPLAYINI) = 2',
        '$long_and(S_R.REPORTING, 2) = 2',
        'S_R.OUTPUTBUFFERS = eps',
        '$call_sourcefile(S_R.FILES, porigin_site) = $base64(' + encoded + ')',
        'z = 5',
        '$integer_float_notices([RANGEWARNING], n_bits) = [(2, n_message*)]',
        'n_message* = $ptascii("The float 1.0E+20 is not representable as an int, cast occurred")',
        'pevent_range = DIAGNOSTIC "Warning" n_message* z',
        '$error_default_event(S_R, pevent_range) = pevent_range',
        '$display_events(S_R, pevent_range) = [pevent_range]',
        '$error_dispatch(S_R, 2, n_message*, z, pevent_range, THROW_SEARCH n_throwable) = S_R[.EVENTS = S_R.EVENTS ++ [pevent_range]]',
        *shared.public('S_R'),
    ]


def conditions(program, path):
    checks = front(program, path)
    if PRELAW:
        return checks + [
        '~$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
        '$error_read_discard(S_R, perrorcall_entered.RESUME) = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
        'PhpStep: S_D ~> S_old',
        'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
        ], 0
    checks += [
        '$string_unset_cv_range_discard(S_R, perrorcall_entered.RESUME)',
        '~$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
        'S_report = S_R[.EVENTS = S_R.EVENTS ++ [pevent_range]]',
        '$error_read_discard(S_R, perrorcall_entered.RESUME) = S_report',
        '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_report',
        'PhpStep: S_D ~> S_report',
        'S_report.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
        'S_report.OBJECTS = S_R.OBJECTS',
        'S_report.ERRORHANDLER = S_R.ERRORHANDLER',
        '$heap_graph(S_report) = $heap_graph(S_R)',
        '$drive_steps(S_D, 0) = S_D[.COMPLETION = BUDGET]',
        '$drive_steps(S_D, 1) = S_report[.COMPLETION = BUDGET]',
        *shared.public('S_report'),
        'S_DONE = $drive_steps(S_report, 2000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        'S_DONE.STORE[n_key] = S_R.STORE[n_key]',
        'S_DONE.OBJECTS[n_throwable] = S_R.OBJECTS[n_throwable]',
        r'S_DONE.CODE = S_R.CODE /\ S_DONE.POOLS = S_R.POOLS',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + shared.term(cases.OUTPUTS[cases.NAME]),
        *shared.public('S_DONE'),
        '$drive_steps(S_D, 2000) = S_DONE',
        '$drive_steps(S_A, 3000) = S_DONE',
        '$drive_steps(S_E, 3000) = S_DONE',
        'n_missing = |S_R.OBJECTS|',
    ]
    reached = len(checks)
    for changed in (
        'S_R[.COMPLETION = BUDGET]', 'S_R[.TODO = eps]',
        'S_R[.TODO = (THROW_SEARCH n_missing) :: ptask_after*]',
        'S_R[.OBJECTS[n_throwable] = THROWABLE pthrowable[.KIND = "stdClass"]]',
        'S_R[.SOURCES = eps]', 'S_R[.CODE = eps]', 'S_R[.ORIGIN = eps]',
        'S_R[.ERRORHANDLER.CALLBACK = eps]',
        'S_R[.ERRORHANDLER.CALLBACK = (PARRAY 0)]',
        'S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
        'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
        'S_R[.STORE[n_key] = UNDEFINED]',
        'S_R[.STORE[n_key] = DEFINED (POBJECT 0)]',
        'S_R[.STORE[n_key] = DEFINED (PFLOAT 18446744073709551616)]',
        'S_R[.HELD = [HOBJECT n_throwable]]',
    ):
        checks.append('~$string_unset_cv_range_discard(' + changed + ', perrorcall_entered.RESUME)')
    checks += [
        'S_zero = S_R[.ERRORHANDLER.LEVELS = 0]',
        '$string_unset_cv_range_discard(S_zero, perrorcall_entered.RESUME)',
        '$error_read_discard(S_zero, perrorcall_entered.RESUME) = S_report[.ERRORHANDLER.LEVELS = 0]',
        'S_eligible = S_R[.ERRORHANDLER.LEVELS = 30719]',
        '~$string_unset_cv_range_discard(S_eligible, perrorcall_entered.RESUME)',
        '$string_unset_bool_cv_post_discard_cell(S_eligible, n_key_name*, z_key, n_key)',
        '$error_read_discard(S_eligible, perrorcall_entered.RESUME) = S_eligible',
        'S_fit = S_R[.STORE[n_key] = DEFINED (PFLOAT 4609434218613702656)]',
        '~$string_unset_cv_range_discard(S_fit, perrorcall_entered.RESUME)',
        '$error_read_discard(S_fit, perrorcall_entered.RESUME) = S_fit',
        'S_quiet = S_R[.REPORTING = 0][.REPORTINGINI = $ptascii("0")][.REPORTINGMODIFIED = true]',
        '$string_unset_cv_range_discard(S_quiet, perrorcall_entered.RESUME)',
        '$error_read_discard(S_quiet, perrorcall_entered.RESUME) = S_quiet',
        'S_hidden = S_R[.DISPLAYINI = ($ptascii("0"))][.DISPLAYMODIFIED = true]',
        '$string_unset_cv_range_discard(S_hidden, perrorcall_entered.RESUME)',
        '$error_read_discard(S_hidden, perrorcall_entered.RESUME) = S_hidden',
    ]
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    own = Path(__file__).resolve()
    watched = [own, Path(shared.__file__), Path(sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.NAME, runner.OUTPUT = cases.NAME, cases.OUTPUTS[cases.NAME]
    runner.cases, runner.conditions, runner.PREFIX, runner.recorded = cases, conditions, shared.PREFIX, sl.recorded
    passed = runner.main(expected_stderr=cases.stderr)
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Prelaw actual callback throw, raw restoration, live512 mask, saved ordinary finite-OOB CV, '
        'exact pending Throwable/tail and existing default renderer precede Unsupported. Source0/native0.' if PRELAW else
        'Actual callback throw and raw restoration preserve the saved ordinary finite-OOB CV. Existing default '
        'reporting adds one Warning while retaining the exact Throwable, complete caller tail and full state/heap. '
        'Quiet/eligible/fitting and refusal controls stay distinct. Whole/split; source0/native0, saved original reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
