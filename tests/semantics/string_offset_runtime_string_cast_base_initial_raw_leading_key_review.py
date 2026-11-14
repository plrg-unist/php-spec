"""Direct emitted string casts retain their exact INTERNED base header."""

from string_offset_initial_raw_leading_key_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    early = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprCastString expression_child metadata)
expression_child = NScalarString (BYTES text_child) metadata_child
$base64(text_child) = $ptascii("abc")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_child)
$origin_node(S_capture.SOURCES,porigin_child) = (expression_child)
$compiled_read(S_capture,porigin_child) = (PSTRING ($ptascii("abc")))
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
$compiled_precision(S_capture,(porigin_child)) = (z_precision)
$string_read_runtime_value(S_capture,porigin_child) = (pkeyread.BASE)
$cast_apply(S_capture,CASTSTRING,pkeyread.BASE,12) = S_capture[.RESULT = KNOWN pkeyread.BASE]
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_base) = eps\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
porigin_base = PORIGIN n_unit pcpath_base
porigin_child = PORIGIN n_unit pcpath_child
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_budget_cast,porigin_base) = eps
$string_read_raw_known_base(S_budget_cast,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_unused_cast_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_cast_pool,porigin_base) = eps
$string_read_raw_known_base(S_unused_cast_pool,porigin_base,pkeyread.BASE)
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 12 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('child_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('child_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PINT 1)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_cast_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_cast_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_cast_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('kind', 'pcpath_base', 'NExprCastBool expression_child metadata'),
            ('child', 'pcpath_child', 'NScalarString (BYTES text_child) eps')):
        checks += [f'S_bad_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_budget_forged_cast = S_bad_cast_child_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_budget_forged_cast,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
