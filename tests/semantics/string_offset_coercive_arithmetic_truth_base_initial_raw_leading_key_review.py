"""Quiet original scalar arithmetic retains finite FLOAT truth and frozen offsets."""

from string_offset_float_conditional_base_initial_raw_leading_key_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMul expression_add_coercive expression_factor_coercive metadata_cond)')
    old_hex = '  -- if n_cond = $hex_bits(text_cond,0)\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '').replace('n_cond = 4607182418800017408', 'n_cond = 4890909195324358656')
    count -= 1
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpMul expression_add_coercive expression_factor_coercive metadata_cond)
expression_add_coercive = NExprBinaryOpPlus expression_max_coercive expression_true_coercive metadata_add_coercive
expression_max_coercive = NScalarString (BYTES text_max_coercive) metadata_max_coercive
expression_true_coercive = NExprConstFetch (NName (BYTES text_true_name_coercive) metadata_true_name_coercive) metadata_true_coercive
expression_factor_coercive = NScalarString (BYTES text_factor_coercive) metadata_factor_coercive
$base64(text_max_coercive) = $ptascii("9223372036854775807")
$ptlc($base64(text_true_name_coercive)) = $ptascii("true")
$base64(text_factor_coercive) = $ptascii("1.0")
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_add_coercive)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_factor_coercive)
$origin_child((porigin_add_coercive),[PCFIELD 0]) = (porigin_max_coercive)
$origin_child((porigin_add_coercive),[PCFIELD 1]) = (porigin_true_coercive)
$origin_child((porigin_true_coercive),[PCFIELD 0]) = (porigin_true_name_coercive)
$origin_node(S_capture.SOURCES,porigin_true_name_coercive) = (NName (BYTES text_true_name_coercive) metadata_true_name_coercive)
''')
    for name, value in (('add', 'PFLOAT n_cond'),
                        ('max', 'PSTRING ($ptascii("9223372036854775807"))'),
                        ('true', 'PBOOL true'), ('factor', 'PSTRING ($ptascii("1.0"))')):
        checks += lines(f'''
$origin_node(S_capture.SOURCES,porigin_{name}_coercive) = (expression_{name}_coercive)
$compiled_read(S_capture,porigin_{name}_coercive) = ({value})
$string_read_raw_truth(S_capture,porigin_{name}_coercive,{value})
porigin_{name}_coercive = PORIGIN n_unit pcpath_{name}_coercive
''')
    checks += lines(r'''
