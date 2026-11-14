"""Quiet integer trees preserve the false base through initial-key reference rebinding."""

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary expression_actual_condition')
    early = lines(r'''
porigin_actual_condition = porigin_left
$origin_node(S_capture.SOURCES,porigin_left) = (expression_actual_condition)
expression_actual_condition = NExprBinaryOpBitwiseOr expression_actual_left expression_actual_right metadata_cond
expression_actual_left = NExprBinaryOpShiftLeft expression_actual_maximum expression_actual_left_count metadata_actual_left
expression_actual_right = NExprBinaryOpBitwiseXor expression_actual_shift expression_actual_right_negative metadata_actual_right
expression_actual_shift = NExprBinaryOpShiftRight expression_actual_left_negative expression_actual_right_count metadata_actual_shift
expression_actual_left_negative = NExprUnaryMinus expression_actual_left_one metadata_actual_left_negative
expression_actual_right_negative = NExprUnaryMinus expression_actual_right_one metadata_actual_right_negative
expression_actual_maximum = NScalarInt (INTEGER 9223372036854775807) metadata_actual_maximum
expression_actual_left_count = NScalarInt (INTEGER 64) metadata_actual_left_count
expression_actual_right_count = NScalarInt (INTEGER 64) metadata_actual_right_count
expression_actual_left_one = NScalarInt (INTEGER 1) metadata_actual_left_one
expression_actual_right_one = NScalarInt (INTEGER 1) metadata_actual_right_one
''')
    for parent, index, child, value in (
            ('condition', 0, 'left', 0), ('condition', 1, 'right', 0),
            ('left', 0, 'maximum', 9223372036854775807), ('left', 1, 'left_count', 64),
            ('right', 0, 'shift', -1), ('right', 1, 'right_negative', -1),
            ('shift', 0, 'left_negative', -1), ('shift', 1, 'right_count', 64),
            ('left_negative', 0, 'left_one', 1), ('right_negative', 0, 'right_one', 1)):
        value = str(value) if value >= 0 else f'$({value})'
        early += lines(f'''
$origin_child((porigin_actual_{parent}),[PCFIELD {index}]) = (porigin_actual_{child})
$origin_node(S_capture.SOURCES,porigin_actual_{child}) = (expression_actual_{child})
$compiled_read(S_capture,porigin_actual_{child}) = (PINT {value})
''')
    early += lines(r'''
$binary_apply(S_capture,SHIFTLEFT,PINT 9223372036854775807,PINT 64,0) = S_capture[.RESULT = KNOWN (PINT 0)]
$unary_apply(S_capture,NEGATIVE,PINT 1,0) = S_capture[.RESULT = KNOWN (PINT $(-1))]
$binary_apply(S_capture,SHIFTRIGHT,PINT $(-1),PINT 64,0) = S_capture[.RESULT = KNOWN (PINT $(-1))]
$binary_apply(S_capture,BITXOR,PINT $(-1),PINT $(-1),0) = S_capture[.RESULT = KNOWN (PINT 0)]
$binary_apply(S_capture,BITOR,PINT 0,PINT 0,0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_unary_integer(S_capture,porigin_left,0)
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + x + '\n' for x in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_actual_left = PORIGIN n_unit pcpath_actual_left
porigin_actual_right = PORIGIN n_unit pcpath_actual_right
porigin_actual_maximum = PORIGIN n_unit pcpath_actual_maximum
porigin_actual_left_count = PORIGIN n_unit pcpath_actual_left_count
porigin_actual_shift = PORIGIN n_unit pcpath_actual_shift
porigin_actual_left_one = PORIGIN n_unit pcpath_actual_left_one
S_budget_group = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget_group,porigin_left,PINT 0)
$string_read_raw_known_base(S_budget_group,porigin_base,pvalue_base)
S_precision_group = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_precision_group,porigin_base,pvalue_base)
S_shorthand_group = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary expression_actual_condition ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_group,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_group,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PINT 1'), ('own_type', 'pcpath_left', 'PFLOAT 0'),
            ('left', 'pcpath_actual_left', 'PINT 1'), ('right', 'pcpath_actual_right', 'PINT 1'),
            ('shift', 'pcpath_actual_shift', 'PINT 0'),
            ('maximum', 'pcpath_actual_maximum', 'PINT 9223372036854775806'),
            ('count', 'pcpath_actual_left_count', 'PINT 65'), ('one', 'pcpath_actual_left_one', 'PINT 2')):
        result = value if label in ('own', 'own_type') else 'PINT 0'
        checks += lines(f'''
S_pool_group_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_pool_group_{label},porigin_left,{result})
~$string_read_raw_known_base(S_pool_group_{label},porigin_base,pvalue_base)
''')
    for label, path, node in (
            ('left', 'pcpath_actual_left', 'NExprBinaryOpShiftLeft expression_actual_maximum expression_actual_left_count eps'),
            ('right', 'pcpath_actual_right', 'NExprBinaryOpBitwiseXor expression_actual_shift expression_actual_right_negative eps'),
            ('maximum', 'pcpath_actual_maximum', 'NScalarInt (INTEGER 9223372036854775807) eps')):
        checks += lines(f'''
