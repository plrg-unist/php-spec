#!/usr/bin/env python3
"""Independent emitted-code, quiet truth and actual runtime-carrier controls."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as cases
import string_offset_request_base_float_boolnot_special_concat_leading_key_protocol as source

runner = source.runner
HELPERS = r'''
dec $float_not_review_expressions(pcodeexpr*, pcpath, bool?) : pcodeexpr*
def $float_not_review_expressions(eps, pcpath, b?) = eps
def $float_not_review_expressions((CODEEXPR pcpath z b_old) :: pcodeexpr*, pcpath, eps) = pcodeexpr*
def $float_not_review_expressions((CODEEXPR pcpath z b_old) :: pcodeexpr*, pcpath, (b_new)) = (CODEEXPR pcpath z b_new) :: pcodeexpr*
def $float_not_review_expressions(pcodeexpr :: pcodeexpr_tail*, pcpath, b?) = pcodeexpr :: $float_not_review_expressions(pcodeexpr_tail*, pcpath, b?)
  -- if $code_expression([pcodeexpr], pcpath) = eps
'''


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    key = source.KEYS[index]
    guards = [
        'n_runtime_unit = 0',
        'pcode_peer_float_not = S_after.CODE[0]',
        'pcode_peer_float_not.UNIT = 0',
        'ppool_peer_float_not = S_after.POOLS[0]',
        'ppool_peer_float_not.UNIT = 0',
        'pcunit_peer_float_not = S_after.SOURCES[0]',
        'pcunit_peer_float_not.ID = 0',
        'porigin_float_child = PORIGIN 0 pcpath_peer_float_child',
        '$string_read_runtime_bytes(S_after, porigin_key) = ($ptascii(' + json.dumps(key) + '))',
        '$string_read_runtime_bytes(S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true], porigin_key) = ($ptascii(' + json.dumps(key) + '))',
    ]
    for tag, origin in (('root', 'porigin_key'), ('concat', 'porigin_float_concat'),
                        ('not', 'porigin_float_not'), ('child', 'porigin_float_child')):
        path = 'pcpath_peer_float_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + path)
        for label, replacement in (('drop', 'eps'), ('flip', '(true)' if tag != 'child' else '(false)')):
            state = 'S_peer_float_' + tag + '_' + label
            guards += [state + ' = S_after[.CODE[0] = pcode_peer_float_not[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_float_not.EXPRESSIONS, ' + path + ', ' + replacement + ')]]',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_peer_float_' + tag + '_precision'
        guards += [state + ' = S_after[.POOLS[0] = ppool_peer_float_not[.CONSTANTS = (PCCPRECISION ' + path + ' 17) :: ppool_peer_float_not.CONSTANTS]]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (17)',
                   '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_peer_float_' + tag + '_source'
        guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_float_not[.OCCURRENCES = (PCOCCURRENCE ' + path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_float_not.OCCURRENCES]]',
                   '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    guards += [
        '$string_read_request_base_saved(S_after, pstringread[.READ.INPUT = KNOWN (PSTRING ($ptascii(' + json.dumps(key) + ')))][.READ.VALUE = PSTRING ($ptascii(' + json.dumps(key) + '))]) = eps',
        'pstringread_peer_invalid = pstringread[.READ.INPUT = KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii(' + json.dumps(key) + ')))][.READ.VALUE = PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii(' + json.dumps(key) + '))]',
        '~$string_carrier_valid(S_after, pstringread_peer_invalid.READ.VALUE)',
        '$string_read_request_base_saved(S_after, pstringread_peer_invalid) = eps',
        'pstringread_peer_mismatch = pstringread[.READ.INPUT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(key) + '))) ]',
        '$string_read_request_base_saved(S_after, pstringread_peer_mismatch) = eps',
        '$string_read_request_base_saved(S_after, pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pstringread.READ.BASE)]) = eps',
        '$compiled_special_concat_bytes(S_after, porigin_float_not) = eps',
        '$compiled_special_concat_bytes(S_after, porigin_key) = eps',
        '$compiled_string_value(S_after, porigin_key, PSTRING ($ptascii(' + json.dumps(key) + '))) = PSTRING ($ptascii(' + json.dumps(key) + '))',
    ]
    if index == 0:
        guards += [
            'S_peer_float_signed_zero = S_after[.POOLS[0] = ppool_peer_float_not[.CONSTANTS = (PCONSTANT pcpath_peer_float_child (PFLOAT 9223372036854775808)) :: ppool_peer_float_not.CONSTANTS]]',
            '$compiled_identity_value(S_peer_float_signed_zero, porigin_float_child) = (PFLOAT 9223372036854775808)',
            '$number_bool(NFLOAT 9223372036854775808) = (false, false)',
            '$string_read_runtime_bytes(S_peer_float_signed_zero, porigin_float_not) = ($ptascii("1"))',
            '$string_read_request_base_saved(S_peer_float_signed_zero, pstringread) = (1)',
        ]
    if index == 2:
        for label, value in (('nan', 'PFLOAT 9221120237041090560'),
                             ('negative-nan', 'PFLOAT 18444492273895866368'),
                             ('payload-nan', 'PFLOAT 9221120237041090561'),
                             ('invalid', 'PFLOAT 18446744073709551616'),
                             ('integer', 'PINT 1'), ('boolean', 'PBOOL true'),
                             ('null', 'PNULL'), ('string', 'PSTRING ($ptascii("1"))')):
            state = 'S_peer_float_value_' + label.replace('-', '_')
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_float_not[.CONSTANTS = (PCONSTANT pcpath_peer_float_child (' + value + ')) :: ppool_peer_float_not.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_float_child) = (' + value + ')']
            if 'nan' in label:
                guards += ['$compiled_identity_value(' + state + ', porigin_float_child) = (' + value + ')',
                           '$number_bool(NFLOAT ' + value.split()[1] + ') = (true, true)']
            guards += ['$string_read_runtime_bytes(' + state + ', porigin_float_not) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        guards += [
            'S_peer_float_changed = S_after[.POOLS[0] = ppool_peer_float_not[.CONSTANTS = (PCONSTANT pcpath_peer_float_child (PFLOAT 0)) :: ppool_peer_float_not.CONSTANTS]]',
            '$compiled_identity_value(S_peer_float_changed, porigin_float_child) = (PFLOAT 0)',
            '$string_read_runtime_bytes(S_peer_float_changed, porigin_float_not) = ($ptascii("1"))',
            '$string_read_runtime_bytes(S_peer_float_changed, porigin_key) = ($ptascii("01x"))',
            '$string_read_request_base_saved(S_peer_float_changed, pstringread) = eps',
        ]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = ('Four authentic source-reached runtime NOT/CONCAT histories retain the author '
                       'prefixes exactly and add independent missing/flipped CODE, source, precision, '
                       'typed child and carrier controls. Quiet signed-zero substitution remains '
                       'admitted at the existing compiler-output boundary; three genuine NaN VALUE '
                       'mutations isolate the warning-flag refusal. Changed quiet truth authenticates '
                       'new bytes but refuses the saved old key. Runtime roots keep no compiler BYTE '
                       'or invented INTERNED normalization. Native observations are reused once; '
                       'these fixture conditions add source0 and no source/native replay.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
