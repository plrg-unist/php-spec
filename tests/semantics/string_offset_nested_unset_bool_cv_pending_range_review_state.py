#!/usr/bin/env python3
"""Independent actual pending Exception and masked range-reporting frontier."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_float_post_review_state as shared
import string_offset_nested_unset_bool_cv_pending_range_cases as cases

PREFIX = shared.PREFIX
PRELAW = False


def conditions(program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    checks = [
        'S_I = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_I.COMPLETION = BUDGET',
        'S_I.DISPLAYINIT = ($ptascii("stderr"))',
        'S_I.DISPLAYINI = S_I.DISPLAYINIT',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_E.ENV, n_key_name*) = (n_key)',
        'S_E.STORE[n_key] = DEFINED (PBOOL false)',
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_E.ERRORHANDLER.LEVELS = 30719',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_after*',
        'perrorcall_first.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_A, perrorcall_first)',
        'S_A.STORE = S_E.STORE',
        'S_D_found = $review_cv_seek(S_A, "discard", 1000)',
        '$review_cv_at(S_D_found, "discard")',
        'S_D = $review_cv_running(S_D_found)',
        'S_D.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
        'ptask_after* = ptask_first :: ptask_rest*',
        'perrorcall_entered.RESUME = perrorcall_first.RESUME',
        'perrorcall_entered.CALLBACK = pvalue_callback',
        '$call_task_valid(S_D, ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_D.OBJECTS[n_exception] = THROWABLE pthrowable',
        'pthrowable.KIND = "Exception"',
        '$throwable_member(S_D, n_exception)',
        '$throwable_field(S_D, n_exception, "message") = PSTRING_CARRIER INTERNED_STRING ($ptascii("handler"))',
        '$throwable_field(S_D, n_exception, "line") = PINT 2',
        'S_D.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_D.ERRORHANDLER.LEVELS = 512',
        'S_cut = S_D[.TODO = (THROW_SEARCH n_exception) :: ptask_after*]',
        '$identity_read_discard(S_cut, perrorcall_entered.RESUME) = S_cut',
        '$error_handler_restore(S_cut, pvalue_callback) = S_cut',
        'S_R = S_cut',
        'S_R.COMPLETION = NORMAL',
        'S_R.ORIGIN = (porigin_site)',
        'S_R.TODO = (THROW_SEARCH n_exception) :: ptask_after*',
        r'S_R.REQUEST = eps /\ S_R.CURRENT = eps /\ S_R.FRAMES = eps /\ S_R.HELD = eps',
        r'S_R.SOURCEPENDING = eps /\ S_R.CONSTCONTEXT = eps',
        'S_R.RESULT = KNOWN PNULL',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        'porigin_key = PORIGIN 0 pcpath_key',
        '$origin_node(S_R.SOURCES, porigin_key) = (NExprVariable (BYTES text_key) metadata_key)',
        '$base64(text_key) = n_key_name*',
        '$source_line(metadata_key) = z_key',
        '$source_emission_cv(S_R, 0, pcpath_key, NExprVariable (BYTES text_key) metadata_key)',
        '$compiled_read(S_R, porigin_key) = eps',
        '$lookup(S_R.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_R.STORE|)',
        '~$environment_blocked(S_R, n_key_name*)',
        '~(n_key <- S_R.REFCELLS)',
        '~$foreach_released_cell(S_R, n_key)',
        '~$typed_cv_string_released_cell(S_R, n_key)',
        '~$update_released_cell(S_R, n_key)',
        'n_bits = ' + str(cases.BITS),
        'S_R.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$(n_bits < 18446744073709551616)',
        '$float_decode(n_bits) = FINITE n_sign n_num n_den',
        '~$fparts_fits(FINITE n_sign n_num n_den)',
        '$resolve_at(S_R, VARIABLE n_key_name* z_key, z_key) = S_R[.RESULT = KNOWN (PFLOAT n_bits)]',
        '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_snapshot(S_R, porigin_site, z, n_key, n_bits)',
        '$call_task_valid(S_R, perrorcall_entered.RESUME)',
        '$arithmetic_add_named(S_R)',
        '~$error_handler_eligible(S_R, 2)',
        '~$eval_compile_recorded_error(S_R, 2)',
        '~$recorded_runtime_pending(S_R, 2)',
        'S_R.REPORTING = 30719',
        '$display_state_mode(S_R) = 2',
        'S_R.OUTPUTBUFFERS = eps',
        'S_R.ERRORFATALTRACE = eps',
        '$call_sourcefile(S_R.FILES, porigin_site) = $base64(' + encoded + ')',
        'z = 5',
        '$integer_float_notices([RANGEWARNING], n_bits) = [(2, n_message*)]',
        'n_message* = $ptascii("The float 1.0E+20 is not representable as an int, cast occurred")',
        'pevent_range = DIAGNOSTIC "Warning" n_message* z',
        '$event_source(S_R, pevent_range) = pevent_range',
        '$display_events(S_R, pevent_range) = [pevent_range]',
        '$error_dispatch(S_R, 2, n_message*, z, pevent_range, THROW_SEARCH n_exception) = S_R[.EVENTS = S_R.EVENTS ++ [pevent_range]]',
        '$review_cv_outputs(S_R.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        '$float_post_diagnostics(S_R.EVENTS) = eps',
        *shared.public('S_D'),
        *shared.public('S_R'),
    ]
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
        'S_report.TODO = (THROW_SEARCH n_exception) :: ptask_after*',
        'S_report.OBJECTS = S_D.OBJECTS',
        'S_report.STORE = S_D.STORE',
        'S_report.ENV = S_D.ENV',
        'S_report.ERRORHANDLER = S_D.ERRORHANDLER',
        'S_report.ERRORHANDLERS = S_D.ERRORHANDLERS',
        '$float_post_diagnostics(S_report.EVENTS) = [pevent_range]',
        '$review_cv_outputs(S_report.EVENTS) = $review_cv_outputs(S_D.EVENTS)',
        '$heap_graph(S_report) = $heap_graph(S_R)',
        '$drive_steps(S_D, 0) = S_D[.COMPLETION = BUDGET]',
        '$drive_steps(S_D, 1) = S_report[.COMPLETION = BUDGET]',
        *shared.public('S_report'),
        'S_done = $drive_steps(S_report, 2000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.EXITSTATUS = 0',
        r'S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
        'S_done.OBJECTS = S_D.OBJECTS',
        'S_done.STORE[n_key] = S_R.STORE[n_key]',
        'S_done.ERRORHANDLER = S_R.ERRORHANDLER',
        'S_done.ERRORHANDLERS = S_R.ERRORHANDLERS',
        r'S_done.CODE = S_R.CODE /\ S_done.POOLS = S_R.POOLS',
        '$review_cv_outputs(S_done.EVENTS) = ' + shared.term(cases.OUTPUTS[cases.NAME]),
        '$float_post_diagnostics(S_done.EVENTS) = [pevent_range]',
        *shared.public('S_done'),
        '$drive_steps(S_D, 2000) = S_done',
        '$drive_steps(S_A, 3000) = S_done',
        '$drive_steps(S_E, 3000) = S_done',
    ]
    reached = len(checks)
    checks += ['n_missing = |S_R.OBJECTS|']
    for changed in (
        'S_R[.COMPLETION = BUDGET]',
        'S_R[.TODO = eps]',
        'S_R[.TODO = (THROW_SEARCH n_missing) :: ptask_after*]',
        'S_R[.OBJECTS[n_exception] = THROWABLE pthrowable[.KIND = "stdClass"]]',
        'S_R[.SOURCES = eps]', 'S_R[.CODE = eps]', 'S_R[.ORIGIN = eps]',
        'S_R[.ERRORHANDLER.CALLBACK = eps]',
        'S_R[.ERRORHANDLER.CALLBACK = (PARRAY 0)]',
        'S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]',
        'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]',
        'S_R[.STORE[n_key] = DEFINED (POBJECT n_exception)]',
        'S_R[.STORE[n_key] = DEFINED (PFLOAT 18446744073709551616)]',
        'S_R[.HELD = [HOBJECT n_exception]]',
    ):
        checks += ['~$string_unset_cv_range_discard(' + changed + ', perrorcall_entered.RESUME)']
    checks += [
        '~$string_unset_cv_range_discard(S_R, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site $(z + 1) n_key)',
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
    watched = [own, Path(shared.__file__), Path(shared.seek.__file__), Path(shared.sl.__file__),
               Path(cases.__file__), Path(cases.prior.__file__),
               Path(sys.modules[shared.public.__module__].__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = shared.runner
    runner.NAME, runner.OUTPUT = cases.NAME, cases.OUTPUTS[cases.NAME]
    runner.cases, runner.conditions, runner.PREFIX = cases, conditions, PREFIX
    runner.recorded = shared.sl.recorded
    passed = runner.main(expected_stderr=cases.stderr)
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent prelaw-revision source reaches the actual first-handler Exception, '
        'already re-registered named callback/live512 mask and exact pending handler-result/caller tail. '
        'Same saved ordinary cell, finite nonfitting bits, source/CODE/quiet read, real Exception '
        'message/line and existing same-head default-dispatch equality precede the old Unsupported '
        'step. No new discard predicate proves reachability. Source0/native0; exact native reused.' if PRELAW else
        'Independent actual callback throw and live512 mask retain the same finite-OOB saved cell '
        'and real Exception. Existing default reporting appends exactly one source-anchored Warning '
        'while the full restored state, identical Throwable and entire pending caller tail remain. '
        'No nested Error appears; heap, object arena, callback/mask, quiet reporting/display and '
        'whole/split are checked. Eligible/fitting identity and absent/owner/source/pending '
        'refusals stay separate. Source0/native0; exact saved native reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