S_source_group_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_source_group_{label},porigin_left,PINT 0)
~$string_read_raw_known_base(S_source_group_{label},porigin_base,pvalue_base)
''')
    # Negative and extreme raw leaves below are constructed controls, with source0.
    for label, constructor, operator, left, right, result, accepted in (
            ('mod', 'Mod', 'MODULO', 5, 2, 1, True),
            ('mod_negative', 'Mod', 'MODULO', -5, 2, -1, True),
            ('mod_min', 'Mod', 'MODULO', -9223372036854775808, -1, 0, True),
            ('mod_zero', 'Mod', 'MODULO', 1, 0, 0, False),
            ('shl_boundary', 'ShiftLeft', 'SHIFTLEFT', 1, 63, -9223372036854775808, True),
            ('shl_wide', 'ShiftLeft', 'SHIFTLEFT', 1, 64, 0, True),
            ('shl_wrap', 'ShiftLeft', 'SHIFTLEFT', -9223372036854775808, 1, 0, True),
            ('shl_negative', 'ShiftLeft', 'SHIFTLEFT', 1, -1, 0, False),
            ('shr_boundary', 'ShiftRight', 'SHIFTRIGHT', -9223372036854775808, 63, -1, True),
            ('shr_wide', 'ShiftRight', 'SHIFTRIGHT', -1, 64, -1, True),
            ('shr_zero', 'ShiftRight', 'SHIFTRIGHT', 1, 64, 0, True),
            ('shr_negative', 'ShiftRight', 'SHIFTRIGHT', 1, -1, 0, False),
            ('and', 'BitwiseAnd', 'BITAND', -9223372036854775808, 9223372036854775807, 0, True),
            ('or', 'BitwiseOr', 'BITOR', -9223372036854775808, 9223372036854775807, -1, True),
            ('xor', 'BitwiseXor', 'BITXOR', -9223372036854775808, -1, 9223372036854775807, True),
            ('power', 'Pow', 'POWER', 2, 1, 2, True),
            ('power_boundary', 'Pow', 'POWER', -2, 63, -9223372036854775808, True),
            ('power_zero', 'Pow', 'POWER', 0, 0, 1, True),
            ('power_overflow', 'Pow', 'POWER', 2, 63, 0, False),
            ('power_negative', 'Pow', 'POWER', 2, -1, 0, False),
            ('power_unit_negative', 'Pow', 'POWER', 1, -1, 1, False),
            ('power_zero_negative', 'Pow', 'POWER', 0, -1, 0, False),
            ('power_child_range', 'Pow', 'POWER', 9223372036854775808, 0, 1, False),
            ('old_divide', 'Div', 'DIVIDE', 4, 2, 2, True)):
        selected = 'pvalue_base' if result == 0 else 'pvalue_wrong'
        l, r, value = (str(n) if n >= 0 else f'$({n})' for n in (left, right, result))
        checks += lines(f'''
expression_projected_{label}_left = NScalarInt (INTEGER {l}) metadata_actual_left
expression_projected_{label}_right = NScalarInt (INTEGER {r}) metadata_actual_right
expression_projected_{label} = NExprBinaryOp{constructor} expression_projected_{label}_left expression_projected_{label}_right metadata_cond
expression_projected_{label}_base = NExprTernary expression_projected_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_projected_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_projected_{label}_base) :: (PCOCCURRENCE pcpath_left expression_projected_{label}) :: (PCOCCURRENCE pcpath_actual_left expression_projected_{label}_left) :: (PCOCCURRENCE pcpath_actual_right expression_projected_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT {value})) :: (PCONSTANT pcpath_actual_left (PINT {l})) :: (PCONSTANT pcpath_actual_right (PINT {r})) :: ppool.CONSTANTS]]]
$compiled_read(S_projected_{label},porigin_left) = (PINT {value})
{'' if accepted else '~'}$string_read_raw_unary_integer(S_projected_{label},porigin_left,{value})
{'' if accepted else '~'}$string_read_raw_truth(S_projected_{label},porigin_left,PINT {value})
''')
        if accepted:
            checks += [f'$binary_apply(S_projected_{label},{operator},PINT {l},PINT {r},0) = S_projected_{label}[.RESULT = KNOWN (PINT {value})]',
                       f'$string_read_raw_known_base(S_projected_{label},porigin_base,{selected})']
        else:
            checks += [f'~$string_read_raw_known_base(S_projected_{label},porigin_base,{base})'
                       for base in ('pvalue_base', 'pvalue_wrong')]
    for label, node, value in (
            ('float', 'NScalarFloat (FLOAT "0000000000000000")', 'PFLOAT 0'),
            ('string', 'NScalarString (BYTES "MA==")', 'PSTRING ($ptascii("0"))')):
        checks += lines(f'''
