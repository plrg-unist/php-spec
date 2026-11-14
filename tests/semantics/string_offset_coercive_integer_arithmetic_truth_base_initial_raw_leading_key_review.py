"""Quiet original scalar arithmetic retains PINT truth and frozen raw offsets."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMul expression_sum_integer expression_factor_integer metadata_cond)')
    body = body.replace('PINT 1', 'PINT 3')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpMul expression_sum_integer expression_factor_integer metadata_cond)
expression_sum_integer = NExprBinaryOpPlus expression_string_integer expression_true_integer metadata_sum_integer
expression_string_integer = NScalarString (BYTES text_string_integer) metadata_string_integer
expression_true_integer = NExprConstFetch (NName (BYTES text_true_integer) metadata_true_name_integer) metadata_true_integer
expression_factor_integer = NScalarString (BYTES text_factor_integer) metadata_factor_integer
$base64(text_string_integer) = $ptascii("2")
$ptlc($base64(text_true_integer)) = $ptascii("true")
$base64(text_factor_integer) = $ptascii("1")
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_sum_integer)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_factor_integer)
$origin_child((porigin_sum_integer),[PCFIELD 0]) = (porigin_string_integer)
$origin_child((porigin_sum_integer),[PCFIELD 1]) = (porigin_true_integer)
$origin_child((porigin_true_integer),[PCFIELD 0]) = (porigin_true_name_integer)
$origin_node(S_capture.SOURCES,porigin_true_name_integer) = (NName (BYTES text_true_integer) metadata_true_name_integer)
''')
    for name, value in (('sum', 'PINT 3'), ('string', 'PSTRING ($ptascii("2"))'),
                        ('true', 'PBOOL true'), ('factor', 'PSTRING ($ptascii("1"))')):
        checks += lines(f'''
$origin_node(S_capture.SOURCES,porigin_{name}_integer) = (expression_{name}_integer)
$compiled_read(S_capture,porigin_{name}_integer) = ({value})
$string_read_raw_truth(S_capture,porigin_{name}_integer,{value})
porigin_{name}_integer = PORIGIN n_unit pcpath_{name}_integer
''')
    checks += lines(r'''
$compiled_string_value(S_capture,porigin_string_integer,PSTRING ($ptascii("2"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))
$coerce_number(PSTRING ($ptascii("2"))) = COERCED (NINT 2) false
$coerce_number(PBOOL true) = COERCED (NINT 1) false
$coerce_number(PSTRING ($ptascii("1"))) = COERCED (NINT 1) false
~$string_read_raw_unary_integer(S_capture,porigin_sum_integer,3)
~$string_read_raw_unary_integer(S_capture,porigin_cond,3)
$binary_apply(S_capture,ADD,PSTRING ($ptascii("2")),PBOOL true,0) = S_capture[.RESULT = KNOWN (PINT 3)]
$binary_apply(S_capture,MULTIPLY,PINT 3,PSTRING ($ptascii("1")),0) = S_capture[.RESULT = KNOWN (PINT 3)]
$string_read_raw_truth(S_capture,porigin_cond,PINT 3)
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_true_name_integer = PORIGIN n_unit pcpath_true_name_integer
S_budget_integer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
$string_read_raw_truth(S_budget_integer,porigin_cond,PINT 3)
$string_read_raw_known_base(S_budget_integer,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own_result', 'pcpath_cond', 'PINT 4'),
            ('sum_result', 'pcpath_sum_integer', 'PINT 4'),
            ('string_tag', 'pcpath_string_integer', 'PINT 2'),
            ('boolean_tag', 'pcpath_true_integer', 'PINT 1'),
            ('factor_value', 'pcpath_factor_integer', 'PSTRING ($ptascii("2"))')):
        own = value if label == 'own_result' else 'PINT 3'
        checks += [f'S_bad_integer_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_integer_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_integer_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('sum', 'pcpath_sum_integer', 'NExprBinaryOpPlus expression_string_integer expression_true_integer eps'),
            ('factor', 'pcpath_factor_integer', 'NScalarString (BYTES text_factor_integer) eps'),
            ('true_name', 'pcpath_true_name_integer', 'NName (BYTES text_true_integer) eps')):
        checks += [f'S_bad_integer_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_integer_{label}_source,porigin_cond,PINT 3)',
                   f'~$string_read_raw_known_base(S_bad_integer_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_bad_integer_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_factor_integer 12 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_integer_code,porigin_cond,PINT 3)
expression_nul_integer_base = NExprTernary (NExprBinaryOpMul expression_sum_integer expression_factor_integer metadata_cond) (NScalarString (BYTES "YQBi") metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_nul_integer_base = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_nul_integer_base) :: (PCOCCURRENCE (pcpath_base ++ [PCFIELD 1]) (NScalarString (BYTES "YQBi") metadata_true)) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 1]) (PSTRING ([97,0,98]))) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_nul_integer_base,porigin_base,PSTRING_CARRIER INTERNED_STRING ([97,0,98]))
$string_read_raw_leading(PSTRING_CARRIER INTERNED_STRING ([97,0,98]),pkeyread.VALUE) = eps
$string_read_raw_capture(S_nul_integer_base[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97,0,98]))],pkeyread.INPUT,PSTRING_CARRIER INTERNED_STRING ([97,0,98])) = eps
S_bool_integer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL true)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_bool_integer,porigin_cond,PBOOL true)
S_float_integer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 4613937818241073152)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_float_integer,porigin_cond,PFLOAT 4613937818241073152)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
