"""Exact signed64 integer division retains a full-ternary base and raw offset."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpDiv expression_numerator expression_denominator metadata_cond)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_condition_division)
expression_condition_division = NExprBinaryOpDiv expression_numerator expression_denominator metadata_cond
expression_numerator = NScalarInt (INTEGER 6) metadata_numerator
expression_denominator = NScalarInt (INTEGER 6) metadata_denominator
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_numerator)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_denominator)
$origin_node(S_capture.SOURCES,porigin_numerator) = (expression_numerator)
$origin_node(S_capture.SOURCES,porigin_denominator) = (expression_denominator)
$compiled_read(S_capture,porigin_numerator) = (PINT 6)
$compiled_read(S_capture,porigin_denominator) = (PINT 6)
$string_read_raw_unary_integer(S_capture,porigin_numerator,6)
$string_read_raw_unary_integer(S_capture,porigin_denominator,6)
$binary_apply(S_capture,DIVIDE,PINT 6,PINT 6,0) = S_capture[.RESULT = KNOWN (PINT 1)]
$string_read_raw_unary_integer(S_capture,porigin_cond,1)
$string_read_raw_truth(S_capture,porigin_cond,PINT 1)
porigin_numerator = PORIGIN n_unit pcpath_numerator
porigin_denominator = PORIGIN n_unit pcpath_denominator
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
S_budget_division = S_capture[.COMPLETION = BUDGET]
$string_read_raw_unary_integer(S_budget_division,porigin_cond,1)
$string_read_raw_known_base(S_budget_division,porigin_base,pkeyread.BASE)
S_precision_division = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond 17) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_precision_division,porigin_base,pkeyread.BASE)
S_wrong_result_division = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT 2)) :: ppool.CONSTANTS]]]
~$string_read_raw_unary_integer(S_wrong_result_division,porigin_cond,2)
~$string_read_raw_known_base(S_wrong_result_division,porigin_base,pkeyread.BASE)
S_wrong_child_division = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_denominator (PINT 3)) :: ppool.CONSTANTS]]]
~$string_read_raw_unary_integer(S_wrong_child_division,porigin_cond,1)
~$string_read_raw_known_base(S_wrong_child_division,porigin_base,pkeyread.BASE)
''')
    for label, path, node in (
            ('numerator', 'pcpath_numerator', 'NScalarInt (INTEGER 6) eps'),
            ('denominator', 'pcpath_denominator', 'NScalarInt (INTEGER 6) eps')):
        checks += lines(f'''
S_metadata_{label}_division = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_unary_integer(S_metadata_{label}_division,porigin_cond,1)
~$string_read_raw_known_base(S_metadata_{label}_division,porigin_base,pkeyread.BASE)
''')
    # Negative raw atoms and extrema are constructed projections, with source0.
    for label, numerator, denominator, result, accepted in (
            ('two_by_one', 2, 1, 2, True),
            ('four_by_two', 4, 2, 2, True),
            ('negative', -6, 3, -2, True),
            ('negative_rhs', 6, -3, -2, True),
            ('zero', 0, 2, 0, True),
            ('maximum', 9223372036854775807, 1, 9223372036854775807, True),
            ('minimum', -9223372036854775808, 1, -9223372036854775808, True),
            ('zero_rhs', 6, 0, 0, False),
            ('fraction', 1, 2, 0, False),
            ('minimum_promotion', -9223372036854775808, -1, 0, False),
            ('outside_child', 9223372036854775808, 1, 0, False)):
        num, den, value = (str(v) if v >= 0 else f'$({v})'
                           for v in (numerator, denominator, result))
        checks += lines(f'''
expression_num_{label} = NScalarInt (INTEGER {num}) metadata_numerator
expression_den_{label} = NScalarInt (INTEGER {den}) metadata_denominator
expression_div_{label} = NExprBinaryOpDiv expression_num_{label} expression_den_{label} metadata_cond
expression_base_{label} = NExprTernary expression_div_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_div_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}) :: (PCOCCURRENCE pcpath_cond expression_div_{label}) :: (PCOCCURRENCE pcpath_numerator expression_num_{label}) :: (PCOCCURRENCE pcpath_denominator expression_den_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT {value})) :: (PCONSTANT pcpath_numerator (PINT {num})) :: (PCONSTANT pcpath_denominator (PINT {den})) :: ppool.CONSTANTS]]]
$compiled_read(S_div_{label},porigin_cond) = (PINT {value})
$string_read_raw_unary_integer(S_div_{label},porigin_cond,{value}) = {str(accepted).lower()}
''')
        if accepted:
            selected = 'pkeyread.BASE' if result else 'pvalue_wrong'
            checks += [f'$binary_apply(S_div_{label},DIVIDE,PINT {num},PINT {den},0) = S_div_{label}[.RESULT = KNOWN (PINT {value})]',
                       f'$string_read_raw_known_base(S_div_{label},porigin_base,{selected})']
        else:
            checks += [f'~$string_read_raw_known_base(S_div_{label},porigin_base,{value})'
                       for value in ('pkeyread.BASE', 'pvalue_wrong')]
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
