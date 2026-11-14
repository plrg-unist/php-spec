"""Integer complement preserves the false base through initial-key reference rebinding."""

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary expression_actual_bitnot')
    early = lines(r'''
$origin_node(S_capture.SOURCES,porigin_left) = (expression_actual_bitnot)
expression_actual_bitnot = NExprBitwiseNot expression_actual_negative metadata_cond
expression_actual_negative = NExprUnaryMinus expression_actual_one metadata_actual_negative
expression_actual_one = NScalarInt (INTEGER 1) metadata_actual_one
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_actual_negative)
$origin_child((porigin_actual_negative),[PCFIELD 0]) = (porigin_actual_one)
$origin_node(S_capture.SOURCES,porigin_actual_negative) = (expression_actual_negative)
$origin_node(S_capture.SOURCES,porigin_actual_one) = (expression_actual_one)
$compiled_read(S_capture,porigin_actual_negative) = (PINT $(-1))
$compiled_read(S_capture,porigin_actual_one) = (PINT 1)
$unary_apply(S_capture,NEGATIVE,PINT 1,0) = S_capture[.RESULT = KNOWN (PINT $(-1))]
$bitnot_value(S_capture,PINT $(-1),0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_unary_integer(S_capture,porigin_left,0)
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + x + '\n' for x in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_actual_negative = PORIGIN n_unit pcpath_actual_negative
porigin_actual_one = PORIGIN n_unit pcpath_actual_one
S_bitnot_budget = S_capture[.COMPLETION = BUDGET]
$string_read_raw_unary_integer(S_bitnot_budget,porigin_left,0)
$string_read_raw_known_base(S_bitnot_budget,porigin_base,pvalue_base)
S_bitnot_budget_result = S_bitnot_budget[.RESULT = KNOWN (PINT 1)]
$bitnot_apply(S_bitnot_budget_result,PINT $(-1),0) = S_bitnot_budget_result
$bitnot_value(S_bitnot_budget_result,PINT $(-1),0) = S_bitnot_budget_result[.RESULT = KNOWN (PINT 0)]
$string_read_raw_unary_integer(S_bitnot_budget_result,porigin_left,0)
S_bitnot_forged_budget = S_bitnot_budget_result[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 1)) :: ppool.CONSTANTS]]]
~$string_read_raw_unary_integer(S_bitnot_forged_budget,porigin_left,1)
~$string_read_raw_truth(S_bitnot_forged_budget,porigin_left,PINT 1)
~$string_read_raw_known_base(S_bitnot_forged_budget,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_bitnot_forged_budget,porigin_base,pvalue_wrong)
S_bitnot_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_bitnot_precision,porigin_base,pvalue_base)
S_bitnot_shorthand = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary expression_actual_bitnot ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_bitnot_shorthand,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_bitnot_shorthand,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PINT 1'),
            ('own_type', 'pcpath_left', 'PFLOAT 0'),
            ('child', 'pcpath_actual_negative', 'PINT 0'),
            ('child_type', 'pcpath_actual_negative', 'PFLOAT 13830554455654793216'),
            ('leaf', 'pcpath_actual_one', 'PINT 2')):
        result = value if label in ('own', 'own_type') else 'PINT 0'
        checks += lines(f'''
S_bitnot_pool_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_bitnot_pool_{label},porigin_left,{result})
~$string_read_raw_known_base(S_bitnot_pool_{label},porigin_base,pvalue_base)
''')
    for label, path, node in (
            ('own', 'pcpath_left', 'NExprBitwiseNot expression_actual_negative eps'),
            ('child', 'pcpath_actual_negative', 'NExprUnaryMinus expression_actual_one eps'),
            ('leaf', 'pcpath_actual_one', 'NScalarInt (INTEGER 1) eps')):
        checks += lines(f'''
S_bitnot_source_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
{'' if label == 'own' else '~'}$string_read_raw_truth(S_bitnot_source_{label},porigin_left,PINT 0)
~$string_read_raw_known_base(S_bitnot_source_{label},porigin_base,pvalue_base)
''')
    # Signed extreme raw leaves and the projections below are constructed, with source0.
    for label, operand, result, accepted in (
            ('zero', 0, -1, True), ('negative_one', -1, 0, True),
            ('minimum', -9223372036854775808, 9223372036854775807, True),
            ('maximum', 9223372036854775807, -9223372036854775808, True),
            ('outside_positive', 9223372036854775808, -9223372036854775809, False),
            ('outside_negative', -9223372036854775809, 9223372036854775808, False)):
        value, complement = (str(i) if i >= 0 else f'$({i})' for i in (operand, result))
        selected = 'pvalue_base' if result == 0 else 'pvalue_wrong'
        checks += lines(f'''
