#!/usr/bin/env python3
"""Independent Boolean/null unary source, fact, precision and owner controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_bool_null_unary_special_concat_leading_key_cases as cases
import string_offset_request_base_bool_null_unary_special_concat_leading_key_protocol as source
import string_offset_request_base_unary_const_arithmetic_special_concat_leading_key_review_state as prior
import string_offset_request_base_numeric_string_unary_special_concat_leading_key_review_state as strings

runner = prior.runner
STRING_CONTROL = 'certified-numeric-string-child'
CONTROLS = {name: prior.CONTROLS[name] for name in ('unary-boolean-constant', 'unary-numeric-concat')} | {
    STRING_CONTROL: b"<?php $x = (+('1'.false) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tags = ['bool_unary'] if index < 3 else ['bool_unary', 'bool_unary_child_l', 'bool_unary_child_r_l']
    guards = []
    for tag in tags:
        origin, child = 'porigin_' + tag, 'porigin_' + tag + '_child'
        stem = 'S_peer_' + tag
        guards += [
            origin + ' = PORIGIN n_peer_' + tag + ' pcpath_peer_' + tag,
            stem + '_drop = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', eps)]',
            '$compiled_read(' + stem + '_drop, ' + origin + ') = eps',
            '$compiled_special_concat_bytes(' + stem + '_drop, ' + origin + ') = eps',
            '$string_read_request_base_saved(' + stem + '_drop, pstringread) = eps',
            stem + '_child = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
            '$compiled_read(' + stem + '_child, ' + child + ') = eps',
            '$compiled_special_concat_bytes(' + stem + '_child, ' + origin + ') = eps',
            '$string_read_request_base_saved(' + stem + '_child, pstringread) = eps',
            stem + '_wrong = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', (PINT 99))]',
            '$compiled_special_concat_bytes(' + stem + '_wrong, ' + origin + ') = eps',
            '$string_read_request_base_saved(' + stem + '_wrong, pstringread) = eps',
            stem + '_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
            '$compiled_precision(' + stem + '_precision, (' + origin + ')) = (14)',
            '$compiled_precision(' + stem + '_precision, (' + child + ')) = (17)',
            '$compiled_special_concat_bytes(' + stem + '_precision, ' + origin + ') = eps',
            '$string_read_request_base_saved(' + stem + '_precision, pstringread) = eps',
            stem + '_root_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
            '$compiled_precision(' + stem + '_root_precision, (' + origin + ')) = (17)',
            '$compiled_precision(' + stem + '_root_precision, (' + child + ')) = (14)',
            '$compiled_special_concat_bytes(' + stem + '_root_precision, ' + origin + ') = eps',
            stem + '_missing = S_after[.SOURCES = [{ID n_peer_' + tag + ', AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_peer_' + tag + ' expression_' + tag + ')])}]]',
            '$compiled_read(' + stem + '_missing, ' + origin + ') = pvalue_peer_' + tag + '?',
            '$compiled_read(S_after, ' + origin + ') = pvalue_peer_' + tag + '?',
            '$compiled_special_concat_bytes(' + stem + '_missing, ' + origin + ') = eps',
            'expression_peer_wrong_' + tag + ' = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag,
            stem + '_kind = S_after[.SOURCES = [{ID n_peer_' + tag + ', AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_peer_' + tag + ' expression_peer_wrong_' + tag + ')])}]]',
            '$compiled_read(' + stem + '_kind, ' + origin + ') = pvalue_peer_' + tag + '?',
            '$compiled_special_concat_bytes(' + stem + '_kind, ' + origin + ') = eps']
    key = ('1x', '-1x', '0x', '-4x')[index]
    guards += runner.lines(r'''
S_peer_equal = S_after[.STRINGDATA = S_after.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii("abc")))]
$string_carrier_valid(S_peer_equal, PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii("abc")))
~$string_read_retainer(S_peer_equal, pstringread, BIND ($ptascii("keeper")) n_keeper)
~$string_read_ready(S_peer_equal, pstringread)
$string_read_resume(S_peer_equal, pstringread) = S_peer_equal[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
$string_read_discard(S_peer_equal, pstringread) = S_peer_equal[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_peer_live_precision = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]
$precision_value(S_peer_live_precision) = 9
''') + ['$compiled_special_concat_bytes(S_peer_live_precision, porigin_key) = ($ptascii("' + key + '"))']
    if index == 0:
        legacy, _ = prior.conditions(program, path, 0)
        guards += [check.replace('porigin_unary_root_child', 'porigin_bool_unary_child').replace('porigin_unary_root', 'porigin_bool_unary')
            for check in legacy if 'S_boolean' in check]
    checks += guards
    return checks, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = prior.compiler_conditions({name: value for name, value in checked.items() if name in prior.CONTROLS}, paths)
    boolean = 'unary-boolean-constant'
    if boolean in checked:
        checks += strings.compiler_conditions({strings.CONST_CONTROL: checked[boolean]}, {strings.CONST_CONTROL: paths[boolean]})
    if STRING_CONTROL not in checked:
        return checks
    checks += ['S_text = $php_run(' + checked[STRING_CONTROL]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[STRING_CONTROL])).decode()) + ')']
    return checks + runner.lines(r'''
S_text.COMPLETION = BUDGET
$special_review_concat_path(S_text.SOURCES[0].OCCURRENCES) = (pcpath_text)
porigin_text = PORIGIN 0 pcpath_text
$compiled_read(S_text, porigin_text) = (PSTRING ($ptascii("1x")))
$compiled_special_concat_bytes(S_text, porigin_text) = eps
$compiled_string_value(S_text, porigin_text, PSTRING ($ptascii("1x"))) = PSTRING ($ptascii("1x"))
$origin_child((porigin_text), [PCFIELD 0, PCFIELD 0]) = (porigin_text_unary)
$origin_node(S_text.SOURCES, porigin_text_unary) = (NExprUnaryPlus expression_text_child metadata_text_unary)
$compiled_precision(S_text, (porigin_text_unary)) = (14)
$compiled_read(S_text, porigin_text_unary) = (PINT 1)
$origin_child((porigin_text_unary), [PCFIELD 0]) = (porigin_text_child)
$origin_node(S_text.SOURCES, porigin_text_child) = (expression_text_child)
expression_text_child = NExprBinaryOpConcat expression_text_literal expression_text_false metadata_text_child
$parser_literal_at(expression_text_child, 14) = eps
$compiled_precision(S_text, (porigin_text_child)) = (14)
$compiled_read(S_text, porigin_text_child) = (PSTRING ($ptascii("1")))
$compiled_special_concat_bytes(S_text, porigin_text_child) = ($ptascii("1"))
$coerce_number(PSTRING ($ptascii("1"))) = COERCED (NINT 1) false
$unary_apply(S_text, POSITIVE, PSTRING ($ptascii("1")), 0) = S_text[.RESULT = KNOWN (PINT 1)]
$compiled_special_concat_bytes(S_text, porigin_text_unary) = eps
$origin_child((porigin_text_child), [PCFIELD 0]) = (porigin_text_literal)
$origin_node(S_text.SOURCES, porigin_text_literal) = (NScalarString (BYTES "MQ==") metadata_text_literal)
$origin_child((porigin_text_child), [PCFIELD 1]) = (porigin_text_false)
$origin_node(S_text.SOURCES, porigin_text_false) = (NExprConstFetch name_text_false metadata_text_false)
$ptast(name_text_false) = PTNAME PTPLAIN ($ptascii("false"))
$compiled_read(S_text, porigin_text_false) = (PBOOL false)
''')


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.arithmetic, source.runner, prior, prior.arithmetic, prior.constants, prior.nested, prior.prior, prior.arithmetic.floating, strings)] + [Path(__file__)]
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
    report['scope'] = 'Four fresh Boolean/null unary source-state fixtures reuse the actual reached-state builder and add independent missing/wrong facts, actual child/source-kind and both precision-direction controls for every unary node. Equal bytes in a distinct REQUEST header do not retain the borrowed base. Signed/zero indices, supplied throw, nested arithmetic, fixed negative bounds and budget laws remain. Fresh compiler checks exercise only the affected Boolean promotions plus retained guards; an actual recursively certified PSTRING child remains refused despite quiet coercion, matching compiled precision and exact pure unary result. Earlier source/native/state/compiler campaigns retain separate cuts without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
