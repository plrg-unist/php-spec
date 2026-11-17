"""Folded raw INT/STRING CONCAT keeps the falsey header and raw CV offset."""

from string_offset_literal_concat_runtime_scalar_coalesce_base_initial_raw_leading_key_review import render as render_string
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_string(program, filename_b64)
    for old, new in (
            ('$string_read_literal_bytes(expression_left) = ($ptascii("0"))',
             '$string_read_folded_concat_bytes(expression_left) = ($ptascii("0"))'),
            ('expression_suffix = NScalarString (BYTES text_suffix) metadata_suffix',
             'expression_suffix = NScalarInt (INTEGER 0) metadata_suffix'),
            ('$base64(text_suffix) = $ptascii("0")', '$long_range(0)'),
            ('NScalarString (BYTES text_suffix) eps', 'NScalarInt (INTEGER 0) eps')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    assert 'text_suffix' not in body
    checks = lines(r'''
$string_read_literal_bytes(expression_left) = eps
$string_read_folded_concat_bytes(NScalarInt (INTEGER 0) eps) = ($ptascii("0"))
$string_read_folded_concat_bytes(NScalarInt (INTEGER $(-1)) eps) = ($ptascii("-1"))
$string_read_folded_concat_bytes(NScalarInt (INTEGER 9223372036854775807) eps) = ($ptascii("9223372036854775807"))
$string_read_folded_concat_bytes(NScalarInt (INTEGER $(-9223372036854775808)) eps) = ($ptascii("-9223372036854775808"))
$string_read_folded_concat_bytes(NScalarInt (INTEGER 9223372036854775808) eps) = eps
$string_read_folded_concat_bytes(NScalarInt (INTEGER $(-9223372036854775809)) eps) = eps
$string_read_folded_concat_bytes(NScalarFloat (FLOAT "0000000000000000") eps) = eps
$string_read_folded_concat_bytes(NExprUnaryMinus expression_suffix eps) = eps
$string_read_folded_concat_bytes(NExprConstFetch (NName (BYTES "dHJ1ZQ==") eps) eps) = eps
$string_read_folded_concat_bytes(NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) = eps
expression_integer_float = NScalarFloat (FLOAT "0000000000000000") metadata_suffix
expression_integer_bad_left = NExprBinaryOpConcat expression_prefix expression_integer_float metadata_left
expression_integer_bad_base = NExprBinaryOpCoalesce expression_integer_bad_left expression_right metadata_base
S_integer_float = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_integer_bad_base) :: (PCOCCURRENCE pcpath_left expression_integer_bad_left) :: (PCOCCURRENCE pcpath_suffix expression_integer_float) :: pcunit.OCCURRENCES]]]
$parser_literal_at(expression_integer_bad_left,z_precision) = (PSTRING ($ptascii("0")))
$compiled_read(S_integer_float,porigin_left) = (PSTRING ($ptascii("0")))
$compiled_string_value(S_integer_float,porigin_left,PSTRING ($ptascii("0"))) = pkeyread.BASE
$string_read_folded_concat_bytes(expression_integer_bad_left) = eps
$string_read_runtime_value(S_integer_float,porigin_left) = eps
$string_read_runtime_value(S_integer_float,porigin_base) = eps
~$string_read_raw_known_base(S_integer_float,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
