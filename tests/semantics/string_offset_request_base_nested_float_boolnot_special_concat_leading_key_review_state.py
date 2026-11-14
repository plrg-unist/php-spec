#!/usr/bin/env python3
"""Independent typed runtime NOT chains, quiet leaves and source controls."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as prior
import string_offset_request_base_nested_float_boolnot_special_concat_leading_key_cases as cases
import string_offset_request_base_nested_float_boolnot_special_concat_leading_key_protocol as source

runner = source.runner
DEPTHS = (2, 2, 3, 3)


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = [
        'pcode_peer_nested = S_after.CODE[0]',
        'pcode_peer_nested.UNIT = 0',
        'ppool_peer_nested = S_after.POOLS[0]',
        'ppool_peer_nested.UNIT = 0',
        'pcunit_peer_nested = S_after.SOURCES[0]',
        'pcunit_peer_nested.ID = 0',
        '$origin_child((porigin_key), [PCFIELD 0]) = (porigin_peer_nested_concat)',
        'porigin_peer_nested_0 = porigin_nested_not',
        'porigin_nested_float = PORIGIN 0 pcpath_peer_nested_leaf',
    ]
    for level in range(DEPTHS[index]):
        origin = 'porigin_peer_nested_' + str(level)
        boolean = str(bool((index >= 2) ^ ((DEPTHS[index] - level) % 2))).lower()
        child = ('porigin_peer_nested_' + str(level + 1)
                 if level + 1 < DEPTHS[index] else 'porigin_nested_float')
        guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')',
                   '$string_read_runtime_value(S_after, ' + origin + ') = (PBOOL ' + boolean + ')',
                   '$compiled_read(S_after, ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = ($echo_value(PBOOL ' + boolean + '))']
    nodes = [('root', 'porigin_key'), ('concat', 'porigin_peer_nested_concat')]
    nodes += [('not' + str(level), 'porigin_peer_nested_' + str(level))
              for level in range(DEPTHS[index])]
    nodes.append(('leaf', 'porigin_nested_float'))
    for tag, origin in nodes:
        target = 'pcpath_peer_nested_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        for label, replacement in (('drop', 'eps'), ('flip', '(false)' if tag == 'leaf' else '(true)')):
            state = 'S_peer_nested_' + tag + '_' + label
            guards += [state + ' = S_after[.CODE[0] = pcode_peer_nested[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_nested.EXPRESSIONS, ' + target + ', ' + replacement + ')]]',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_peer_nested_' + tag + '_precision'
        guards += [state + ' = S_after[.POOLS[0] = ppool_peer_nested[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_nested.CONSTANTS]]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (17)',
                   '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_peer_nested_' + tag + '_source'
        guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_nested[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_nested.OCCURRENCES]]',
                   '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    if index == 0:
        guards += [
            'S_peer_nested_signed_zero = S_after[.POOLS[0] = ppool_peer_nested[.CONSTANTS = (PCONSTANT pcpath_peer_nested_leaf (PFLOAT 9223372036854775808)) :: ppool_peer_nested.CONSTANTS]]',
            '$compiled_identity_value(S_peer_nested_signed_zero, porigin_nested_float) = (PFLOAT 9223372036854775808)',
            '$string_read_runtime_value(S_peer_nested_signed_zero, porigin_nested_float) = (PFLOAT 9223372036854775808)',
            '$string_read_runtime_value(S_peer_nested_signed_zero, porigin_nested_not) = (PBOOL false)',
            '$string_read_request_base_saved(S_peer_nested_signed_zero, pstringread) = (1)',
        ]
    if index == 2:
        for label, value in (('nan', 'PFLOAT 9221120237041090560'),
                             ('negative_nan', 'PFLOAT 18444492273895866368'),
                             ('payload_nan', 'PFLOAT 9221120237041090561'),
                             ('invalid', 'PFLOAT 18446744073709551616'),
                             ('integer', 'PINT 0'), ('boolean', 'PBOOL false'),
                             ('null', 'PNULL'), ('string', 'PSTRING ($ptascii(""))')):
            state = 'S_peer_nested_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_nested[.CONSTANTS = (PCONSTANT pcpath_peer_nested_leaf (' + value + ')) :: ppool_peer_nested.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_nested_float) = (' + value + ')']
            if 'nan' in label:
                guards += ['$compiled_identity_value(' + state + ', porigin_nested_float) = (' + value + ')',
                           '$number_bool(NFLOAT ' + value.split()[1] + ') = (true, true)']
            guards += ['$string_read_runtime_value(' + state + ', porigin_nested_float) = eps',
                       '$string_read_runtime_value(' + state + ', porigin_nested_not) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        for label, bits, boolean, key in (('same', '4609434218613702656', 'false', '0x'),
                                         ('changed', '0', 'true', '01x')):
            state = 'S_peer_nested_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_nested[.CONSTANTS = (PCONSTANT pcpath_peer_nested_leaf (PFLOAT ' + bits + ')) :: ppool_peer_nested.CONSTANTS]]',
                       '$compiled_identity_value(' + state + ', porigin_nested_float) = (PFLOAT ' + bits + ')',
                       '$string_read_runtime_value(' + state + ', porigin_nested_not) = (PBOOL ' + boolean + ')',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = ($ptascii(' + json.dumps(key) + '))',
                       '$string_read_request_base_saved(' + state + ', pstringread) = ' + ('(0)' if label == 'same' else 'eps')]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += prior.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = ('Four authentic reached nested runtime NOT histories retain the exact author '
                       'prefixes and add independent typed Boolean results and per-link CODE/source/'
                       'precision controls. Quiet PFLOAT leaves retain the trusted compiler-output '
                       'boundary; NaN VALUE, invalid bits and non-FLOAT leaf types refuse. Equal-truth '
                       'substitutions retain the key, while changed truth computes new bytes and '
                       'rejects the saved old key. Actual carriers, owners, pending throw and fixed '
                       'bounds retain existing laws. These fixtures add source0/native0, with no '
                       'accepted source/native replay or NaN-warning/ownership expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
