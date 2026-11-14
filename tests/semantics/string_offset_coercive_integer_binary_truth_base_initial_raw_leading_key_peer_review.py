"""Quiet coercive powers and shifts retain frozen raw keys through reference rebinding."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpShiftRight expression_integer_power expression_integer_true metadata_cond)')
    early = lines(r'''
expression_integer_power = NExprBinaryOpPow expression_integer_null expression_integer_false metadata_integer_power
expression_integer_true = NExprConstFetch (NName (BYTES text_integer_true) metadata_integer_true_name) metadata_integer_true
expression_integer_false = NExprConstFetch (NName (BYTES text_integer_false) metadata_integer_false_name) metadata_integer_false
expression_integer_null = NExprConstFetch (NName (BYTES text_integer_null) metadata_integer_null_name) metadata_integer_null
$ptlc($base64(text_integer_true)) = $ptascii("true")
$ptlc($base64(text_integer_false)) = $ptascii("false")
$ptlc($base64(text_integer_null)) = $ptascii("null")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_integer_power)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_integer_true)
$origin_child((porigin_integer_power),[PCFIELD 0]) = (porigin_integer_null)
$origin_child((porigin_integer_power),[PCFIELD 1]) = (porigin_integer_false)
''')
    for name, value in (('power', 'PINT 1'), ('true', 'PBOOL true'), ('false', 'PBOOL false'), ('null', 'PNULL')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_integer_{name}) = (expression_integer_{name})',
                  f'$compiled_read(S_capture,porigin_integer_{name}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_integer_{name},{value})']
        if name != 'power':
            early += [f'$origin_child((porigin_integer_{name}),[PCFIELD 0]) = (porigin_integer_{name}_name)',
                      f'$origin_node(S_capture.SOURCES,porigin_integer_{name}_name) = (NName (BYTES text_integer_{name}) metadata_integer_{name}_name)']
    early += lines(r'''
~$string_read_raw_unary_integer(S_capture,porigin_left,0)
~$string_read_raw_unary_integer(S_capture,porigin_integer_power,1)
$power_prepare(NINT 0,NINT 0) = POWERDONE (NINT 1) false
$binary_apply(S_capture,POWER,PNULL,PBOOL false,0) = S_capture[.RESULT = KNOWN (PINT 1)]
$binary_apply(S_capture,SHIFTRIGHT,PINT 1,PBOOL true,0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_integer_power = PORIGIN n_unit pcpath_integer_power
porigin_integer_true = PORIGIN n_unit pcpath_integer_true
porigin_integer_false = PORIGIN n_unit pcpath_integer_false
porigin_integer_null = PORIGIN n_unit pcpath_integer_null
porigin_integer_false_name = PORIGIN n_unit pcpath_integer_false_name
S_budget_integer_binary = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
~$string_read_raw_unary_integer(S_budget_integer_binary,porigin_left,0)
$string_read_raw_truth(S_budget_integer_binary,porigin_left,PINT 0)
$string_read_raw_known_base(S_budget_integer_binary,porigin_base,pvalue_base)
S_shorthand_integer_binary = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprBinaryOpShiftRight expression_integer_power expression_integer_true metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_integer_binary,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_integer_binary,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PINT 1'),
            ('power', 'pcpath_integer_power', 'PINT 2'),
            ('power_tag', 'pcpath_integer_power', 'PFLOAT 4607182418800017408'),
            ('true_tag', 'pcpath_integer_true', 'PINT 1')):
        own = value if label == 'own' else 'PINT 0'
        checks += [f'S_bad_integer_binary_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_integer_binary_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_integer_binary_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('power', 'pcpath_integer_power', 'NExprBinaryOpPow expression_integer_null expression_integer_false eps'),
            ('name', 'pcpath_integer_false_name', 'NName (BYTES text_integer_false) eps')):
        checks += [f'S_bad_integer_binary_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_integer_binary_{label}_source,porigin_left,PINT 0)']

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        spelling = f'$({i})' if i < 0 else str(i)
        return f'NScalarInt (INTEGER {spelling})', f'PINT {spelling}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    add = ('Plus', 'PINT 6', string(b'6'), false)
    modulo = ('Mod', 'PINT 2', add, string(b'4'))
    shifted = ('ShiftLeft', 'PINT 4', modulo, true)
    mixed_and = ('BitwiseAnd', 'PINT 1', string(b'1'), true)
    source_a = ('BitwiseXor', 'PINT 1', ('BitwiseOr', 'PINT 5', shifted, mixed_and), integer(4))
    power = ('Pow', 'PINT 1', null, false)
    source_b = ('ShiftRight', 'PINT 0', power, true)
    minimum, maximum = -9223372036854775808, 9223372036854775807
    bad_legacy = ('Div', 'PINT 0', integer(1), integer(0))
    matrices = [
        ('source_a', source_a, True), ('source_b', source_b, True),
        ('fresh_mod_gate', ('Mod', 'PINT 0', null, string(b'2')), True),
        ('fresh_shift_gate', ('ShiftLeft', 'PINT 0', null, string(b'2')), True),
        ('fresh_power_gate', ('Pow', 'PINT 0', null, string(b'2')), True),
        ('negative_mod', ('Mod', 'PINT $(-1)', string(b'-5'), integer(2)), True),
        ('minimum_mod', ('Mod', 'PINT 0', string(str(minimum).encode()), integer(-1)), True),
        ('shift_boundary', ('ShiftLeft', f'PINT $({minimum})', true, integer(63)), True),
        ('shift_wide', ('ShiftLeft', 'PINT 0', string(b'1'), integer(64)), True),
        ('signed_right_wide', ('ShiftRight', 'PINT $(-1)', string(b'-1'), integer(64)), True),
        ('mixed_xor', ('BitwiseXor', 'PINT 2', string(b'3'), true), True),
        ('signed_parent', ('UnaryMinus', 'PINT $(-1)', source_a), True),
        ('complement_parent', ('BitwiseNot', 'PINT $(-1)', source_b), True),
        ('float_parent', ('Plus', 'PFLOAT 4607182418800017408', source_b, string(b'1.0')), True),
        ('folded_not', ('BooleanNot', 'PBOOL true', source_b), True),
        ('legacy_mod', ('Mod', 'PINT 1', integer(3), integer(2)), True),
        ('wrong_result', ('ShiftRight', 'PINT 1', power, true), False),
        ('outside_own', ('Mod', f'PINT {maximum + 1}', null, true), False),
        ('outside_child', ('Mod', 'PINT 0', ('Plus', f'PINT {maximum + 1}', integer(maximum), true), integer(2)), False),
        ('both_string_and', ('BitwiseAnd', 'PINT 0', string(b'1'), string(b'2')), False),
        ('both_string_or', ('BitwiseOr', 'PINT 3', string(b'1'), string(b'2')), False),
        ('both_string_xor', ('BitwiseXor', 'PINT 3', string(b'1'), string(b'2')), False),
        ('mod_zero', ('Mod', 'PINT 0', null, false), False),
        ('negative_shift', ('ShiftLeft', 'PINT 0', null, string(b'-1')), False),
        ('leading_string', ('Mod', 'PINT 0', null, string(b'2x')), False),
        ('decimal_string', ('Mod', 'PINT 0', null, string(b'2.0')), False),
        ('power_overflow', ('Pow', 'PINT 0', string(b'2'), integer(63)), False),
        ('power_negative', ('Pow', 'PINT 1', string(b'1'), integer(-1)), False),
        ('power_general', ('Pow', 'PINT 1', string(b'2'), string(b'0.5')), False),
        ('power_deprecated', ('Pow', 'PINT 0', null, string(b'-1')), False),
        ('cached_division', ('Mod', 'PINT 0', bad_legacy, true), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection(label, tree, accepted)
    for label in ('mod', 'shift', 'power'):
        checks.append(f'~$string_read_raw_unary_integer(S_sign_fresh_{label}_gate,porigin_left,0)')
    checks += lines(r'''
S_cached_budget_integer_binary = S_sign_cached_division[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
~$string_read_raw_unary_integer(S_cached_budget_integer_binary,porigin_left,0)
$string_read_raw_truth(S_cached_budget_integer_binary,PORIGIN n_unit (pcpath_left ++ [PCFIELD 0]),PINT 0)
$binary_apply(S_cached_budget_integer_binary,MODULO,PINT 0,PBOOL true,0) = S_cached_budget_integer_binary
~$string_read_raw_truth(S_cached_budget_integer_binary,porigin_left,PINT 0)
S_modzero_budget_integer_binary = S_sign_mod_zero[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
~$string_read_raw_unary_integer(S_modzero_budget_integer_binary,porigin_left,0)
$binary_apply(S_modzero_budget_integer_binary,MODULO,PNULL,PBOOL false,0) = S_modzero_budget_integer_binary
~$string_read_raw_truth(S_modzero_budget_integer_binary,porigin_left,PINT 0)
S_range_budget_integer_binary = S_sign_outside_child[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
~$string_read_raw_unary_integer(S_range_budget_integer_binary,porigin_left,0)
~$string_read_raw_truth(S_range_budget_integer_binary,porigin_left,PINT 0)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
