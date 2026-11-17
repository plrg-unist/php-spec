"""A nonconstant empty CONCAT keeps the other exact INTERNED header."""

from string_offset_initial_raw_leading_key_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpConcat expression_left expression_right metadata)
expression_left = NExprCastString expression_empty metadata_left
expression_empty = NScalarString (BYTES text_empty) metadata_empty
expression_right = NScalarString (BYTES text_right) metadata_right
$base64(text_empty) = eps
$base64(text_right) = $ptascii("abc")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_empty)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$origin_node(S_capture.SOURCES,porigin_empty) = (expression_empty)
$compiled_read(S_capture,porigin_left) = eps
$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("abc")))
$compiled_read(S_capture,porigin_empty) = (PSTRING eps)
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
$compiled_precision(S_capture,(porigin_left)) = (z_precision)
$compiled_precision(S_capture,(porigin_right)) = (z_precision)
$compiled_precision(S_capture,(porigin_empty)) = (z_precision)
~$concat_constant(S_capture,(porigin_left))
$concat_constant(S_capture,(porigin_right))
$string_read_runtime_value(S_capture,porigin_left) = (PSTRING_CARRIER INTERNED_STRING eps)
$string_read_runtime_value(S_capture,porigin_right) = (pkeyread.BASE)
$string_concat(S_capture,PSTRING_CARRIER INTERNED_STRING eps,pkeyread.BASE,false,true) = S_capture[.RESULT = KNOWN pkeyread.BASE]
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
porigin_base = PORIGIN n_unit pcpath_base
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
porigin_empty = PORIGIN n_unit pcpath_empty
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_budget_concat = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_budget_concat,porigin_base) = eps
$string_read_raw_known_base(S_budget_concat,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_concat,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 12 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('right_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PINT 1)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_concat_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_concat_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_concat_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('kind', 'pcpath_base', 'NExprBinaryOpPlus expression_left expression_right metadata'),
            ('left', 'pcpath_left', 'NExprCastString expression_empty eps'),
            ('right', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        checks += [f'S_bad_concat_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_concat_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_budget_forged_concat = S_bad_concat_right_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_budget_forged_concat,porigin_base,pkeyread.BASE)
S_const_empty_concat = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 12 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING eps)) :: ppool.CONSTANTS]]]
$concat_constant(S_const_empty_concat,(porigin_left))
$string_read_runtime_value(S_const_empty_concat,porigin_base) = eps
~$string_read_raw_known_base(S_const_empty_concat,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
