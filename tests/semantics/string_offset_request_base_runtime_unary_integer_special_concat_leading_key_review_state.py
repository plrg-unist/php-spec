#!/usr/bin/env python3
"""Independent typed sign, source authority and integer-byte controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as prior
import string_offset_request_base_runtime_unary_integer_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_unary_integer_special_concat_leading_key_protocol as source

runner = source.runner
VALUES = ('1', '$(-1)', '0', '$(-1)')
TEXTS = ('1', '-1', '0', '-1')
KEYS = ('1x', '-1x', '0x', '-4x')
CONTROL = None


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    value, text, key = VALUES[index], TEXTS[index], KEYS[index]
    guards = [
        'pcode_peer_sign = S_after.CODE[0]', 'pcode_peer_sign.UNIT = 0',
        'ppool_peer_sign = S_after.POOLS[0]', 'ppool_peer_sign.UNIT = 0',
        'pcunit_peer_sign = S_after.SOURCES[0]', 'pcunit_peer_sign.ID = 0',
        'porigin_runtime_float = PORIGIN 0 pcpath_peer_sign_leaf',
        'porigin_runtime_unary = PORIGIN 0 pcpath_peer_sign_unary',
        '$string_read_runtime_value(S_after, porigin_runtime_unary) = (PINT ' + value + ')',
        '$string_read_runtime_bytes(S_after, porigin_runtime_unary) = ($ptascii(' + json.dumps(text) + '))',
        '$string_read_runtime_bytes(S_after, porigin_key) = ($ptascii(' + json.dumps(key) + '))',
        '$string_read_runtime_bytes(S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true], porigin_key) = ($ptascii(' + json.dumps(key) + '))',
        '$ntsigned(' + value + ') = $decimal_integer(' + value + ')',
    ]
    nodes = [('root', 'porigin_key'), ('concat', 'porigin_runtime_concat'),
             ('unary', 'porigin_runtime_unary'), ('not', 'porigin_runtime_not'),
             ('leaf', 'porigin_runtime_float')]
    if index == 3:
        nodes.append(('outer_not', 'porigin_runtime_outer_not'))
    for tag, origin in nodes:
        target = 'pcpath_peer_sign_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        for label, replacement in (('drop', 'eps'), ('flip', '(false)' if tag == 'leaf' else '(true)')):
            state = 'S_peer_sign_' + tag + '_' + label
            guards += [state + ' = S_after[.CODE[0] = pcode_peer_sign[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_sign.EXPRESSIONS, ' + target + ', ' + replacement + ')]]',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_peer_sign_' + tag + '_precision'
        guards += [state + ' = S_after[.POOLS[0] = ppool_peer_sign[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_sign.CONSTANTS]]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (17)',
                   '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_peer_sign_' + tag + '_source'
        guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_sign[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_sign.OCCURRENCES]]',
                   '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    guards += [
        '$coerce_number(PINT $(-1)) = COERCED (NINT $(-1)) false',
        '$unary_apply(S_after, NEGATIVE, PINT $(-1), 5) = S_after[.RESULT = KNOWN (PINT 1)]',
        '$unary_apply(S_after, POSITIVE, PINT 0, 5) = S_after[.RESULT = KNOWN (PINT 0)]',
        '$coerce_number(PFLOAT 4607182418800017408) = COERCED (NFLOAT 4607182418800017408) false',
        '$unary_apply(S_after, POSITIVE, PFLOAT 4607182418800017408, 5) = S_after[.RESULT = KNOWN (PFLOAT 4607182418800017408)]',
    ]
    if index == 0:
        guards += [
            'S_peer_sign_signed_zero = S_after[.POOLS[0] = ppool_peer_sign[.CONSTANTS = (PCONSTANT pcpath_peer_sign_leaf (PFLOAT 9223372036854775808)) :: ppool_peer_sign.CONSTANTS]]',
            '$compiled_identity_value(S_peer_sign_signed_zero, porigin_runtime_float) = (PFLOAT 9223372036854775808)',
            '$string_read_runtime_value(S_peer_sign_signed_zero, porigin_runtime_unary) = (PINT 1)',
            '$string_read_request_base_saved(S_peer_sign_signed_zero, pstringread) = (1)',
            'S_peer_sign_unused = S_after[.POOLS[0] = ppool_peer_sign[.CONSTANTS = (PCONSTANT pcpath_peer_sign_unary (PINT 99)) :: ppool_peer_sign.CONSTANTS]]',
            '$pool_value(S_peer_sign_unused.POOLS, porigin_runtime_unary) = (PINT 99)',
            '$compiled_read(S_peer_sign_unused, porigin_runtime_unary) = eps',
            '$string_read_runtime_value(S_peer_sign_unused, porigin_runtime_unary) = (PINT 1)',
            '$string_read_runtime_bytes(S_peer_sign_unused, porigin_key) = ($ptascii("1x"))',
            '$string_read_request_base_saved(S_peer_sign_unused, pstringread) = (1)',
        ]
        if CONTROL is not None:
            fixture, control, target, node = CONTROL
            guards += [
                'S_peer_recursive = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(control)).decode()) + ')',
                'S_peer_recursive.COMPLETION = BUDGET',
                'porigin_peer_recursive = PORIGIN 0 ' + occurrences.path_term(target),
                '$origin_node(S_peer_recursive.SOURCES, porigin_peer_recursive) = (' + occurrences.node_term(node) + ')',
                '$origin_child((porigin_peer_recursive), [PCFIELD 0]) = (porigin_peer_recursive_inner)',
                '$origin_child((porigin_peer_recursive_inner), [PCFIELD 0]) = (porigin_peer_recursive_not)',
                'porigin_peer_recursive = PORIGIN 0 pcpath_peer_recursive',
                'porigin_peer_recursive_inner = PORIGIN 0 pcpath_peer_recursive_inner',
                '$code_at(S_peer_recursive.CODE, 0) = (pcode_peer_recursive)',
                '$code_expression(pcode_peer_recursive.EXPRESSIONS, pcpath_peer_recursive) = ((5, false))',
                '$code_expression(pcode_peer_recursive.EXPRESSIONS, pcpath_peer_recursive_inner) = ((5, false))',
                '$compiled_read(S_peer_recursive, porigin_peer_recursive) = eps',
                '$compiled_read(S_peer_recursive, porigin_peer_recursive_inner) = eps',
                '$compiled_precision(S_peer_recursive, (porigin_peer_recursive)) = (14)',
                '$compiled_precision(S_peer_recursive, (porigin_peer_recursive_inner)) = (14)',
                '$string_read_runtime_value(S_peer_recursive, porigin_peer_recursive_not) = (PBOOL true)',
                '$string_read_runtime_value(S_peer_recursive, porigin_peer_recursive_inner) = (PINT $(-1))',
                '$coerce_number(PINT $(-1)) = COERCED (NINT $(-1)) false',
                '$unary_apply(S_peer_recursive, NEGATIVE, PINT $(-1), 5) = S_peer_recursive[.RESULT = KNOWN (PINT 1)]',
                '$string_read_runtime_value(S_peer_recursive, porigin_peer_recursive) = (PINT 1)',
                '$string_read_runtime_bytes(S_peer_recursive, porigin_peer_recursive) = ($ptascii("1"))',
            ]
    if index == 2:
        for label, changed in (('nan', 'PFLOAT 9221120237041090560'),
                               ('negative_nan', 'PFLOAT 18444492273895866368'),
                               ('payload_nan', 'PFLOAT 9221120237041090561'),
                               ('invalid', 'PFLOAT 18446744073709551616'),
                               ('integer', 'PINT 0'), ('boolean', 'PBOOL false'),
                               ('null', 'PNULL'), ('array', 'PARRAY 0'),
                               ('object', 'POBJECT 0')):
            state = 'S_peer_sign_value_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_sign[.CONSTANTS = (PCONSTANT pcpath_peer_sign_leaf (' + changed + ')) :: ppool_peer_sign.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_runtime_float) = (' + changed + ')']
            if 'nan' in label:
                guards += ['$compiled_identity_value(' + state + ', porigin_runtime_float) = (' + changed + ')',
                           '$number_bool(NFLOAT ' + changed.split()[1] + ') = (true, true)']
            guards += ['$string_read_runtime_value(' + state + ', porigin_runtime_unary) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        for label, bits, result, rendered in (('same', '4609434218613702656', '0', '0x'),
                                              ('changed', '0', '1', '1x')):
            state = 'S_peer_sign_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_sign[.CONSTANTS = (PCONSTANT pcpath_peer_sign_leaf (PFLOAT ' + bits + ')) :: ppool_peer_sign.CONSTANTS]]',
                       '$compiled_identity_value(' + state + ', porigin_runtime_float) = (PFLOAT ' + bits + ')',
                       '$string_read_runtime_value(' + state + ', porigin_runtime_unary) = (PINT ' + result + ')',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = ($ptascii(' + json.dumps(rendered) + '))',
                       '$string_read_request_base_saved(' + state + ', pstringread) = ' + ('(0)' if label == 'same' else 'eps')]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    control = prep / 'recursive-sign.php'
    original = next(iter(cases.CASES.values()))
    assert original.count(b'+(!0.0)') == 1
    control.write_bytes(original.replace(b'+(!0.0)', b'-(-(!0.0))'))
    root = runner.ROOT
    profile = json.loads((root / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = runner.Worker([str(root / '.tools/php/bin/php'), '-n', *flags, '-d',
                              'extension=' + str(root / '.tools/php-file.so'),
                              str(root / 'frontend/worker.php')], prep / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(control.read_bytes()).decode()})
        assert parsed['accepted']
    finally:
        frontend.close()
    adapter = runner.Worker([str(root / '_build/default/adapter/main.exe'), str(root)], prep / 'adapter')
    try:
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        adapter.close()
    targets = [(path, node) for index, statement in enumerate(parsed['ast']['program'])
               for path, node in occurrences.expected(statement, [('INDEX', index)])
               if node['node'] == 'Expr_UnaryMinus' and node['fields'][0]['node'] == 'Expr_UnaryMinus']
    assert len(targets) == 1
    CONTROL = checked['fixture'], control, *targets[0]
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    watched.add(control)
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += prior.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = ('Four authentic reached sign/NOT histories retain exact author prefixes and '
                       'add typed PINT bytes, per-node source/CODE/precision and quiet-leaf controls. '
                       'Genuine NaN VALUE, invalid bits and forged scalar/owning leaf types refuse. '
                       'An unused own pool entry cannot replace an emitted runtime result; equal '
                       'truth preserves the key and changed truth rejects its old saved bytes. '
                       'Pure integer sign and FLOAT type controls distinguish the fitting NINT '
                       'contract; one additional checked-source compiler fixture authenticates '
                       'recursive sign-over-PINT without native/source agreement credit. No runtime '
                       'FLOAT formatting. Existing actual carriers, '
                       'owners, pending throw and fixed bounds remain; source0/native0, no accepted '
                       'source/native replay or compiler/schema/ownership expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
