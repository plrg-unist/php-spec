"""Integer complement retains a certified coercive child across raw-key rebinding."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBitwiseNot expression_bitnot_child metadata_cond)')
    early = lines(r'''
expression_bitnot_child = NExprBinaryOpMinus expression_bitnot_division expression_bitnot_true metadata_bitnot_child
expression_bitnot_division = NExprBinaryOpDiv expression_bitnot_null expression_bitnot_string metadata_bitnot_division
expression_bitnot_true = NExprConstFetch (NName (BYTES text_bitnot_true) metadata_bitnot_true_name) metadata_bitnot_true
expression_bitnot_null = NExprConstFetch (NName (BYTES text_bitnot_null) metadata_bitnot_null_name) metadata_bitnot_null
expression_bitnot_string = NScalarString (BYTES text_bitnot_string) metadata_bitnot_string
$ptlc($base64(text_bitnot_true)) = $ptascii("true")
$ptlc($base64(text_bitnot_null)) = $ptascii("null")
$base64(text_bitnot_string) = $ptascii("2")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_bitnot_child)
$origin_child((porigin_bitnot_child),[PCFIELD 0]) = (porigin_bitnot_division)
$origin_child((porigin_bitnot_child),[PCFIELD 1]) = (porigin_bitnot_true)
$origin_child((porigin_bitnot_division),[PCFIELD 0]) = (porigin_bitnot_null)
$origin_child((porigin_bitnot_division),[PCFIELD 1]) = (porigin_bitnot_string)
$origin_child((porigin_bitnot_true),[PCFIELD 0]) = (porigin_bitnot_true_name)
$origin_child((porigin_bitnot_null),[PCFIELD 0]) = (porigin_bitnot_null_name)
$origin_node(S_capture.SOURCES,porigin_bitnot_true_name) = (NName (BYTES text_bitnot_true) metadata_bitnot_true_name)
$origin_node(S_capture.SOURCES,porigin_bitnot_null_name) = (NName (BYTES text_bitnot_null) metadata_bitnot_null_name)
''')
    for name, value in (('child', 'PINT $(-1)'), ('division', 'PINT 0'), ('true', 'PBOOL true'),
                        ('null', 'PNULL'), ('string', 'PSTRING ($ptascii("2"))')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_bitnot_{name}) = (expression_bitnot_{name})',
                  f'$compiled_read(S_capture,porigin_bitnot_{name}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_bitnot_{name},{value})']
    early += lines(r'''
~$string_read_raw_unary_integer(S_capture,porigin_left,0)
$bitnot_value(S_capture,PINT $(-1),0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_bitnot_child = PORIGIN n_unit pcpath_bitnot_child
porigin_bitnot_division = PORIGIN n_unit pcpath_bitnot_division
porigin_bitnot_true = PORIGIN n_unit pcpath_bitnot_true
porigin_bitnot_null = PORIGIN n_unit pcpath_bitnot_null
porigin_bitnot_string = PORIGIN n_unit pcpath_bitnot_string
porigin_bitnot_true_name = PORIGIN n_unit pcpath_bitnot_true_name
porigin_bitnot_null_name = PORIGIN n_unit pcpath_bitnot_null_name
S_budget_bitnot = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
~$string_read_raw_unary_integer(S_budget_bitnot,porigin_left,0)
$string_read_raw_truth(S_budget_bitnot,porigin_left,PINT 0)
$string_read_raw_known_base(S_budget_bitnot,porigin_base,pvalue_base)
S_shorthand_bitnot = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprBitwiseNot expression_bitnot_child metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_bitnot,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_bitnot,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PINT 1'),
            ('child', 'pcpath_bitnot_child', 'PINT 0'),
            ('child_tag', 'pcpath_bitnot_child', 'PFLOAT 13830554455654793216'),
            ('true_tag', 'pcpath_bitnot_true', 'PINT 1')):
        own = value if label == 'own' else 'PINT 0'
        checks += [f'S_bad_bitnot_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_bitnot_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_bitnot_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('child', 'pcpath_bitnot_child', 'NExprBinaryOpMinus expression_bitnot_division expression_bitnot_true eps'),
            ('name', 'pcpath_bitnot_true_name', 'NName (BYTES text_bitnot_true) eps')):
        checks += [f'S_bad_bitnot_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_bitnot_{label}_source,porigin_left,PINT 0)']

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        spelling = f'$({i})' if i < 0 else str(i)
        return f'NScalarInt (INTEGER {spelling})', f'PINT {spelling}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    add = ('Plus', 'PINT 3', string(b'2'), true)
    complement = ('BitwiseNot', 'PINT $(-4)', add)
    zero = ('BitwiseNot', 'PINT 0', ('Minus', 'PINT $(-1)', ('Div', 'PINT 0', null, string(b'2')), true))
    minimum, maximum = -9223372036854775808, 9223372036854775807
    minimum_child = ('Plus', f'PINT $({minimum})', integer(minimum), false)
    maximum_child = ('Plus', f'PINT {maximum}', integer(maximum), false)
    bad_division = ('Div', 'PINT 1', string(b'1'), integer(0))
    bad_legacy = ('Div', 'PINT 1', integer(1), integer(0))
    matrices = [
        ('source_a', ('BitwiseNot', 'PINT $(-4)', ('Mul', 'PINT 3', add, string(b'1'))), True),
        ('fresh_gate', complement, True),
        ('reference_zero', zero, True),
        ('nested_complement', ('BitwiseNot', 'PINT 3', complement), True),
        ('positive_parent', ('UnaryPlus', 'PINT $(-4)', complement), True),
        ('negative_parent', ('UnaryMinus', 'PINT 4', complement), True),
        ('signed_child', ('BitwiseNot', 'PINT 2', ('UnaryMinus', 'PINT $(-3)', add)), True),
        ('integer_parent', ('Plus', 'PINT $(-3)', complement, integer(1)), True),
        ('float_parent', ('Plus', 'PFLOAT 13837309855095848960', complement, string(b'1.0')), True),
        ('folded_not', ('BooleanNot', 'PBOOL true', zero), True),
        ('minimum_child', ('BitwiseNot', f'PINT {maximum}', minimum_child), True),
        ('maximum_child', ('BitwiseNot', f'PINT $({minimum})', maximum_child), True),
        ('legacy_literal', ('BitwiseNot', 'PINT $(-4)', integer(3)), True),
        ('legacy_true_sign', ('BitwiseNot', 'PINT 0', ('UnaryMinus', 'PINT $(-1)', true)), True),
        ('legacy_nested', ('BitwiseNot', 'PINT 0', ('BitwiseNot', 'PINT $(-1)', integer(0))), True),
        ('wrong_result', ('BitwiseNot', 'PINT 4', add), False),
        ('wrong_child', ('BitwiseNot', 'PINT $(-5)', ('Plus', 'PINT 4', string(b'2'), true)), False),
        ('outside_own', ('BitwiseNot', f'PINT {maximum + 1}', add), False),
        ('outside_child', ('BitwiseNot', 'PINT 0', ('Plus', f'PINT {maximum + 1}', integer(maximum), true)), False),
        ('direct_string', ('BitwiseNot', 'PINT $(-3)', string(b'2')), False),
        ('direct_true', ('BitwiseNot', 'PINT $(-2)', true), False),
        ('direct_null', ('BitwiseNot', 'PINT $(-1)', null), False),
        ('direct_float', ('BitwiseNot', 'PINT $(-3)', ('NScalarFloat (FLOAT "4000000000000000")', 'PFLOAT 4611686018427387904')), False),
        ('fraction', ('BitwiseNot', 'PINT $(-2)', ('Div', 'PINT 1', string(b'3'), string(b'2'))), False),
        ('zero_divisor', ('BitwiseNot', 'PINT $(-2)', bad_division), False),
        ('nested_zero', ('BitwiseNot', 'PINT $(-2)', ('Plus', 'PINT 1', bad_legacy, false)), False),
        ('leading', ('BitwiseNot', 'PINT $(-3)', ('Plus', 'PINT 2', string(b'2x'), false)), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection(label, tree, accepted)
    checks += lines(r'''
~$string_read_raw_unary_integer(S_sign_fresh_gate,porigin_left,$(-4))
S_zero_budget_bitnot = S_sign_zero_divisor[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT $(-2))]
~$string_read_raw_unary_integer(S_zero_budget_bitnot,porigin_left,$(-2))
$bitnot_value(S_zero_budget_bitnot,PINT 1,0) = S_zero_budget_bitnot[.RESULT = KNOWN (PINT $(-2))]
~$string_read_raw_truth(S_zero_budget_bitnot,porigin_left,PINT $(-2))
S_nested_budget_bitnot = S_sign_nested_zero[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
~$string_read_raw_unary_integer(S_nested_budget_bitnot,porigin_left,$(-2))
$string_read_raw_truth(S_nested_budget_bitnot,PORIGIN n_unit (pcpath_left ++ [PCFIELD 0,PCFIELD 0]),PINT 1)
~$string_read_raw_truth(S_nested_budget_bitnot,porigin_left,PINT $(-2))
S_range_budget_bitnot = S_sign_outside_child[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
~$string_read_raw_unary_integer(S_range_budget_bitnot,porigin_left,0)
~$string_read_raw_truth(S_range_budget_bitnot,porigin_left,PINT 0)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
