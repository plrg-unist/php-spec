"""Finite FLOAT signs retain exact bits, source and the initial reference key."""

from string_offset_float_conditional_base_initial_raw_leading_key_peer_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprUnaryMinus (NExprUnaryMinus (NScalarFloat (FLOAT text_cond) metadata_leaf) metadata_inner) metadata_cond)')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_left) = (expression_condition)
expression_condition = NExprUnaryMinus expression_inner metadata_cond
expression_inner = NExprUnaryMinus expression_leaf metadata_inner
expression_leaf = NScalarFloat (FLOAT text_cond) metadata_leaf
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_inner) = (expression_inner)
$origin_node(S_capture.SOURCES,porigin_leaf) = (expression_leaf)
$compiled_read(S_capture,porigin_inner) = (PFLOAT 9223372036854775808)
$compiled_read(S_capture,porigin_leaf) = (PFLOAT 0)
$string_read_raw_truth(S_capture,porigin_leaf,PFLOAT 0)
$unary_apply(S_capture,NEGATIVE,PFLOAT 0,0) = S_capture[.RESULT = KNOWN (PFLOAT 9223372036854775808)]
$string_read_raw_truth(S_capture,porigin_inner,PFLOAT 9223372036854775808)
$unary_apply(S_capture,NEGATIVE,PFLOAT 9223372036854775808,0) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_capture,porigin_left,PFLOAT 0)
$truth_value(S_capture,PFLOAT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$origin_node(S_capture.SOURCES,porigin_right) = (expression_fallback)
expression_fallback = NScalarString (BYTES text_right) metadata_right
porigin_inner = PORIGIN n_unit pcpath_inner
porigin_leaf = PORIGIN n_unit pcpath_leaf
$compiled_precision(S_capture,(porigin_left)) = (14)
$compiled_precision(S_capture,(porigin_inner)) = (14)
$compiled_precision(S_capture,(porigin_leaf)) = (14)
S_budget = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget,porigin_left,PFLOAT 0)
$string_read_raw_known_base(S_budget,porigin_base,pvalue_base)
S_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_precision,porigin_base,pvalue_base)
''')
    for label, path, value, result in (
            ('result_sign', 'pcpath_left', 'PFLOAT 9223372036854775808', 'PFLOAT 9223372036854775808'),
            ('inner_sign', 'pcpath_inner', 'PFLOAT 0', 'PFLOAT 0'),
            ('leaf_sign', 'pcpath_leaf', 'PFLOAT 9223372036854775808', 'PFLOAT 0'),
            ('child_type', 'pcpath_inner', 'PINT 0', 'PFLOAT 0'),
            ('infinity', 'pcpath_left', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312')):
        checks += lines(f'''
S_pool_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_pool_{label},porigin_left,{result})
~$string_read_raw_known_base(S_pool_{label},porigin_base,pvalue_base)
$string_read_plan(S_pool_{label}) = eps
''')
    for label, path, node in (
            ('condition', 'pcpath_left', 'NExprUnaryMinus expression_inner eps'),
            ('inner', 'pcpath_inner', 'NExprUnaryMinus expression_leaf eps'),
            ('leaf', 'pcpath_leaf', 'NScalarFloat (FLOAT text_cond) eps'),
            ('fallback', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        checks += lines(f'''
S_metadata_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_metadata_{label},porigin_base,pvalue_base)
$string_read_plan(S_metadata_{label}) = eps
''')
    for label, constructor, operator, bits in (
            ('plus', 'NExprUnaryPlus', 'POSITIVE', 0),
            ('minus', 'NExprUnaryMinus', 'NEGATIVE', 9223372036854775808)):
        checks += lines(f'''
