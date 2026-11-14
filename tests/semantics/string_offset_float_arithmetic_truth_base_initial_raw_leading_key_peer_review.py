"""Finite FLOAT arithmetic keeps the false arm across raw-key reference rebinding."""

from string_offset_float_conditional_base_initial_raw_leading_key_peer_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMinus expression_float_left expression_float_right metadata_cond)')
    old_hex = '  -- if $hex_bits(text_cond,0) = 0\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '')
    count -= 1  # The actual condition is a SUBTRACT tree, not a raw FLOAT atom.
    early = lines(r'''
$origin_node(S_capture.SOURCES,porigin_left) = (NExprBinaryOpMinus expression_float_left expression_float_right metadata_cond)
expression_float_left = NScalarFloat (FLOAT text_float_left) metadata_float_left
expression_float_right = NScalarFloat (FLOAT text_float_right) metadata_float_right
$hex_bits(text_float_left,0) = 4602678819172646912
$hex_bits(text_float_right,0) = 4602678819172646912
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_float_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_float_right)
$origin_node(S_capture.SOURCES,porigin_float_left) = (expression_float_left)
$origin_node(S_capture.SOURCES,porigin_float_right) = (expression_float_right)
$compiled_read(S_capture,porigin_float_left) = (PFLOAT 4602678819172646912)
$compiled_read(S_capture,porigin_float_right) = (PFLOAT 4602678819172646912)
$string_read_raw_truth(S_capture,porigin_left,PFLOAT 0)
$binary_apply(S_capture,SUBTRACT,PFLOAT 4602678819172646912,PFLOAT 4602678819172646912,0) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PFLOAT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + x + '\n' for x in early) + anchor)
    checks = lines(r'''
porigin_float_left = PORIGIN n_unit pcpath_float_left
porigin_float_right = PORIGIN n_unit pcpath_float_right
S_budget_arithmetic = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget_arithmetic,porigin_left,PFLOAT 0)
$string_read_raw_known_base(S_budget_arithmetic,porigin_base,pvalue_base)
S_precision_arithmetic = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_precision_arithmetic,porigin_left,PFLOAT 0)
$string_read_raw_known_base(S_precision_arithmetic,porigin_base,pvalue_base)
S_shorthand_arithmetic = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprBinaryOpMinus expression_float_left expression_float_right metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_arithmetic,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_arithmetic,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('signed_zero', 'pcpath_left', 'PFLOAT 9223372036854775808'),
            ('left_bits', 'pcpath_float_left', 'PFLOAT 0'),
            ('right_bits', 'pcpath_float_right', 'PFLOAT 0'),
            ('left_type', 'pcpath_float_left', 'PINT 0'),
            ('right_type', 'pcpath_float_right', 'PINT 0')):
        result = value if label == 'signed_zero' else 'PFLOAT 0'
        checks += lines(f'''
S_pool_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_pool_{label},porigin_left,{result})
~$string_read_raw_known_base(S_pool_{label},porigin_base,pvalue_base)
''')
    for label, path, node in (
            ('left_metadata', 'pcpath_float_left', 'NScalarFloat (FLOAT text_float_left) eps'),
            ('right_metadata', 'pcpath_float_right', 'NScalarFloat (FLOAT text_float_right) eps'),
            ('left_position', 'pcpath_float_left', 'expression_float_right'),
            ('right_position', 'pcpath_float_right', 'expression_float_left')):
        checks += lines(f'''
S_source_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_source_{label},porigin_left,PFLOAT 0)
~$string_read_raw_known_base(S_source_{label},porigin_base,pvalue_base)
''')
    # Each constructed projection keeps exact parent/child nodes and own pools.
    fhalf = ('NScalarFloat (FLOAT "3fe0000000000000")', 'PFLOAT 4602678819172646912')
    fzero = ('NScalarFloat (FLOAT "0000000000000000")', 'PFLOAT 0')
    fnegativezero = ('NScalarFloat (FLOAT "8000000000000000")', 'PFLOAT 9223372036854775808')
    ftwo = ('NScalarFloat (FLOAT "4000000000000000")', 'PFLOAT 4611686018427387904')
    fmax = ('NScalarFloat (FLOAT "7fefffffffffffff")', 'PFLOAT 9218868437227405311')
    finfinity = ('NScalarFloat (FLOAT "7ff0000000000000")', 'PFLOAT 9218868437227405312')
    fnan = ('NScalarFloat (FLOAT "7ff8000000000000")', 'PFLOAT 9221120237041090560')
    for label, constructor, left, right, bits, accepted in (
            ('add', 'NExprBinaryOpPlus', fhalf, fhalf, 4607182418800017408, True),
            ('multiply_negative_zero', 'NExprBinaryOpMul', fnegativezero, ftwo, 9223372036854775808, True),
            ('divide_negative_zero', 'NExprBinaryOpDiv', fnegativezero, ftwo, 9223372036854775808, True),
            ('mixed_int', 'NExprBinaryOpPlus', ('NScalarInt (INTEGER 0)', 'PINT 0'), fzero, 0, True),
            ('numeric_string', 'NExprBinaryOpPlus', ('NScalarString (BYTES "MA==")', 'PSTRING ($ptascii("0"))'), fzero, 0, False),
            ('leading_string', 'NExprBinaryOpPlus', ('NScalarString (BYTES "MHg=")', 'PSTRING ($ptascii("0x"))'), fzero, 0, False),
            ('integer_promotion', 'NExprBinaryOpPlus', ('NScalarInt (INTEGER 9223372036854775807)', 'PINT 9223372036854775807'), ('NScalarInt (INTEGER 1)', 'PINT 1'), 4890909195324358656, True),
            ('division_zero', 'NExprBinaryOpDiv', fhalf, fzero, 0, False),
            ('forged_overflow', 'NExprBinaryOpMul', fmax, ftwo, 0, False),
            ('actual_overflow', 'NExprBinaryOpMul', fmax, ftwo, 9218868437227405312, False),
            ('infinite_child', 'NExprBinaryOpMul', finfinity, fzero, 0, False),
            ('nan_child', 'NExprBinaryOpPlus', fnan, fzero, 0, False),
            ('power', 'NExprBinaryOpPow', fhalf, ftwo, 4598175219545276416, False)):
        checks += lines(f'''
expression_{label}_left = {left[0]} metadata_float_left
expression_{label}_right = {right[0]} metadata_float_right
expression_{label} = {constructor} expression_{label}_left expression_{label}_right metadata_cond
expression_{label}_base = NExprTernary expression_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_left expression_{label}) :: (PCOCCURRENCE pcpath_float_left expression_{label}_left) :: (PCOCCURRENCE pcpath_float_right expression_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PFLOAT {bits})) :: (PCONSTANT pcpath_float_left ({left[1]})) :: (PCONSTANT pcpath_float_right ({right[1]})) :: ppool.CONSTANTS]]]
$compiled_read(S_{label},porigin_left) = (PFLOAT {bits})
$compiled_read(S_{label},porigin_float_left) = ({left[1]})
$compiled_read(S_{label},porigin_float_right) = ({right[1]})
{'' if accepted else '~'}$string_read_raw_truth(S_{label},porigin_left,PFLOAT {bits})
''')
        if accepted:
            selected = 'pvalue_wrong' if label in ('add', 'integer_promotion') else 'pvalue_base'
            checks.append(f'$string_read_raw_known_base(S_{label},porigin_base,{selected})')
        else:
            checks += [f'~$string_read_raw_known_base(S_{label},porigin_base,{value})'
                       for value in ('pvalue_base', 'pvalue_wrong')]
    checks += lines(r'''
$origin_child((porigin_float_left),[PCFIELD 0]) = (porigin_not_half_left)
$origin_child((porigin_float_left),[PCFIELD 1]) = (porigin_not_half_right)
porigin_not_half_left = PORIGIN n_unit pcpath_not_half_left
porigin_not_half_right = PORIGIN n_unit pcpath_not_half_right
expression_not_sum = NExprBinaryOpPlus expression_float_left expression_float_right metadata_float_left
expression_not = NExprBooleanNot expression_not_sum metadata_cond
expression_not_base = NExprTernary expression_not ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_not = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_not_base) :: (PCOCCURRENCE pcpath_left expression_not) :: (PCOCCURRENCE pcpath_float_left expression_not_sum) :: (PCOCCURRENCE pcpath_not_half_left expression_float_left) :: (PCOCCURRENCE pcpath_not_half_right expression_float_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = [PCONSTANT pcpath_float_left (PFLOAT 4607182418800017408),PCONSTANT pcpath_not_half_left (PFLOAT 4602678819172646912),PCONSTANT pcpath_not_half_right (PFLOAT 4602678819172646912),PCONSTANT pcpath_right (PSTRING ($ptascii("abc"))),PCCPRECISION pcpath_left 14,PCCPRECISION pcpath_float_left 14,PCCPRECISION pcpath_not_half_left 14,PCCPRECISION pcpath_not_half_right 14,PCCPRECISION pcpath_right 14]]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: (CODEEXPR pcpath_float_left 18 true) :: (CODEEXPR pcpath_not_half_left 18 true) :: (CODEEXPR pcpath_not_half_right 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_not,porigin_left) = eps
$string_read_raw_truth(S_not,porigin_float_left,PFLOAT 4607182418800017408)
~$string_read_raw_truth(S_not,porigin_left,PBOOL false)
$string_read_runtime_value(S_not,porigin_float_left) = (PFLOAT 4607182418800017408)
$string_read_runtime_value(S_not,porigin_left) = (PBOOL false)
$string_read_raw_known_base(S_not,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_not[.CODE = eps],porigin_base,pvalue_base)
S_not.POOLS = [ppool_not]
S_not_precision = S_not[.POOLS = [ppool_not[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool_not.CONSTANTS]]]
~$string_read_raw_known_base(S_not_precision,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    added = len(early) + len(checks)
    return body, count + added, derived + len(checks)
