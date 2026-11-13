#!/usr/bin/env python3
"""Nested numeric unary CONCAT keys preserve real Warning continuation history."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nested_unary_numeric_special_concat_leading_key_cases as cases
import string_offset_request_base_unary_numeric_special_concat_leading_key_protocol as prior

runner = prior.runner


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    chain = (('NEGATIVE', 'NEGATIVE'), ('POSITIVE', 'NEGATIVE'),
             ('NEGATIVE', 'POSITIVE', 'NEGATIVE'),
             ('POSITIVE', 'NEGATIVE', 'POSITIVE'))[index]
    values = ((1, -1), (-1, -1), (1, -1, -1), (-4, -4, 4))[index]
    at = checks.index('$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_unary)')
    extra = [checks[at], 'porigin_unary_0 = porigin_unary',
             'S.PRECISIONINI = $ptascii("17") /\\ $precision_value(S) = 17']
    for depth, unary in enumerate(chain):
        origin = 'porigin_unary_' + str(depth)
        expression = 'expression_unary' if depth == 0 else 'expression_unary_' + str(depth)
        child = 'expression_literal' if depth + 1 == len(chain) else 'expression_unary_' + str(depth + 1)
        node = 'NExprUnaryPlus' if unary == 'POSITIVE' else 'NExprUnaryMinus'
        extra += [
            '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
            expression + ' = ' + node + ' ' + child + ' metadata_unary_' + str(depth),
            '$pfshape(' + expression + ') = PFUNARY ' + unary + ' ' + child,
            '$compiled_precision(S, (' + origin + ')) = (14)',
            '$compiled_read(S, ' + origin + ') = (pvalue_unary_' + str(depth) + ')',
            '$parser_literal_at(' + expression + ', 14) = eps',
            '$parser_literal_text_at(pvalue_unary_' + str(depth) + ', 14) = ($ptascii("' + str(values[depth]) + '"))',
            '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii("' + str(values[depth]) + '"))']
        target = 'porigin_literal' if depth + 1 == len(chain) else 'porigin_unary_' + str(depth + 1)
        extra += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + target + ')']
    extra += [
        '$origin_node(S.SOURCES, porigin_literal) = (expression_literal)',
        '$compiled_precision(S, (porigin_literal)) = (14)',
        '$parser_literal_at(expression_literal, 14) = (pvalue_literal)',
        '$compiled_read(S, porigin_literal) = (pvalue_literal)',
        'pvalue_unary = pvalue_unary_0']
    if index < 2:
        term = str(values[0]) if values[0] >= 0 else '$(' + str(values[0]) + ')'
        extra += ['expression_literal = NScalarInt (INTEGER 1) metadata_literal',
                  'pvalue_literal = PINT 1', 'pvalue_unary = PINT ' + term]
    else:
        extra += ['expression_literal = NScalarFloat (FLOAT text_literal) metadata_literal',
                  'pvalue_literal = PFLOAT n_bits_literal',
                  'pvalue_unary = PFLOAT n_bits_unary',
                  '$parser_literal_text_at(pvalue_unary, 17) = (n_live_text*)',
                  'n_live_text* =/= $ptascii("' + str(values[0]) + '")']
    for depth in reversed(range(len(chain))):
        child_value = 'pvalue_literal' if depth + 1 == len(chain) else 'pvalue_unary_' + str(depth + 1)
        extra += ['$unary_apply(S, ' + chain[depth] + ', ' + child_value + ', 0) = S[.RESULT = KNOWN pvalue_unary_' + str(depth) + ']']
    checks[at:at + (19 if index < 2 else 21)] = extra
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(prior.__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh finite nested numeric-unary plus resolved bool/null CONCAT source-state fixtures at compile14/live17. Every unary node has actual child, own compiled fact/precision, pure PHP result and quiet conversion checks. Existing borrowed-owner, fixed-index, throw, bounds and budget laws remain. Older source/native/state and compiler-control cuts retain their identities without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
