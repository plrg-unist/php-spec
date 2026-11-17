#!/usr/bin/env python3
"""Independent restored-mask default Warning and normal range continuation."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_float_post_review_state as shared
import string_offset_nested_unset_bool_cv_range_default_cases as cases

PREFIX = shared.PREFIX
FRONT_ONLY = False


def conditions(program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    checks = [
        'S_I = $php_display_run(' + program + ', 0, ' + encoded + ', eps, ($ptascii("stderr")))',
        'S_I.COMPLETION = BUDGET',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_E.ENV, n_key_name*) = (n_key)',
        'S_E.STORE[n_key] = DEFINED (PBOOL true)',
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_E.ERRORHANDLER.LEVELS = 30719',
        'S_E.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}]',
        'S_E.DISPLAYINIT = ($ptascii("stderr"))',
        'S_E.DISPLAYINI = S_E.DISPLAYINIT',
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
        'ptask_after* = ptask_first :: ptask_rest*',
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
        '$string_unset_cv_range_snapshot(S_P, porigin_site, z, n_key, n_bits)',
        'S_P.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_P.ERRORHANDLER.LEVELS = 0',
        'S_P.ERRORHANDLERS = eps',
        '~$error_handler_eligible(S_P, 2)',
        '$arithmetic_add_named(S_P)',
        'S_P.REPORTING = 30719',
        'S_P.DISPLAYINIT = S_E.DISPLAYINIT',
        'S_P.DISPLAYINI = S_E.DISPLAYINI',
        '$display_state_mode(S_P) = 2',
        'S_P.OUTPUTBUFFERS = eps',
        'S_P.RESULT = KNOWN PNULL',
        r'S_P.CURRENT = eps /\ S_P.FRAMES = eps /\ S_P.HELD = eps /\ S_P.REQUEST = eps',
        r'S_P.SOURCEPENDING = eps /\ S_P.CONSTCONTEXT = eps',
        '~$eval_compile_recorded_error(S_P, 2)',
        '~$recorded_runtime_pending(S_P, 2)',
        'S_P.ERRORFATALTRACE = eps',
        '$integer_float_notices([RANGEWARNING], n_bits) = [(2, n_message*)]',
        'n_message* = $ptascii("The float 1.0E+20 is not representable as an int, cast occurred")',
        'pevent_range = DIAGNOSTIC "Warning" n_message* z',
        '$event_source(S_P, pevent_range) = pevent_range',
        '$display_events(S_P, pevent_range) = [pevent_range]',
        '$error_default(S_P, pevent_range, 2) = S_P[.EVENTS = S_P.EVENTS ++ [pevent_range]]',
        '$review_cv_outputs(S_P.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        '$float_post_diagnostics(S_P.EVENTS) = eps',
        *shared.public('S_P'),
    ]
    if FRONT_ONLY:
        return checks + [
            'PhpStep: S_P ~> S_unsupported',
            'S_unsupported = S_P[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
        ], 0
    checks += [
        '$lookup(S_P.ENV, n_base_name*) = (n_base)',
        '$lookup(S_P.ENV, $ptascii("last")) = (n_last)',
        '$string_unset_cv_range_plan(S_P) = ((porigin_site, z, n_key, n_bits))',
        'ptask_range = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key n_bits',
        '$task_nodes(ptask_range) = eps',
        'PhpStep: S_P ~> S_default',
        'S_default.TODO = ptask_range :: ptask_after*',
        'S_default = S_P[.TODO = ptask_range :: ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.ERRORFATALTRACE = eps][.EVENTS = S_P.EVENTS ++ [pevent_range]]',
        '$call_task_valid(S_default, ptask_range)',
        'S_default.ERRORHANDLER = S_P.ERRORHANDLER',
        'S_default.ERRORHANDLERS = eps',
        '$review_cv_outputs(S_default.EVENTS) = $review_cv_outputs(S_P.EVENTS)',
        '$float_post_diagnostics(S_default.EVENTS) = [pevent_range]',
        '$heap_graph(S_default) = $heap_graph(S_P)',
        '$drive_steps(S_P, 0) = S_P[.COMPLETION = BUDGET]',
        '$drive_steps(S_P, 1) = S_default[.COMPLETION = BUDGET]',
        *shared.public('S_default'),
        'PhpStep: S_default ~> S_error',
        'S_error = S_default[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
        'S_Q = $drive_steps(S_default, 1)',
        'S_Q.COMPLETION = BUDGET',
        'S_Q.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_Q.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "Error"',
        '$throwable_field(S_Q, n_error, "message") = PSTRING ($ptascii("Cannot use string offset as an array"))',
        '$throwable_field(S_Q, n_error, "line") = PINT z',
        'S_Q.EVENTS = S_default.EVENTS',
        'S_Q.ERRORHANDLER = S_P.ERRORHANDLER',
        *shared.public('S_Q'),
    ]
    reached = len(checks)
    for tag, changed in (
        ('absent', 'S_P[.ERRORHANDLER.CALLBACK = eps]'),
        ('nonfinite', 'S_P[.STORE[n_key] = DEFINED (PFLOAT 9218868437227405312)]'),
    ):
        state = 'S_default_bad_' + tag
        checks += [state + ' = ' + changed,
            '$string_unset_cv_range_plan(' + state + ') = eps',
            'PhpStep: ' + state + ' ~> ' + state + '_next',
            state + '_next = ' + state + '[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    checks += [
        'S_unreported = S_P[.REPORTING = 0][.REPORTINGINI = $ptascii("0")][.REPORTINGMODIFIED = true]',
        '$string_unset_cv_range_plan(S_unreported) = ((porigin_site, z, n_key, n_bits))',
        'PhpStep: S_unreported ~> S_unreported_next',
        'S_unreported_next = S_default[.REPORTING = 0][.REPORTINGINI = $ptascii("0")][.REPORTINGMODIFIED = true][.EVENTS = S_P.EVENTS]',
        'S_pending = S_Q[.COMPLETION = NORMAL]',
        '$string_unset_cv_range_plan(S_pending) = eps',
        '~$string_unset_bool_cv_post_discard_cell(S_pending, n_key_name*, z_key, n_key)',
        '$error_read_discard(S_pending, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = S_pending[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
    ]
    derived = len(checks) - reached
    checks += [
        'S_done = $drive_steps(S_Q[.COMPLETION = NORMAL], 2000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.EXITSTATUS = 0',
        r'S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
        'S_done.ERRORHANDLER = S_P.ERRORHANDLER',
        'S_done.ERRORHANDLERS = eps',
        'S_done.STORE[n_key] = S_P.STORE[n_key]',
        'S_done.STORE[n_base] = S_P.STORE[n_base]',
        'S_done.STORE[n_last] = S_P.STORE[n_last]',
        r'S_done.CODE = S_P.CODE /\ S_done.POOLS = S_P.POOLS',
        '$review_cv_outputs(S_done.EVENTS) = ' + shared.term(cases.OUTPUTS[tuple(cases.CASES)[1]]),
        '$float_post_diagnostics(S_done.EVENTS) = [pevent_range]',
        *shared.public('S_done'),
        '$drive_steps(S_E, 2000) = S_done',
        '$drive_steps(S_A, 2000) = S_done',
        '$drive_steps(S_P, 2000) = S_done',
        '$drive_steps(S_default, 2000) = S_done',
    ]
    return checks, derived


if __name__ == '__main__':
    FRONT_ONLY = '--front-only' in sys.argv
    if FRONT_ONLY:
        sys.argv.remove('--front-only')
    own = Path(__file__).resolve()
    watched = [own, Path(shared.__file__), Path(shared.seek.__file__), Path(shared.sl.__file__),
               Path(cases.prior.__file__), Path(cases.prior.prior.__file__),
               Path(sys.modules[shared.public.__module__].__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = shared.runner
    runner.NAME = tuple(cases.CASES)[1]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions, runner.PREFIX = cases, conditions, PREFIX
    runner.recorded = shared.sl.recorded
    passed = runner.main(expected_stderr=cases.stderr)
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Actual NORMAL first-handler return restores its raw named callback but keeps '
        'the popped initial mask0. Original source/CODE/saved ordinary cell/quiet finite OOB bits, '
        'matching stderr initialization, reporting and existing default renderer facts precede the '
        'old exact Unsupported step. No future plan premise proves reachability. Source0/native0; '
        'the two fresh normal native identities are reused without execution.' if FRONT_ONLY else
        'Actual NORMAL first-handler return restores the original named callback with mask0. The '
        'existing default dispatcher appends one source-anchored stderr Warning, retains the copied '
        'nonowning task and entire caller tail without another callback, then raises the fixed Error. '
        'Exact raw/public states, real Error identity/line, no added owners, source storage and whole/split '
        'are retained. Absent/nonfinite and pending masked discard stay outside admission; reporting0 '
        'uses the existing suppression rule. Source0/native0; exact fresh native reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
