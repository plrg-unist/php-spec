"""Nonnull FLOAT coalesce trees keep exact bits and one-row RHS allocation."""

import string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_review as minus
from string_offset_retained_carrier_protocol import lines


def coalesce_tree(text, reference):
    selected = ('NExprCastDouble (NExprUnaryMinus '
        '(NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_negative) metadata_rhs_selected')
    skipped = ('NExprCastDouble (NExprBinaryOpDiv '
        '(NScalarFloat (FLOAT "3ff0000000000000") metadata_rhs_skipped_one) '
        '(NScalarFloat (FLOAT "0000000000000000") metadata_rhs_skipped_zero) metadata_rhs_skipped_div) metadata_rhs_skipped')
    coalesce = f'NExprBinaryOpCoalesce ({selected}) ({skipped})'
    if reference:
        expression = ('NExprBinaryOpDiv (NExprBinaryOpPlus (NExprBinaryOpMinus '
            f'({coalesce} metadata_nn) '
            '(NExprBinaryOpMul (NScalarFloat (FLOAT "0000000000000000") metadata_product_zero) '
            '(NScalarFloat (FLOAT "4000000000000000") metadata_two) metadata_product) metadata_subtract) '
            '(NScalarFloat (FLOAT "0000000000000000") metadata_sum_zero) metadata_sum) '
            '(NExprCastDouble (NExprBinaryOpPlus (NScalarFloat (FLOAT "3ff0000000000000") metadata_one_left) '
            '(NScalarFloat (FLOAT "3ff0000000000000") metadata_one_right) metadata_divisor) metadata_divisor_cast) metadata_right_number')
        before_bits = 'text_right_bits = "4029000000000000"'
        assert text.count(before_bits) == 1
        text = text.replace(before_bits, 'text_right_bits = "4039000000000000"')
    else:
        expression = coalesce + ' metadata_right_number'
    before = 'NExprUnaryMinus (NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_right_number'
    assert text.count(before) == 1
    text = text.replace(before, expression)
    before_path = '$origin_child((porigin_right_number),[PCFIELD 0]) = (porigin_atom)'
    assert text.count(before_path) == 1
    path = ','.join(['PCFIELD 0'] * (6 if reference else 3))
    text = text.replace(before_path, f'$origin_child((porigin_right_number),[{path}]) = (porigin_atom)')
    before_code = '$code_expression(pcode.EXPRESSIONS,pcpath_right_number) = ((z_unary,true))'
    assert text.count(before_code) == 1
    text = text.replace(before_code, before_code.replace('true', 'false'))
    bits = 13846598529327300608 if reference else 9223372036854775808
    before_read = f'$compiled_read(S_capture,porigin_right_number) = (PFLOAT {bits})'
    assert text.count(before_read) == 1
    return text.replace(before_read, '$compiled_read(S_capture,porigin_right_number) = eps')


def coalesce_checks(reference):
    bits = 13851102128954671104 if reference else 9223372036854775808
    path = '[PCFIELD 0,PCFIELD 0,PCFIELD 0]' if reference else 'eps'
    return lines(f'''
$origin_child((porigin_right_number),{path}) = (porigin_nn)
$origin_node(S_capture.SOURCES,porigin_nn) = (NExprBinaryOpCoalesce expression_nn_left expression_nn_right metadata_nn_root)
$origin_child((porigin_nn),[PCFIELD 0]) = (porigin_nn_left)
$origin_child((porigin_nn),[PCFIELD 1]) = (porigin_nn_right)
$origin_node(S_capture.SOURCES,porigin_nn_left) = (expression_nn_left)
$origin_node(S_capture.SOURCES,porigin_nn_right) = (expression_nn_right)
expression_nn_right = NExprCastDouble expression_skipped_div metadata_nn_skipped
$origin_child((porigin_nn_right),[PCFIELD 0]) = (porigin_skipped_div)
$origin_node(S_capture.SOURCES,porigin_skipped_div) = (expression_skipped_div)
$string_read_runtime_value(S_capture,porigin_nn) = (PFLOAT {bits})
$string_read_runtime_value(S_capture,porigin_nn_left) = (PFLOAT {bits})
$string_read_runtime_value(S_capture,porigin_nn_right) = eps
$string_read_runtime_value(S_capture,porigin_skipped_div) = eps
$compiled_read(S_capture,porigin_nn) = eps
$compiled_read(S_capture,porigin_nn_left) = eps
$compiled_read(S_capture,porigin_nn_right) = eps
$compiled_precision(S_capture,(porigin_nn)) = (14)
$compiled_precision(S_capture,(porigin_nn_left)) = (14)
porigin_nn = PORIGIN n_unit pcpath_nn
porigin_nn_left = PORIGIN n_unit pcpath_nn_left
porigin_nn_right = PORIGIN n_unit pcpath_nn_right
porigin_skipped_div = PORIGIN n_unit pcpath_skipped_div
''')


def front(program, filename_b64, reference=False):
    prefix, checks = minus.front(program, filename_b64, reference=reference)
    return prefix, coalesce_tree('\n'.join(checks), reference).splitlines() + coalesce_checks(reference)


def render(program, filename_b64, reference=False):
    body, count, derived = minus.render(program, filename_b64, reference=reference)
    body = coalesce_tree(body, reference)
    before_pool = '~$string_read_allocated_value(S_number_pool,porigin_base,pvalue_base)'
    assert body.count(before_pool) == 1
    body = body.replace(before_pool, before_pool[1:])
    before_fold = '''S_unary_fold = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_number z_unary false) :: pcode.EXPRESSIONS]]]
  -- if $string_read_allocated_value(S_unary_fold,porigin_base,pvalue_base)
  -- if $string_read_plan(S_unary_fold) = (pstringread)'''
    assert body.count(before_fold) == 1
    body = body.replace(before_fold, before_fold.replace('z_unary false', 'z_unary true').replace(
        '  -- if $string_read_allocated_value', '  -- if ~$string_read_allocated_value').replace('= (pstringread)', '= eps'))
    checks = coalesce_checks(reference) + lines(r'''
$string_read_raw_float_sign_tree(expression_right_number)
$string_read_raw_float_sign_tree(NExprBinaryOpCoalesce expression_right_number expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprBinaryOpCoalesce (NScalarInt (INTEGER 1) eps) expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprBinaryOpCoalesce expression_right_number (NScalarString (BYTES "MQ==") eps) eps)
S_nn_skipped_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_nn_right 17) :: (PCCPRECISION pcpath_skipped_div 17) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_nn_skipped_precision,porigin_nn) = $string_read_runtime_value(S_capture,porigin_nn)
$string_read_allocated_value(S_nn_skipped_precision,porigin_base,pvalue_base)
$string_read_plan(S_nn_skipped_precision) = (pstringread)
''')
    for node in ('nn', 'nn_left'):
        checks += [f'S_bad_{node} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_{node},porigin_nn) = eps',
                   f'~$string_read_allocated_value(S_bad_{node},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_bad_{node}) = eps']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
