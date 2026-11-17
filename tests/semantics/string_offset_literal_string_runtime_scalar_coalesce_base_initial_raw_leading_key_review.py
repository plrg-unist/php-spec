"""A literal falsey STRING keeps its coalesce header and frozen raw offset."""

from string_offset_initial_raw_leading_key_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    for old, new in (('$ptascii("abc")', '$ptascii("0")'),
                     ('$ptascii("1x")', '$ptascii("0x")'), (r'\"1x\"', r'\"0x\"'),
                     ('512:1x;', '512:0x;'),
                     ('STRING_LEADING 1', 'STRING_LEADING 0'), ('([98])', '([48])'), ('R:b;', 'R:0;')):
        body = body.replace(old, new)
    for old in ('$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (1)',
                '$string_read_raw_saved(S_capture,pstringread) = (1)',
                '$string_read_raw_saved(S,pstringread) = (1)'):
        assert body.count(old) == 1
        body = body.replace(old, old.replace('= (1)', '= (0)'))
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
expression_left = NScalarString (BYTES text_left) metadata_left
expression_right = NExprTernary expression_guard expression_selected expression_unused metadata_right
$base64(text_left) = $ptascii("0")
$string_read_literal_bytes(expression_right) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$compiled_read(S_capture,porigin_left) = (PSTRING ($ptascii("0")))
$compiled_read(S_capture,porigin_right) = eps
$compiled_string_value(S_capture,porigin_left,PSTRING ($ptascii("0"))) = pkeyread.BASE
$string_read_runtime_value(S_capture,porigin_left) = (pkeyread.BASE)
$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)
~$truth(S_capture,pkeyread.BASE)
$truth_value(S_capture,pkeyread.BASE,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
porigin_base = PORIGIN n_unit pcpath_base
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
$compiled_precision(S_capture,(porigin_left)) = (z_precision)
S_literal_budget = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_literal_budget,porigin_base) = eps
$string_read_raw_known_base(S_literal_budget,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_literal_budget,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
''')
    for label, update in (
            ('root_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('root_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 12 true) :: pcode.EXPRESSIONS]]'),
            ('root_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 12 false) :: pcode.EXPRESSIONS]]'),
            ('left_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('left_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left (NScalarString (BYTES text_left) eps)) :: pcunit.OCCURRENCES]]'),
            ('right_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprTernary expression_guard expression_selected expression_unused eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_bad_literal_coalesce_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_literal_ignored_root_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$compiled_read(S_literal_ignored_root_pool,porigin_base) = eps
$string_read_runtime_value(S_literal_ignored_root_pool,porigin_base) = (pkeyread.BASE)
$string_read_raw_known_base(S_literal_ignored_root_pool,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
