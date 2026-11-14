"""Completed finite FLOAT powers retain exact bits and the frozen raw offset."""

from string_offset_float_conditional_base_initial_raw_leading_key_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpPow expression_decimal_power expression_false_power metadata_cond)')
    old_hex = '  -- if n_cond = $hex_bits(text_cond,0)\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '')
    count -= 1
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpPow expression_decimal_power expression_false_power metadata_cond)
expression_decimal_power = NScalarString (BYTES text_decimal_power) metadata_decimal_power
expression_false_power = NExprConstFetch (NName (BYTES text_false_power) metadata_false_name_power) metadata_false_power
$base64(text_decimal_power) = $ptascii("2.0")
$ptlc($base64(text_false_power)) = $ptascii("false")
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_decimal_power)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_false_power)
''')
    for name, value in (('decimal', 'PSTRING ($ptascii("2.0"))'), ('false', 'PBOOL false')):
        checks += lines(f'''
$origin_node(S_capture.SOURCES,porigin_{name}_power) = (expression_{name}_power)
$compiled_read(S_capture,porigin_{name}_power) = ({value})
$string_read_raw_truth(S_capture,porigin_{name}_power,{value})
porigin_{name}_power = PORIGIN n_unit pcpath_{name}_power
''')
    checks += lines(r'''
$origin_child((porigin_false_power),[PCFIELD 0]) = (porigin_false_name_power)
$origin_node(S_capture.SOURCES,porigin_false_name_power) = (NName (BYTES text_false_power) metadata_false_name_power)
porigin_false_name_power = PORIGIN n_unit pcpath_false_name_power
$coerce_number(PSTRING ($ptascii("2.0"))) = COERCED (NFLOAT 4611686018427387904) false
$coerce_number(PBOOL false) = COERCED (NINT 0) false
$power_prepare(NFLOAT 4611686018427387904,NINT 0) = POWERDONE (NFLOAT n_cond) false
$binary_apply(S_capture,POWER,PSTRING ($ptascii("2.0")),PBOOL false,0) = S_capture[.RESULT = KNOWN (PFLOAT n_cond)]
$string_read_raw_truth(S_capture,porigin_cond,PFLOAT n_cond)
S_budget_power = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_budget_power,porigin_cond,PFLOAT n_cond)
$string_read_raw_known_base(S_budget_power,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own_bits', 'pcpath_cond', 'PFLOAT 0'), ('own_tag', 'pcpath_cond', 'PINT 1'),
            ('decimal_bytes', 'pcpath_decimal_power', 'PSTRING ($ptascii("3.0"))'),
            ('decimal_tag', 'pcpath_decimal_power', 'PFLOAT 4611686018427387904'),
            ('false_null', 'pcpath_false_power', 'PNULL'), ('false_int', 'pcpath_false_power', 'PINT 0')):
        own = value if path == 'pcpath_cond' else 'PFLOAT n_cond'
        checks += [f'S_bad_power_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_power_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_power_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('root', 'pcpath_cond', 'NExprBinaryOpPow expression_decimal_power expression_false_power eps'),
            ('decimal', 'pcpath_decimal_power', 'NScalarString (BYTES text_decimal_power) eps'),
            ('name', 'pcpath_false_name_power', 'NName (BYTES text_false_power) eps')):
        checks += [f'S_bad_power_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'{"" if label == "root" else "~"}$string_read_raw_truth(S_bad_power_{label}_source,porigin_cond,PFLOAT n_cond)',
                   f'~$string_read_raw_known_base(S_bad_power_{label}_source,porigin_base,pkeyread.BASE)']
    for label, left_node, right_node, left_value, right_value, bits in (
            ('general', 'NScalarFloat (FLOAT "4000000000000000") metadata_decimal_power', 'NScalarInt (INTEGER 3) metadata_false_power', 'PFLOAT 4611686018427387904', 'PINT 3', 4620693217682128896),
            ('integer_result', 'NScalarInt (INTEGER 2) metadata_decimal_power', 'NScalarInt (INTEGER 0) metadata_false_power', 'PINT 2', 'PINT 0', 4607182418800017408),
            ('infinite_child', 'NScalarFloat (FLOAT "7ff0000000000000") metadata_decimal_power', 'NScalarInt (INTEGER 0) metadata_false_power', 'PFLOAT 9218868437227405312', 'PINT 0', 4607182418800017408),
            ('nan_child', 'NScalarFloat (FLOAT "7ff8000000000000") metadata_decimal_power', 'NScalarInt (INTEGER 0) metadata_false_power', 'PFLOAT 9221120237041090560', 'PINT 0', 4607182418800017408),
            ('leading_numeric', 'NScalarString (BYTES "Mi4weA==") metadata_decimal_power', 'NScalarInt (INTEGER 0) metadata_false_power', 'PSTRING ($ptascii("2.0x"))', 'PINT 0', 4607182418800017408)):
        checks += lines(f'''
expression_{label}_power_left = {left_node}
expression_{label}_power_right = {right_node}
expression_{label}_power = NExprBinaryOpPow expression_{label}_power_left expression_{label}_power_right metadata_cond
expression_{label}_power_base = NExprTernary expression_{label}_power (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_{label}_power = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_power_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_power) :: (PCOCCURRENCE pcpath_decimal_power expression_{label}_power_left) :: (PCOCCURRENCE pcpath_false_power expression_{label}_power_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT {bits})) :: (PCONSTANT pcpath_decimal_power ({left_value})) :: (PCONSTANT pcpath_false_power ({right_value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_{label}_power,porigin_cond,PFLOAT {bits})
~$string_read_raw_known_base(S_{label}_power,porigin_base,pkeyread.BASE)
''')
    checks += lines(r'''
$power_prepare(NFLOAT 4611686018427387904,NINT 3) = POWERGENERAL n_factor_power n_ix_power n_y_power n_sign_power false
$power_prepare(NFLOAT 0,NINT $(-1)) = POWERDONE (NFLOAT 9218868437227405312) true
S_general_budget_power = S_general_power[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 4620693217682128896)]
~$string_read_raw_truth(S_general_budget_power,porigin_cond,PFLOAT 4620693217682128896)
~$string_read_raw_known_base(S_general_budget_power,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
