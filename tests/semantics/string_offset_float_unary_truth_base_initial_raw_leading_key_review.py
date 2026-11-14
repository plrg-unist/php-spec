"""Finite FLOAT-only sign trees authenticate quiet full-ternary truth."""

from string_offset_float_conditional_base_initial_raw_leading_key_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprUnaryPlus (NExprUnaryMinus (NExprUnaryMinus (NScalarFloat (FLOAT text_cond) metadata_leaf_sign) metadata_inner_sign) metadata_outer_sign) metadata_cond)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_cond_sign)
expression_cond_sign = NExprUnaryPlus expression_outer_sign metadata_cond
expression_outer_sign = NExprUnaryMinus expression_inner_sign metadata_outer_sign
expression_inner_sign = NExprUnaryMinus expression_leaf_sign metadata_inner_sign
expression_leaf_sign = NScalarFloat (FLOAT text_cond) metadata_leaf_sign
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_outer_sign)
$origin_child((porigin_outer_sign),[PCFIELD 0]) = (porigin_inner_sign)
$origin_child((porigin_inner_sign),[PCFIELD 0]) = (porigin_leaf_sign)
$origin_node(S_capture.SOURCES,porigin_outer_sign) = (expression_outer_sign)
$origin_node(S_capture.SOURCES,porigin_inner_sign) = (expression_inner_sign)
$origin_node(S_capture.SOURCES,porigin_leaf_sign) = (expression_leaf_sign)
$compiled_read(S_capture,porigin_outer_sign) = (PFLOAT n_cond)
$compiled_read(S_capture,porigin_inner_sign) = (PFLOAT 13830554455654793216)
$compiled_read(S_capture,porigin_leaf_sign) = (PFLOAT n_cond)
$string_read_raw_truth(S_capture,porigin_leaf_sign,PFLOAT n_cond)
$string_read_raw_truth(S_capture,porigin_inner_sign,PFLOAT 13830554455654793216)
$string_read_raw_truth(S_capture,porigin_outer_sign,PFLOAT n_cond)
$string_read_raw_truth(S_capture,porigin_cond,PFLOAT n_cond)
$unary_apply(S_capture,NEGATIVE,PFLOAT n_cond,0) = S_capture[.RESULT = KNOWN (PFLOAT 13830554455654793216)]
$unary_apply(S_capture,NEGATIVE,PFLOAT 13830554455654793216,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$unary_apply(S_capture,POSITIVE,PFLOAT n_cond,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
porigin_leaf_sign = PORIGIN n_unit pcpath_leaf_sign
porigin_inner_sign = PORIGIN n_unit pcpath_inner_sign
S_budget_sign = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget_sign,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_budget_sign,porigin_base,pkeyread.BASE)
S_precision_sign = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond 17) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_precision_sign,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_precision_sign,porigin_base,pkeyread.BASE)
S_child_type_sign = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf_sign (PINT 1)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_child_type_sign,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_child_type_sign,porigin_base,pkeyread.BASE)
S_wrong_bits_sign = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner_sign (PFLOAT n_cond)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_wrong_bits_sign,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_wrong_bits_sign,porigin_base,pkeyread.BASE)
S_leaf_metadata_sign = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_leaf_sign (NScalarFloat (FLOAT text_cond) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_leaf_metadata_sign,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_leaf_metadata_sign,porigin_base,pkeyread.BASE)
''')
    # Each canonical finite atom supplies only FLOAT children to either sign.
    for label, text, value, negated in (
            ('zero', '0000000000000000', 0, 9223372036854775808),
            ('negative_zero', '8000000000000000', 9223372036854775808, 0),
            ('minsubnormal', '0000000000000001', 1, 9223372036854775809),
            ('maxfinite', '7fefffffffffffff', 9218868437227405311, 18442240474082181119)):
        for operator, constructor, result in (('POSITIVE', 'NExprUnaryPlus', value), ('NEGATIVE', 'NExprUnaryMinus', negated)):
            name = label + '_' + operator.lower()
            checks += lines(f'''
expression_atom_{name} = NScalarFloat (FLOAT "{text}") metadata_inner_sign
expression_unary_{name} = {constructor} expression_atom_{name} metadata_cond
expression_base_{name} = NExprTernary expression_unary_{name} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_{name} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{name}) :: (PCOCCURRENCE pcpath_cond expression_unary_{name}) :: (PCOCCURRENCE (pcpath_cond ++ [PCFIELD 0]) expression_atom_{name}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT {result})) :: (PCONSTANT (pcpath_cond ++ [PCFIELD 0]) (PFLOAT {value})) :: ppool.CONSTANTS]]]
$unary_apply(S_{name},{operator},PFLOAT {value},0) = S_{name}[.RESULT = KNOWN (PFLOAT {result})]
$string_read_raw_truth(S_{name},porigin_cond,PFLOAT {result})
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