expression_bitnot_{label}_child = NScalarInt (INTEGER {value}) metadata_actual_negative
expression_bitnot_{label} = NExprBitwiseNot expression_bitnot_{label}_child metadata_cond
expression_bitnot_{label}_base = NExprTernary expression_bitnot_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_bitnot_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bitnot_{label}_base) :: (PCOCCURRENCE pcpath_left expression_bitnot_{label}) :: (PCOCCURRENCE pcpath_actual_negative expression_bitnot_{label}_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT {complement})) :: (PCONSTANT pcpath_actual_negative (PINT {value})) :: ppool.CONSTANTS]]]
{'' if accepted else '~'}$string_read_raw_unary_integer(S_bitnot_{label},porigin_left,{complement})
{'' if accepted else '~'}$string_read_raw_truth(S_bitnot_{label},porigin_left,PINT {complement})
''')
        if accepted:
            checks += [f'$bitnot_value(S_bitnot_{label},PINT {value},0) = S_bitnot_{label}[.RESULT = KNOWN (PINT {complement})]',
                       f'$string_read_raw_known_base(S_bitnot_{label},porigin_base,{selected})']
        else:
            checks += [f'~$string_read_raw_known_base(S_bitnot_{label},porigin_base,{base})'
                       for base in ('pvalue_base', 'pvalue_wrong')]
    for label, node, value in (
            ('float', 'NScalarFloat (FLOAT "bff0000000000000")', 'PFLOAT 13830554455654793216'),
            ('string', 'NScalarString (BYTES "MA==")', 'PSTRING ($ptascii("0"))')):
        checks += lines(f'''
expression_bitnot_typed_{label}_child = {node} metadata_actual_negative
expression_bitnot_typed_{label} = NExprBitwiseNot expression_bitnot_typed_{label}_child metadata_cond
expression_bitnot_typed_{label}_base = NExprTernary expression_bitnot_typed_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_bitnot_typed_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bitnot_typed_{label}_base) :: (PCOCCURRENCE pcpath_left expression_bitnot_typed_{label}) :: (PCOCCURRENCE pcpath_actual_negative expression_bitnot_typed_{label}_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 0)) :: (PCONSTANT pcpath_actual_negative ({value})) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_bitnot_typed_{label},porigin_actual_negative,{value})
~$string_read_raw_unary_integer(S_bitnot_typed_{label},porigin_left,0)
~$string_read_raw_truth(S_bitnot_typed_{label},porigin_left,PINT 0)
~$string_read_raw_known_base(S_bitnot_typed_{label},porigin_base,pvalue_base)
''')
    checks += lines(r'''
expression_bitnot_inner_zero = NScalarInt (INTEGER 0) metadata_actual_one
expression_bitnot_inner = NExprBitwiseNot expression_bitnot_inner_zero metadata_actual_negative
expression_bitnot_double = NExprBitwiseNot expression_bitnot_inner metadata_cond
expression_bitnot_double_base = NExprTernary expression_bitnot_double (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_bitnot_double = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bitnot_double_base) :: (PCOCCURRENCE pcpath_left expression_bitnot_double) :: (PCOCCURRENCE pcpath_actual_negative expression_bitnot_inner) :: (PCOCCURRENCE pcpath_actual_one expression_bitnot_inner_zero) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_actual_one (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_raw_unary_integer(S_bitnot_double,porigin_actual_negative,$(-1))
$string_read_raw_unary_integer(S_bitnot_double,porigin_left,0)
$string_read_raw_known_base(S_bitnot_double,porigin_base,pvalue_base)
$origin_child((porigin_actual_negative),[PCFIELD 1]) = (porigin_bitnot_zero)
porigin_bitnot_zero = PORIGIN n_unit pcpath_bitnot_zero
expression_bitnot_binary_left = NScalarInt (INTEGER $(-1)) metadata_actual_one
expression_bitnot_binary_right = NScalarInt (INTEGER 0) metadata_actual_one
expression_bitnot_binary = NExprBinaryOpBitwiseOr expression_bitnot_binary_left expression_bitnot_binary_right metadata_actual_negative
expression_bitnot_over_binary = NExprBitwiseNot expression_bitnot_binary metadata_cond
expression_bitnot_over_binary_base = NExprTernary expression_bitnot_over_binary (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_capture.CODE = [pcode]
S_bitnot_binary = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bitnot_over_binary_base) :: (PCOCCURRENCE pcpath_left expression_bitnot_over_binary) :: (PCOCCURRENCE pcpath_actual_negative expression_bitnot_binary) :: (PCOCCURRENCE pcpath_actual_one expression_bitnot_binary_left) :: (PCOCCURRENCE pcpath_bitnot_zero expression_bitnot_binary_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_actual_one (PINT $(-1))) :: (PCONSTANT pcpath_bitnot_zero (PINT 0)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_bitnot_zero 18 true) :: pcode.EXPRESSIONS]]]
$string_read_raw_unary_integer(S_bitnot_binary,porigin_actual_negative,$(-1))
$string_read_raw_unary_integer(S_bitnot_binary,porigin_left,0)
$binary_apply(S_bitnot_binary,BITOR,PINT $(-1),PINT 0,0) = S_bitnot_binary[.RESULT = KNOWN (PINT $(-1))]
$string_read_raw_known_base(S_bitnot_binary,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
