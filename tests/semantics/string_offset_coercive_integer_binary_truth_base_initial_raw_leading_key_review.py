"""Coercive integer binary trees preserve typed children and the frozen raw key."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpBitwiseXor expression_or_binary expression_mask_binary metadata_cond)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpBitwiseXor expression_or_binary expression_mask_binary metadata_cond)
expression_or_binary = NExprBinaryOpBitwiseOr expression_shift_binary expression_and_binary metadata_or_binary
expression_shift_binary = NExprBinaryOpShiftLeft expression_modulo_binary expression_count_binary metadata_shift_binary
expression_modulo_binary = NExprBinaryOpMod expression_add_binary expression_modulus_binary metadata_modulo_binary
expression_add_binary = NExprBinaryOpPlus expression_six_binary expression_false_binary metadata_add_binary
expression_and_binary = NExprBinaryOpBitwiseAnd expression_digit_binary expression_flag_binary metadata_and_binary
expression_six_binary = NScalarString (BYTES text_six_binary) metadata_six_binary
expression_false_binary = NExprConstFetch (NName (BYTES text_false_binary) metadata_false_name_binary) metadata_false_binary
expression_modulus_binary = NScalarString (BYTES text_modulus_binary) metadata_modulus_binary
expression_count_binary = NExprConstFetch (NName (BYTES text_count_binary) metadata_count_name_binary) metadata_count_binary
expression_digit_binary = NScalarString (BYTES text_digit_binary) metadata_digit_binary
expression_flag_binary = NExprConstFetch (NName (BYTES text_flag_binary) metadata_flag_name_binary) metadata_flag_binary
expression_mask_binary = NScalarInt (INTEGER 4) metadata_mask_binary
$base64(text_six_binary) = $ptascii("6")
$ptlc($base64(text_false_binary)) = $ptascii("false")
$base64(text_modulus_binary) = $ptascii("4")
$ptlc($base64(text_count_binary)) = $ptascii("true")
$base64(text_digit_binary) = $ptascii("1")
$ptlc($base64(text_flag_binary)) = $ptascii("true")
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for parent, field, child, value in (
            ('cond', 0, 'or', 'PINT 5'), ('cond', 1, 'mask', 'PINT 4'),
            ('or_binary', 0, 'shift', 'PINT 4'), ('or_binary', 1, 'and', 'PINT 1'),
            ('shift_binary', 0, 'modulo', 'PINT 2'), ('shift_binary', 1, 'count', 'PBOOL true'),
            ('modulo_binary', 0, 'add', 'PINT 6'), ('modulo_binary', 1, 'modulus', 'PSTRING ($ptascii("4"))'),
            ('add_binary', 0, 'six', 'PSTRING ($ptascii("6"))'), ('add_binary', 1, 'false', 'PBOOL false'),
            ('and_binary', 0, 'digit', 'PSTRING ($ptascii("1"))'), ('and_binary', 1, 'flag', 'PBOOL true')):
        checks += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_{child}_binary)',
                   f'$origin_node(S_capture.SOURCES,porigin_{child}_binary) = (expression_{child}_binary)',
                   f'$compiled_read(S_capture,porigin_{child}_binary) = ({value})',
                   f'$string_read_raw_truth(S_capture,porigin_{child}_binary,{value})',
                   f'porigin_{child}_binary = PORIGIN n_unit pcpath_{child}_binary']
    for name in ('false', 'count', 'flag'):
        checks += [f'$origin_child((porigin_{name}_binary),[PCFIELD 0]) = (porigin_{name}_name_binary)',
                   f'$origin_node(S_capture.SOURCES,porigin_{name}_name_binary) = (NName (BYTES text_{name}_binary) metadata_{name}_name_binary)',
                   f'porigin_{name}_name_binary = PORIGIN n_unit pcpath_{name}_name_binary']
    for operator, left, right, result in (
            ('MODULO', 'PINT 6', 'PSTRING ($ptascii("4"))', 2),
            ('SHIFTLEFT', 'PINT 2', 'PBOOL true', 4),
            ('BITAND', 'PSTRING ($ptascii("1"))', 'PBOOL true', 1),
            ('BITOR', 'PINT 4', 'PINT 1', 5), ('BITXOR', 'PINT 5', 'PINT 4', 1)):
        checks.append(f'$binary_apply(S_capture,{operator},{left},{right},0) = S_capture[.RESULT = KNOWN (PINT {result})]')
    checks += lines(r'''
~$string_read_raw_unary_integer(S_capture,porigin_cond,1)
$string_read_raw_truth(S_capture,porigin_cond,PINT 1)
S_budget_binary = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
$string_read_raw_truth(S_budget_binary,porigin_cond,PINT 1)
$string_read_raw_known_base(S_budget_binary,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PINT 0'), ('or', 'pcpath_or_binary', 'PINT 4'),
            ('modulo', 'pcpath_modulo_binary', 'PINT 0'),
            ('false_null', 'pcpath_false_binary', 'PNULL'),
            ('count_int', 'pcpath_count_binary', 'PINT 1'),
            ('and_float', 'pcpath_and_binary', 'PFLOAT 4607182418800017408'),
            ('mask', 'pcpath_mask_binary', 'PINT 5')):
        own = value if label == 'own' else 'PINT 1'
        checks += [f'S_bad_binary_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_binary_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_binary_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('or', 'pcpath_or_binary', 'NExprBinaryOpBitwiseOr expression_shift_binary expression_and_binary eps'),
            ('and', 'pcpath_and_binary', 'NExprBinaryOpBitwiseAnd expression_digit_binary expression_flag_binary eps'),
            ('false_name', 'pcpath_false_name_binary', 'NName (BYTES text_false_binary) eps')):
        checks += [f'S_bad_binary_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_binary_{label}_source,porigin_cond,PINT 1)',
                   f'~$string_read_raw_known_base(S_bad_binary_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_bad_binary_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_and_binary 12 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_binary_code,porigin_cond,PINT 1)
S_bad_binary_own_float = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 4607182418800017408)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_bad_binary_own_float,porigin_cond,PFLOAT 4607182418800017408)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
