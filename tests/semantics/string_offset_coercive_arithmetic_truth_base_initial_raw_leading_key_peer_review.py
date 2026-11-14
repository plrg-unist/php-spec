"""Quiet scalar arithmetic keeps the false arm across raw-key reference rebinding."""

import base64

from string_offset_float_conditional_base_initial_raw_leading_key_peer_review import render as render_float
from string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMinus expression_coercive_left expression_coercive_right metadata_cond)')
    old_hex = '  -- if $hex_bits(text_cond,0) = 0\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '')
    count -= 1
    early = lines(r'''
expression_coercive_left = NExprBinaryOpDiv expression_coercive_null expression_coercive_string metadata_coercive_left
expression_coercive_right = NExprConstFetch (NName (BYTES text_false_name) metadata_false_name) metadata_coercive_right
expression_coercive_null = NExprConstFetch (NName (BYTES text_null_name) metadata_null_name) metadata_coercive_null
expression_coercive_string = NScalarString (BYTES text_coercive_string) metadata_coercive_string
$ptlc($base64(text_false_name)) = $ptascii("false")
$ptlc($base64(text_null_name)) = $ptascii("null")
$base64(text_coercive_string) = $ptascii("1e309")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_coercive_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_coercive_right)
$origin_child((porigin_coercive_left),[PCFIELD 0]) = (porigin_coercive_null)
$origin_child((porigin_coercive_left),[PCFIELD 1]) = (porigin_coercive_string)
$origin_child((porigin_coercive_null),[PCFIELD 0]) = (porigin_null_name)
$origin_child((porigin_coercive_right),[PCFIELD 0]) = (porigin_false_name)
$origin_node(S_capture.SOURCES,porigin_null_name) = (NName (BYTES text_null_name) metadata_null_name)
$origin_node(S_capture.SOURCES,porigin_false_name) = (NName (BYTES text_false_name) metadata_false_name)
''')
    for name, value in (('coercive_left', 'PFLOAT 0'),
                        ('coercive_right', 'PBOOL false'),
                        ('coercive_null', 'PNULL'),
                        ('coercive_string', 'PSTRING ($ptascii("1e309"))')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_{name}) = (expression_{name})',
                  f'$compiled_read(S_capture,porigin_{name}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_{name},{value})']
    early += lines(r'''
$compiled_string_value(S_capture,porigin_coercive_string,PSTRING ($ptascii("1e309"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("1e309"))
$coerce_number(PNULL) = COERCED (NINT 0) false
$coerce_number(PBOOL false) = COERCED (NINT 0) false
$coerce_number(PSTRING ($ptascii("1e309"))) = COERCED (NFLOAT 9218868437227405312) false
$binary_apply(S_capture,DIVIDE,PNULL,PSTRING ($ptascii("1e309")),0) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$binary_apply(S_capture,SUBTRACT,PFLOAT 0,PBOOL false,0) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_capture,porigin_left,PFLOAT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PFLOAT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
porigin_coercive_left = PORIGIN n_unit pcpath_coercive_left
porigin_coercive_right = PORIGIN n_unit pcpath_coercive_right
porigin_coercive_null = PORIGIN n_unit pcpath_coercive_null
porigin_coercive_string = PORIGIN n_unit pcpath_coercive_string
porigin_null_name = PORIGIN n_unit pcpath_null_name
porigin_false_name = PORIGIN n_unit pcpath_false_name
expression_coercive = NExprBinaryOpMinus expression_coercive_left expression_coercive_right metadata_cond
S_budget_coercive = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 4607182418800017408)]
$string_read_raw_truth(S_budget_coercive,porigin_left,PFLOAT 0)
$string_read_raw_known_base(S_budget_coercive,porigin_base,pvalue_base)
S_shorthand_coercive = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary expression_coercive ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_coercive,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_coercive,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own_sign', 'pcpath_left', 'PFLOAT 9223372036854775808'),
            ('left_tag', 'pcpath_coercive_null', 'PBOOL false'),
            ('right_tag', 'pcpath_coercive_right', 'PNULL'),
            ('raw_bytes', 'pcpath_coercive_string', 'PSTRING ($ptascii("0"))'),
            ('carrier', 'pcpath_coercive_string', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1e309"))')):
        own = value if label == 'own_sign' else 'PFLOAT 0'
        checks += [f'S_bad_coercive_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_coercive_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_coercive_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('division', 'pcpath_coercive_left', 'NExprBinaryOpDiv expression_coercive_null expression_coercive_string eps'),
            ('literal', 'pcpath_coercive_string', 'NScalarString (BYTES text_coercive_string) eps'),
            ('null_name', 'pcpath_null_name', 'NName (BYTES text_null_name) eps'),
            ('false_name', 'pcpath_false_name', 'NName (BYTES text_false_name) eps')):
        checks += [f'S_bad_coercive_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_coercive_{label}_source,porigin_left,PFLOAT 0)',
                   f'~$string_read_raw_known_base(S_bad_coercive_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_bad_coercive_read = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_coercive_string 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_coercive_read,porigin_left,PFLOAT 0)
~$string_read_raw_known_base(S_bad_coercive_read,porigin_base,pvalue_base)
''')
    def string(raw):
        encoded = base64.b64encode(raw).decode()
        return f'NScalarString (BYTES "{encoded}")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        return f'NScalarInt (INTEGER {i})', f'PINT {i}'
    def floating(bits):
        return f'NScalarFloat (FLOAT "{bits:016x}")', f'PFLOAT {bits}'
    def constant(name, value):
        encoded = base64.b64encode(name.encode()).decode()
        return f'NExprConstFetch (NName (BYTES "{encoded}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    one, half, two, negative_zero, infinity = 4607182418800017408, 4602678819172646912, 4611686018427387904, 9223372036854775808, 9218868437227405312
    promotion = ('Plus', 'PFLOAT 4890909195324358656', string(b'9223372036854775807'), true)
    bad_integer = ('Div', 'PINT 1', integer(1), integer(0))
    matrices = [
        ('source_a', ('Mul', 'PFLOAT 4890909195324358656', promotion, string(b'1.0')), True),
        ('old_bool_left', ('Plus', f'PFLOAT {one}', true, floating(0)), True),
        ('old_bool_right', ('Plus', f'PFLOAT {one}', floating(0), true), True),
        ('old_null_right', ('Plus', 'PFLOAT 0', floating(0), null), True),
        ('old_numeric_string', ('Plus', 'PFLOAT 0', string(b'0'), floating(0)), True),
        ('boolean_multiply', ('Mul', f'PFLOAT {two}', true, string(b'2.0')), True),
        ('null_left', ('Plus', f'PFLOAT {half}', null, string(b'0.5')), True),
        ('false_right', ('Minus', 'PFLOAT 0', string(b'0.0'), false), True),
        ('strings_divide', ('Div', 'PFLOAT 4598175219545276416', string(b'0.5'), string(b'2')), True),
        ('strings_add', ('Plus', f'PFLOAT {one}', string(b'0.5'), string(b'0.5')), True),
        ('whitespace', ('Plus', f'PFLOAT {half}', string(b'\t0.5 \n'), false), True),
        ('negative_zero', ('Mul', f'PFLOAT {negative_zero}', string(b'-0.0'), true), True),
        ('string_infinite_quotient', ('Div', 'PFLOAT 0', true, string(b'1e309')), True),
        ('negative_infinite_quotient', ('Div', f'PFLOAT {negative_zero}', null, string(b'-1e309')), True),
        ('integer_forgery', ('Plus', f'PFLOAT {two}', string(b'1'), true), False),
        ('integer_zero_forgery', ('Mul', 'PFLOAT 0', string(b'0'), false), False),
        ('null_bool_forgery', ('Plus', 'PFLOAT 0', null, false), False),
        ('exact_division_forgery', ('Div', 'PFLOAT 4616189618054758400', string(b'4'), true), False),
        ('zero_divisor', ('Div', 'PFLOAT 0', true, string(b'0.0')), False),
        ('negative_zero_divisor', ('Div', 'PFLOAT 0', true, string(b'-0.0')), False),
        ('leading_left', ('Plus', f'PFLOAT {half}', string(b'0.5x'), false), False),
        ('leading_right', ('Plus', f'PFLOAT {half}', false, string(b'0.5x')), False),
        ('nul_leading', ('Plus', f'PFLOAT {half}', string(b'0.5\0'), false), False),
        ('nonnumeric', ('Plus', 'PFLOAT 0', string(b'x'), false), False),
        ('infinite_result', ('Plus', f'PFLOAT {infinity}', string(b'1e309'), false), False),
        ('fake_finite_infinite', ('Plus', 'PFLOAT 0', string(b'1e309'), false), False),
        ('nan_result', ('Mul', 'PFLOAT 9221120237041090560', string(b'1e309'), null), False),
        ('fake_finite_nan', ('Mul', 'PFLOAT 0', string(b'1e309'), null), False),
        ('original_infinite', ('Div', 'PFLOAT 0', null, floating(infinity)), False),
        ('interned_carrier', ('Plus', f'PFLOAT {half}', ('NScalarString (BYTES "MC41")', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5"))'), false), False),
        ('request_carrier', ('Plus', f'PFLOAT {half}', ('NScalarString (BYTES "MC41")', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("0.5"))'), false), False),
        ('nested_zero', ('Plus', f'PFLOAT {one}', bad_integer, string(b'0.0')), False),
        ('power_gate', ('Pow', 'PFLOAT 4598175219545276416', string(b'0.5'), string(b'2')), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection(label, tree, accepted)
    checks += lines(r'''
S_zero_budget_coercive = S_projected_zero_divisor[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
$binary_apply(S_zero_budget_coercive,DIVIDE,PBOOL true,PSTRING ($ptascii("0.0")),0) = S_zero_budget_coercive
~$string_read_raw_truth(S_zero_budget_coercive,porigin_left,PFLOAT 0)
S_leading_budget_coercive = S_projected_leading_left[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 4602678819172646912)]
$coerce_number(PSTRING ($ptascii("0.5x"))) = COERCED (NFLOAT 4602678819172646912) true
~$string_read_raw_truth(S_leading_budget_coercive,porigin_left,PFLOAT 4602678819172646912)
S_nested_budget_coercive = S_projected_nested_zero[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
$string_read_raw_truth(S_nested_budget_coercive,porigin_coercive_left,PINT 1)
~$string_read_raw_truth(S_nested_budget_coercive[.COMPLETION = NORMAL],porigin_coercive_left,PINT 1)
~$string_read_raw_truth(S_nested_budget_coercive,porigin_left,PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_nested_budget_coercive,porigin_base,pvalue_wrong)
$binary_apply(S_projected_original_infinite,DIVIDE,PNULL,PFLOAT 9218868437227405312,0) = S_projected_original_infinite[.RESULT = KNOWN (PFLOAT 0)]
~$string_read_raw_truth(S_projected_original_infinite,porigin_coercive_right,PFLOAT 9218868437227405312)
''')
    checks += _projection('not_coercive', ('Plus', f'PFLOAT {half}', null, string(b'0.5')), True, not_shorthand=True)
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    added = len(early) + len(checks)
    return body, count + added, derived + len(checks)
