"""An emitted selected NULL preserves the literal shorthand fallback header."""

from string_offset_runtime_null_truth_base_initial_raw_leading_key_review import render as render_full
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_full(program, filename_b64)
    old = 'NExprTernary expression_cond (NScalarString (BYTES text_skipped) metadata_skipped) (NScalarString (BYTES text_selected) metadata_selected)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary expression_cond ABSENT (NScalarString (BYTES text_selected) metadata_selected)')
    old = '$base64(text_selected) = $ptascii("abc") /\\ $base64(text_skipped) = $ptascii("XYZ")'
    assert body.count(old) == 1
    body = body.replace(old, '$base64(text_selected) = $ptascii("abc")')
    removed = [line for line in body.splitlines(keepends=True) if 'skipped' in line]
    assert len(removed) == 8
    body = ''.join(line for line in body.splitlines(keepends=True) if 'skipped' not in line)
    anchor = '  -- if $origin_child((porigin_base),[PCFIELD 2]) = (porigin_selected)\n'
    assert body.count(anchor) == 1
    absent = lines(r'''
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$compiled_read(S_capture,porigin_absent) = eps
''')
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in absent) + anchor)
    old = '  -- if $string_read_raw_known_base(S_nonnull,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))'
    assert body.count(old) == 1
    body = body.replace(old, old.replace('if $', 'if ~$'))
    return body, count - len(removed) + len(absent), derived - 5
