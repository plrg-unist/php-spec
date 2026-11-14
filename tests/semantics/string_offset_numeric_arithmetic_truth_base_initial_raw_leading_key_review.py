"""Finite numeric arithmetic retains exact FLOAT truth and a frozen raw offset."""

from string_offset_float_conditional_base_initial_raw_leading_key_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMul expression_sum_numeric expression_one_numeric metadata_cond)')
    old_hex = '  -- if n_cond = $hex_bits(text_cond,0)\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '').replace('n_cond = 4607182418800017408', 'n_cond = 4890909195324358656')
    count -= 1
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpMul expression_sum_numeric expression_one_numeric metadata_cond)
expression_sum_numeric = NExprBinaryOpPlus expression_max_numeric expression_add_one_numeric metadata_sum_numeric
expression_max_numeric = NScalarInt (INTEGER 9223372036854775807) metadata_max_numeric
expression_add_one_numeric = NScalarInt (INTEGER 1) metadata_add_one_numeric
expression_one_numeric = NScalarInt (INTEGER 1) metadata_one_numeric
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_sum_numeric)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_one_numeric)
$origin_child((porigin_sum_numeric),[PCFIELD 0]) = (porigin_max_numeric)
$origin_child((porigin_sum_numeric),[PCFIELD 1]) = (porigin_add_one_numeric)
''')
    for name, value in (('sum', 'PFLOAT n_cond'), ('one', 'PINT 1'),
                        ('max', 'PINT 9223372036854775807'), ('add_one', 'PINT 1')):
        checks += lines(f'''
$origin_node(S_capture.SOURCES,porigin_{name}_numeric) = (expression_{name}_numeric)
$compiled_read(S_capture,porigin_{name}_numeric) = ({value})
$string_read_raw_truth(S_capture,porigin_{name}_numeric,{value})
porigin_{name}_numeric = PORIGIN n_unit pcpath_{name}_numeric
''')
    checks += lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
$binary_apply(S_capture,ADD,PINT 9223372036854775807,PINT 1,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$binary_apply(S_capture,MULTIPLY,PFLOAT n_cond,PINT 1,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$string_read_raw_truth(S_capture,porigin_cond,PFLOAT n_cond)
S_budget_numeric = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_budget_numeric,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_budget_numeric,porigin_base,pkeyread.BASE)
S_wrong_own_numeric = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT 9223372036854775807)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_wrong_own_numeric,porigin_cond,PINT 9223372036854775807)
~$string_read_raw_known_base(S_wrong_own_numeric,porigin_base,pkeyread.BASE)
S_wrong_child_numeric = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_sum_numeric (PFLOAT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_wrong_child_numeric,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_wrong_child_numeric,porigin_base,pkeyread.BASE)
S_wrong_source_numeric = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_sum_numeric (NExprBinaryOpPlus expression_max_numeric expression_add_one_numeric eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_wrong_source_numeric,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_wrong_source_numeric,porigin_base,pkeyread.BASE)
''')
    for label, constructor, left, right, bits, accepted in (
            ('fraction', 'Div', 1, 2, 4602678819172646912, True),
            ('exact_integer', 'Div', 4, 2, 4611686018427387904, False),
            ('integer_sum', 'Plus', 1, 1, 4611686018427387904, False),
            ('zero_divisor', 'Div', 1, 0, 0, False)):
        checks += lines(f'''
expression_projected_{label}_left = NScalarInt (INTEGER {left}) metadata_sum_numeric
expression_projected_{label}_right = NScalarInt (INTEGER {right}) metadata_one_numeric
expression_projected_{label} = NExprBinaryOp{constructor} expression_projected_{label}_left expression_projected_{label}_right metadata_cond
expression_projected_{label}_base = NExprTernary expression_projected_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_projected_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_projected_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_projected_{label}) :: (PCOCCURRENCE pcpath_sum_numeric expression_projected_{label}_left) :: (PCOCCURRENCE pcpath_one_numeric expression_projected_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT {bits})) :: (PCONSTANT pcpath_sum_numeric (PINT {left})) :: (PCONSTANT pcpath_one_numeric (PINT {right})) :: ppool.CONSTANTS]]]
{'' if accepted else '~'}$string_read_raw_truth(S_projected_{label},porigin_cond,PFLOAT {bits})
''')
        if accepted:
            checks += [f'$string_read_raw_known_base(S_projected_{label},porigin_base,pkeyread.BASE)']
        else:
            checks += [f'~$string_read_raw_known_base(S_projected_{label},porigin_base,{value})'
                       for value in ('pkeyread.BASE', 'pvalue_wrong')]
    checks += lines(r'''
S_zero_budget_numeric = S_projected_zero_divisor[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
~$string_read_raw_truth(S_zero_budget_numeric,porigin_cond,PFLOAT 0)
~$string_read_raw_known_base(S_zero_budget_numeric,porigin_base,pkeyread.BASE)
expression_nested_rhs_numeric = NScalarInt (INTEGER 0) metadata_max_numeric
expression_nested_zero_numeric = NExprBinaryOpDiv expression_add_one_numeric expression_nested_rhs_numeric metadata_sum_numeric
expression_nested_float_numeric = NScalarFloat (FLOAT "0000000000000000") metadata_one_numeric
expression_nested_root_numeric = NExprBinaryOpPlus expression_nested_zero_numeric expression_nested_float_numeric metadata_cond
expression_nested_base_numeric = NExprTernary expression_nested_root_numeric (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_nested_zero_numeric = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)][.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_nested_base_numeric) :: (PCOCCURRENCE pcpath_cond expression_nested_root_numeric) :: (PCOCCURRENCE pcpath_sum_numeric expression_nested_zero_numeric) :: (PCOCCURRENCE pcpath_max_numeric expression_add_one_numeric) :: (PCOCCURRENCE pcpath_add_one_numeric expression_nested_rhs_numeric) :: (PCOCCURRENCE pcpath_one_numeric expression_nested_float_numeric) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 4607182418800017408)) :: (PCONSTANT pcpath_sum_numeric (PINT 1)) :: (PCONSTANT pcpath_max_numeric (PINT 1)) :: (PCONSTANT pcpath_add_one_numeric (PINT 0)) :: (PCONSTANT pcpath_one_numeric (PFLOAT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_nested_zero_numeric,porigin_cond,PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_nested_zero_numeric,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
