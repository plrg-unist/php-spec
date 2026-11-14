"""Immutable emitted string-cast truth preserves the captured raw CV offset."""

from string_offset_runtime_cast_truth_base_initial_raw_leading_key_review import render as render_cast
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_cast(program, filename_b64)
    replacements = (
        ('NExprCastBool expression_cast_int', 'NExprCastString expression_cast_int'),
        ('$truth(S_capture,PBOOL true)', '$truth(S_capture,PSTRING_CARRIER INTERNED_STRING ([49]))'),
        ('$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL true)',
         '$string_read_runtime_value(S_capture,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([49]))'),
        ('$cast_apply(S_capture,CASTBOOL,PINT 1,12) = S_capture[.RESULT = KNOWN (PBOOL true)]',
         '$cast_apply(S_capture,CASTSTRING,PINT 1,12) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]'),
        ('$truth_value(S_capture,PBOOL true,0)',
         '$truth_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([49]),0)'),
        ('$string_read_runtime_value(S_unused_cast_pool,porigin_cond) = (PBOOL true)',
         '$string_read_runtime_value(S_unused_cast_pool,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([49]))'),
        ('S_budget_forged_cast = S_bad_cast_leaf[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]',
         'S_budget_forged_cast = S_bad_cast_leaf[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]'),
    )
    for old, new in replacements:
        assert old in body, old
        body = body.replace(old, new)
    checks = lines(r'''
$string_read_runtime_value(S_budget_cast,porigin_cond) = eps
$string_read_runtime_bytes(S_budget_cast,porigin_cond) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