expression_zero_{label} = {constructor} expression_leaf metadata_cond
expression_zero_base_{label} = NExprTernary expression_zero_{label} ABSENT expression_fallback metadata
S_zero_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_zero_base_{label}) :: (PCOCCURRENCE pcpath_left expression_zero_{label}) :: (PCOCCURRENCE pcpath_inner expression_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PFLOAT {bits})) :: (PCONSTANT pcpath_inner (PFLOAT 0)) :: ppool.CONSTANTS]]]
S_zero_{label}.SOURCES = [pcunit_zero_{label}]
$string_read_raw_truth(S_zero_{label},porigin_left,PFLOAT {bits})
$unary_apply(S_zero_{label},{operator},PFLOAT 0,0) = S_zero_{label}[.RESULT = KNOWN (PFLOAT {bits})]
$string_read_raw_known_base(S_zero_{label},porigin_base,pvalue_base)
S_zero_condition_{label} = S_zero_{label}[.SOURCES = [pcunit_zero_{label}[.OCCURRENCES = (PCOCCURRENCE pcpath_left ({constructor} expression_leaf eps)) :: pcunit_zero_{label}.OCCURRENCES]]]
~$string_read_raw_known_base(S_zero_condition_{label},porigin_base,pvalue_base)
S_zero_fallback_{label} = S_zero_{label}[.SOURCES = [pcunit_zero_{label}[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NScalarString (BYTES text_right) eps)) :: pcunit_zero_{label}.OCCURRENCES]]]
~$string_read_raw_known_base(S_zero_fallback_{label},porigin_base,pvalue_base)
expression_short_leaf_{label} = NScalarFloat (FLOAT "0") metadata_leaf
expression_short_sign_{label} = {constructor} expression_short_leaf_{label} metadata_cond
expression_short_base_{label} = NExprTernary expression_short_sign_{label} ABSENT expression_fallback metadata
S_zero_short_{label} = S_zero_{label}[.SOURCES = [pcunit_zero_{label}[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_short_base_{label}) :: (PCOCCURRENCE pcpath_left expression_short_sign_{label}) :: (PCOCCURRENCE pcpath_inner expression_short_leaf_{label}) :: pcunit_zero_{label}.OCCURRENCES]]]
~$string_read_raw_truth(S_zero_short_{label},porigin_left,PFLOAT {bits})
~$string_read_raw_known_base(S_zero_short_{label},porigin_base,pvalue_base)
''')
    # Shared shorthand and emitted-NOT consumers compose locally; source credit0.
    checks += lines(r'''
expression_shorthand = NExprTernary expression_condition ABSENT expression_fallback metadata
S_shorthand = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_shorthand) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand,porigin_base,pvalue_base)
expression_signed_child = NExprUnaryMinus (NScalarFloat (FLOAT "3ff0000000000000") metadata_leaf) metadata_inner
expression_not = NExprBooleanNot expression_signed_child metadata_cond
expression_not_base = NExprTernary expression_not ABSENT expression_fallback metadata
S_not = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_not_base) :: (PCOCCURRENCE pcpath_left expression_not) :: (PCOCCURRENCE pcpath_inner expression_signed_child) :: (PCOCCURRENCE pcpath_leaf (NScalarFloat (FLOAT "3ff0000000000000") metadata_leaf)) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner (PFLOAT 13830554455654793216)) :: (PCONSTANT pcpath_leaf (PFLOAT 4607182418800017408)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_not,porigin_left) = eps
$string_read_raw_truth(S_not,porigin_inner,PFLOAT 13830554455654793216)
$truth_value(S_not,PFLOAT 13830554455654793216,0) = S_not[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_not,porigin_left) = (PBOOL false)
$string_read_raw_known_base(S_not,porigin_base,pvalue_base)
S_not_forged = S_not[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: (PCONSTANT pcpath_inner (PFLOAT 13830554455654793216)) :: (PCONSTANT pcpath_leaf (PFLOAT 4607182418800017408)) :: ppool.CONSTANTS]]][.CODE = [pcode]]
~$string_read_raw_truth(S_not_forged,porigin_left,PBOOL false)
~$string_read_raw_known_base(S_not_forged,porigin_base,pvalue_base)
expression_overflow_child = NScalarInt (INTEGER $(-9223372036854775808)) metadata_inner
expression_overflow = NExprUnaryMinus expression_overflow_child metadata_cond
expression_overflow_base = NExprTernary expression_overflow (NScalarString (BYTES text_true) metadata_true) expression_fallback metadata
S_overflow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_overflow_base) :: (PCOCCURRENCE pcpath_left expression_overflow) :: (PCOCCURRENCE pcpath_inner expression_overflow_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PFLOAT 4890909195324358656)) :: (PCONSTANT pcpath_inner (PINT $(-9223372036854775808))) :: ppool.CONSTANTS]]]
$unary_apply(S_overflow,NEGATIVE,PINT $(-9223372036854775808),0) = S_overflow[.RESULT = KNOWN (PFLOAT 4890909195324358656)]
$string_read_raw_truth(S_overflow,porigin_left,PFLOAT 4890909195324358656)
$string_read_raw_known_base(S_overflow,porigin_base,pvalue_wrong)
expression_string_child = NScalarString (BYTES "MS4w") metadata_inner
expression_string_sign = NExprUnaryPlus expression_string_child metadata_cond
expression_string_base = NExprTernary expression_string_sign (NScalarString (BYTES text_true) metadata_true) expression_fallback metadata
S_string = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_string_base) :: (PCOCCURRENCE pcpath_left expression_string_sign) :: (PCOCCURRENCE pcpath_inner expression_string_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PFLOAT 4607182418800017408)) :: (PCONSTANT pcpath_inner (PSTRING ($ptascii("1.0")))) :: ppool.CONSTANTS]]]
$unary_apply(S_string,POSITIVE,PSTRING ($ptascii("1.0")),0) = S_string[.RESULT = KNOWN (PFLOAT 4607182418800017408)]
$string_read_raw_truth(S_string,porigin_left,PFLOAT 4607182418800017408)
$string_read_raw_known_base(S_string,porigin_base,pvalue_wrong)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
