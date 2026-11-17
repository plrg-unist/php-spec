#!/usr/bin/env python3
"""Actual normal mask512 range reporting, exact continuation and renderer."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as shared
import string_offset_nested_unset_bool_cv_range_default_cases as cases

NAME = tuple(cases.CASES)[0]
PENDING_ONLY = False


def front(program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    checks = [
        'S_I = $php_display_run(' + program + ', 0, ' + encoded + ', eps, ($ptascii("stderr")))',
        'S_I.COMPLETION = BUDGET',
        'S_I.DISPLAYINI = ($ptascii("stderr"))',
        'S_I.DISPLAYINIT = S_I.DISPLAYINI',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        'S_E.STORE[n_key] = DEFINED (PBOOL true)',
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_E.ERRORHANDLER.LEVELS = 30719',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_after*',
        'perrorcall_first.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_A, perrorcall_first)',
        'S_R_found = $review_cv_seek(S_A, "resume", 1000)',
        '$review_cv_at(S_R_found, "resume")',
        'S_R = $review_cv_running(S_R_found)',
        'S_R.COMPLETION = NORMAL',
        'S_R.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
        'ptask_after* = ptask_first :: ptask_rest*',
        '$string_unset_bool_cv_source(S_R, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_R.ENV, n_key_name*) = (n_key)',
        '~(n_key <- S_R.REFCELLS)',
        '~$foreach_released_cell(S_R, n_key)',
        '~$typed_cv_string_released_cell(S_R, n_key)',
        '~$update_released_cell(S_R, n_key)',
        'n_bits = ' + str(cases.BITS),
        'S_R.STORE[n_key] = DEFINED (PFLOAT n_bits)',
        '$(n_bits < 18446744073709551616)',
        '$float_decode(n_bits) = FINITE n_sign n_num n_den',
        '~$fparts_fits($float_decode(n_bits))',
        '$resolve_at(S_R, VARIABLE n_key_name* z_key, z_key) = S_R[.RESULT = KNOWN (PFLOAT n_bits)]',
        '$string_unset_cv_range_snapshot(S_R, porigin_site, z, n_key, n_bits)',
        'S_R.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_R.ERRORHANDLER.LEVELS = 512',
        '~$error_handler_eligible(S_R, 2)',
        '$arithmetic_add_named(S_R)',
        r'S_R.REQUEST = eps /\ S_R.CURRENT = eps /\ S_R.FRAMES = eps /\ S_R.HELD = eps',
        r'S_R.SOURCEPENDING = eps /\ S_R.CONSTCONTEXT = eps',
        'S_R.RESULT = KNOWN PNULL',
        'S_R.DISPLAYINI = S_I.DISPLAYINI',
        'S_R.DISPLAYINIT = S_I.DISPLAYINIT',
        '$display_mode(S_R.DISPLAYINI) = 2',
        '$long_and(S_R.REPORTING, 2) = 2',
        'S_R.OUTPUTBUFFERS = eps',
        'S_R.ERRORFATALTRACE = eps',
        'porigin_site = PORIGIN 0 pcpath_site',
        '$call_sourcefile(S_R.FILES, porigin_site) = $base64(' + encoded + ')',
        'z = 5',
        '$integer_float_notices([RANGEWARNING], n_bits) = [(2, n_message*)]',
        'n_message* = $ptascii("The float 1.0E+20 is not representable as an int, cast occurred")',
        'pevent_range = DIAGNOSTIC "Warning" n_message* z',
        '$error_default_event(S_R, pevent_range) = pevent_range',
        '$display_events(S_R, pevent_range) = [pevent_range]',
        '$error_default(S_R, pevent_range, 2) = S_R[.EVENTS = S_R.EVENTS ++ [pevent_range]]',
        '$review_cv_outputs(S_R.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        *shared.public('S_R'),
    ]
    return checks


def conditions(program, path):
    if PENDING_ONLY:
        checks = front(program, path) + [
            'S_report = S_R[.TODO = (STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits) :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps][.EVENTS = S_R.EVENTS ++ [pevent_range]]',
            'S_pending_budget = $drive_steps(S_report, 1)',
            'S_pending = $review_cv_running(S_pending_budget)',
            'S_pending.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            'S_pending.OBJECTS[n_error] = THROWABLE pthrowable',
            'pthrowable.KIND = "Error"',
        ]
        changed = pending_checks()
        return checks + changed, len(changed)
    checks = front(program, path) + [
        '$string_unset_cv_range_plan(S_R) = ((porigin_site, z, n_key, n_bits))',
        'ptask_range = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits',
        '$task_nodes(ptask_range) = eps',
        'PhpStep: S_R ~> S_report',
        'S_report = S_R[.TODO = ptask_range :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps][.EVENTS = S_R.EVENTS ++ [pevent_range]]',
        'S_report.TODO = ptask_range :: ptask_after*',
        'S_report.ERRORHANDLER = S_R.ERRORHANDLER',
        '$call_task_valid(S_report, ptask_range)',
        '$heap_graph(S_report) = $heap_graph(S_R)',
        '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]',
        '$drive_steps(S_R, 1) = S_report[.COMPLETION = BUDGET]',
        *shared.public('S_report'),
        'PhpStep: S_report ~> S_error',
        'S_error = S_report[.TODO = ptask_after*][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
        'S_error.EVENTS = S_report.EVENTS',
        'S_DONE = $drive_steps(S_report, 2000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        'S_DONE.STORE[n_key] = S_R.STORE[n_key]',
        r'S_DONE.CODE = S_R.CODE /\ S_DONE.POOLS = S_R.POOLS',
        '$review_cv_outputs(S_DONE.EVENTS) = $base64(' + json.dumps(base64.b64encode(cases.OUTPUTS[NAME]).decode()) + ')',
        *shared.public('S_DONE'),
        '$drive_steps(S_R, 2000) = S_DONE',
        '$drive_steps(S_E, 3000) = S_DONE',
    ]
    reached = len(checks)
    for tag, changed in (
        ('absent_handler', 'S_R[.ERRORHANDLER.CALLBACK = eps]'),
        ('nonnamed', 'S_R[.ERRORHANDLER.CALLBACK = (PARRAY 0)]'),
        ('budget', 'S_R[.COMPLETION = BUDGET]'),
        ('no_source', 'S_R[.SOURCES = eps]'),
        ('no_code', 'S_R[.CODE = eps]'),
        ('no_origin', 'S_R[.ORIGIN = eps]'),
        ('reference', 'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]'),
        ('undefined', 'S_R[.STORE[n_key] = UNDEFINED]'),
        ('owning', 'S_R[.STORE[n_key] = DEFINED (POBJECT 0)]'),
        ('nonfinite', 'S_R[.STORE[n_key] = DEFINED (PFLOAT 9218868437227405312)]'),
        ('out_bits', 'S_R[.STORE[n_key] = DEFINED (PFLOAT 18446744073709551616)]'),
    ):
        checks.append('$string_unset_cv_range_plan(' + changed + ') = eps')
    checks += [
        '$error_handler_restore(S_R[.ERRORHANDLER.CALLBACK = eps], pvalue_callback) = S_R',
        'S_quiet = S_R[.REPORTING = 0][.REPORTINGINI = $ptascii("0")][.REPORTINGMODIFIED = true]',
        '$string_unset_cv_range_plan(S_quiet) = ((porigin_site, z, n_key, n_bits))',
        'PhpStep: S_quiet ~> S_quiet_report',
        'S_quiet_report = S_quiet[.TODO = ptask_range :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps]',
        'S_hidden = S_R[.DISPLAYINI = ($ptascii("0"))][.DISPLAYMODIFIED = true]',
        '$string_unset_cv_range_plan(S_hidden) = ((porigin_site, z, n_key, n_bits))',
        'PhpStep: S_hidden ~> S_hidden_report',
        'S_hidden_report = S_hidden[.TODO = ptask_range :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps]',
        'S_pending_budget = $drive_steps(S_report, 1)',
        'S_pending = $review_cv_running(S_pending_budget)',
        'S_pending.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_pending.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "Error"',
    ] + pending_checks()
    return checks, len(checks) - reached


def pending_checks():
    return [
        '$string_unset_cv_range_plan(S_pending) = eps',
        '~$string_unset_bool_cv_post_discard_cell(S_pending, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_discard(S_pending, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
        '$error_read_discard(S_pending, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = S_pending[.EVENTS = S_pending.EVENTS ++ [pevent_range]]',
    ]


if __name__ == '__main__':
    PENDING_ONLY = '--pending-only' in sys.argv
    if PENDING_ONLY:
        sys.argv.remove('--pending-only')
    own = Path(__file__).resolve()
    watched = [own, Path(shared.__file__), Path(sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.NAME, runner.OUTPUT = NAME, cases.OUTPUTS[NAME]
    runner.cases, runner.conditions, runner.PREFIX, runner.recorded = cases, conditions, shared.PREFIX, sl.recorded
    passed = runner.main(expected_stderr=cases.stderr)
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Only the prior manual pending-Error discard assertion now uses the existing default Warning '
        'while preserving its entire state and tail. Actual normal source/front remains unchanged; source0/native0.' if PENDING_ONLY else
        'Actual NORMAL first-handler resume has the saved ordinary CV/finite OOB bits, '
        'exact source/CODE/quiet read and restored same named callback with live512 mask. Existing '
        'stderr/reporting/source renderer produces exactly one range event before the copied nonowning '
        'resume raises the fixed Error, preserving the complete caller tail, state/heap and whole/split. '
        'Reporting0/display0 remain quiet; absent/nonnamed/nonfinite/owning/ref/source forgeries and '
        'pending discard uses its separate finite-OOB default-reporting route. Source0/native0, exact saved native reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
