"""A quiet integer sign preserves the exact certified arithmetic child and raw key."""

from string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_review import render as render_arithmetic
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_arithmetic(program, filename_b64)
    arithmetic = 'NExprBinaryOpMul expression_sum_integer expression_factor_integer metadata_cond'
    assert body.count(arithmetic) == 3
    child = 'NExprBinaryOpMul expression_sum_integer expression_factor_integer metadata_arithmetic_unary'
    body = body.replace(arithmetic, f'NExprUnaryPlus ({child}) metadata_cond')
    early = lines(r'''
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_arithmetic_unary)
$origin_node(S_capture.SOURCES,porigin_arithmetic_unary) = (NExprBinaryOpMul expression_sum_integer expression_factor_integer metadata_arithmetic_unary)
$compiled_read(S_capture,porigin_arithmetic_unary) = (PINT 3)
$string_read_raw_truth(S_capture,porigin_arithmetic_unary,PINT 3)
~$string_read_raw_unary_integer(S_capture,porigin_arithmetic_unary,3)
''')
    anchor = '  -- if $origin_child((porigin_cond),[PCFIELD 0]) = (porigin_sum_integer)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor.replace('porigin_cond', 'porigin_arithmetic_unary'))
    anchor = '  -- if $origin_child((porigin_cond),[PCFIELD 1]) = (porigin_factor_integer)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, anchor.replace('porigin_cond', 'porigin_arithmetic_unary'))
    checks = lines(r'''
porigin_arithmetic_unary = PORIGIN n_unit pcpath_arithmetic_unary
$unary_apply(S_capture,POSITIVE,PINT 3,0) = S_capture[.RESULT = KNOWN (PINT 3)]
$unary_apply(S_capture,NEGATIVE,PINT 3,0) = S_capture[.RESULT = KNOWN (PINT $(-3))]
S_unary_child_float = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_arithmetic_unary (PFLOAT 4613937818241073152)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_unary_child_float,porigin_cond,PINT 3)
~$string_read_raw_known_base(S_unary_child_float,porigin_base,pkeyread.BASE)
S_unary_child_bool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_arithmetic_unary (PBOOL true)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_unary_child_bool,porigin_cond,PINT 3)
S_unary_child_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_arithmetic_unary (NExprBinaryOpMul expression_sum_integer expression_factor_integer eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_unary_child_source,porigin_cond,PINT 3)
expression_negated_unary = NExprUnaryMinus (NExprBinaryOpMul expression_sum_integer expression_factor_integer metadata_arithmetic_unary) metadata_cond
expression_negative_base_unary = NExprTernary expression_negated_unary (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_wrong_sign_unary = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_negative_base_unary) :: (PCOCCURRENCE pcpath_cond expression_negated_unary) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_wrong_sign_unary,porigin_cond,PINT 3)
~$string_read_raw_known_base(S_wrong_sign_unary,porigin_base,pkeyread.BASE)
S_negative_unary = S_wrong_sign_unary[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT $(-3))) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_negative_unary,porigin_cond,PINT $(-3))
$string_read_raw_known_base(S_negative_unary,porigin_base,pkeyread.BASE)
S_negative_budget_unary = S_negative_unary[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 3)]
$string_read_raw_truth(S_negative_budget_unary,porigin_cond,PINT $(-3))
$string_read_raw_known_base(S_negative_budget_unary,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(early) + len(checks)
