"""Quiet infinite FLOAT casts retain exact allocation and saved raw offsets."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_direct_allocated_string_base_initial_raw_leading_key_review import render as render_direct
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_review import render as render_float


def render(program, filename_b64, reference=False):
    renderer = render_float if reference else render_direct
    body, _, _ = renderer(program, filename_b64, reference=reference)
    if reference:
        body = body.replace('-10.5', '-INF').replace('10.5', 'INF')
        body = body.replace('4025000000000000', '7ff0000000000000')
        body = body.replace('13845472629420457984', '18442240474082181120')
        body = body.replace('4622100592565682176', '9218868437227405312')
        body = body.replace('FINITE 0 n_float_num n_float_den', 'INFINITE 0')
        body = body.replace('([46])', '([70])').replace('([53])', '([98])')
        body = body.replace('R:.;K:4;', 'R:F;K:4;')
    else:
        body = body.replace('$ptascii("10")', '$ptascii("INF")')
        body = body.replace('PINT 10', 'PFLOAT 9218868437227405312')
        old = 'expression_integer = NScalarInt (INTEGER 10) metadata_integer'
        assert body.count(old) == 1
        body = body.replace(old, 'expression_integer = NScalarFloat (FLOAT "7ff0000000000000") metadata_integer')
        body = body.replace('([49])', '([73])').replace('R:1;K:', 'R:I;K:')
    bits = 18442240474082181120 if reference else 9218868437227405312
    sign = 1 if reference else 0
    word = '-INF' if reference else 'INF'
    checks = [f'$float_decode({bits}) = INFINITE {sign}',
              f'$number_text(NFLOAT {bits},14) = ($ptascii("{word}"),false)',
              '$precision_value(S_capture) = 14',
              f'$string_read_runtime_value(S_capture,porigin_integer) = (PFLOAT {bits})',
              '$origin_node(S_capture.SOURCES,porigin_integer) = (expression_integer)',
              '$compiled_precision(S_capture,(porigin_integer)) = (14)']
    # The reference renderer already authenticates some of these facts.
    checks = [check for check in checks if '  -- if ' + check + '\n' not in body]
    anchor = f'  -- if $compiled_identity_value(S_capture,porigin_integer) = (PFLOAT {bits})\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, anchor + ''.join('  -- if ' + check + '\n' for check in checks))
    derived = lines(r'''
S_infinite_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:1]]
''') + [f'$cast_apply(S_infinite_prefix,CASTSTRING,PFLOAT {bits},z_key) = S_infinite_prefix[.STRINGDATA = S_infinite_prefix.STRINGDATA ++ [$ptascii("{word}")]][.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("{word}")))]']
    if not reference:
        derived += lines(r'''
S_live_precision = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$precision_value(S_live_precision) = 17
~$string_read_allocated_value(S_live_precision,porigin_base,pvalue_base)
$string_read_plan(S_live_precision) = eps
S_post_precision = S[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$string_read_raw_saved(S_post_precision,pstringread) = eps
S_abrupt = S_capture[.COMPLETION = UNSUPPORTED "control"]
~$string_read_allocated_value(S_abrupt,porigin_base,pvalue_base)
S_infinite_child_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_integer (NScalarFloat (FLOAT "7ff0000000000000") eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_infinite_child_shadow,porigin_integer) = (PFLOAT 9218868437227405312)
~$string_read_allocated_base(S_infinite_child_shadow,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
