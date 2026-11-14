#!/usr/bin/env python3
"""Quiet primitive integer coercions retain original values and key owners."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_primitive_integer_binary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_null_cast_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
TRUTH = prior.prior.prior.TRUTH
TRUE = ('TERNARY', TRUTH, ('COMPILED', 'PBOOL true', 'true'), True)
FALSE = ('TERNARY', TRUTH, ('COMPILED', 'PBOOL false', 'false'), True)
NULL = ('NULL_TERNARY',)
ONE = prior.ONE
THREE = ('ADD', ONE, ('ADD', ONE, ONE, 2), 3)
INTEGER_OPS = ('MODULO', 'BITAND', 'BITOR', 'BITXOR', 'SHIFTLEFT', 'SHIFTRIGHT')
TREES = (
    ('SHIFTRIGHT', ('BITOR', TRUE, NULL, 1), NULL, 1),
    ('BITNOT', ('BITXOR', ('POSITIVE', ('BITAND', TRUE, FALSE, 0), 0), NULL, 0), -1),
    ('SHIFTLEFT', NULL, TRUE, 0),
    ('BITNOT', ('BITOR', ('POSITIVE', THREE, 3), ('POSITIVE', ('MODULO', TRUE, TRUE, 0), 0), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    kind = tree[0]
    if kind not in INTEGER_OPS:
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY ' + kind + ' ' + expression + '_0 ' + expression + '_1',
               'S.COMPLETION = NORMAL']
    children = []
    for index, child in enumerate(tree[1:3]):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        child_value, number = value(checks, child_tag, child)
        checks += ['$string_read_runtime_integer_quiet(' + child_value + ')',
                   '$long_range(' + number + ')']
        if kind in ('BITAND', 'BITOR', 'BITXOR'):
            checks += ['$integer_tmp_source(expression_' + child_tag + ')']
        children.append((child_value, number))
    left, right = children
    number = integers.integer(tree[-1])
    result = 'PINT ' + number
    checks += ['$integer_coerce(S, ' + left[0] + ', 5) = S[.RESULT = KNOWN (PINT ' + left[1] + ')]',
               '$integer_coerce(S[.RESULT = KNOWN (PINT ' + left[1] + ')], ' + right[0] + ', 5) = S[.RESULT = KNOWN (PINT ' + right[1] + ')]',
               '$integer_source_swapped(S, ' + origin + ', ' + kind + ', KNOWN (' + left[0] + '), KNOWN (' + right[0] + ')) = (false)',
               '$integer_binary(' + kind + ', ' + left[1] + ', ' + right[1] + ') = IRESULT ' + number,
               '$long_range(' + number + ')',
               '$binary_apply(S, ' + kind + ', ' + left[0] + ', ' + right[0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, number


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES
conditions = prior.conditions


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four emitted MOD/BW/shift trees admit exact BOOL/NULL/signed64 INT values under explicit types/ranges, ordered quiet full-state integer_coerce, exact IRESULT and actual full-state binary_apply. New non-PINT operands require NORMAL; original pure-PINT completion independence is retained. Genuine ternary/unary TMP operands preserve unchanged387 slot authority. Zero-divisor/negative-shift errors, nonquiet FLOAT/string/owning/location/warningful operands and wider producers stay outside. Real REQUEST keys1/-1/0/-4 preserve captured14/live17 precision, returning Warning, supplied Throwable, bounds, cleanup and budget rejoining. FLOAT BYTE/formatter/compiler/API/owner and exact holds are unchanged; saved native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
