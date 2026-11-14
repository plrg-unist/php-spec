"""Finite FLOAT comparisons and XOR retain frozen raw reference-key offsets."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpLogicalXor expression_boolean_equal expression_boolean_word metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = (PBOOL false)')
    body = body.replace('~$truth(S_capture,PINT 0)', '~$truth(S_capture,PBOOL false)')
    old_wrong = 'S_wrong_left = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: ppool.CONSTANTS]]]'
    assert body.count(old_wrong) == 1
    body = body.replace(old_wrong, old_wrong.replace('PBOOL false', 'PBOOL true'))
    early = lines(r'''
expression_boolean_equal = NExprBinaryOpEqual expression_boolean_division expression_boolean_one metadata_boolean_equal
expression_boolean_division = NExprBinaryOpDiv expression_boolean_two_string expression_boolean_two metadata_boolean_division
expression_boolean_word = NScalarString (BYTES text_boolean_word) metadata_boolean_word
expression_boolean_two_string = NScalarString (BYTES text_boolean_two_string) metadata_boolean_two_string
expression_boolean_two = NScalarInt (INTEGER 2) metadata_boolean_two
expression_boolean_one = NScalarInt (INTEGER 1) metadata_boolean_one
$base64(text_boolean_word) = $ptascii("word")
$base64(text_boolean_two_string) = $ptascii("2.0")
''')
    children = (
        ('left', 0, 'equal', 'PBOOL true'), ('left', 1, 'word', 'PSTRING ($ptascii("word"))'),
        ('boolean_equal', 0, 'division', 'PFLOAT 4607182418800017408'), ('boolean_equal', 1, 'one', 'PINT 1'),
        ('boolean_division', 0, 'two_string', 'PSTRING ($ptascii("2.0"))'), ('boolean_division', 1, 'two', 'PINT 2'))
    for parent, field, child, value in children:
        early += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_boolean_{child})',
                  f'$origin_node(S_capture.SOURCES,porigin_boolean_{child}) = (expression_boolean_{child})',
                  f'$compiled_read(S_capture,porigin_boolean_{child}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_boolean_{child},{value})']
    early += lines(r'''
$binary_apply(S_capture,DIVIDE,PSTRING ($ptascii("2.0")),PINT 2,0) = S_capture[.RESULT = KNOWN (PFLOAT 4607182418800017408)]
$binary_apply(S_capture,EQUAL,PFLOAT 4607182418800017408,PINT 1,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$binary_apply(S_capture,LOGICALXOR,PBOOL true,PSTRING ($ptascii("word")),0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_truth(S_capture,porigin_left,PBOOL false)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PBOOL false)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for name in (child for _, _, child, _ in children):
        checks.append(f'porigin_boolean_{name} = PORIGIN n_unit pcpath_boolean_{name}')
    checks += lines(r'''
S_budget_boolean = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$string_read_raw_truth(S_budget_boolean,porigin_left,PBOOL false)
$string_read_raw_known_base(S_budget_boolean,porigin_base,pvalue_base)
S_shorthand_boolean = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprBinaryOpLogicalXor expression_boolean_equal expression_boolean_word metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_boolean,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_boolean,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PBOOL true'), ('own_tag', 'pcpath_left', 'PINT 0'),
            ('equal', 'pcpath_boolean_equal', 'PBOOL false'), ('division', 'pcpath_boolean_division', 'PFLOAT 0'),
            ('division_tag', 'pcpath_boolean_division', 'PINT 1'), ('word', 'pcpath_boolean_word', 'PSTRING ($ptascii("0"))')):
        own = value if label in ('own', 'own_tag') else 'PBOOL false'
        checks += [f'S_bad_boolean_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_boolean_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_boolean_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('equal', 'pcpath_boolean_equal', 'NExprBinaryOpEqual expression_boolean_division expression_boolean_one eps'),
            ('division', 'pcpath_boolean_division', 'NExprBinaryOpDiv expression_boolean_two_string expression_boolean_two eps'),
            ('swapped', 'pcpath_boolean_equal', 'NExprBinaryOpEqual expression_boolean_one expression_boolean_division metadata_boolean_equal')):
        checks += [f'S_bad_boolean_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_boolean_{label}_source,porigin_left,PBOOL false)']
    checks += lines(r'''
S_bad_boolean_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_boolean_division 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_boolean_code,porigin_left,PBOOL false)
~$string_read_raw_known_base(S_bad_boolean_code,porigin_base,pvalue_base)
''')

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        return f'NScalarInt (INTEGER {i})', f'PINT {i}'
    def floating(bits):
        return f'NScalarFloat (FLOAT "{bits:016x}")', f'PFLOAT {bits}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    one, half, zero, negative_zero = floating(4607182418800017408), floating(4609434218613702656), floating(0), floating(9223372036854775808)
    infinity, nan = floating(9218868437227405312), floating(9221120237041090560)
    division = ('Div', 'PFLOAT 4607182418800017408', string(b'2.0'), integer(2))
    bad_division = ('Div', 'PFLOAT 4607182418800017408', one, zero)
    equal = ('Equal', 'PBOOL true', division, integer(1))
    xor_false = ('LogicalXor', 'PBOOL false', equal, string(b'word'))
    matrices = [
        ('equal_true', ('Equal', 'PBOOL true', one, integer(1)), True), ('equal_false', ('Equal', 'PBOOL false', half, integer(1)), True),
        ('notequal_true', ('NotEqual', 'PBOOL true', half, integer(1)), True), ('notequal_false', ('NotEqual', 'PBOOL false', one, integer(1)), True),
        ('identical_true', ('Identical', 'PBOOL true', one, one), True), ('identical_false', ('Identical', 'PBOOL false', one, integer(1)), True),
        ('notidentical_true', ('NotIdentical', 'PBOOL true', one, integer(1)), True), ('notidentical_false', ('NotIdentical', 'PBOOL false', one, one), True),
        ('less_true', ('Smaller', 'PBOOL true', one, half), True), ('less_false', ('Smaller', 'PBOOL false', half, one), True),
        ('lessequal_true', ('SmallerOrEqual', 'PBOOL true', one, integer(1)), True), ('lessequal_false', ('SmallerOrEqual', 'PBOOL false', half, one), True),
        ('greater_true', ('Greater', 'PBOOL true', half, one), True), ('greater_false', ('Greater', 'PBOOL false', one, half), True),
        ('greaterequal_true', ('GreaterOrEqual', 'PBOOL true', one, integer(1)), True), ('greaterequal_false', ('GreaterOrEqual', 'PBOOL false', one, half), True),
        ('signed_zero_identity', ('Identical', 'PBOOL true', zero, negative_zero), True),
        ('xor_source', xor_false, True), ('xor_float_true', ('LogicalXor', 'PBOOL true', one, false), True),
        ('xor_float_false', ('LogicalXor', 'PBOOL false', one, true), True), ('xor_zero', ('LogicalXor', 'PBOOL false', null, negative_zero), True),
        ('xor_subnormal', ('LogicalXor', 'PBOOL true', floating(1), false), True),
        ('xor_string_zero', ('LogicalXor', 'PBOOL true', one, string(b'0')), True),
        ('xor_signed', ('LogicalXor', 'PBOOL true', ('UnaryMinus', 'PFLOAT 13832806255468478464', half), zero), True),
        ('xor_nested', ('LogicalXor', 'PBOOL true', xor_false, ('Smaller', 'PBOOL true', one, half)), True),
        ('not_parent', ('BooleanNot', 'PBOOL true', xor_false), True),
        ('wrong_result', ('LogicalXor', 'PBOOL true', equal, string(b'word')), False),
        ('wrong_tag', ('LogicalXor', 'PINT 0', equal, string(b'word')), False),
        ('nan_compare', ('Equal', 'PBOOL false', nan, one), False), ('infinite_compare', ('Equal', 'PBOOL true', infinity, infinity), False),
        ('nan_xor', ('LogicalXor', 'PBOOL true', nan, false), False), ('infinite_xor', ('LogicalXor', 'PBOOL true', infinity, false), False),
        ('negative_infinite_xor', ('LogicalXor', 'PBOOL true', floating(18442240474082181120), false), False),
        ('float_payload_mismatch', ('Equal', 'PBOOL true', ('NScalarFloat (FLOAT "3ff8000000000000")', 'PFLOAT 4607182418800017408'), one), False),
        ('or_gate', ('LogicalOr', 'PBOOL true', one, false), True), ('and_gate', ('LogicalAnd', 'PBOOL false', one, false), True),
        ('spaceship', ('Spaceship', 'PBOOL false', one, one), False),
        ('cached_division', ('LogicalXor', 'PBOOL true', bad_division, false), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection('boolean_' + label, tree, accepted)
    checks += lines(r'''
S_cached_budget_boolean = S_sign_boolean_cached_division[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$binary_apply(S_cached_budget_boolean,LOGICALXOR,PFLOAT 4607182418800017408,PBOOL false,0) = S_cached_budget_boolean
~$string_read_raw_truth(S_cached_budget_boolean,porigin_left,PBOOL true)
S_missing_budget_boolean = S_sign_boolean_xor_source[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL false)][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR (pcpath_left ++ [PCFIELD 0]) 18 false) :: pcode.EXPRESSIONS]]]
$binary_apply(S_missing_budget_boolean,LOGICALXOR,PBOOL true,PSTRING ($ptascii("word")),0) = S_missing_budget_boolean[.RESULT = KNOWN (PBOOL true)]
~$string_read_raw_truth(S_missing_budget_boolean,porigin_left,PBOOL false)
S_masked_nan_boolean = S_sign_boolean_nan_xor[.REPORTING = 0]
~$string_read_raw_truth(S_masked_nan_boolean,porigin_left,PBOOL true)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