$coerce_number(PSTRING ($ptascii("9223372036854775807"))) = COERCED (NINT 9223372036854775807) false
$coerce_number(PBOOL true) = COERCED (NINT 1) false
$coerce_number(PSTRING ($ptascii("1.0"))) = COERCED (NFLOAT 4607182418800017408) false
$binary_apply(S_capture,ADD,PSTRING ($ptascii("9223372036854775807")),PBOOL true,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$binary_apply(S_capture,MULTIPLY,PFLOAT n_cond,PSTRING ($ptascii("1.0")),0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$string_read_raw_truth(S_capture,porigin_cond,PFLOAT n_cond)
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_true_name_coercive = PORIGIN n_unit pcpath_true_name_coercive
S_budget_coercive = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_budget_coercive,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_budget_coercive,porigin_base,pkeyread.BASE)
S_child_type_coercive = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_max_coercive (PINT 9223372036854775807)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_child_type_coercive,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_child_type_coercive,porigin_base,pkeyread.BASE)
S_child_name_coercive = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_true_name_coercive (NName (BYTES "ZmFsc2U=") metadata_true_name_coercive)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_child_name_coercive,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_child_name_coercive,porigin_base,pkeyread.BASE)
expression_null_coercive = NExprConstFetch (NName (BYTES "bnVsbA==") metadata_max_coercive) metadata_add_coercive
expression_inf_string_coercive = NScalarString (BYTES "MWUzMDk=") metadata_factor_coercive
expression_quotient_coercive = NExprBinaryOpDiv expression_null_coercive expression_inf_string_coercive metadata_cond
expression_quotient_base_coercive = NExprTernary expression_quotient_coercive (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_inf_quotient_coercive = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_quotient_base_coercive) :: (PCOCCURRENCE pcpath_cond expression_quotient_coercive) :: (PCOCCURRENCE pcpath_add_coercive expression_null_coercive) :: (PCOCCURRENCE pcpath_max_coercive (NName (BYTES "bnVsbA==") metadata_max_coercive)) :: (PCOCCURRENCE pcpath_factor_coercive expression_inf_string_coercive) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 0)) :: (PCONSTANT pcpath_add_coercive PNULL) :: (PCONSTANT pcpath_factor_coercive (PSTRING ($ptascii("1e309")))) :: ppool.CONSTANTS]]]
$coerce_number(PSTRING ($ptascii("1e309"))) = COERCED (NFLOAT 9218868437227405312) false
$coerce_number(PNULL) = COERCED (NINT 0) false
$binary_apply(S_inf_quotient_coercive,DIVIDE,PNULL,PSTRING ($ptascii("1e309")),0) = S_inf_quotient_coercive[.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_inf_quotient_coercive,porigin_cond,PFLOAT 0)
$string_read_raw_known_base(S_inf_quotient_coercive,porigin_base,pvalue_wrong)
expression_leading_string_coercive = NScalarString (BYTES "MWUzMDl4") metadata_factor_coercive
expression_leading_coercive = NExprBinaryOpDiv expression_null_coercive expression_leading_string_coercive metadata_cond
expression_leading_base_coercive = NExprTernary expression_leading_coercive (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_leading_coercive = S_inf_quotient_coercive[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)][.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_leading_base_coercive) :: (PCOCCURRENCE pcpath_cond expression_leading_coercive) :: (PCOCCURRENCE pcpath_add_coercive expression_null_coercive) :: (PCOCCURRENCE pcpath_max_coercive (NName (BYTES "bnVsbA==") metadata_max_coercive)) :: (PCOCCURRENCE pcpath_factor_coercive expression_leading_string_coercive) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 0)) :: (PCONSTANT pcpath_add_coercive PNULL) :: (PCONSTANT pcpath_factor_coercive (PSTRING ($ptascii("1e309x")))) :: ppool.CONSTANTS]]]
$coerce_number(PSTRING ($ptascii("1e309x"))) = COERCED (NFLOAT 9218868437227405312) true
~$string_read_raw_truth(S_leading_coercive,porigin_cond,PFLOAT 0)
~$string_read_raw_known_base(S_leading_coercive,porigin_base,pvalue_wrong)
expression_zero_string_coercive = NScalarString (BYTES "MC4w") metadata_factor_coercive
expression_zero_div_coercive = NExprBinaryOpDiv expression_null_coercive expression_zero_string_coercive metadata_cond
expression_zero_div_base_coercive = NExprTernary expression_zero_div_coercive (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_zero_div_coercive = S_inf_quotient_coercive[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)][.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_zero_div_base_coercive) :: (PCOCCURRENCE pcpath_cond expression_zero_div_coercive) :: (PCOCCURRENCE pcpath_add_coercive expression_null_coercive) :: (PCOCCURRENCE pcpath_max_coercive (NName (BYTES "bnVsbA==") metadata_max_coercive)) :: (PCOCCURRENCE pcpath_factor_coercive expression_zero_string_coercive) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 0)) :: (PCONSTANT pcpath_add_coercive PNULL) :: (PCONSTANT pcpath_factor_coercive (PSTRING ($ptascii("0.0")))) :: ppool.CONSTANTS]]]
$coerce_number(PSTRING ($ptascii("0.0"))) = COERCED (NFLOAT 0) false
~$string_read_raw_truth(S_zero_div_coercive,porigin_cond,PFLOAT 0)
~$string_read_raw_known_base(S_zero_div_coercive,porigin_base,pvalue_wrong)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
