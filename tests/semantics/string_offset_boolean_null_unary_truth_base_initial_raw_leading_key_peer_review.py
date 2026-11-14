"""Quiet null signs retain exact child authority across raw-key reference rebinding."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprUnaryMinus expression_primitive_child metadata_cond)')
    early = lines(r'''
expression_primitive_child = NExprConstFetch (NName (BYTES text_primitive_null) metadata_primitive_name) metadata_primitive_child
$ptlc($base64(text_primitive_null)) = $ptascii("null")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_primitive_child)
$origin_node(S_capture.SOURCES,porigin_primitive_child) = (expression_primitive_child)
$compiled_read(S_capture,porigin_primitive_child) = (PNULL)
$origin_child((porigin_primitive_child),[PCFIELD 0]) = (porigin_primitive_name)
$origin_node(S_capture.SOURCES,porigin_primitive_name) = (NName (BYTES text_primitive_null) metadata_primitive_name)
$string_read_raw_truth(S_capture,porigin_primitive_child,PNULL)
~$string_read_raw_unary_integer(S_capture,porigin_left,0)
$coerce_number(PNULL) = COERCED (NINT 0) false
$unary_apply(S_capture,NEGATIVE,PNULL,0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_primitive_child = PORIGIN n_unit pcpath_primitive_child
porigin_primitive_name = PORIGIN n_unit pcpath_primitive_name
S_budget_primitive = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
~$string_read_raw_unary_integer(S_budget_primitive,porigin_left,0)
$string_read_raw_truth(S_budget_primitive,porigin_left,PINT 0)
$string_read_raw_known_base(S_budget_primitive,porigin_base,pvalue_base)
S_shorthand_primitive = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprUnaryMinus expression_primitive_child metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_primitive,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_primitive,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PINT 1'),
            ('child_bool', 'pcpath_primitive_child', 'PBOOL false'),
            ('child_int', 'pcpath_primitive_child', 'PINT 0'),
            ('child_float', 'pcpath_primitive_child', 'PFLOAT 0'),
            ('child_string', 'pcpath_primitive_child', 'PSTRING ([48])')):
        own = value if label == 'own' else 'PINT 0'
        checks += [f'S_bad_primitive_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_primitive_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_primitive_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('child', 'pcpath_primitive_child', 'NExprConstFetch (NName (BYTES text_primitive_null) metadata_primitive_name) eps'),
            ('name', 'pcpath_primitive_name', 'NName (BYTES text_primitive_null) eps')):
        checks += [f'S_bad_primitive_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_primitive_{label}_source,porigin_left,PINT 0)']
    checks += lines(r'''
S_bad_primitive_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_primitive_child 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_primitive_code,porigin_left,PINT 0)
''')

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        spelling = f'$({i})' if i < 0 else str(i)
        return f'NScalarInt (INTEGER {spelling})', f'PINT {spelling}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    plus_false = ('UnaryPlus', 'PINT 0', false)
    minus_null = ('UnaryMinus', 'PINT 0', null)
    minimum, maximum = -9223372036854775808, 9223372036854775807
    one_float = ('NScalarFloat (FLOAT "3ff0000000000000")', 'PFLOAT 4607182418800017408')
    bad_legacy = ('Div', 'PINT 1', integer(1), integer(0))
    matrices = [
        ('source_a', plus_false, True),
        ('reference_null', minus_null, True),
        ('fresh_null_plus', ('UnaryPlus', 'PINT 0', null), True),
        ('fresh_false_minus', ('UnaryMinus', 'PINT 0', false), True),
        ('legacy_true_plus', ('UnaryPlus', 'PINT 1', true), True),
        ('legacy_true_minus', ('UnaryMinus', 'PINT $(-1)', true), True),
        ('not_false', ('UnaryPlus', 'PINT 1', ('BooleanNot', 'PBOOL true', false)), True),
        ('not_true', ('UnaryMinus', 'PINT 0', ('BooleanNot', 'PBOOL false', true)), True),
        ('nested_signs', ('UnaryMinus', 'PINT 0', ('UnaryPlus', 'PINT 0', minus_null)), True),
        ('complement_parent', ('BitwiseNot', 'PINT $(-1)', plus_false), True),
        ('integer_parent', ('Plus', 'PINT 1', plus_false, integer(1)), True),
        ('float_parent', ('Plus', 'PFLOAT 4607182418800017408', plus_false, string(b'1.0')), True),
        ('folded_not', ('BooleanNot', 'PBOOL true', minus_null), True),
        ('legacy_minimum', ('UnaryPlus', f'PINT $({minimum})', integer(minimum)), True),
        ('legacy_minimum_float', ('UnaryMinus', 'PFLOAT 4890909195324358656', integer(minimum)), True),
        ('legacy_string', ('UnaryPlus', 'PINT 2', string(b'2')), True),
        ('legacy_float', ('UnaryPlus', 'PFLOAT 4607182418800017408', one_float), True),
        ('wrong_result', ('UnaryPlus', 'PINT 1', false), False),
        ('wrong_own_tag', ('UnaryPlus', 'PBOOL false', false), False),
        ('outside_own', ('UnaryPlus', f'PINT {maximum + 1}', false), False),
        ('outside_child', ('UnaryPlus', 'PINT 0', ('Plus', f'PINT {maximum + 1}', integer(maximum), true)), False),
        ('float_integer_forgery', ('UnaryPlus', 'PINT 1', one_float), False),
        ('leading_string', ('UnaryPlus', 'PINT 2', string(b'2x')), False),
        ('cached_not', ('UnaryPlus', 'PINT 0', ('BooleanNot', 'PBOOL false', bad_legacy)), False),
        ('nested_zero', ('UnaryMinus', 'PINT $(-1)', ('Plus', 'PINT 1', bad_legacy, false)), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection(label, tree, accepted)
    checks += lines(r'''
~$string_read_raw_unary_integer(S_sign_fresh_null_plus,porigin_left,0)
~$string_read_raw_unary_integer(S_sign_fresh_false_minus,porigin_left,0)
S_cached_budget_primitive = S_sign_cached_not[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
~$string_read_raw_unary_integer(S_cached_budget_primitive,porigin_left,0)
$string_read_raw_truth(S_cached_budget_primitive,PORIGIN n_unit (pcpath_left ++ [PCFIELD 0]),PBOOL false)
$unary_apply(S_cached_budget_primitive,POSITIVE,PBOOL false,0) = S_cached_budget_primitive[.RESULT = KNOWN (PINT 0)]
~$string_read_raw_truth(S_cached_budget_primitive,porigin_left,PINT 0)
S_nested_budget_primitive = S_sign_nested_zero[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
~$string_read_raw_unary_integer(S_nested_budget_primitive,porigin_left,$(-1))
$string_read_raw_truth(S_nested_budget_primitive,PORIGIN n_unit (pcpath_left ++ [PCFIELD 0,PCFIELD 0]),PINT 1)
~$string_read_raw_truth(S_nested_budget_primitive,porigin_left,PINT $(-1))
S_range_budget_primitive = S_sign_outside_child[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
~$string_read_raw_unary_integer(S_range_budget_primitive,porigin_left,0)
~$string_read_raw_truth(S_range_budget_primitive,porigin_left,PINT 0)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
