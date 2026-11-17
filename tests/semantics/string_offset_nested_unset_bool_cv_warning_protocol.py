#!/usr/bin/env python3
"""Late Boolean-CV reads retain the borrowed cell through both Warning exits."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_null_warning_protocol as null
import string_offset_nested_unset_bool_cv_warning_cases as cases

INDEX = 2
PREFIX = null.PREFIX.replace('STRING_UNSET_WARNING_RESULT porigin z',
                            'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin z n_cv')


def conditions(program, path):
    null.INDEX = int(INDEX == 1)
    checks, derived = null.conditions(program, path)
    replacements = {
        'S.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) 5)) (KNOWN PNULL) 5) (KNOWN (PINT 7)) 5':
        'S.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) 5)) (VARIABLE ($ptascii("key")) 5) 5) (KNOWN (PINT 7)) 5',
        '$string_unset_warning_source(S, porigin_site, 5) = (($ptascii("base"), 5))':
        '$string_unset_bool_cv_source(S, porigin_site, 5) = (($ptascii("base"), 5, $ptascii("key"), 5))',
        '$string_unset_warning_plan(S) = ((porigin_site, 5))':
        '$string_unset_bool_cv_plan(S) = ((porigin_site, 5, n_key))',
    }
    for old, new in replacements.items():
        assert checks.count(old) == 1
        checks[checks.index(old)] = new
    checks = [check.replace('STRING_UNSET_WARNING_RESULT porigin_site 5',
                            'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site 5 n_key') for check in checks]
    at = checks.index('$string_unset_bool_cv_plan(S) = ((porigin_site, 5, n_key))') + 1
    checks[at:at] = [
        '$lookup(S.ENV, $ptascii("key")) = (n_key)',
        'S.STORE[n_key] = DEFINED (PBOOL false)',
        '$string_unset_bool_cv_cell(S, $ptascii("key"), 5, n_key)',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        'porigin_key = PORIGIN 0 pcpath_key',
        '$origin_node(S.SOURCES, porigin_key) = (NExprVariable (BYTES text_key) metadata_key)',
        '$base64(text_key) = $ptascii("key")',
        '$variable_line(BYTES text_key, metadata_key) = 5',
        '$compiled_read(S, porigin_key) = eps',
        '$code_at(S.CODE, 0) = (pcode_key)',
        '$code_expression(pcode_key.EXPRESSIONS, pcpath_key) = ((z_key, false))',
    ]
    controls = [
        '$string_unset_bool_cv_plan(S[.ENV = $unbind(S.ENV, $ptascii("key"))]) = eps',
        '$string_unset_bool_cv_plan(S[.STORE[n_key] = UNDEFINED]) = eps',
        '$string_unset_bool_cv_plan(S[.STORE[n_key] = DEFINED (PINT 7)]) = eps',
        '$string_unset_bool_cv_plan(S[.REFCELLS = S.REFCELLS ++ [n_key]]) = eps',
        'n_oob = |S_dispatch.STORE|',
        '~$call_task_valid(S_dispatch, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site 5 n_oob)',
    ]
    if INDEX == 2:
        controls += [
            'S_flip = S_resumed[.STORE[n_key] = DEFINED (PBOOL true)]',
            '$string_unset_bool_cv_cell(S_flip, $ptascii("key"), 5, n_key)',
            'PhpStep: S_flip ~> S_flip_error',
            'S_flip_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) 5',
            r'S_flip_error.STORE = S_flip.STORE /\ S_flip_error.EVENTS = S_flip.EVENTS',
            'S_no_base = S_resumed[.ENV = $unbind(S_resumed.ENV, $ptascii("base"))]',
            '$call_task_valid(S_no_base, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site 5 n_key)',
            'PhpStep: S_no_base ~> S_no_base_error',
            'S_no_base_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) 5',
            'S_no_base_error.ENV = S_no_base.ENV',
            'S_unsafe = S_resumed[.STORE[n_key] = DEFINED (PINT 7)]',
            '$call_task_valid(S_unsafe, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site 5 n_key)',
            'PhpStep: S_unsafe ~> S_unsafe_next',
            'S_unsafe_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
            r'S_unsafe_next.STORE = S_unsafe.STORE /\ S_unsafe_next.EVENTS = S_unsafe.EVENTS',
            'S_forged = S_resumed[.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site 5 n_base) :: ptask_tail*]',
            '$call_task_valid(S_forged, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site 5 n_base)',
            'PhpStep: S_forged ~> S_forged_next',
            'S_forged_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
        ]
    else:
        controls += [
            'S_unsafe = S_discard[.STORE[n_key] = DEFINED (PINT 7)]',
            '$call_task_valid(S_unsafe, STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site 5 n_key)',
            '$error_read_discard(S_unsafe, perrorcall_entered.RESUME).COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
            'PhpStep: S_unsafe ~> S_unsafe_next',
            'S_unsafe_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
            'S_unsafe_next.ERRORHANDLER = S.ERRORHANDLER',
            'S_unsafe_next.OBJECTS[n_exception] = S_discard.OBJECTS[n_exception]',
            r'S_unsafe_next.STORE = S_unsafe.STORE /\ S_unsafe_next.EVENTS = S_unsafe.EVENTS',
        ]
    return checks + controls, derived + len(controls)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(null.__file__), Path(null.cases.__file__), Path(cases.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 2)
    prior = null.prior
    prior.NAME = tuple(cases.CASES)[INDEX]
    prior.OUTPUT = cases.OUTPUTS[prior.NAME]
    prior.cases, prior.conditions, prior.recorded, prior.PREFIX = cases, conditions, null.recorded, PREFIX
    passed = prior.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Genuine delayed INT-to-false/false-throw Boolean-CV unset fronts retain actual '
        'source/CODE/read-eps, saved ordinary cell and producer tail without a root. Normal and pending-throw '
        'postguards, same-cell BOOL flip, independent base removal, unsafe conversion and forged-cell refusals, '
        'same Throwable/restoration and whole/split budgets are fixture source0/native0; saved originals reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
