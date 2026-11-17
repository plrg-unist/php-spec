"""A nonnull STRING coalesce skips deeper emitted RHS cast certificates."""

from string_offset_runtime_scalar_coalesce_base_initial_raw_leading_key_peer_review import render as render_raw
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_raw(program, filename_b64)
    old = '(NScalarString (BYTES text_right) metadata_right)'
    assert body.count(old) == 7
    body = body.replace(old, '(NExprCastString expression_right metadata_right)')
    for old, new in (
            ('$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("XYZ")))', '$compiled_read(S_capture,porigin_right) = eps'),
            ('$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("XYZ"))) = pvalue_fallback', '$string_read_runtime_value(S_capture,porigin_right) = (pvalue_fallback)'),
            ('PCONSTANT pcpath_right (PSTRING ($ptascii("bad")))', 'PCONSTANT pcpath_right_child (PSTRING ($ptascii("bad")))'),
            ('~$string_read_raw_known_base(S_coalesce_wrong_right,porigin_base,pvalue_base)', '$string_read_raw_known_base(S_coalesce_wrong_right,porigin_base,pvalue_base)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    anchor = '  -- if $origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left (NExprCastString expression_right metadata_right) metadata_base)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, anchor + '  -- if expression_right = NScalarString (BYTES text_right) metadata_right_child\n')
    early = lines(r'''
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_child)
$origin_node(S_capture.SOURCES,porigin_right_child) = (expression_right)
porigin_right_child = PORIGIN n_unit pcpath_right_child
$compiled_read(S_capture,porigin_right_child) = (PSTRING ($ptascii("XYZ")))
$compiled_string_value(S_capture,porigin_right_child,PSTRING ($ptascii("XYZ"))) = pvalue_fallback
$compiled_precision(S_capture,(porigin_right)) = (14)
$compiled_precision(S_capture,(porigin_right_child)) = (14)
''')
    anchor = '  -- if $origin_node(S_capture.SOURCES,porigin_right) = (NExprCastString expression_right metadata_right)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, anchor + ''.join('  -- if ' + check + '\n' for check in early))
    checks = ['$string_read_runtime_value(S_coalesce_wrong_right,porigin_right) = eps']
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]'),
            ('child_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_child 18 false) :: pcode.EXPRESSIONS]]'),
            ('child_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right_child 17) :: ppool.CONSTANTS]]'),
            ('child_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_child (NScalarString (BYTES text_right) eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_coalesce_skipped_right_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_right) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_fallback)']
    checks += lines(r'''
S_coalesce_wrong_right_metadata = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprCastString expression_right eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_coalesce_wrong_right_metadata,porigin_base) = eps
~$string_read_raw_known_base(S_coalesce_wrong_right_metadata,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + 1 + len(early) + len(checks), derived + 1 + len(early) + len(checks)
