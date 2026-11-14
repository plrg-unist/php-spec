"""A certified zero tree retains the shorthand fallback and original key."""

from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_peer_review import render as render_zero
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_zero(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpPlus expression_product expression_six metadata_cond)')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_left) = (expression_condition)
expression_condition = NExprBinaryOpPlus expression_product expression_six metadata_cond
expression_product = NExprBinaryOpMul expression_outer expression_minus metadata_product
expression_outer = NExprUnaryPlus expression_inner metadata_outer
expression_inner = NExprUnaryPlus expression_text metadata_inner
expression_text = NScalarString (BYTES text_two) metadata_text
expression_minus = NExprUnaryMinus (NScalarInt (INTEGER 3) metadata_three) metadata_minus
expression_six = NScalarInt (INTEGER 6) metadata_six
$base64(text_two) = $ptascii("2")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_product)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_six)
$origin_child((porigin_product),[PCFIELD 0]) = (porigin_outer)
$origin_child((porigin_product),[PCFIELD 1]) = (porigin_minus)
$origin_node(S_capture.SOURCES,porigin_product) = (expression_product)
$origin_node(S_capture.SOURCES,porigin_outer) = (expression_outer)
$origin_node(S_capture.SOURCES,porigin_minus) = (expression_minus)
$origin_node(S_capture.SOURCES,porigin_six) = (expression_six)
$compiled_read(S_capture,porigin_product) = (PINT $(-6))
$compiled_read(S_capture,porigin_outer) = (PINT 2)
$compiled_read(S_capture,porigin_minus) = (PINT $(-3))
$compiled_read(S_capture,porigin_six) = (PINT 6)
$string_read_raw_unary_integer(S_capture,porigin_left,0)
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
$truth_value(S_capture,PINT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$origin_node(S_capture.SOURCES,porigin_right) = (expression_fallback)
expression_fallback = NScalarString (BYTES text_right) metadata_right
porigin_product = PORIGIN n_unit pcpath_product
porigin_six = PORIGIN n_unit pcpath_six
S_budget = S_capture[.COMPLETION = BUDGET]
$string_read_raw_known_base(S_budget,porigin_base,pvalue_base)
S_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_precision,porigin_base,pvalue_base)
expression_truthy_condition = NExprBinaryOpPlus expression_product (NScalarInt (INTEGER 7) metadata_six) metadata_cond
expression_truthy_base = NExprTernary expression_truthy_condition ABSENT expression_fallback metadata
S_truthy = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_truthy_base) :: (PCOCCURRENCE pcpath_left expression_truthy_condition) :: (PCOCCURRENCE pcpath_six (NScalarInt (INTEGER 7) metadata_six)) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 1)) :: (PCONSTANT pcpath_six (PINT 7)) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_truthy,porigin_left,PINT 1)
$truth_value(S_truthy,PINT 1,0) = S_truthy[.RESULT = KNOWN (PBOOL true)]
~$string_read_raw_known_base(S_truthy,porigin_base,pvalue_base)
''')
    for label, path, node in (
            ('condition', 'pcpath_left', 'NExprBinaryOpPlus expression_product expression_six eps'),
            ('fallback', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        checks += lines(f'''
S_metadata_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_metadata_{label},porigin_base,pvalue_base)
$string_read_plan(S_metadata_{label}) = eps
''')
    checks += lines(r'''
