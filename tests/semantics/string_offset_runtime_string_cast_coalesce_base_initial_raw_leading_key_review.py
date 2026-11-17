"""A falsey nonnull emitted string cast retains the coalesce header."""

from string_offset_coalesce_base_initial_raw_leading_key_review import render as render_coalesce
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_coalesce(program, filename_b64)
    for old, new in (
            ('NExprBinaryOpCoalesce (NScalarString (BYTES text_left) metadata_left)', 'NExprBinaryOpCoalesce (NExprCastString expression_child metadata_left)'),
            ('$compiled_read(S_capture,porigin_left) = (PSTRING ($ptascii("0")))', '$compiled_read(S_capture,porigin_left) = eps'),
            ('$compiled_string_value(S_capture,porigin_left,PSTRING ($ptascii("0"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_left) = (pkeyread.BASE)'),
            ('$base64(text_right) = $ptascii("abc")', '$base64(text_right) = $ptascii("XYZ")'),
            ('$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("XYZ")))'),
            ('$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("abc"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))', '$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("XYZ"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))'),
            ('PCONSTANT (pcpath_base ++ [PCFIELD 1]) (PSTRING ($ptascii("XYZ")))', 'PCONSTANT (pcpath_base ++ [PCFIELD 1]) (PSTRING ($ptascii("bad")))'),
            ('pcpath_base ++ [PCFIELD 0]', 'pcpath_base ++ [PCFIELD 0,PCFIELD 0]')):
        assert old in body
        body = body.replace(old, new)
    anchor = 'NExprBinaryOpCoalesce (NExprCastString expression_child metadata_left) (NScalarString (BYTES text_right) metadata_right) metadata)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, anchor + '  -- if expression_child = NScalarString (BYTES text_left) metadata_child\n')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_left) = (NExprCastString expression_child metadata_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_child)
$origin_node(S_capture.SOURCES,porigin_child) = (expression_child)
$compiled_read(S_capture,porigin_child) = (PSTRING ($ptascii("0")))
$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
$compiled_precision(S_capture,(porigin_left)) = (z_precision)
$compiled_precision(S_capture,(porigin_child)) = (z_precision)
~$truth(S_capture,pkeyread.BASE)
S_capture.SOURCES = [pcunit]
porigin_left = PORIGIN n_unit pcpath_left
porigin_child = PORIGIN n_unit pcpath_child
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_budget_cast,porigin_base) = eps
$string_read_raw_known_base(S_budget_cast,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('left_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('child_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_cast_{label} = S_capture[{update}]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('left_kind', 'pcpath_left', 'NExprCastBool expression_child metadata_left'),
            ('child', 'pcpath_child', 'NScalarString (BYTES text_left) eps')):
        checks += [f'S_bad_cast_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label},porigin_base,pkeyread.BASE)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks) + 1, derived + len(checks)
