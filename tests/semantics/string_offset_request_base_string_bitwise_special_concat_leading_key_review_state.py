#!/usr/bin/env python3
"""Independent byte algebra, length boundaries and raw compiler-value checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_string_bitwise_special_concat_leading_key_cases as cases
import string_offset_request_base_string_bitwise_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
term = source.bytes_term
PAIRS = {'empty': (b'', b''), 'left-empty': (b'', b'\0\xff'),
         'right-empty': (b'\0\xff', b''), 'left-tail': (b'\x0f\xa0\x7f', b'\xf0'),
         'right-tail': (b'\x0f', b'\xf0\xa0\x7f'), 'high-zero': (b'\0\xff', b'\xff\0'),
         'overlap': (b'\x06', b'\x03'), 'text': (b'12', b'03')}
BINARY = {}
for operation in ('BITAND', 'BITOR', 'BITXOR'):
    for name, (left, right) in PAIRS.items():
        result = bytes((a & b if operation == 'BITAND' else a | b if operation == 'BITOR' else a ^ b)
                       for a, b in zip(left, right))
        if operation == 'BITOR':
            result += (left if len(left) > len(right) else right)[min(len(left), len(right)):]
        BINARY[operation.lower() + '-' + name] = operation, left, right, result
NOT = {name: (value, bytes(255 - byte for byte in value)) for name, value in {
    'not-empty': b'', 'not-zero-high': b'\0\xff', 'not-sign': b'\x7f\x80',
    'not-text': b'3', 'not-bounds': b'\xd2\xcb', 'not-all-bytes': bytes(range(256))}.items()}


def literal(data):
    return '"' + ''.join('\\x%02x' % byte for byte in data) + '"'


CONTROLS = {name: ("<?php $x = ((" + literal(left) + ' ' + {'BITAND': '&', 'BITOR': '|', 'BITXOR': '^'}[operation] + ' ' + literal(right) + ") . null) . 'x';\n").encode()
            for name, (operation, left, right, result) in BINARY.items()} | {
    name: ("<?php $x = ((~" + literal(value) + ") . null) . 'x';\n").encode()
    for name, (value, result) in NOT.items()} | {
    'mixed-integer': b"<?php $x = (('1' | 2) . null) . 'x';\n",
    'mixed-float': b"<?php $x = (('1' | 2.0) . null) . 'x';\n",
    'array-byte': b"<?php $x = (([] | '1') . null) . 'x';\n",
    'boolean-not': b"<?php $x = ((~true) . null) . 'x';\n",
    'numeric-bitand': b"<?php $x = ((6 & 3) . null) . 'x';\n",
    'numeric-bitnot': b"<?php $x = ((~3) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    origin, expression = 'porigin_byte_root', 'expression_byte_root'
    children = ('_child',) if index == 3 else ('_l', '_r')
    guards = [origin + ' = PORIGIN n_byte pcpath_byte'] + [origin + suffix + ' = PORIGIN n_byte pcpath_byte' + suffix for suffix in children]
    for suffix, value in (('drop', 'eps'), ('wrong', '(PSTRING ($ptascii("99")))'),
                          ('type', '(PINT ' + ('1', '$(-1)', '0', '$(-4)')[index] + ')')):
        state = 'S_byte_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    wrong = ((b'0', b'2'), (b',', b'\0' + b'0'), (b'0', b'\x02'), (b'\0',))[index]
    for suffix, value in zip(children, wrong):
        child = origin + suffix
        for operation, replacement in (('drop', 'eps'), ('wrong', '(PSTRING ' + term(value) + ')')):
            state = 'S_byte_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_byte_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        occurrences = ['(PCOCCURRENCE pcpath_byte ' + expression + ')'] + [
            '(PCOCCURRENCE pcpath_byte' + other + ' ' + ('expression_byte_other' if other == suffix else expression + other) + ')' for other in children]
        state = 'S_byte_source' + suffix
        if suffix == children[0]:
            guards += ['expression_byte_other = NExprVariable (BYTES "dW5hdXRo") metadata_byte_root']
        guards += [state + ' = S_after[.SOURCES = [{ID n_byte, AST (PROGRAM eps), OCCURRENCES ([' + ', '.join(occurrences) + '])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_byte_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_byte_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_byte_precision, (' + origin + children[0] + ')) = (14)',
               '$compiled_special_concat_bytes(S_byte_precision, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_byte_control_' + str(index), 'porigin_byte_control_' + str(index)
        operator = origin + '_operator'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_byte_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_byte_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + operator + ')']
        if name in BINARY:
            operation, left, right, result = BINARY[name]
            values = (left, right)
        elif name in NOT:
            value, result = NOT[name]
            values = (value,)
        else:
            values = ()
        if values:
            key = result + b'x'
            checks += ['$compiled_read(' + state + ', ' + operator + ') = (PSTRING ' + term(result) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + operator + ') = (' + term(result) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = (' + term(key) + ')',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ' + term(key) + ') = PSTRING_CARRIER INTERNED_STRING ' + term(key)]
            for field, value in enumerate(values):
                child = operator + '_' + str(field)
                checks += ['$origin_child((' + operator + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (PSTRING ' + term(value) + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = (' + term(value) + ')']
            if name in ('bitand-overlap', 'not-text'):
                for field, value in enumerate(values):
                    changed, child = state + '_carrier_' + str(field), operator + '_' + str(field)
                    checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PSTRING_CARRIER INTERNED_STRING ' + term(value) + '))]',
                               '$compiled_read(' + changed + ', ' + child + ') = (PSTRING_CARRIER INTERNED_STRING ' + term(value) + ')',
                               '$string_plain(PSTRING_CARRIER INTERNED_STRING ' + term(value) + ') = PSTRING ' + term(value),
                               '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = (' + term(value) + ')',
                               '$compiled_read(' + changed + ', ' + operator + ') = (PSTRING ' + term(result) + ')',
                               '$compiled_special_concat_bytes(' + changed + ', ' + operator + ') = eps']
        elif name in ('numeric-bitand', 'numeric-bitnot'):
            value, result = ('PINT 2', b'2') if name == 'numeric-bitand' else ('PINT $(-4)', b'-4')
            checks += ['$compiled_read(' + state + ', ' + operator + ') = (' + value + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + operator + ') = (' + term(result) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = (' + term(result + b'x') + ')']
        else:
            value = '(PINT 3)' if name in ('mixed-integer', 'mixed-float') else 'eps'
            checks += ['$compiled_read(' + state + ', ' + operator + ') = ' + value,
                       '$compiled_special_concat_bytes(' + state + ', ' + operator + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = compiler_conditions
    runner.CONTROLS = CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source-seeded byte fixtures add own-result/type, missing/outcome-changing child reads, exact child sources and every evaluated precision direction. Independent Python byte algebra supplies NOT and overlapping AND/OR/XOR results, empty inputs, both unequal-length directions, high/NUL bytes and all256 NOT inputs. Interned-carrier pool mutations preserve plain byte authority and cached results while exact raw compiled PSTRING reads remain required; no carrier lifetime claim is made. Integer NOT/AND controls retain the prior disjoint PINT route, while mixed numeric conversion and unsupported operands remain refused here. Compiler results may include NUL bytes; downstream REQUEST/key restrictions are unchanged, and original final keys/bases are non-NUL. Two historical byte selectors are promoted separately. Native4 are reused once, author recipes remain exact prefixes, and owners/supplied throw/fixed bounds/budgets retain existing laws. Compiler/derived checks carry source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
