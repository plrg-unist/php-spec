"""Reached sign-tree RHS rows preserve exact source and continuation state."""

import string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_review as minus
from string_offset_retained_carrier_protocol import lines


def sign_tree(text, reference):
    atom = 'NScalarFloat (FLOAT text_right_bits) metadata_atom'
    before = f'NExprUnaryMinus ({atom}) metadata_right_number'
    signs = ('NExprUnaryMinus', 'NExprUnaryMinus', 'NExprUnaryPlus', 'NExprUnaryMinus') if reference else (
        'NExprUnaryPlus', 'NExprUnaryMinus', 'NExprUnaryPlus')
    expression = atom
    for index in range(len(signs) - 1, -1, -1):
        metadata = 'metadata_right_number' if index == 0 else f'metadata_sign{index}'
        expression = f'{signs[index]} ({expression}) {metadata}'
    assert text.count(before) == 1
    text = text.replace(before, expression)
    before_path = '$origin_child((porigin_right_number),[PCFIELD 0]) = (porigin_atom)'
    assert text.count(before_path) == 1
    path = ','.join('PCFIELD 0' for _ in signs)
    return text.replace(before_path,
        f'$origin_child((porigin_right_number),[{path}]) = (porigin_atom)')


def front(program, filename_b64, reference=False):
    prefix, checks = minus.front(program, filename_b64, reference=reference)
    return prefix, sign_tree('\n'.join(checks), reference).splitlines()


def render(program, filename_b64, reference=False):
    body, count, derived = minus.render(program, filename_b64, reference=reference)
    body = sign_tree(body, reference)
    checks = lines(r'''
$string_read_raw_float_sign_tree(expression_right_number)
$string_read_raw_float_sign_tree(NScalarFloat (FLOAT text_right_bits) metadata_atom)
$string_read_raw_float_sign_tree(NExprUnaryPlus expression_right_number eps)
$string_read_raw_float_sign_tree(NExprUnaryMinus expression_right_number eps)
~$string_read_raw_float_sign_tree(NScalarInt (INTEGER 12) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprUnaryPlus (NExprCastDouble expression_right_number eps) eps)
~$string_read_raw_float_sign_tree(NExprBitwiseNot expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprBinaryOpPlus expression_right_number expression_right_number eps)
~$string_read_raw_float_sign_tree(NScalarString (BYTES "MTIuNQ==") eps)
''')
    for index in range(1, 4 if reference else 3):
        path = ','.join('PCFIELD 0' for _ in range(index))
        checks += [
            f'$origin_child((porigin_right_number),[{path}]) = (porigin_sign{index})',
            f'porigin_sign{index} = PORIGIN n_unit pcpath_sign{index}',
            f'S_source_sign{index} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_sign{index} (NScalarFloat (FLOAT text_right_bits) metadata_atom)) :: pcunit.OCCURRENCES]]]',
            f'~$string_read_allocated_value(S_source_sign{index},porigin_base,pvalue_base)',
            f'$string_read_plan(S_source_sign{index}) = eps',
        ]
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
