"""Folded direct integer plus preserves the falsey INTERNED coalesce base."""

from string_offset_literal_signed_integer_concat_runtime_scalar_coalesce_base_initial_raw_leading_key_review import render as render_minus
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_minus(program, filename_b64)
    for old, new in (
            ('expression_suffix = NExprUnaryMinus expression_sign_atom metadata_suffix',
             'expression_suffix = NExprUnaryPlus expression_sign_atom metadata_suffix'),
            ('NExprUnaryMinus expression_sign_atom eps)) :: pcunit.OCCURRENCES',
             'NExprUnaryPlus expression_sign_atom eps)) :: pcunit.OCCURRENCES')):
        assert body.count(old) == 1, old
        body = body.replace(old, new)
    checks = lines(r'''
$string_read_folded_concat_bytes(NExprUnaryPlus expression_sign_atom eps) = ($ptascii("0"))
$string_read_folded_concat_bytes(NExprUnaryPlus (NScalarInt (INTEGER 9223372036854775807) eps) eps) = ($ptascii("9223372036854775807"))
$string_read_folded_concat_bytes(NExprUnaryPlus (NScalarInt (INTEGER $(-9223372036854775808)) eps) eps) = ($ptascii("-9223372036854775808"))
$string_read_folded_concat_bytes(NExprUnaryPlus (NScalarInt (INTEGER 9223372036854775808) eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryPlus (NScalarInt (INTEGER $(-9223372036854775809)) eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryPlus (NScalarFloat (FLOAT "0000000000000000") eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryPlus expression_prefix eps) = eps
$string_read_folded_concat_bytes(NExprUnaryPlus (NExprUnaryMinus expression_sign_atom eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryPlus (NExprUnaryPlus expression_sign_atom eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryPlus (NExprConstFetch (NName (BYTES "dHJ1ZQ==") eps) eps) eps) = ($ptascii("1"))
$string_read_folded_concat_bytes(NExprUnaryPlus (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) eps) = ($ptascii("0"))
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
