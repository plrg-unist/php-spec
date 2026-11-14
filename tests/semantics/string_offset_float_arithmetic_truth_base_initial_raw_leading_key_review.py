"""Finite FLOAT-only arithmetic authenticates full-ternary selected headers."""

from string_offset_float_conditional_base_initial_raw_leading_key_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMul expression_sum_arithmetic expression_quotient_arithmetic metadata_cond)')
    old_hex = '  -- if n_cond = $hex_bits(text_cond,0)\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '')
    count -= 1  # The condition is an actual arithmetic tree, not a raw atom.
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_condition_arithmetic)
expression_condition_arithmetic = NExprBinaryOpMul expression_sum_arithmetic expression_quotient_arithmetic metadata_cond
expression_sum_arithmetic = NExprBinaryOpPlus expression_half_left expression_half_right metadata_sum_arithmetic
expression_quotient_arithmetic = NExprBinaryOpDiv expression_two_left expression_two_right metadata_quotient_arithmetic
expression_half_left = NScalarFloat (FLOAT text_half_left) metadata_half_left
expression_half_right = NScalarFloat (FLOAT text_half_right) metadata_half_right
expression_two_left = NScalarFloat (FLOAT text_two_left) metadata_two_left
expression_two_right = NScalarFloat (FLOAT text_two_right) metadata_two_right
$hex_bits(text_half_left,0) = 4602678819172646912
$hex_bits(text_half_right,0) = 4602678819172646912
$hex_bits(text_two_left,0) = 4611686018427387904
$hex_bits(text_two_right,0) = 4611686018427387904
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_sum_arithmetic)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_quotient_arithmetic)
$origin_child((porigin_sum_arithmetic),[PCFIELD 0]) = (porigin_half_left)
$origin_child((porigin_sum_arithmetic),[PCFIELD 1]) = (porigin_half_right)
$origin_child((porigin_quotient_arithmetic),[PCFIELD 0]) = (porigin_two_left)
$origin_child((porigin_quotient_arithmetic),[PCFIELD 1]) = (porigin_two_right)
$origin_node(S_capture.SOURCES,porigin_sum_arithmetic) = (expression_sum_arithmetic)
$origin_node(S_capture.SOURCES,porigin_quotient_arithmetic) = (expression_quotient_arithmetic)
$origin_node(S_capture.SOURCES,porigin_half_left) = (expression_half_left)
$origin_node(S_capture.SOURCES,porigin_half_right) = (expression_half_right)
$origin_node(S_capture.SOURCES,porigin_two_left) = (expression_two_left)
$origin_node(S_capture.SOURCES,porigin_two_right) = (expression_two_right)
$compiled_read(S_capture,porigin_sum_arithmetic) = (PFLOAT n_cond)
$compiled_read(S_capture,porigin_quotient_arithmetic) = (PFLOAT n_cond)
$compiled_read(S_capture,porigin_half_left) = (PFLOAT 4602678819172646912)
$compiled_read(S_capture,porigin_half_right) = (PFLOAT 4602678819172646912)
$compiled_read(S_capture,porigin_two_left) = (PFLOAT 4611686018427387904)
$compiled_read(S_capture,porigin_two_right) = (PFLOAT 4611686018427387904)
$string_read_raw_truth(S_capture,porigin_sum_arithmetic,PFLOAT n_cond)
$string_read_raw_truth(S_capture,porigin_quotient_arithmetic,PFLOAT n_cond)
$string_read_raw_truth(S_capture,porigin_cond,PFLOAT n_cond)
$binary_apply(S_capture,ADD,PFLOAT 4602678819172646912,PFLOAT 4602678819172646912,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$binary_apply(S_capture,DIVIDE,PFLOAT 4611686018427387904,PFLOAT 4611686018427387904,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$binary_apply(S_capture,MULTIPLY,PFLOAT n_cond,PFLOAT n_cond,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
porigin_sum_arithmetic = PORIGIN n_unit pcpath_sum_arithmetic
porigin_quotient_arithmetic = PORIGIN n_unit pcpath_quotient_arithmetic
porigin_half_left = PORIGIN n_unit pcpath_half_left
S_budget_arithmetic = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget_arithmetic,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_budget_arithmetic,porigin_base,pkeyread.BASE)
S_precision_arithmetic = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond 17) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_precision_arithmetic,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_precision_arithmetic,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PFLOAT 0'),
            ('left', 'pcpath_sum_arithmetic', 'PFLOAT 0'),
            ('right', 'pcpath_quotient_arithmetic', 'PFLOAT 0'),
            ('type', 'pcpath_sum_arithmetic', 'PINT 1')):
        checks += lines(f'''
S_pool_{label}_arithmetic = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_pool_{label}_arithmetic,porigin_cond,{value if label == 'own' else 'PFLOAT n_cond'})
~$string_read_raw_known_base(S_pool_{label}_arithmetic,porigin_base,pkeyread.BASE)
''')
    for label, path, node in (
            ('left', 'pcpath_sum_arithmetic', 'NExprBinaryOpPlus expression_half_left expression_half_right eps'),
            ('right', 'pcpath_quotient_arithmetic', 'NExprBinaryOpDiv expression_two_left expression_two_right eps'),
            ('leaf', 'pcpath_half_left', 'NScalarFloat (FLOAT text_half_left) eps')):
        checks += lines(f'''
S_metadata_{label}_arithmetic = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_metadata_{label}_arithmetic,porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_metadata_{label}_arithmetic,porigin_base,pkeyread.BASE)
''')
    for label, constructor, left_text, left_bits, right_text, right_bits in (
            ('zero_division', 'NExprBinaryOpDiv', '3ff0000000000000', 4607182418800017408, '0000000000000000', 0),
            ('overflow', 'NExprBinaryOpMul', '7fefffffffffffff', 9218868437227405311, '4000000000000000', 4611686018427387904)):
        checks += lines(f'''
expression_bad_left_{label} = NScalarFloat (FLOAT "{left_text}") metadata_sum_arithmetic
expression_bad_right_{label} = NScalarFloat (FLOAT "{right_text}") metadata_quotient_arithmetic
expression_bad_{label} = {constructor} expression_bad_left_{label} expression_bad_right_{label} metadata_cond
expression_bad_base_{label} = NExprTernary expression_bad_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_bad_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bad_base_{label}) :: (PCOCCURRENCE pcpath_cond expression_bad_{label}) :: (PCOCCURRENCE pcpath_sum_arithmetic expression_bad_left_{label}) :: (PCOCCURRENCE pcpath_quotient_arithmetic expression_bad_right_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT n_cond)) :: (PCONSTANT pcpath_sum_arithmetic (PFLOAT {left_bits})) :: (PCONSTANT pcpath_quotient_arithmetic (PFLOAT {right_bits})) :: ppool.CONSTANTS]]]
$compiled_read(S_bad_{label},porigin_cond) = (PFLOAT n_cond)
$string_read_raw_truth(S_bad_{label},porigin_sum_arithmetic,PFLOAT {left_bits})
$string_read_raw_truth(S_bad_{label},porigin_quotient_arithmetic,PFLOAT {right_bits})
~$string_read_raw_truth(S_bad_{label},porigin_cond,PFLOAT n_cond)
~$string_read_raw_known_base(S_bad_{label},porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
