"""Negated PINT minimum retains its exact FLOAT truth and frozen raw offset."""

from string_offset_float_conditional_base_initial_raw_leading_key_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprUnaryMinus expression_min_numeric metadata_cond)')
    old_hex = '  -- if n_cond = $hex_bits(text_cond,0)\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '').replace('n_cond = 4607182418800017408', 'n_cond = 4890909195324358656')
    count -= 1
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprUnaryMinus expression_min_numeric metadata_cond)
expression_min_numeric = NExprBinaryOpMinus expression_negative_max_numeric expression_one_numeric metadata_min_numeric
expression_negative_max_numeric = NExprUnaryMinus expression_max_numeric metadata_negative_max_numeric
expression_max_numeric = NScalarInt (INTEGER 9223372036854775807) metadata_max_numeric
expression_one_numeric = NScalarInt (INTEGER 1) metadata_one_numeric
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_min_numeric)
$origin_child((porigin_min_numeric),[PCFIELD 0]) = (porigin_negative_max_numeric)
$origin_child((porigin_min_numeric),[PCFIELD 1]) = (porigin_one_numeric)
$origin_child((porigin_negative_max_numeric),[PCFIELD 0]) = (porigin_max_numeric)
''')
    for name, value in (('min', 'PINT $(-9223372036854775808)'),
                        ('negative_max', 'PINT $(-9223372036854775807)'),
                        ('max', 'PINT 9223372036854775807'), ('one', 'PINT 1')):
        checks += lines(f'''
$origin_node(S_capture.SOURCES,porigin_{name}_numeric) = (expression_{name}_numeric)
$compiled_read(S_capture,porigin_{name}_numeric) = ({value})
$string_read_raw_truth(S_capture,porigin_{name}_numeric,{value})
porigin_{name}_numeric = PORIGIN n_unit pcpath_{name}_numeric
''')
    checks += lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
$unary_apply(S_capture,NEGATIVE,PINT $(-9223372036854775808),0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$string_read_raw_truth(S_capture,porigin_cond,PFLOAT n_cond)
S_budget_numeric = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT $(-9223372036854775808))]
$string_read_raw_truth(S_budget_numeric,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_budget_numeric,porigin_base,pkeyread.BASE)
S_wrong_bits_numeric = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 14114281232179134464)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_wrong_bits_numeric,porigin_cond,PFLOAT 14114281232179134464)
~$string_read_raw_known_base(S_wrong_bits_numeric,porigin_base,pkeyread.BASE)
S_wrong_child_numeric = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_min_numeric (PFLOAT 14114281232179134464)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_wrong_child_numeric,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_wrong_child_numeric,porigin_base,pkeyread.BASE)
S_wrong_source_numeric = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_min_numeric (NExprBinaryOpMinus expression_negative_max_numeric expression_one_numeric eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_wrong_source_numeric,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_wrong_source_numeric,porigin_base,pkeyread.BASE)
expression_plus_min_numeric = NExprUnaryPlus expression_min_numeric metadata_cond
expression_plus_min_base_numeric = NExprTernary expression_plus_min_numeric (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_plus_min_numeric = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_plus_min_base_numeric) :: (PCOCCURRENCE pcpath_cond expression_plus_min_numeric) :: pcunit.OCCURRENCES]]]
$unary_apply(S_plus_min_numeric,POSITIVE,PINT $(-9223372036854775808),0) = S_plus_min_numeric[.RESULT = KNOWN (PINT $(-9223372036854775808))]
~$string_read_raw_truth(S_plus_min_numeric,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_plus_min_numeric,porigin_base,pkeyread.BASE)
expression_zero_numeric = NScalarFloat (FLOAT "0000000000000000") metadata_min_numeric
expression_negative_zero_numeric = NExprUnaryMinus expression_zero_numeric metadata_cond
expression_negative_zero_base_numeric = NExprTernary expression_negative_zero_numeric (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_negative_zero_numeric = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_negative_zero_base_numeric) :: (PCOCCURRENCE pcpath_cond expression_negative_zero_numeric) :: (PCOCCURRENCE pcpath_min_numeric expression_zero_numeric) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 9223372036854775808)) :: (PCONSTANT pcpath_min_numeric (PFLOAT 0)) :: ppool.CONSTANTS]]]
$unary_apply(S_negative_zero_numeric,NEGATIVE,PFLOAT 0,0) = S_negative_zero_numeric[.RESULT = KNOWN (PFLOAT 9223372036854775808)]
$string_read_raw_truth(S_negative_zero_numeric,porigin_cond,PFLOAT 9223372036854775808)
$string_read_raw_known_base(S_negative_zero_numeric,porigin_base,pvalue_wrong)
S_wrong_zero_numeric = S_negative_zero_numeric[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 0)) :: (PCONSTANT pcpath_min_numeric (PFLOAT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_wrong_zero_numeric,porigin_cond,PFLOAT 0)
~$string_read_raw_known_base(S_wrong_zero_numeric,porigin_base,pvalue_wrong)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
