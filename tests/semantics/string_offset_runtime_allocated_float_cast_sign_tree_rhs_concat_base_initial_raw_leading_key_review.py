"""Reached FLOAT cast/sign trees retain exact value and one RHS row."""

import string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_review as minus
from string_offset_retained_carrier_protocol import lines


def cast_sign_tree(text, reference):
    atom = 'NScalarFloat (FLOAT text_right_bits) metadata_atom'
    before = f'NExprUnaryMinus ({atom}) metadata_right_number'
    nodes = ('NExprUnaryMinus', 'NExprCastDouble', 'NExprUnaryMinus', 'NExprCastDouble', 'NExprUnaryPlus', 'NExprUnaryMinus') if reference else (
        'NExprUnaryPlus', 'NExprCastDouble', 'NExprUnaryMinus', 'NExprCastDouble', 'NExprUnaryPlus')
    expression = atom
    for index in range(len(nodes) - 1, -1, -1):
        metadata = 'metadata_right_number' if index == 0 else f'metadata_layer{index}'
        expression = f'{nodes[index]} ({expression}) {metadata}'
    assert text.count(before) == 1
    text = text.replace(before, expression)
    before_path = '$origin_child((porigin_right_number),[PCFIELD 0]) = (porigin_atom)'
    assert text.count(before_path) == 1
    path = ','.join('PCFIELD 0' for _ in nodes)
    text = text.replace(before_path,
        f'$origin_child((porigin_right_number),[{path}]) = (porigin_atom)')
    before_code = '$code_expression(pcode.EXPRESSIONS,pcpath_right_number) = ((z_unary,true))'
    assert text.count(before_code) == 1
    text = text.replace(before_code, before_code.replace('true', 'false'))
    bits = 13846598529327300608 if reference else 9223372036854775808
    before_read = f'$compiled_read(S_capture,porigin_right_number) = (PFLOAT {bits})'
    assert text.count(before_read) == 1
    return text.replace(before_read, '$compiled_read(S_capture,porigin_right_number) = eps')


def front(program, filename_b64, reference=False):
    prefix, checks = minus.front(program, filename_b64, reference=reference)
    return prefix, cast_sign_tree('\n'.join(checks), reference).splitlines()


def render(program, filename_b64, reference=False):
    body, count, derived = minus.render(program, filename_b64, reference=reference)
    body = cast_sign_tree(body, reference)
    # An emitted unary reads its genuine child; unused folded-pool entries do
    # not replace that authority.
    before_pool = '~$string_read_allocated_value(S_number_pool,porigin_base,pvalue_base)'
    assert body.count(before_pool) == 1
    body = body.replace(before_pool, before_pool[1:])
    before = '''S_unary_fold = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_number z_unary false) :: pcode.EXPRESSIONS]]]
  -- if $string_read_allocated_value(S_unary_fold,porigin_base,pvalue_base)
  -- if $string_read_plan(S_unary_fold) = (pstringread)'''
    assert body.count(before) == 1
    body = body.replace(before, before.replace('z_unary false', 'z_unary true').replace(
        '  -- if $string_read_allocated_value', '  -- if ~$string_read_allocated_value').replace(
        '= (pstringread)', '= eps'))
    reached = []
    for index in (1, 3):
        path = ','.join('PCFIELD 0' for _ in range(index))
        bits = (4623226492472524800 if index == 1 else 13846598529327300608) if reference else (
            9223372036854775808 if index == 1 else 0)
        reached += [
            f'$origin_child((porigin_right_number),[{path}]) = (porigin_cast{index})',
            f'porigin_cast{index} = PORIGIN n_unit pcpath_cast{index}',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_cast{index}) = ((z_cast{index},false))',
            f'$(z_cast{index} > 0)',
            f'$compiled_read(S_capture,porigin_cast{index}) = eps',
            f'$compiled_precision(S_capture,(porigin_cast{index})) = (14)',
            f'$origin_child((porigin_cast{index}),[PCFIELD 0]) = (porigin_child{index})',
            f'$string_read_runtime_value(S_capture,porigin_child{index}) = (PFLOAT {bits})',
            f'$string_read_runtime_value(S_capture,porigin_cast{index}) = (PFLOAT {bits})',
            f'$cast_apply(S_capture,CASTFLOAT,PFLOAT {bits},z_cast{index}) = S_capture[.RESULT = KNOWN (PFLOAT {bits})]',
        ]
    marker = '  -- if $string_read_allocated_value(S_capture,porigin_base,pvalue_base)\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in reached) + marker)
    checks = lines(r'''
$string_read_raw_float_sign_tree(expression_right_number)
$string_read_raw_float_sign_tree(NExprCastDouble expression_right_number eps)
$string_read_raw_float_sign_tree(NExprUnaryPlus (NExprCastDouble expression_right_number eps) eps)
$string_read_raw_float_sign_tree(NExprCastDouble (NScalarFloat (FLOAT "4029000000000000") eps) eps)
$string_read_raw_float_sign_tree(NExprUnaryPlus (NExprCastDouble (NScalarFloat (FLOAT "4029000000000000") eps) eps) eps)
$compiled_read(S_number_pool,porigin_right_number) = eps
$string_read_runtime_value(S_number_pool,porigin_right_number) = $string_read_runtime_value(S_capture,porigin_right_number)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarInt (INTEGER 12) eps) eps)
~$string_read_raw_float_sign_tree(NExprBinaryOpPlus expression_right_number expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NExprBinaryOpPlus expression_right_number expression_right_number eps) eps)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(reached) + len(checks), derived + len(checks)
