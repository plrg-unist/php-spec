"""Quiet integer complements retain a selected full-ternary base and raw offset."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBitwiseNot expression_shift_bitnot metadata_cond)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBitwiseNot expression_shift_bitnot metadata_cond)
expression_shift_bitnot = NExprBinaryOpShiftLeft expression_inner_bitnot expression_count_bitnot metadata_shift_bitnot
expression_inner_bitnot = NExprBitwiseNot expression_zero_bitnot metadata_inner_bitnot
expression_zero_bitnot = NScalarInt (INTEGER 0) metadata_zero_bitnot
expression_count_bitnot = NScalarInt (INTEGER 1) metadata_count_bitnot
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_shift_bitnot)
$origin_child((porigin_shift_bitnot),[PCFIELD 0]) = (porigin_inner_bitnot)
$origin_child((porigin_shift_bitnot),[PCFIELD 1]) = (porigin_count_bitnot)
$origin_child((porigin_inner_bitnot),[PCFIELD 0]) = (porigin_zero_bitnot)
''')
    for name, value in (('shift', -2), ('inner', -1), ('count', 1), ('zero', 0)):
        value = str(value) if value >= 0 else f'$({value})'
        checks += lines(f'''
$origin_node(S_capture.SOURCES,porigin_{name}_bitnot) = (expression_{name}_bitnot)
$compiled_read(S_capture,porigin_{name}_bitnot) = (PINT {value})
$string_read_raw_unary_integer(S_capture,porigin_{name}_bitnot,{value})
porigin_{name}_bitnot = PORIGIN n_unit pcpath_{name}_bitnot
''')
    checks += lines(r'''
$bitnot_value(S_capture,PINT 0,0) = S_capture[.RESULT = KNOWN (PINT $(-1))]
$binary_apply(S_capture,SHIFTLEFT,PINT $(-1),PINT 1,0) = S_capture[.RESULT = KNOWN (PINT $(-2))]
$bitnot_value(S_capture,PINT $(-2),0) = S_capture[.RESULT = KNOWN (PINT 1)]
$string_read_raw_unary_integer(S_capture,porigin_cond,1)
$string_read_raw_truth(S_capture,porigin_cond,PINT 1)
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
S_budget_bitnot = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 7)]
$bitnot_apply(S_budget_bitnot,PINT $(-2),0) = S_budget_bitnot
$bitnot_value(S_budget_bitnot,PINT $(-2),0) = S_budget_bitnot[.RESULT = KNOWN (PINT 1)]
$string_read_raw_unary_integer(S_budget_bitnot,porigin_cond,1)
$string_read_raw_known_base(S_budget_bitnot,porigin_base,pkeyread.BASE)
S_budget_forged_bitnot = S_budget_bitnot[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT 7)) :: ppool.CONSTANTS]]]
~$string_read_raw_unary_integer(S_budget_forged_bitnot,porigin_cond,7)
~$string_read_raw_known_base(S_budget_forged_bitnot,porigin_base,pkeyread.BASE)
S_precision_bitnot = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond 17) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_precision_bitnot,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PINT 0'),
            ('child', 'pcpath_shift_bitnot', 'PINT $(-3)'),
            ('inner', 'pcpath_inner_bitnot', 'PINT 0'),
            ('leaf', 'pcpath_zero_bitnot', 'PINT 1'),
            ('type', 'pcpath_shift_bitnot', 'PFLOAT 13835058055282163712')):
        checks += lines(f'''
S_pool_{label}_bitnot = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_pool_{label}_bitnot,porigin_cond,{'PINT 0' if label == 'own' else 'PINT 1'})
~$string_read_raw_known_base(S_pool_{label}_bitnot,porigin_base,pkeyread.BASE)
''')
    for label, path, node in (
            ('own', 'pcpath_cond', 'NExprBitwiseNot expression_shift_bitnot eps'),
            ('child', 'pcpath_shift_bitnot', 'NExprBinaryOpShiftLeft expression_inner_bitnot expression_count_bitnot eps'),
            ('inner', 'pcpath_inner_bitnot', 'NExprBitwiseNot expression_zero_bitnot eps')):
        checks += lines(f'''
S_metadata_{label}_bitnot = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
{'' if label == 'own' else '~'}$string_read_raw_truth(S_metadata_{label}_bitnot,porigin_cond,PINT 1)
~$string_read_raw_known_base(S_metadata_{label}_bitnot,porigin_base,pkeyread.BASE)
''')
    # Negative raw atoms and extrema here are constructed projections, with source0.
    for label, operand, result, accepted in (
            ('raw_zero', 0, -1, True), ('negative_one', -1, 0, True),
            ('minimum', -9223372036854775808, 9223372036854775807, True),
            ('maximum', 9223372036854775807, -9223372036854775808, True),
            ('child_outside', 9223372036854775808, -9223372036854775809, False),
            ('result_outside', -9223372036854775809, 9223372036854775808, False)):
        child, complement = (str(v) if v >= 0 else f'$({v})' for v in (operand, result))
        checks += lines(f'''
expression_{label}_child_bitnot = NScalarInt (INTEGER {child}) metadata_shift_bitnot
expression_{label}_bitnot = NExprBitwiseNot expression_{label}_child_bitnot metadata_cond
expression_{label}_base_bitnot = NExprTernary expression_{label}_bitnot (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_{label}_bitnot = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base_bitnot) :: (PCOCCURRENCE pcpath_cond expression_{label}_bitnot) :: (PCOCCURRENCE pcpath_shift_bitnot expression_{label}_child_bitnot) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT {complement})) :: (PCONSTANT pcpath_shift_bitnot (PINT {child})) :: ppool.CONSTANTS]]]
$string_read_raw_unary_integer(S_{label}_bitnot,porigin_cond,{complement}) = {str(accepted).lower()}
''')
        if accepted:
            selected = 'pvalue_wrong' if result == 0 else 'pkeyread.BASE'
            checks += [f'$bitnot_value(S_{label}_bitnot,PINT {child},0) = S_{label}_bitnot[.RESULT = KNOWN (PINT {complement})]',
                       f'$string_read_raw_known_base(S_{label}_bitnot,porigin_base,{selected})']
        else:
            checks += [f'~$string_read_raw_known_base(S_{label}_bitnot,porigin_base,{value})'
                       for value in ('pkeyread.BASE', 'pvalue_wrong')]
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
