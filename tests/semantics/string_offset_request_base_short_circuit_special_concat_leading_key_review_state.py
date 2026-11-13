#!/usr/bin/env python3
"""Independent logical branches, evaluated types and skipped-code checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_short_circuit_special_concat_leading_key_cases as cases
import string_offset_request_base_short_circuit_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
FORMS = {'BooleanAnd': ('&&', False), 'LogicalAnd': ('and', False),
         'BooleanOr': ('||', True), 'LogicalOr': ('or', True)}
SCALARS = {
    'false': ('false', 'PBOOL false', '', False), 'true': ('true', 'PBOOL true', '1', True),
    'zero': ('0', 'PINT 0', '0', False), 'one': ('1', 'PINT 1', '1', True),
    'negative': ('-1', 'PINT $(-1)', '-1', True), 'null': ('null', 'PNULL', '', False),
    'zero-string': ("'0'", 'PSTRING ($ptascii("0"))', '0', False),
    'empty-string': ("''", 'PSTRING ($ptascii(""))', '', False),
    'truthy-string': ("'1tail'", 'PSTRING ($ptascii("1tail"))', '1tail', True),
    'double-zero': ("'00'", 'PSTRING ($ptascii("00"))', '00', True),
    'float-zero': ('0.0', 'PFLOAT 0', '0', False),
    'float-one': ('1.0', 'PFLOAT 4607182418800017408', '1', True),
    'array': ('[]', None, None, False), 'call': ('short_control_never()', None, None, None),
    'variable': ('$missing', None, None, None)}
ROWS = {form + '-' + left + '-' + right: (form, left, right, True)
        for form in FORMS for left in ('false', 'true') for right in ('false', 'true')} | {
    'literal-or': ('BooleanOr', 'zero', 'one', True),
    'literal-and': ('BooleanAnd', 'one', 'zero', True),
    'string-or': ('LogicalOr', 'zero-string', 'truthy-string', True),
    'string-and': ('LogicalAnd', 'truthy-string', 'zero-string', True),
    'empty-and': ('BooleanAnd', 'empty-string', 'call', True),
    'null-or': ('BooleanOr', 'null', 'one', True),
    'negative-or': ('LogicalOr', 'negative', 'call', True),
    'zero-and': ('LogicalAnd', 'zero', 'call', True),
    'text-or': ('BooleanOr', 'double-zero', 'call', True),
    'dead-float': ('BooleanAnd', 'false', 'float-one', True),
    'dead-array': ('LogicalOr', 'true', 'array', True),
    'float-left-zero': ('BooleanOr', 'float-zero', 'true', False),
    'float-left-one': ('BooleanOr', 'float-one', 'call', False),
    'float-right-or': ('LogicalOr', 'false', 'float-one', False),
    'float-right-and': ('LogicalAnd', 'true', 'float-zero', False),
    'array-left': ('BooleanAnd', 'array', 'call', False),
    'array-right': ('BooleanOr', 'false', 'array', False),
    'variable-left': ('LogicalOr', 'variable', 'true', False),
    'variable-right': ('BooleanOr', 'false', 'variable', False)}
CONTROLS = {name: ("<?php $x = ((" + SCALARS[left][0] + ' ' + FORMS[form][0] + ' ' + SCALARS[right][0] + ") . null) . 'x';\n").encode()
            for name, (form, left, right, admitted) in ROWS.items()}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('short_root', 'short_root_child', 'short_root_l', 'short_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_short pcpath_short',
              origin + '_l = PORIGIN n_short pcpath_short_l',
              origin + '_r = PORIGIN n_short pcpath_short_r']
    wrong = 'PBOOL true' if index == 2 else 'PBOOL false'
    own = 'PBOOL false' if index == 2 else 'PBOOL true'
    for suffix, value in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(PINT ' + ('0' if index == 2 else '1') + ')')):
        state = 'S_short_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('PFLOAT 0', 'PSTRING ($ptascii("0"))'), ('PBOOL false', 'PINT 0'),
               ('PBOOL true', None), ('PBOOL false', None))[index]
    for suffix, value in zip(('_l', '_r'), mutants):
        child = origin + suffix
        if value is not None:
            for operation, replacement in (('drop', 'eps'), ('wrong', '(' + value + ')')):
                state = 'S_short_child' + suffix + '_' + operation
                guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                           '$string_read_request_base_saved(' + state + ', pstringread) = eps']
            state = 'S_short_precision' + suffix
            guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        else:
            state = 'S_short_unused'
            guards += [state + ' = S_after[.POOLS = $float_review_precision($special_review_pools(S_after.POOLS, ' + child + ', (PINT 99)), ' + child + ', 17)]',
                       '$compiled_read(' + state + ', ' + child + ') = eps',
                       '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($echo_value(' + own + '))',
                       '$string_read_request_base_saved(' + state + ', pstringread) =/= eps']
        left = 'expression_short_other' if suffix == '_l' else expression + '_l'
        right = 'expression_short_other' if suffix == '_r' else expression + '_r'
        if suffix == '_l':
            guards += ['expression_short_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        state = 'S_short_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_short, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_short ' + expression + '), (PCOCCURRENCE pcpath_short_l ' + left + '), (PCOCCURRENCE pcpath_short_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_short_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_short_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_short_precision, (' + origin + '_l)) = (14)',
               '$compiled_special_concat_bytes(S_short_precision, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, (name, (form, left_name, right_name, admitted)) in enumerate(ROWS.items()):
        state, origin = 'S_short_control_' + str(index), 'porigin_short_control_' + str(index)
        binary, expression = origin + '_binary', 'expression_short_control_' + str(index)
        b_or, left, right = FORMS[form][1], SCALARS[left_name], SCALARS[right_name]
        skipped = left[3] is not None and left[3] == b_or
        result = b_or if skipped else right[3] if left[3] is not None else None
        own = 'PBOOL ' + str(result).lower() if result is not None else None
        text = '1' if result else ''
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_short_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_short_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')',
                   '$origin_node(' + state + '.SOURCES, ' + binary + ') = (' + expression + ')',
                   expression + ' = NExprBinaryOp' + form + ' ' + expression + '_l ' + expression + '_r metadata_short_control_' + str(index),
                   '$compiled_read(' + state + ', ' + binary + ') = ' + ('(' + own + ')' if own else 'eps')]
        if admitted:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))']
        else:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        for field, scalar in ((0, left), (1, right)):
            child = binary + '_' + str(field)
            checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')']
            if field == 0 and scalar[1] is not None or field == 1 and not skipped and left[3] is not None and scalar[1] is not None:
                checks += ['$compiled_read(' + state + ', ' + child + ') = (' + scalar[1] + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(scalar[2]) + '))',
                           '$truth(' + state + ', ' + scalar[1] + ') = ' + str(scalar[3]).lower()]
            elif field == 1 and skipped:
                checks += [child + ' = PORIGIN n_short_dead_' + str(index) + ' pcpath_short_dead_' + str(index),
                           '$code_at(' + state + '.CODE, n_short_dead_' + str(index) + ') = (pcode_short_dead_' + str(index) + ')',
                           '$code_expression(pcode_short_dead_' + str(index) + '.EXPRESSIONS, pcpath_short_dead_' + str(index) + ') = eps',
                           '$compiled_read(' + state + ', ' + child + ') = eps',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_precision(' + state + ', (' + child + ')) = $source_precision(' + state + ', (' + child + '))']
        if name in ('literal-or', 'literal-and'):
            for field, bits in ((0, 0 if name == 'literal-or' else 4607182418800017408),
                                (1, 4607182418800017408 if name == 'literal-or' else 0)):
                changed, child = state + '_float_' + str(field), binary + '_' + str(field)
                scalar = left if field == 0 else right
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PFLOAT ' + str(bits) + '))]',
                           '$compiled_read(' + changed + ', ' + child + ') = (PFLOAT ' + str(bits) + ')',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii(' + json.dumps(scalar[2]) + '))',
                           '$truth(' + changed + ', PFLOAT ' + str(bits) + ') = ' + str(scalar[3]).lower(),
                           '$compiled_read(' + changed + ', ' + binary + ') = (' + own + ')',
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.arithmetic, source.unary, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
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
    report['scope'] = 'Four authentic-source-seeded logical fixtures add own-result/type, missing/typed or outcome-changing evaluated reads, both child source refusals and evaluated precision boundaries. The active OR left value is result-insensitive with a truthy RHS; no independent left-value coherence rejection is claimed. Decisive source cases preserve admission with an unused raw pool entry and conflicting RHS precision while compiled_read stays absent. Independent compiler tables cover all four AST forms and Boolean combinations, string zero/empty/truthy leaves, null and integer truth, dead calls/float/array syntax, and live float/array/nonconstant refusals. Literal-pool floats preserve original truth, byte certificates and own results while evaluated type gates refuse them. Actual dead RHS code/read absence and declaration precision fallback are distinct. Native4 are reused once, author recipes remain exact prefixes, and owners/supplied throw/fixed bounds/budgets retain their laws. Fixture/compiler conditions carry source0 and do not validate new runtime coercion or ownership routes.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
