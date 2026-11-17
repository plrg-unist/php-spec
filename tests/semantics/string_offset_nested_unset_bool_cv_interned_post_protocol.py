#!/usr/bin/env python3
"""Actual quiet INTERNED poststrings before the saved-cell admission changes."""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

import string_offset_terminal_unset_protocol as runner
import string_offset_nested_unset_null_warning_protocol as sl
import string_offset_nested_unset_bool_cv_warning_review_state as shared
import string_offset_nested_unset_bool_cv_interned_post_cases as cases

INDEX = 0
PRELAW = False


def front(program, path):
    name = tuple(cases.CASES)[INDEX]
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    return [
        'S_I = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_I.COMPLETION = BUDGET',
        'S_E_found = $review_cv_seek(S_I, "entry", 1000)',
        '$review_cv_at(S_E_found, "entry")',
        'S_E = $review_cv_running(S_E_found)',
        '$string_unset_bool_cv_plan(S_E) = ((porigin_site, z, n_key))',
        '$string_unset_bool_cv_source(S_E, porigin_site, z) = ((n_base_name*, z_outer, n_key_name*, z_key))',
        'S_E.STORE[n_key] = DEFINED ' + cases.ENTRY_VALUES[name],
        'S_E.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_E.ERRORHANDLER.LEVELS = 30719',
        '$task_nodes(STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) = eps',
        'PhpStep: S_E ~> S_A',
        'S_A.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_after*',
        'perrorcall_first.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
        '$error_call_valid(S_A, perrorcall_first)',
        'S_P_found = $review_cv_seek(S_A, "resume", 1000)',
        '$review_cv_at(S_P_found, "resume")',
        'S_P = $review_cv_running(S_P_found)',
        'S_P.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*',
        '$lookup(S_P.ENV, n_key_name*) = (n_key)',
        '~(n_key <- S_P.REFCELLS)',
        '~$foreach_released_cell(S_P, n_key)',
        '~$typed_cv_string_released_cell(S_P, n_key)',
        '~$update_released_cell(S_P, n_key)',
        'pvalue_post = ' + cases.post_value(name),
        'S_P.STORE[n_key] = DEFINED pvalue_post',
        'pvalue_post = PSTRING_CARRIER INTERNED_STRING n_post*',
        '$startup_bytes(n_post*)',
        '$c_string(n_post*) = n_post*',
        '$string_carrier_valid(S_P, pvalue_post)',
        '$value_nodes(pvalue_post) = eps',
        '$resolve_at(S_P, VARIABLE n_key_name* z_key, z_key) = S_P[.RESULT = KNOWN pvalue_post]',
        '$call_task_valid(S_P, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
        'S_P.ERRORHANDLER.CALLBACK = (pvalue_callback)',
        'S_P.ERRORHANDLER.LEVELS = 30719',
        r'S_P.REQUEST = eps /\ S_P.CURRENT = eps /\ S_P.FRAMES = eps /\ S_P.HELD = eps',
        r'S_P.SOURCEPENDING = eps /\ S_P.CONSTCONTEXT = eps',
        '$review_cv_outputs(S_P.EVENTS) = $ptascii("H:2:String offset cast occurred;")',
        *shared.public('S_P'),
    ]


