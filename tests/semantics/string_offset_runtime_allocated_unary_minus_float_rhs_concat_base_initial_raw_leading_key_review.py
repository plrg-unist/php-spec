"""Reached single-minus FLOAT RHSs retain sign bits and one-row allocation."""

import json

import string_offset_runtime_allocated_unary_plus_float_rhs_concat_base_initial_raw_leading_key_review as positive
from string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_cases import CASES
from string_offset_runtime_allocated_raw_float_rhs_concat_base_initial_raw_leading_key_cases import CASES as RAW_CASES


def negative(text, reference):
    before = 'NExprUnaryPlus (NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_right_number'
    assert text.count(before) <= 1
    text = text.replace(before, before.replace('NExprUnaryPlus', 'NExprUnaryMinus'))
    bits = 4623226492472524800 if reference else 0
    for tag in ('PFLOAT', 'NFLOAT'):
        text = text.replace(f'{tag} {bits}', f'{tag} {bits + 9223372036854775808}')
    if reference:
        text = text.replace('$ptascii("-10.5bcde12.5")', '$ptascii("-10.5bcde-12.5")')
        text = text.replace('$ptascii("12.5")', '$ptascii("-12.5")')
        text = text.replace('$ptascii("11x")', '$ptascii("9x")').replace('i = 11', 'i = 9')
        text = text.replace('S.STORE[n_current] = DEFINED (PINT 12)',
                            'S.STORE[n_current] = DEFINED (PINT 13)')
        text = text.replace('$string_byte_read(S,$ptascii("-10.5bcde-12.5"),12,z_key)',
                            '$string_byte_read(S,$ptascii("-10.5bcde-12.5"),13,z_key)')
        text = text.replace('([46])', '([45])')
    else:
        text = text.replace('$ptascii("420")', '$ptascii("42-0")')
        text = text.replace('$ptascii("0")', '$ptascii("-0")').replace('([48])', '([45])')
    return text.replace(json.dumps(RAW_CASES[int(reference)]['expected_stdout']),
                        json.dumps(CASES[int(reference)]['expected_stdout']))


def front(program, filename_b64, reference=False):
    prefix, checks = positive.front(program, filename_b64, reference=reference)
    return negative(prefix, reference), negative('\n'.join(checks), reference).splitlines()


def render(program, filename_b64, reference=False):
    body, count, derived = positive.render(program, filename_b64, reference=reference)
    return negative(body, reference), count, derived