expression_typed_{label}_left = {node} metadata_actual_left
expression_typed_{label}_right = NScalarInt (INTEGER 0) metadata_actual_right
expression_typed_{label} = NExprBinaryOpBitwiseOr expression_typed_{label}_left expression_typed_{label}_right metadata_cond
expression_typed_{label}_base = NExprTernary expression_typed_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_typed_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_typed_{label}_base) :: (PCOCCURRENCE pcpath_left expression_typed_{label}) :: (PCOCCURRENCE pcpath_actual_left expression_typed_{label}_left) :: (PCOCCURRENCE pcpath_actual_right expression_typed_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 0)) :: (PCONSTANT pcpath_actual_left ({value})) :: (PCONSTANT pcpath_actual_right (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_typed_{label},porigin_actual_left,{value})
~$string_read_raw_truth(S_typed_{label},porigin_left,PINT 0)
~$string_read_raw_known_base(S_typed_{label},porigin_base,pvalue_base)
''')
    checks += lines(r'''
expression_shared_power_left = NScalarInt (INTEGER 2) metadata_actual_maximum
expression_shared_power_right = NScalarInt (INTEGER 1) metadata_actual_left_count
expression_shared_power = NExprBinaryOpPow expression_shared_power_left expression_shared_power_right metadata_actual_left
expression_shared_not = NExprBooleanNot expression_shared_power metadata_cond
expression_shared_not_base = NExprTernary expression_shared_not ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_shared_not = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_shared_not_base) :: (PCOCCURRENCE pcpath_left expression_shared_not) :: (PCOCCURRENCE pcpath_actual_left expression_shared_power) :: (PCOCCURRENCE pcpath_actual_maximum expression_shared_power_left) :: (PCOCCURRENCE pcpath_actual_left_count expression_shared_power_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: (PCONSTANT pcpath_actual_left (PINT 2)) :: (PCONSTANT pcpath_actual_maximum (PINT 2)) :: (PCONSTANT pcpath_actual_left_count (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_raw_unary_integer(S_shared_not,porigin_actual_left,2)
$string_read_raw_truth(S_shared_not,porigin_left,PBOOL false)
$string_read_raw_known_base(S_shared_not,porigin_base,pvalue_base)
S_shared_not.POOLS = [ppool_shared]
S_shared_wrong_not = S_shared_not[.POOLS = [ppool_shared[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL true)) :: ppool_shared.CONSTANTS]]]
~$string_read_raw_truth(S_shared_wrong_not,porigin_left,PBOOL true)
~$string_read_raw_known_base(S_shared_wrong_not,porigin_base,pvalue_base)
$origin_child((porigin_actual_maximum),[PCFIELD 0]) = (porigin_shared_power_left)
$origin_child((porigin_actual_maximum),[PCFIELD 1]) = (porigin_shared_power_right)
porigin_shared_power_left = PORIGIN n_unit pcpath_shared_power_left
porigin_shared_power_right = PORIGIN n_unit pcpath_shared_power_right
expression_shared_positive = NExprUnaryPlus expression_shared_power metadata_actual_left
expression_shared_signed_not = NExprBooleanNot expression_shared_positive metadata_cond
expression_shared_signed_base = NExprTernary expression_shared_signed_not ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_shared_signed = S_shared_not[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_shared_signed_base) :: (PCOCCURRENCE pcpath_left expression_shared_signed_not) :: (PCOCCURRENCE pcpath_actual_left expression_shared_positive) :: (PCOCCURRENCE pcpath_actual_maximum expression_shared_power) :: (PCOCCURRENCE pcpath_shared_power_left expression_shared_power_left) :: (PCOCCURRENCE pcpath_shared_power_right expression_shared_power_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool_shared[.CONSTANTS = (PCONSTANT pcpath_actual_maximum (PINT 2)) :: (PCONSTANT pcpath_shared_power_left (PINT 2)) :: (PCONSTANT pcpath_shared_power_right (PINT 1)) :: ppool_shared.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_shared_power_left 18 true) :: (CODEEXPR pcpath_shared_power_right 18 true) :: pcode.EXPRESSIONS]]]
$string_read_raw_unary_integer(S_shared_signed,porigin_actual_left,2)
$string_read_raw_truth(S_shared_signed,porigin_left,PBOOL false)
$string_read_raw_known_base(S_shared_signed,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
