#!/usr/bin/env python3
"""Independent reached INTERNED posts, quiet discard and identity refusals."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import encoding_declare_protocol as structure
import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as seek
import string_offset_nested_unset_bool_cv_interned_post_cases as cases

INDEX = 1
PRELAW = False
term = lambda data: '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


def conditions(program, path):
    name = tuple(cases.CASES)[INDEX]
    throwing = cases.THROWING[name]
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
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
        'S_E.STORE[n_key] = DEFINED ' + cases.ENTRY_VALUES[name],
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        '$task_nodes(' + resume + ') = eps',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_original_tail*',
        'perrorcall_first.RESUME = ' + resume,
        '$error_call_valid(S_A, perrorcall_first)',
        'S_P_found = $review_cv_seek(S_A, "' + ('discard' if throwing else 'resume') + '", 1000)',
        '$review_cv_at(S_P_found, "' + ('discard' if throwing else 'resume') + '")',
        'S_P = $review_cv_running(S_P_found)',
        '$string_unset_bool_cv_source(S_P, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        '$lookup(S_P.ENV, n_key_name*) = (n_key)',
        '$(n_key < |S_P.STORE|)',
        '~$environment_blocked(S_P, n_key_name*)',
        '~(n_key <- S_P.REFCELLS)',
        '~$foreach_released_cell(S_P, n_key)',
        '~$typed_cv_string_released_cell(S_P, n_key)',
        '~$update_released_cell(S_P, n_key)',
        'n_bytes* = ' + term(cases.POST_BYTES[name]),
        'pvalue_post = PSTRING_CARRIER INTERNED_STRING n_bytes*',
        'S_P.STORE[n_key] = DEFINED pvalue_post',
        '$string_carrier_valid(S_P, pvalue_post)',
        '$startup_bytes(n_bytes*) /\\ $c_string(n_bytes*) = n_bytes*',
        '$resolve_at(S_P, VARIABLE n_key_name* z_key, z_key) = S_P[.RESULT = KNOWN pvalue_post]',
        '$value_nodes(pvalue_post) = eps',
        'S_P.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_P.ERRORHANDLER.LEVELS = ' + str(cases.MASKS[name]),
        '$call_task_valid(S_P, ' + resume + ')',
        '$review_cv_outputs(S_P.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        r'S_P.REQUEST = eps /\ S_P.CURRENT = eps /\ S_P.FRAMES = eps /\ S_P.HELD = eps',
        r'S_P.SOURCEPENDING = eps /\ S_P.CONSTCONTEXT = eps',
        *structure.public('S_P'),
    ]
    if throwing:
        checks += [
            'S_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = ' + resume,
            'perrorcall_entered.CALLBACK = pvalue_callback',
            'S_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_cut = S_P[.TODO = (THROW_SEARCH n_throwable) :: ptask_after*]',
            'S_R = $error_handler_restore(S_cut, pvalue_callback)',
            'S_R = S_cut[.ERRORHANDLER.CALLBACK = (pvalue_callback)]',
        ]
    else:
        checks += ['S_R = S_P', 'S_R.TODO = (' + resume + ') :: ptask_after*']
    checks += ['ptask_after* = ptask_first :: ptask_rest*',
        '~$string_unset_bool_cv_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_cv_range_snapshot(S_R, porigin_site, z, n_key, 4906019910204099648)',
        '$string_unset_cv_range_plan(S_R) = eps',
        '~$string_unset_cv_range_discard(S_R, ' + resume + ')']
    if PRELAW:
        checks += ['~$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)']
        if throwing:
            checks += ['$error_read_discard(S_R, ' + resume + ') = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
                'PhpStep: S_P ~> S_bad', 'S_bad = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        else:
            checks += ['PhpStep: S_R ~> S_bad',
                'S_bad = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        return checks, 0
    checks += ['$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$drive_steps(S_P, 0) = S_P[.COMPLETION = BUDGET]']
    if throwing:
        checks += ['$error_read_discard(S_R, ' + resume + ') = S_R',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R',
            'PhpStep: S_P ~> S_R',
            '$drive_steps(S_P, 1) = S_R[.COMPLETION = BUDGET]']
    else:
        checks += ['PhpStep: S_R ~> S_error',
            'S_error = S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]']
    checks += ['S_DONE = $drive_steps(S_P, 2000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        'S_DONE.STORE[n_key] = S_R.STORE[n_key]',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        'S_DONE.CODE = S_R.CODE /\\ S_DONE.POOLS = S_R.POOLS',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + term(cases.OUTPUTS[name]),
        *structure.public('S_DONE'),
        '$drive_steps(S_E, 2000) = S_DONE', '$drive_steps(S_A, 2000) = S_DONE']
    reached = len(checks)
    for i, data in enumerate((b'', b'word', b'7x', b'1.5', b'1e20', b'-1e20', b'1e309', b'\xff')):
        state = 'S_string_' + str(i)
        checks += [state + ' = S_R[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING (' + term(data) + '))]',
            '$string_unset_bool_cv_post_normal_cell(' + state + ', n_key_name*, z_key, n_key)',
            '~$string_unset_cv_range_snapshot(' + state + ', porigin_site, z, n_key, 4906019910204099648)']
        if throwing:
            checks += ['$error_read_discard(' + state + ', ' + resume + ') = ' + state]
        else:
            checks += ['PhpStep: ' + state + ' ~> ' + state + '_error',
                state + '_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z',
                state + '_error.EVENTS = ' + state + '.EVENTS']
    checks += ['n_request = |S_R.STRINGDATA|',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) n_bytes*',
        'S_request = S_R[.STRINGDATA = S_R.STRINGDATA ++ [n_bytes*]][.STORE[n_key] = DEFINED pvalue_request]',
        '$string_carrier_valid(S_request, pvalue_request)',
        '$heap_valid($heap_graph(S_request))']
    for tag, changed in (
        ('request', 'S_request'),
        ('unknown', 'S_R[.STORE[n_key] = DEFINED (PSTRING n_bytes*)]'),
        ('nul', 'S_R[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([49,0,50]))]'),
        ('invalid', 'S_R[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([256]))]'),
        ('reference', 'S_R[.REFCELLS = S_R.REFCELLS ++ [n_key]]'),
        ('undefined', 'S_R[.STORE[n_key] = UNDEFINED]'),
        ('absent', 'S_R[.ENV = $unbind(S_R.ENV, n_key_name*)]'),
    ):
        state = 'S_refused_' + tag
        checks += [state + ' = ' + changed,
            '~$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)']
        if throwing:
            checks += ['$error_read_discard(' + state + ', ' + resume + ') = ' + state + '[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
        else:
            checks += ['PhpStep: ' + state + ' ~> ' + state + '_next',
                state + '_next = ' + state + '[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    return checks, len(checks) - reached


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(seek.__file__), Path(sl.__file__), Path(structure.__file__),
               *[runner.ROOT / name for name in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 3)
    if '--prelaw' in sys.argv:
        PRELAW = True
        sys.argv.remove('--prelaw')
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = seek.PREFIX, sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent reached source/INTERNED/quiet read/owner-free facts before law; source0/native0.' if PRELAW else
        'Independent exact ordinary INTERNED post, whole/split Error or same pending Throwable/tail, '
        'quiet text classes and valid same-byte REQUEST/UNKNOWN/NUL/reference refusals. Source0/native0; no closed replay.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