$compiled_read(S_metadata_fallback,porigin_right) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_metadata_fallback,porigin_right,PSTRING ($ptascii("abc"))) = pvalue_base
''')
    # These local scalar projections carry no additional source/native credit.
    for label, node, value, name, admitted in (
            ('false', 'NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_cond) metadata_cond', 'PBOOL false', 'ZmFsc2U=', True),
            ('null', 'NExprConstFetch (NName (BYTES "bnVsbA==") metadata_cond) metadata_cond', 'PNULL', 'bnVsbA==', True),
            ('float_zero', 'NScalarFloat (FLOAT "0000000000000000") metadata_cond', 'PFLOAT 0', None, True),
            ('negative_zero', 'NScalarFloat (FLOAT "8000000000000000") metadata_cond', 'PFLOAT 9223372036854775808', None, True),
            ('short_zero', 'NScalarFloat (FLOAT "0") metadata_cond', 'PFLOAT 0', None, False),
            ('long_zero', 'NScalarFloat (FLOAT "00000000000000000") metadata_cond', 'PFLOAT 0', None, False),
            ('bad_hex', 'NScalarFloat (FLOAT "000000000000000g") metadata_cond', 'PFLOAT 0', None, False)):
        child = '' if name is None else f' :: (PCOCCURRENCE (pcpath_left ++ [PCFIELD 0]) (NName (BYTES "{name}") metadata_cond))'
        checks += lines(f'''
expression_scalar_{label} = {node}
expression_base_{label} = NExprTernary expression_scalar_{label} ABSENT expression_fallback metadata
S_scalar_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}) :: (PCOCCURRENCE pcpath_left expression_scalar_{label}){child} :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left ({value})) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_scalar_{label},porigin_left,{value}) = {str(admitted).lower()}
$string_read_raw_known_base(S_scalar_{label},porigin_base,pvalue_base) = {str(admitted).lower()}
''')
        if name is not None:
            checks += lines(f'''
S_bad_name_{label} = S_scalar_{label}[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}) :: (PCOCCURRENCE pcpath_left expression_scalar_{label}) :: (PCOCCURRENCE (pcpath_left ++ [PCFIELD 0]) (NName (BYTES "{name}") eps)) :: pcunit.OCCURRENCES]]]
$compiled_read(S_bad_name_{label},porigin_left) = ({value})
~$string_read_raw_known_base(S_bad_name_{label},porigin_base,pvalue_base)
''')
    checks += lines(r'''
expression_true_child = NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_cond) metadata_cond
expression_folded_not = NExprBooleanNot expression_true_child metadata_cond
expression_folded_base = NExprTernary expression_folded_not ABSENT expression_fallback metadata
S_folded = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_folded_base) :: (PCOCCURRENCE pcpath_left expression_folded_not) :: (PCOCCURRENCE pcpath_product expression_true_child) :: (PCOCCURRENCE (pcpath_product ++ [PCFIELD 0]) (NName (BYTES "dHJ1ZQ==") metadata_cond)) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: (PCONSTANT pcpath_product (PBOOL true)) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_folded,porigin_left,PBOOL false)
$truth_value(S_folded,PBOOL false,0) = S_folded[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_folded,porigin_base,pvalue_base)
expression_float_child = NScalarFloat (FLOAT "3ff0000000000000") metadata_product
expression_float_not = NExprBooleanNot expression_float_child metadata_cond
expression_float_base = NExprTernary expression_float_not ABSENT expression_fallback metadata
S_float = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_float_base) :: (PCOCCURRENCE pcpath_left expression_float_not) :: (PCOCCURRENCE pcpath_product expression_float_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_product (PFLOAT 4607182418800017408)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_float,porigin_left) = eps
$string_read_raw_truth(S_float,porigin_product,PFLOAT 4607182418800017408)
$truth_value(S_float,PFLOAT 4607182418800017408,0) = S_float[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_float,porigin_left) = (PBOOL false)
$string_read_raw_known_base(S_float,porigin_base,pvalue_base)
S_float_forged = S_float[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: (PCONSTANT pcpath_product (PFLOAT 4607182418800017408)) :: ppool.CONSTANTS]]][.CODE = [pcode]]
$compiled_read(S_float_forged,porigin_left) = (PBOOL false)
~$string_read_raw_truth(S_float_forged,porigin_left,PBOOL false)
~$string_read_raw_known_base(S_float_forged,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
