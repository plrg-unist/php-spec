"""Quiet raw-string signs cancel before the initial raw-key Warning and reference retarget."""

import base64

from string_offset_float_conditional_base_initial_raw_leading_key_peer_review import render as render_float
from string_offset_numeric_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpPlus expression_numeric_left expression_numeric_right metadata_cond)')
    old_hex = '  -- if $hex_bits(text_cond,0) = 0\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '')
    count -= 1
    early = lines(r'''
expression_numeric_left = NExprUnaryMinus expression_left_string metadata_numeric_left
expression_numeric_right = NExprUnaryPlus expression_right_string metadata_numeric_right
expression_left_string = NScalarString (BYTES text_left_string) metadata_left_string
expression_right_string = NScalarString (BYTES text_right_string) metadata_right_string
$base64(text_left_string) = $ptascii("0.5")
$base64(text_right_string) = $ptascii("0.5")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_numeric_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_numeric_right)
$origin_child((porigin_numeric_left),[PCFIELD 0]) = (porigin_left_string)
$origin_child((porigin_numeric_right),[PCFIELD 0]) = (porigin_right_string)
''')
    for name, value in (('numeric_left', 'PFLOAT 13826050856027422720'),
                        ('numeric_right', 'PFLOAT 4602678819172646912'),
                        ('left_string', 'PSTRING ($ptascii("0.5"))'),
                        ('right_string', 'PSTRING ($ptascii("0.5"))')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_{name}) = (expression_{name})',
                  f'$compiled_read(S_capture,porigin_{name}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_{name},{value})']
    early += lines(r'''
$compiled_string_value(S_capture,porigin_left_string,PSTRING ($ptascii("0.5"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5"))
$compiled_string_value(S_capture,porigin_right_string,PSTRING ($ptascii("0.5"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5"))
$coerce_number(PSTRING ($ptascii("0.5"))) = COERCED (NFLOAT 4602678819172646912) false
$unary_apply(S_capture,NEGATIVE,PSTRING ($ptascii("0.5")),0) = S_capture[.RESULT = KNOWN (PFLOAT 13826050856027422720)]
$unary_apply(S_capture,POSITIVE,PSTRING ($ptascii("0.5")),0) = S_capture[.RESULT = KNOWN (PFLOAT 4602678819172646912)]
$binary_apply(S_capture,ADD,PFLOAT 13826050856027422720,PFLOAT 4602678819172646912,0) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_capture,porigin_left,PFLOAT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PFLOAT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
porigin_numeric_left = PORIGIN n_unit pcpath_numeric_left
porigin_numeric_right = PORIGIN n_unit pcpath_numeric_right
porigin_left_string = PORIGIN n_unit pcpath_left_string
porigin_right_string = PORIGIN n_unit pcpath_right_string
expression_numeric = NExprBinaryOpPlus expression_numeric_left expression_numeric_right metadata_cond
S_budget_string = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 4607182418800017408)]
$string_read_raw_truth(S_budget_string,porigin_left,PFLOAT 0)
$string_read_raw_known_base(S_budget_string,porigin_base,pvalue_base)
S_shorthand_string = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary expression_numeric ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_string,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_string,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('raw_bytes', 'pcpath_left_string', 'PSTRING ($ptascii("1.0"))'),
            ('literal_type', 'pcpath_right_string', 'PFLOAT 4602678819172646912'),
            ('carrier', 'pcpath_left_string', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5"))'),
            ('result_bits', 'pcpath_numeric_left', 'PFLOAT 4602678819172646912')):
        checks += [f'S_bad_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_{label},porigin_left,PFLOAT 0)',
                   f'~$string_read_raw_known_base(S_bad_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('unary', 'pcpath_numeric_left', 'NExprUnaryMinus expression_left_string eps'),
            ('left_literal', 'pcpath_left_string', 'NScalarString (BYTES text_left_string) eps'),
            ('right_literal', 'pcpath_right_string', 'NScalarString (BYTES text_right_string) eps')):
        checks += [f'S_bad_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_{label}_source,porigin_left,PFLOAT 0)',
                   f'~$string_read_raw_known_base(S_bad_{label}_source,porigin_base,pvalue_base)']
    for label, raw, operator, bits, accepted in (
            ('large', b'9223372036854775808', 'Plus', 4890909195324358656, True),
            ('string_one_float', b'1.0', 'Plus', 4607182418800017408, True),
            ('string_half', b'0.5', 'Plus', 4602678819172646912, True),
            ('negative_half', b'0.5', 'Minus', 13826050856027422720, True),
            ('whitespace', b'\t0.5 \n', 'Plus', 4602678819172646912, True),
            ('keep_negative_zero', b'-0.0', 'Plus', 9223372036854775808, True),
            ('flip_negative_zero', b'-0.0', 'Minus', 0, True),
            ('string_minimum', b'-9223372036854775808', 'Minus', 4890909195324358656, True),
            ('integer_float_forgery', b'1', 'Plus', 4607182418800017408, False),
            ('maximum_float_forgery', b'9223372036854775807', 'Plus', 4890909195324358656, False),
            ('integer_zero_forgery', b'0', 'Minus', 9223372036854775808, False),
            ('leading', b'0.5x', 'Plus', 4602678819172646912, False),
            ('nul_leading', b'0.5\0', 'Plus', 4602678819172646912, False),
            ('nonnumeric', b'x', 'Plus', 0, False),
            ('infinite_result', b'1e309', 'Plus', 9218868437227405312, False),
            ('fake_finite_infinite', b'1e309', 'Plus', 0, False)):
        child = 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")'
        value = 'PSTRING ([' + ','.join(map(str, raw)) + '])'
        checks += _projection(label, operator, child, value, bits, accepted)
    for label, child, value, bits, accepted in (
            ('existing_minimum', 'NScalarInt (INTEGER $(-9223372036854775808))', 'PINT $(-9223372036854775808)', 4890909195324358656, True),
            ('interned_carrier', 'NScalarString (BYTES "MC41")', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5"))', 4602678819172646912, False),
            ('request_carrier', 'NScalarString (BYTES "MC41")', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("0.5"))', 4602678819172646912, False)):
        checks += _projection(label, 'Minus' if label == 'existing_minimum' else 'Plus', child, value, bits, accepted)
    checks += lines(r'''
$coerce_number(PSTRING ($ptascii("0.5x"))) = COERCED (NFLOAT 4602678819172646912) true
$string_read_raw_truth(S_projected_leading,porigin_numeric_left,PSTRING ($ptascii("0.5x")))
S_leading_budget = S_projected_leading[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 4602678819172646912)]
~$string_read_raw_truth(S_leading_budget,porigin_left,PFLOAT 4602678819172646912)
~$string_read_raw_known_base(S_leading_budget,porigin_base,pvalue_wrong)
$unary_apply(S_projected_integer_float_forgery,POSITIVE,PSTRING ($ptascii("1")),0) = S_projected_integer_float_forgery[.RESULT = KNOWN (PINT 1)]
$coerce_number(PSTRING ($ptascii("-9223372036854775808"))) = COERCED (NINT $(-9223372036854775808)) false
$unary_apply(S_projected_string_minimum,NEGATIVE,PSTRING ($ptascii("-9223372036854775808")),0) = S_projected_string_minimum[.RESULT = KNOWN (PFLOAT 4890909195324358656)]
''')
    checks += _projection('not_string_half', 'Plus', 'NScalarString (BYTES "MC41")', 'PSTRING ($ptascii("0.5"))', 4602678819172646912, True, not_shorthand=True)
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    added = len(early) + len(checks)
    return body, count + added, derived + len(checks)
