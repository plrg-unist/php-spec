"""Reached raw-FLOAT arithmetic trees retain exact one-row RHS allocation."""

import string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_review as minus
from string_offset_retained_carrier_protocol import lines


def arithmetic_tree(text, reference):
    before = 'NExprUnaryMinus (NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_right_number'
    if reference:
        expression = ('NExprBinaryOpDiv '
            '(NExprBinaryOpMinus '
            '(NExprBinaryOpPlus '
            '(NExprCastDouble (NExprUnaryMinus (NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_negative) metadata_cast_left) '
            '(NScalarFloat (FLOAT "0000000000000000") metadata_add_zero) metadata_add) '
            '(NExprBinaryOpMul (NScalarFloat (FLOAT "0000000000000000") metadata_multiply_zero) '
            '(NScalarFloat (FLOAT "4000000000000000") metadata_two) metadata_multiply) metadata_subtract) '
            '(NExprCastDouble (NExprBinaryOpPlus (NScalarFloat (FLOAT "3ff0000000000000") metadata_one_left) '
            '(NScalarFloat (FLOAT "3ff0000000000000") metadata_one_right) metadata_divisor) metadata_cast_right) metadata_right_number')
        before_bits = 'text_right_bits = "4029000000000000"'
        assert text.count(before_bits) == 1
        text = text.replace(before_bits, 'text_right_bits = "4039000000000000"')
    else:
        expression = ('NExprCastDouble (NExprBinaryOpDiv '
            '(NExprBinaryOpMul '
            '(NExprBinaryOpMinus (NExprUnaryMinus (NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_negative) '
            '(NScalarFloat (FLOAT "0000000000000000") metadata_subtract_zero) metadata_subtract) '
            '(NExprUnaryPlus (NScalarFloat (FLOAT "4000000000000000") metadata_two) metadata_positive) metadata_multiply) '
            '(NExprBinaryOpPlus (NScalarFloat (FLOAT "3ff0000000000000") metadata_one_left) '
            '(NScalarFloat (FLOAT "3ff0000000000000") metadata_one_right) metadata_add) metadata_divide) metadata_right_number')
    assert text.count(before) == 1
    text = text.replace(before, expression)
    before_path = '$origin_child((porigin_right_number),[PCFIELD 0]) = (porigin_atom)'
    assert text.count(before_path) == 1
    text = text.replace(before_path,
        '$origin_child((porigin_right_number),[PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) = (porigin_atom)')
    before_code = '$code_expression(pcode.EXPRESSIONS,pcpath_right_number) = ((z_unary,true))'
    assert text.count(before_code) == 1
    text = text.replace(before_code, before_code.replace('true', 'false'))
    bits = 13846598529327300608 if reference else 9223372036854775808
    before_read = f'$compiled_read(S_capture,porigin_right_number) = (PFLOAT {bits})'
    assert text.count(before_read) == 1
    return text.replace(before_read, '$compiled_read(S_capture,porigin_right_number) = eps')


def arithmetic_checks(reference):
    negative = 0xc039000000000000 if reference else 9223372036854775808
    result = 13846598529327300608 if reference else 9223372036854775808
    one = 4607182418800017408
    two = 4611686018427387904
    checks = [
        f'$binary_apply(S_capture,ADD,PFLOAT {one},PFLOAT {one},0) = S_capture[.RESULT = KNOWN (PFLOAT {two})]',
        f'$binary_apply(S_capture,SUBTRACT,PFLOAT {negative},PFLOAT 0,0) = S_capture[.RESULT = KNOWN (PFLOAT {negative})]',
        f'$cast_apply(S_capture,CASTFLOAT,PFLOAT {negative},0) = S_capture[.RESULT = KNOWN (PFLOAT {negative})]',
    ]
    if reference:
        checks += [
            f'$binary_apply(S_capture,ADD,PFLOAT {negative},PFLOAT 0,0) = S_capture[.RESULT = KNOWN (PFLOAT {negative})]',
            f'$binary_apply(S_capture,MULTIPLY,PFLOAT 0,PFLOAT {two},0) = S_capture[.RESULT = KNOWN (PFLOAT 0)]',
        ]
    else:
        checks += [f'$binary_apply(S_capture,MULTIPLY,PFLOAT {negative},PFLOAT {two},0) = S_capture[.RESULT = KNOWN (PFLOAT {negative})]']
    checks += [f'$binary_apply(S_capture,DIVIDE,PFLOAT {negative},PFLOAT {two},0) = S_capture[.RESULT = KNOWN (PFLOAT {result})]']
    return checks


def front(program, filename_b64, reference=False):
    prefix, checks = minus.front(program, filename_b64, reference=reference)
    return prefix, arithmetic_tree('\n'.join(checks), reference).splitlines() + arithmetic_checks(reference)


def render(program, filename_b64, reference=False):
    body, count, derived = minus.render(program, filename_b64, reference=reference)
    body = arithmetic_tree(body, reference)
    # Emitted roots ignore unused pools and retain their genuine child VALUE.
    before_pool = '~$string_read_allocated_value(S_number_pool,porigin_base,pvalue_base)'
    assert body.count(before_pool) == 1
    body = body.replace(before_pool, before_pool[1:])
    before_fold = '''S_unary_fold = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_number z_unary false) :: pcode.EXPRESSIONS]]]
  -- if $string_read_allocated_value(S_unary_fold,porigin_base,pvalue_base)
  -- if $string_read_plan(S_unary_fold) = (pstringread)'''
    assert body.count(before_fold) == 1
    body = body.replace(before_fold, before_fold.replace('z_unary false', 'z_unary true').replace(
        '  -- if $string_read_allocated_value', '  -- if ~$string_read_allocated_value').replace('= (pstringread)', '= eps'))
    checks = arithmetic_checks(reference) + lines(r'''
$string_read_raw_float_sign_tree(expression_right_number)
$string_read_raw_float_sign_tree(NExprUnaryPlus expression_right_number eps)
$string_read_raw_float_sign_tree(NExprUnaryMinus expression_right_number eps)
$string_read_raw_float_sign_tree(NExprCastDouble expression_right_number eps)
$string_read_raw_float_sign_tree(NExprBinaryOpPlus expression_right_number expression_right_number eps)
$string_read_raw_float_sign_tree(NExprCastDouble (NExprBinaryOpPlus expression_right_number expression_right_number eps) eps)
$compiled_read(S_number_pool,porigin_right_number) = eps
$string_read_runtime_value(S_number_pool,porigin_right_number) = $string_read_runtime_value(S_capture,porigin_right_number)
~$string_read_raw_float_sign_tree(NExprBinaryOpPow expression_right_number expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprCastInt expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprVariable (BYTES "a2V5") eps)
''')
    for constructor in ('NExprBinaryOpPlus', 'NExprBinaryOpMinus', 'NExprBinaryOpMul', 'NExprBinaryOpDiv'):
        checks += [
            f'$string_read_raw_float_sign_tree({constructor} expression_right_number expression_right_number eps)',
            f'~$string_read_raw_float_sign_tree({constructor} (NScalarInt (INTEGER 1) eps) expression_right_number eps)',
            f'~$string_read_raw_float_sign_tree({constructor} expression_right_number (NScalarString (BYTES "MQ==") eps) eps)',
        ]
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
