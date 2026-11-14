"""Quiet computed-zero shorthand keeps its fallback header and frozen offset."""
import base64

from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_review import render as render_zero
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_zero(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMinus expression_left_raw (NScalarInt (INTEGER 1) metadata_one_raw) metadata_cond)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_condition)
expression_condition = NExprBinaryOpMinus expression_left_raw (NScalarInt (INTEGER 1) metadata_one_raw) metadata_cond
expression_left_raw = NExprUnaryPlus expression_true_raw metadata_plus_raw
expression_true_raw = NExprConstFetch (NName (BYTES text_true_raw) metadata_name_raw) metadata_true_raw
$ptlc($base64(text_true_raw)) = $ptascii("true")
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_left_raw)
$origin_node(S_capture.SOURCES,porigin_left_raw) = (expression_left_raw)
$compiled_read(S_capture,porigin_left_raw) = (PINT 1)
$string_read_raw_unary_integer(S_capture,porigin_left_raw,1)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_one_raw)
$origin_node(S_capture.SOURCES,porigin_one_raw) = (NScalarInt (INTEGER 1) metadata_one_raw)
$compiled_read(S_capture,porigin_one_raw) = (PINT 1)
$binary_apply(S_capture,SUBTRACT,PINT 1,PINT 1,0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_capture,porigin_cond,PINT 0)
~$string_read_raw_truth(S_capture,porigin_cond,PBOOL false)
$truth_value(S_capture,PINT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
S_budget_raw = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget_raw,porigin_cond,PINT 0)
$string_read_raw_known_base(S_budget_raw,porigin_base,pkeyread.BASE)
porigin_false = PORIGIN n_unit pcpath_false_raw
expression_fallback_raw = NScalarString (BYTES text_false) metadata_false
''')
    # Each replaced literal route keeps its real pool and exact indexed source.
    for label, node, value, name in (
            ('null', 'NExprConstFetch (NName (BYTES "TnVMbA==") metadata_name_raw) metadata_cond', 'PNULL', 'NuLl'),
            ('false', 'NExprConstFetch (NName (BYTES "RmFMc0U=") metadata_name_raw) metadata_cond', 'PBOOL false', 'FaLsE'),
            ('zero', 'NScalarInt (INTEGER 0) metadata_cond', 'PINT 0', None),
            ('float_zero', 'NScalarFloat (FLOAT "0000000000000000") metadata_cond', 'PFLOAT 0', None)):
        name_occurrence = ''
        if name is not None:
            encoded = base64.b64encode(name.encode()).decode()
            name_occurrence = f'(PCOCCURRENCE (pcpath_cond ++ [PCFIELD 0]) (NName (BYTES "{encoded}") metadata_name_raw)) :: '
        checks += lines(f'''
expression_{label}_raw = {node}
expression_base_{label}_raw = NExprTernary expression_{label}_raw ABSENT expression_fallback_raw metadata
S_{label}_raw = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}_raw) :: (PCOCCURRENCE pcpath_cond expression_{label}_raw) :: {name_occurrence}pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond ({value})) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_{label}_raw,porigin_cond,{value})
$truth_value(S_{label}_raw,{value},0) = S_{label}_raw[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_{label}_raw,porigin_base,pkeyread.BASE)
S_{label}_condition_metadata_raw = S_{label}_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}_raw) :: (PCOCCURRENCE pcpath_cond (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_{label}_condition_metadata_raw,porigin_base,pkeyread.BASE)
S_{label}_fallback_metadata_raw = S_{label}_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_false_raw (NScalarString (BYTES text_false) eps)) :: (PCOCCURRENCE pcpath_base expression_base_{label}_raw) :: (PCOCCURRENCE pcpath_cond expression_{label}_raw) :: {name_occurrence}pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_{label}_fallback_metadata_raw,porigin_base,pkeyread.BASE)
''')
        if name is not None:
            checks += lines(f'''
S_{label}_name_raw = S_{label}_raw[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_cond ++ [PCFIELD 0]) (NName (BYTES "eA==") metadata_name_raw)) :: (PCOCCURRENCE pcpath_base expression_base_{label}_raw) :: (PCOCCURRENCE pcpath_cond expression_{label}_raw) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_{label}_name_raw,porigin_cond,{value})
~$string_read_raw_known_base(S_{label}_name_raw,porigin_base,pkeyread.BASE)
''')
    checks += lines(r'''
expression_noncanonical_raw = NScalarFloat (FLOAT "00000000000000000") metadata_cond
expression_base_noncanonical_raw = NExprTernary expression_noncanonical_raw ABSENT expression_fallback_raw metadata
S_noncanonical_raw = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_noncanonical_raw) :: (PCOCCURRENCE pcpath_cond expression_noncanonical_raw) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_noncanonical_raw,porigin_cond,PFLOAT 0)
~$string_read_raw_known_base(S_noncanonical_raw,porigin_base,pkeyread.BASE)
expression_not_leaf_raw = NScalarInt (INTEGER 1) metadata_one_raw
expression_not_raw = NExprBooleanNot expression_not_leaf_raw metadata_cond
expression_base_not_raw = NExprTernary expression_not_raw ABSENT expression_fallback_raw metadata
S_not_raw = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_not_raw) :: (PCOCCURRENCE pcpath_cond expression_not_raw) :: (PCOCCURRENCE (pcpath_cond ++ [PCFIELD 0]) expression_not_leaf_raw) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL false)) :: (PCONSTANT (pcpath_cond ++ [PCFIELD 0]) (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_not_raw,porigin_cond,PBOOL false)
$string_read_raw_known_base(S_not_raw,porigin_base,pkeyread.BASE)
S_not_wrong_raw = S_not_raw[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL true)) :: (PCONSTANT (pcpath_cond ++ [PCFIELD 0]) (PINT 1)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_not_wrong_raw,porigin_cond,PBOOL true)
~$string_read_raw_known_base(S_not_wrong_raw,porigin_base,pkeyread.BASE)
expression_string_raw = NScalarString (BYTES "MA==") metadata_cond
expression_base_string_raw = NExprTernary expression_string_raw ABSENT expression_fallback_raw metadata
S_string_raw = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_string_raw) :: (PCOCCURRENCE pcpath_cond expression_string_raw) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PSTRING ([48]))) :: ppool.CONSTANTS]]]
$type_bytes(PSTRING ([48])) = $ptascii("string")
$string_read_raw_truth(S_string_raw,porigin_cond,PSTRING ([48]))
$string_read_raw_known_base(S_string_raw,porigin_base,pkeyread.BASE)
S_child_pool_raw = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0,PCFIELD 1]) (PINT 2)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_child_pool_raw,porigin_cond,PINT 0)
~$string_read_raw_known_base(S_child_pool_raw,porigin_base,pkeyread.BASE)
S_condition_metadata_raw = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_cond (NExprBinaryOpMinus expression_left_raw (NScalarInt (INTEGER 1) metadata_one_raw) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_condition_metadata_raw,porigin_base,pkeyread.BASE)
S_fallback_metadata_raw = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_false_raw (NScalarString (BYTES text_false) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_fallback_metadata_raw,porigin_base,pkeyread.BASE)
S_emitted_raw = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 12 false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_emitted_raw,porigin_cond) = eps
~$string_read_raw_known_base(S_emitted_raw,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
