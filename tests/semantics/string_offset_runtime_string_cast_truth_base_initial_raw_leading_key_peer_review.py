"""Quiet emitted string casts retain literal bases and the original reference key."""

from string_offset_runtime_cast_truth_base_initial_raw_leading_key_peer_review import render as render_cast
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_cast(program, filename_b64)
    for old, new in (
            ('expression_cond = NExprCastDouble expression_bool metadata_cond', 'expression_cond = NExprCastString expression_bool metadata_cond'),
            ('NExprCastDouble expression_bool eps', 'NExprCastString expression_bool eps'),
            ('$string_read_runtime_value(S_capture,porigin_left) = (PFLOAT 0)', '$string_read_runtime_value(S_capture,porigin_left) = (PSTRING_CARRIER INTERNED_STRING ([]))'),
            ('$string_read_runtime_value(S_unused_pool,porigin_left) = (PFLOAT 0)', '$string_read_runtime_value(S_unused_pool,porigin_left) = (PSTRING_CARRIER INTERNED_STRING ([]))'),
            ('$cast_apply(S_capture,CASTFLOAT,PBOOL false,18) = S_capture[.RESULT = KNOWN (PFLOAT 0)]', '$cast_apply(S_capture,CASTSTRING,PBOOL false,18) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([]))]'),
            ('$truth_value(S_capture,PFLOAT 0,0)', '$truth_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([]),0)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    checks = lines(r'''
$string_read_runtime_cast_quiet(CASTSTRING,PBOOL false)
~$string_read_runtime_cast_quiet(CASTSTRING,PINT 10)
~$string_read_runtime_cast_quiet(CASTSTRING,PFLOAT 4607182418800017408)
$truth_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([48]),0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$truth_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([48,48]),0) = S_capture[.RESULT = KNOWN (PBOOL true)]
''')
    for label, child, raw, value, truth in (
            ('zero', 'NScalarString (BYTES "MA==") metadata_text', 'PSTRING ([48])', 'PSTRING_CARRIER INTERNED_STRING ([48])', False),
            ('two_zeroes', 'NScalarString (BYTES "MDA=") metadata_text', 'PSTRING ([48,48])', 'PSTRING_CARRIER INTERNED_STRING ([48,48])', True),
            ('empty', 'NScalarString (BYTES "") metadata_text', 'PSTRING ([])', 'PSTRING_CARRIER INTERNED_STRING ([])', False),
            ('integer_ten', 'NScalarInt (INTEGER 10) metadata_text', 'PINT 10', None, False),
            ('float_one', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_text', 'PFLOAT 4607182418800017408', None, False),
            ('nul', 'NScalarString (BYTES "AA==") metadata_text', 'PSTRING ([0])', None, False)):
        state = 'S_string_cast_' + label
        checks += lines(f'''
expression_string_cast_{label}_child = {child}
expression_string_cast_{label} = NExprCastString expression_string_cast_{label}_child metadata_cond
expression_string_cast_{label}_base = NExprTernary expression_string_cast_{label} expression_true expression_false metadata
{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_string_cast_{label}_base) :: (PCOCCURRENCE pcpath_left expression_string_cast_{label}) :: (PCOCCURRENCE pcpath_bool expression_string_cast_{label}_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_bool ({raw})) :: (PCCPRECISION pcpath_left 14) :: (PCCPRECISION pcpath_bool 14) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: (CODEEXPR pcpath_bool 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read({state},porigin_left) = eps
$string_read_runtime_value({state},porigin_left) = {"(" + value + ")" if value else "eps"}
$string_read_raw_known_base({state},porigin_base,pvalue_wrong) = {str(value is not None and truth).lower()}
$string_read_raw_known_base({state},porigin_base,pvalue_base) = {str(value is not None and not truth).lower()}
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
