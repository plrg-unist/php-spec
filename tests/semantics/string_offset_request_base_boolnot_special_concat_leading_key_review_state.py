#!/usr/bin/env python3
"""Independent Boolean-not truth, literal authority and float refusal checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_boolnot_special_concat_leading_key_cases as cases
import string_offset_request_base_boolnot_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
CONTROLS = {
    'literal-int-zero': b"<?php $x = ((!0) . null) . 'x';\n",
    'literal-string-truthy': b"<?php $x = ((!\"nope\") . false) . 'x';\n",
    'constant-boolean': b"<?php $x = ((!true) . false) . 'x';\n",
    'finite-float': b"<?php $x = ((!0.0) . false) . 'x';\n",
    'nan-float': b"<?php $x = ((!NAN) . false) . 'x';\n",
    'array-child': b"<?php $x = ((![]) . false) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('boolnot_root', 'boolnot_root_child', 'boolnot_root_l', 'boolnot_root_child_l')[index]
    origin, child, expression = 'porigin_' + tag, 'porigin_' + tag + '_child', 'expression_' + tag
    wrong = 'PBOOL true' if index == 2 else 'PBOOL false'
    guards = [origin + ' = PORIGIN n_not pcpath_not',
              child + ' = PORIGIN n_not pcpath_not_child']
    for suffix, value in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(PINT 1)')):
        state = 'S_not_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    guards += [
        'expression_not_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag,
        'S_not_kind = S_after[.SOURCES = [{ID n_not, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_not expression_not_other)])}]]',
        '$compiled_read(S_not_kind, ' + origin + ') = pvalue_not?',
        '$compiled_read(S_after, ' + origin + ') = pvalue_not?',
        '$compiled_special_concat_bytes(S_not_kind, ' + origin + ') = eps']
    if index == 0:
        guards += [
            'S_not_literal_drop = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
            '$compiled_read(S_not_literal_drop, ' + child + ') = eps',
            '$compiled_special_concat_bytes(S_not_literal_drop, ' + origin + ') = ($ptascii("1"))',
            'S_not_literal_root = S_after[.SOURCES = [{ID n_not, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_not ' + expression + ')])}]]',
            '$compiled_read(S_not_literal_root, ' + origin + ') = (PBOOL true)',
            '$compiled_special_concat_bytes(S_not_literal_root, ' + origin + ') = ($ptascii("1"))',
            'expression_not_one = NExprBooleanNot (NScalarString (BYTES "MQ==") metadata_' + tag + '_child) metadata_' + tag,
            'S_not_one = S_after[.SOURCES = [{ID n_not, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_not expression_not_one)])}]]',
            '$compiled_read(S_not_one, ' + origin + ') = (PBOOL true)',
            '$truth(S_not_one, PSTRING ($ptascii("1"))) = true',
            '$compiled_special_concat_bytes(S_not_one, ' + origin + ') = eps',
            'expression_not_float = NExprBooleanNot (NScalarFloat (FLOAT "0000000000000000") metadata_' + tag + '_child) metadata_' + tag,
            'S_not_float = S_after[.SOURCES = [{ID n_not, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_not expression_not_float)])}]]',
            '$compiled_read(S_not_float, ' + origin + ') = (PBOOL true)',
            '$parser_literal_at(NScalarFloat (FLOAT "0000000000000000") metadata_' + tag + '_child, 14) = (PFLOAT 0)',
            '$truth(S_not_float, PFLOAT 0) = false',
            '$compiled_special_concat_bytes(S_not_float, ' + origin + ') = eps']
    else:
        for suffix, value in (('drop', 'eps'), ('wrong', '(PINT 99)')):
            state = 'S_not_child_' + suffix
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + value + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        for suffix, changed, root_precision, child_precision in (
                ('child', child, 14, 17), ('root', origin, 17, 14)):
            state = 'S_not_precision_' + suffix
            guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + changed + ', 17)]',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (' + str(root_precision) + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (' + str(child_precision) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        guards += [
            'expression_not_child_other = NScalarInt (INTEGER 0) metadata_' + tag,
            'S_not_child_source = S_after[.SOURCES = [{ID n_not, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_not ' + expression + '), (PCOCCURRENCE pcpath_not_child expression_not_child_other)])}]]',
            '$compiled_special_concat_bytes(S_not_child_source, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_not_control_' + str(index), 'porigin_not_control_' + str(index)
        unary = origin + '_unary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_not_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_not_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + unary + ')',
                   '$origin_node(' + state + '.SOURCES, ' + unary + ') = (NExprBooleanNot expression_not_control_' + str(index) + ' metadata_not_control_' + str(index) + ')']
        if index < 3:
            truth, text = ('true', '1') if index == 0 else ('false', '')
            key = text + 'x'
            checks += ['$compiled_read(' + state + ', ' + unary + ') = (PBOOL ' + truth + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + unary + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(key) + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(key) + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(key) + '))']
        else:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + unary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            if index < 5:
                checks += ['$compiled_read(' + state + ', ' + unary + ') = eps']
            else:
                checks += ['$compiled_read(' + state + ', ' + unary + ') = (PBOOL true)',
                           '$compiled_read(' + state + ', ' + origin + ') = (PSTRING ($ptascii("1x")))']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.strings, source.arithmetic, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
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
    report['scope'] = 'Four authentic Boolean-not source-state fixtures add independent own-result/type/source refusals, literal parsed-value authority with omitted descendant facts, changed embedded truth, and a plausible correct finite-float Boolean fact that must still be refused. Nonliteral children retain own reads, source identity and both precision directions. Fresh compiler controls separate scalar admission from every-float and owning-array refusal. Borrowed headers, supplied throw, fixed bounds and budgets keep their original laws. Native/source observations are reused once, not replayed.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
