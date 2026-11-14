"""Quiet raw numeric-string signs retain original bytes and exact FLOAT truth."""

import base64

from string_offset_float_conditional_base_initial_raw_leading_key_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprUnaryPlus (NScalarString (BYTES text_string_numeric) metadata_string_numeric) metadata_cond)')
    old_hex = '  -- if n_cond = $hex_bits(text_cond,0)\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '').replace('n_cond = 4607182418800017408', 'n_cond = 4890909195324358656')
    count -= 1
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_string_numeric)
$origin_node(S_capture.SOURCES,porigin_string_numeric) = (NScalarString (BYTES text_string_numeric) metadata_string_numeric)
n_string_numeric* = $base64(text_string_numeric)
n_string_numeric* = $ptascii("9223372036854775808")
$compiled_read(S_capture,porigin_string_numeric) = (PSTRING n_string_numeric*)
$compiled_string_value(S_capture,porigin_string_numeric,PSTRING n_string_numeric*) = PSTRING_CARRIER INTERNED_STRING n_string_numeric*
$string_read_raw_truth(S_capture,porigin_string_numeric,PSTRING n_string_numeric*)
$coerce_number(PSTRING n_string_numeric*) = COERCED (NFLOAT n_cond) false
$unary_apply(S_capture,POSITIVE,PSTRING n_string_numeric*,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$string_read_raw_truth(S_capture,porigin_cond,PFLOAT n_cond)
porigin_string_numeric = PORIGIN n_unit pcpath_string_numeric
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
S_budget_string_numeric = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_budget_string_numeric,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_budget_string_numeric,porigin_base,pkeyread.BASE)
S_child_type_string_numeric = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_string_numeric (PFLOAT n_cond)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_child_type_string_numeric,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_child_type_string_numeric,porigin_base,pkeyread.BASE)
S_child_bytes_string_numeric = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_string_numeric (PSTRING ($ptascii("0.5")))) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_child_bytes_string_numeric,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_child_bytes_string_numeric,porigin_base,pkeyread.BASE)
S_child_source_string_numeric = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_string_numeric (NScalarString (BYTES text_string_numeric) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_child_source_string_numeric,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_child_source_string_numeric,porigin_base,pkeyread.BASE)
''')
    for label, raw, operator, bits, accepted in (
            ('positive_zero', '0.0', 'Plus', 0, True),
            ('negative_zero', '0.0', 'Minus', 9223372036854775808, True),
            ('keep_negative_zero', '-0.0', 'Plus', 9223372036854775808, True),
            ('flip_negative_zero', '-0.0', 'Minus', 0, True),
            ('minimum_overflow', '-9223372036854775808', 'Minus', 4890909195324358656, True),
            ('exact_integer', '1', 'Plus', 4607182418800017408, False),
            ('leading', '0.5x', 'Plus', 4602678819172646912, False),
            ('nonnumeric', 'x', 'Plus', 0, False),
            ('infinite', '1e309', 'Plus', 9218868437227405312, False),
            ('fake_finite_infinite', '1e309', 'Plus', 0, False)):
        encoded = base64.b64encode(raw.encode()).decode()
        checks += lines(f'''
expression_string_{label} = NScalarString (BYTES "{encoded}") metadata_string_numeric
expression_sign_{label} = NExprUnary{operator} expression_string_{label} metadata_cond
expression_base_string_{label} = NExprTernary expression_sign_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_projected_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_string_{label}) :: (PCOCCURRENCE pcpath_cond expression_sign_{label}) :: (PCOCCURRENCE pcpath_string_numeric expression_string_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT {bits})) :: (PCONSTANT pcpath_string_numeric (PSTRING ($ptascii("{raw}")))) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_projected_{label},porigin_string_numeric,PSTRING ($ptascii("{raw}")))
{'' if accepted else '~'}$string_read_raw_truth(S_projected_{label},porigin_cond,PFLOAT {bits})
''')
        if accepted:
            selected = 'pvalue_wrong' if bits in (0, 9223372036854775808) else 'pkeyread.BASE'
            checks.append(f'$string_read_raw_known_base(S_projected_{label},porigin_base,{selected})')
        else:
            checks += [f'~$string_read_raw_known_base(S_projected_{label},porigin_base,{value})'
                       for value in ('pkeyread.BASE', 'pvalue_wrong')]
    checks += lines(r'''
$coerce_number(PSTRING ($ptascii("0.5x"))) = COERCED (NFLOAT 4602678819172646912) true
$coerce_number(PSTRING ($ptascii("x"))) = BADNUMBER
$unary_apply(S_projected_exact_integer,POSITIVE,PSTRING ($ptascii("1")),0) = S_projected_exact_integer[.RESULT = KNOWN (PINT 1)]
$unary_apply(S_projected_negative_zero,NEGATIVE,PSTRING ($ptascii("0.0")),0) = S_projected_negative_zero[.RESULT = KNOWN (PFLOAT 9223372036854775808)]
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