def conditions(program, path):
    checks = front(program, path)
    if PRELAW:
        return checks + [
        '~$string_unset_bool_cv_post_value(pvalue_post)',
        '~$string_unset_bool_cv_post_cell(S_P, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_P, n_key_name*, z_key, n_key)',
        'PhpStep: S_P ~> S_old',
        'S_old = S_P[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
        ], 0
    name = tuple(cases.CASES)[INDEX]
    checks += [
        '$string_unset_bool_cv_post_value(pvalue_post)',
        '$string_unset_bool_cv_post_cell(S_P, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_normal_cell(S_P, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_discard_cell(S_P, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_plan(S_P) = eps',
        '~$string_unset_cv_range_snapshot(S_P, porigin_site, z, n_key, 4906019910204099648)',
        '~$string_unset_cv_range_discard(S_P, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)',
        'PhpStep: S_P ~> S_error',
        'S_error = S_P[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
        '$heap_graph(S_error) = $heap_graph(S_P)',
        '$drive_steps(S_P, 0) = S_P[.COMPLETION = BUDGET]',
        'S_B = $drive_steps(S_P, 1)',
        'S_B.COMPLETION = BUDGET',
        'S_B.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_B.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "Error"',
        'S_B.EVENTS = S_P.EVENTS',
        'S_DONE = $drive_steps($review_cv_running(S_B), 2000)',
        r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_P.ERRORHANDLER',
        'S_DONE.STORE[n_key] = DEFINED pvalue_post',
        r'S_DONE.CODE = S_P.CODE /\ S_DONE.POOLS = S_P.POOLS',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + shared.term(cases.OUTPUTS[name]),
        *shared.public('S_DONE'),
        '$drive_steps(S_P, 2000) = S_DONE',
        '$drive_steps(S_E, 3000) = S_DONE',
    ]
    reached = len(checks)
    for data in (b'', b'0', b'bad', b'7x', b'-12xyz', b' +7.9suffix', b'1e20', b'-1e20', b'1e9999', b'1e-9999', b'NAN'):
        value = '(PSTRING_CARRIER INTERNED_STRING (' + shared.term(data) + '))'
        checks += ['$string_unset_bool_cv_post_value(' + value + ')',
            '$string_unset_bool_cv_post_normal_value(' + value + ')',
            '$string_unset_bool_cv_post_cell(S_P[.STORE[n_key] = DEFINED ' + value + '], n_key_name*, z_key, n_key)']
    checks += [
        'n_request = |S_P.STRINGDATA|',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) n_post*',
        'S_request = S_P[.STRINGDATA = S_P.STRINGDATA ++ [n_post*]][.STORE[n_key] = DEFINED pvalue_request]',
        '$string_carrier_valid(S_request, pvalue_request)',
        '~$string_unset_bool_cv_post_value(pvalue_request)',
        '~$string_unset_bool_cv_post_cell(S_request, n_key_name*, z_key, n_key)',
        'n_rebound = |S_P.STORE|',
    ]
    for changed in (
        'S_P[.STORE[n_key] = DEFINED (PSTRING n_post*)]',
        'S_P[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING (n_post* ++ [0]))]',
        'S_P[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([256]))]',
        'S_P[.REFCELLS = S_P.REFCELLS ++ [n_key]]',
        'S_P[.STORE[n_key] = UNDEFINED]',
        'S_P[.STORE[n_key] = DEFINED (POBJECT 0)]',
        'S_P[.STORE[n_key] = DEFINED (PARRAY 0)]',
        'S_P[.ENV = $unbind(S_P.ENV, n_key_name*)]',
        'S_P[.ENV = (BIND n_key_name* n_rebound) :: $unbind(S_P.ENV, n_key_name*)][.STORE = S_P.STORE ++ [DEFINED pvalue_post]][.ALLOCATIONS = S_P.ALLOCATIONS ++ [HCELL n_rebound]]',
    ):
        checks.append('~$string_unset_bool_cv_post_cell(' + changed + ', n_key_name*, z_key, n_key)')
    for changed in ('S_P[.CODE = eps]', 'S_P[.SOURCES = eps]', 'S_P[.ORIGIN = eps]'):
        checks.append('~$call_task_valid(' + changed + ', STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key)')
    return checks, len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    own = Path(__file__).resolve()
    watched = [own, Path(shared.__file__), Path(sl.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 2)
    name = tuple(cases.CASES)[INDEX]
    runner.NAME, runner.OUTPUT = name, cases.OUTPUTS[name]
    runner.cases, runner.conditions, runner.PREFIX, runner.recorded = cases, conditions, shared.PREFIX, sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Prelaw actual ordinary saved CV has the source-produced valid non-NUL INTERNED poststring, '
        'full-state quiet read and zero owner nodes before exact old Unsupported. Source0/native0.' if PRELAW else
        'Actual ordinary saved CV retains the exact source-produced valid non-NUL INTERNED string through the '
        'fixed nested Error, unchanged heap/storage/events and whole/split. Quiet string-class admissions and '
        'valid REQUEST/UNKNOWN/NUL/ref/rebound/malformed refusals remain distinct. Source0/native0, native reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
