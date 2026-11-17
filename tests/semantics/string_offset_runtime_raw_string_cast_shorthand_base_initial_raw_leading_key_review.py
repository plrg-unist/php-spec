"""A truthy raw header survives while an emitted string-cast fallback stays skipped."""

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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond ABSENT expression_right metadata)
expression_cond = NScalarString (BYTES text_cond) metadata_cond
expression_right = NExprCastString expression_unused metadata_right
expression_unused = NExprConstFetch (NName (BYTES text_unused) metadata_name) metadata_unused
$base64(text_cond) = $ptascii("b")
$base64(text_unused) = $ptascii("MissingFallback")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_unused)
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_cond)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$compiled_read(S_capture,porigin_cond) = (PSTRING ($ptascii("b")))
$compiled_precision(S_capture,(porigin_base)) = (14)
$compiled_precision(S_capture,(porigin_cond)) = (14)
$string_read_runtime_value(S_capture,porigin_cond) = (pkeyread.BASE)
$truth_value(S_capture,pkeyread.BASE,12) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
porigin_base = PORIGIN n_unit pcpath_base
porigin_cond = PORIGIN n_unit pcpath_cond
porigin_right = PORIGIN n_unit pcpath_right
porigin_unused = PORIGIN n_unit pcpath_unused
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
S_budget_raw_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))]
$string_read_runtime_value(S_budget_raw_cast,porigin_base) = eps
$string_read_raw_known_base(S_budget_raw_cast,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_raw_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
S_cond_zero_line = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 0 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_cond_zero_line,porigin_base) = (pkeyread.BASE)
$string_read_raw_known_base(S_cond_zero_line,porigin_base,pkeyread.BASE)
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 12 true) :: pcode.EXPRESSIONS]]'),
            ('condition_constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 12 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base 17) :: ppool.CONSTANTS]]'),
            ('condition_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond 17) :: ppool.CONSTANTS]]'),
            ('condition_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PSTRING ($ptascii("X")))) :: ppool.CONSTANTS]]'),
            ('condition_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT 98)) :: ppool.CONSTANTS]]'),
            ('condition_header', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b")))) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_raw_cast_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_raw_cast_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_raw_cast_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('kind', 'pcpath_base', 'NExprBinaryOpConcat expression_cond expression_right metadata'),
            ('condition', 'pcpath_cond', 'NScalarString (BYTES text_cond) eps'),
            ('right', 'pcpath_right', 'NExprCastString expression_unused eps')):
        checks += [f'S_bad_raw_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_raw_cast_{label}_source,porigin_base,pkeyread.BASE)']
    for label, update in (
            ('code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]'),
            ('pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_unused (PSTRING ($ptascii("bad")))) :: ppool.CONSTANTS]]'),
            ('source_child', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused (NScalarInt (INTEGER 3) metadata_unused)) :: pcunit.OCCURRENCES]]')):
        checks += [f'S_skipped_raw_cast_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_skipped_raw_cast_{label},porigin_base) = (pkeyread.BASE)',
                   f'$string_read_raw_known_base(S_skipped_raw_cast_{label},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_budget_forged_raw_cast = S_bad_raw_cast_condition_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_budget_forged_raw_cast,porigin_base,pkeyread.BASE)
expression_right_bool = NExprCastBool expression_unused metadata_right
expression_bool_base = NExprTernary expression_cond ABSENT expression_right_bool metadata
S_right_bool = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bool_base) :: (PCOCCURRENCE pcpath_right expression_right_bool) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_right_bool,porigin_base) = (pkeyread.BASE)
~$string_read_raw_known_base(S_right_bool,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
