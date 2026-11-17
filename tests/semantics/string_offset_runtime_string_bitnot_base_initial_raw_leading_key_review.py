"""A one-byte emitted string NOT retains its exact INTERNED base and frozen raw index."""

from string_offset_initial_raw_leading_key_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)'),
            ('STRING_LEADING 1}', 'STRING_LEADING 0}'),
            ('$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (1)', '$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (0)'),
            ('$string_read_raw_saved(S_capture,pstringread) = (1)', '$string_read_raw_saved(S_capture,pstringread) = (0)'),
            ('$string_read_raw_saved(S,pstringread) = (1)', '$string_read_raw_saved(S,pstringread) = (0)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    body = body.replace('abc', 'b').replace('1x', '0x').replace('-0x', '-1x')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBitwiseNot expression_left metadata)
expression_left = NExprCastString expression_child metadata_left
expression_child = NScalarString (BYTES text_child) metadata_child
$base64(text_child) = [157]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_child)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_child) = (expression_child)
$compiled_read(S_capture,porigin_left) = eps
$compiled_read(S_capture,porigin_child) = (PSTRING ([157]))
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
$compiled_precision(S_capture,(porigin_left)) = (z_precision)
$compiled_precision(S_capture,(porigin_child)) = (z_precision)
$string_read_runtime_value(S_capture,porigin_left) = (PSTRING_CARRIER INTERNED_STRING ([157]))
$bitnot_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([157]),12) = S_capture[.RESULT = KNOWN pkeyread.BASE]
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
porigin_base = PORIGIN n_unit pcpath_base
porigin_left = PORIGIN n_unit pcpath_left
porigin_child = PORIGIN n_unit pcpath_child
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))
S_budget_bitnot = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))]
$string_read_runtime_value(S_budget_bitnot,porigin_base) = eps
$string_read_raw_known_base(S_budget_bitnot,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_bitnot,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 12 true) :: pcode.EXPRESSIONS]]'),
            ('left_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 0 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('child_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PSTRING ($ptascii("x")))) :: ppool.CONSTANTS]]'),
            ('child_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PINT 157)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_bitnot_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_bitnot_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_bitnot_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('kind', 'pcpath_base', 'NExprBooleanNot expression_left metadata'),
            ('left', 'pcpath_left', 'NExprCastString expression_child eps'),
            ('child', 'pcpath_child', 'NScalarString (BYTES text_child) eps')):
        checks += [f'S_bad_bitnot_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_bitnot_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_budget_forged_bitnot = S_bad_bitnot_child_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_budget_forged_bitnot,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
