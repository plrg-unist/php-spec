#!/usr/bin/env python3
"""FLOAT-CV Warning continuation does not read or retain its changed key."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_null_warning_protocol as null
import string_offset_nested_unset_float_cv_warning_cases as cases

INDEX = 3
PREFIX = null.PREFIX.replace('STRING_UNSET_WARNING_RESULT', 'STRING_UNSET_FLOAT_CV_WARNING_RESULT')


def conditions(program, path):
    null.INDEX = int(INDEX == 1)
    checks, derived = null.conditions(program, path)
    replacements = {
        'S.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) 5)) (KNOWN PNULL) 5) (KNOWN (PINT 7)) 5':
        'S.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) 5)) (VARIABLE ($ptascii("key")) 5) 5) (KNOWN (PINT 7)) 5',
        '$string_unset_warning_source(S, porigin_site, 5) = (($ptascii("base"), 5))':
        '$string_unset_bool_cv_source(S, porigin_site, 5) = (($ptascii("base"), 5, $ptascii("key"), 5))',
        '$string_unset_warning_plan(S) = ((porigin_site, 5))':
        '$string_unset_float_cv_plan(S) = ((porigin_site, 5))',
    }
    for old, new in replacements.items():
        assert checks.count(old) == 1
        checks[checks.index(old)] = new
    checks = [check.replace('STRING_UNSET_WARNING_RESULT', 'STRING_UNSET_FLOAT_CV_WARNING_RESULT') for check in checks]
    bits = cases.KEY_BITS[tuple(cases.CASES)[INDEX]]
    at = checks.index('$string_unset_float_cv_plan(S) = ((porigin_site, 5))') + 1
    checks[at:at] = [
        '$lookup(S.ENV, $ptascii("key")) = (n_key)',
        'S.STORE[n_key] = DEFINED (PFLOAT ' + str(bits) + ')',
        '$string_unset_float_cv_cell(S, $ptascii("key"), 5, n_key)',
        '$string_unset_bool_cv_plan(S) = eps',
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        '$origin_node(S.SOURCES, porigin_key) = (NExprVariable (BYTES text_key) metadata_key)',
        '$base64(text_key) = $ptascii("key")',
        '$variable_line(BYTES text_key, metadata_key) = 5',
        '$compiled_read(S, porigin_key) = eps',
    ]
    controls = [
        '$string_unset_float_cv_plan(S[.REFCELLS = S.REFCELLS ++ [n_key]]) = eps',
        '$string_unset_float_cv_plan(S[.STORE[n_key] = UNDEFINED]) = eps',
        '$string_unset_float_cv_plan(S[.STORE[n_key] = DEFINED (PBOOL true)]) = eps',
        '$string_unset_float_cv_plan(S[.HELD = [HCELL n_key]]) = eps',
    ]
    for value in (0, 1, 0x8000000000000000, 0x8000000000000001,
                  0x7ff0000000000000, 0xfff0000000000000,
                  0x7ff8000000000000, 0xfff8000000000000,
                  0x7ff0000000000001, 0xfff0000000000001):
        controls.append('$string_unset_float_cv_cell(S[.STORE[n_key] = DEFINED (PFLOAT '
                        + str(value) + ')], $ptascii("key"), 5, n_key)')
    for value in (1 << 64,):
        controls.append('~$string_unset_float_cv_cell(S[.STORE[n_key] = DEFINED (PFLOAT '
                        + str(value) + ')], $ptascii("key"), 5, n_key)')
    if INDEX == 3:
        controls += [
            '$lookup(S_resumed.ENV, $ptascii("key")) = (n_changed)',
            'S_resumed.STORE[n_changed] = DEFINED (POBJECT n_object)',
            '~$string_unset_float_cv_cell(S_resumed, $ptascii("key"), 5, n_changed)',
            r'$heap_valid($heap_graph(S_resumed)) /\ $call_descriptors_valid(S_resumed)',
            '$heap_graph(S_resumed) = $heap_graph(S_resumed[.TODO = ptask_tail*])',
            'S_no_key = S_resumed[.ENV = $unbind(S_resumed.ENV, $ptascii("key"))]',
            '$call_task_valid(S_no_key, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site 5)',
            'PhpStep: S_no_key ~> S_no_key_error',
            'S_no_key_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) 5',
            r'S_no_key_error.ENV = S_no_key.ENV /\ S_no_key_error.STORE = S_no_key.STORE',
            'S_no_base = S_resumed[.ENV = $unbind(S_resumed.ENV, $ptascii("base"))]',
            '$call_task_valid(S_no_base, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site 5)',
            'PhpStep: S_no_base ~> S_no_base_error',
            'S_no_base_error.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) 5',
            'S_no_base_error.ENV = S_no_base.ENV',
        ]
    else:
        controls += [
            'S_no_key = S_discard[.ENV = $unbind(S_discard.ENV, $ptascii("key"))]',
            '$call_task_valid(S_no_key, STRING_UNSET_FLOAT_CV_WARNING_RESULT porigin_site 5)',
            '$error_read_discard(S_no_key, perrorcall_entered.RESUME) = S_no_key',
        ]
    return checks + controls, derived + len(controls)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(null.__file__), Path(null.cases.__file__), Path(cases.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 3)
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
    report['scope'] = ('Genuine ordinary nonNaN FLOAT-CV entry, mutable source/CODE/read-eps and quiet exact '
        'value. Actual object-return and fractional-throw retain source-only resume/discard without key/base '
        'reread or owner retention. Derived float/NaN boundaries, range/ref/held refusals and key/base removal '
        'are source0/native0; same Throwable/restoration and whole/split reuse saved originals only.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
