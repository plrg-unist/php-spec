"""A literal NULL selects a cast header before the initial reference-key Warning."""

from string_offset_initial_raw_leading_key_peer_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pvalue_base', '$string_read_runtime_value(S_capture,porigin_base) = (pvalue_base)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
expression_left = NExprConstFetch (NName (BYTES text_left) metadata_name) metadata_left
expression_right = NExprCastString expression_inner metadata_right
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_left) = $ptascii("NuLl")
$ptlc($base64(text_left)) = $ptascii("null")
$base64(text_leaf) = $ptascii("abc")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$origin_node(S_capture.SOURCES,porigin_inner) = (expression_inner)
$origin_node(S_capture.SOURCES,porigin_leaf) = (expression_leaf)
$compiled_read(S_capture,porigin_left) = (PNULL)
$compiled_read(S_capture,porigin_right) = eps
$compiled_read(S_capture,porigin_inner) = eps
$compiled_read(S_capture,porigin_leaf) = (PSTRING ($ptascii("abc")))
$string_read_runtime_value(S_capture,porigin_left) = (PNULL)
$string_read_runtime_value(S_capture,porigin_right) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
$string_read_raw_known_base(S_capture,porigin_right,pvalue_base)
$string_read_raw_known_base(S_capture,porigin_inner,pvalue_base)
porigin_base = PORIGIN n_unit pcpath_base
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
porigin_inner = PORIGIN n_unit pcpath_inner
porigin_leaf = PORIGIN n_unit pcpath_leaf
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_budget_coalesce = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_budget_coalesce,porigin_base) = eps
$string_read_raw_known_base(S_budget_coalesce,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_coalesce,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_unused_coalesce_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PINT 999)) :: (PCONSTANT pcpath_right (PBOOL false)) :: (PCONSTANT pcpath_inner (PBOOL false)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_coalesce_pool,porigin_base) = eps
$compiled_read(S_unused_coalesce_pool,porigin_right) = eps
$string_read_raw_known_base(S_unused_coalesce_pool,porigin_base,pvalue_base)
''')
    for label in ('base', 'left', 'right', 'inner', 'leaf'):
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label in ('base', 'right', 'inner'):
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            name = f'S_bad_coalesce_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, update in (
            ('source', '.SOURCES = eps'), ('code', '.CODE = eps'), ('pool', '.POOLS = eps'),
            ('left_code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: pcode.EXPRESSIONS]]'),
            ('leaf_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('leaf_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 1)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_coalesce_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_coalesce_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_coalesce_{label},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprBinaryOpConcat expression_left expression_right metadata_base'),
            ('left', 'NExprConstFetch (NName (BYTES text_left) metadata_name) eps'),
            ('right', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_coalesce_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_coalesce_{label}_source,porigin_base,pvalue_base)']
    for label, name in (
            ('false_name', 'NName (BYTES "ZmFsc2U=") metadata_name'),
            ('unknown_name', 'NName (BYTES "bnVsbHg=") metadata_name'),
            ('fully_qualified', 'NNameFullyQualified (BYTES text_left) metadata_name'),
            ('relative', 'NNameRelative (BYTES text_left) metadata_name')):
        checks += lines(f'''
expression_left_{label} = NExprConstFetch ({name}) metadata_left
expression_base_{label} = NExprBinaryOpCoalesce expression_left_{label} expression_right metadata_base
S_bad_name_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}) :: (PCOCCURRENCE pcpath_left expression_left_{label}) :: pcunit.OCCURRENCES]]]
$compiled_read(S_bad_name_{label},porigin_left) = (PNULL)
~$string_read_raw_known_base(S_bad_name_{label},porigin_base,pvalue_base)
''')
    for label, raw in (('false', 'PBOOL false'), ('true', 'PBOOL true'), ('zero', 'PINT 0')):
        checks += [f'S_bad_null_tag_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left ({raw})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_null_tag_{label},porigin_base) =/= (pvalue_base)',
                   f'~$string_read_raw_known_base(S_bad_null_tag_{label},porigin_base,pvalue_base)']
    checks += lines(r'''
S_budget_forged_coalesce = S_bad_coalesce_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_coalesce,porigin_base,pvalue_base)
''')
    for label, child, raw, value in (
            ('zero', 'NScalarInt (INTEGER 0) metadata_inner', 'PINT 0', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            ('one', 'NScalarInt (INTEGER 1) metadata_inner', 'PINT 1', 'PSTRING_CARRIER INTERNED_STRING ([49])'),
            ('nine', 'NScalarInt (INTEGER 9) metadata_inner', 'PINT 9', 'PSTRING_CARRIER INTERNED_STRING ([57])'),
            ('ten', 'NScalarInt (INTEGER 10) metadata_inner', 'PINT 10', None),
            ('float', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_inner', 'PFLOAT 4607182418800017408', None),
            ('empty', 'NScalarString (BYTES "") metadata_inner', 'PSTRING ([])', 'PSTRING_CARRIER INTERNED_STRING ([])'),
            ('nul', 'NScalarString (BYTES "AA==") metadata_inner', 'PSTRING ([0])', None)):
        checks += lines(f'''
expression_selected_{label}_child = {child}
expression_selected_{label} = NExprCastString expression_selected_{label}_child metadata_right
expression_selected_{label}_base = NExprBinaryOpCoalesce expression_left expression_selected_{label} metadata_base
S_selected_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_selected_{label}_base) :: (PCOCCURRENCE pcpath_right expression_selected_{label}) :: (PCOCCURRENCE pcpath_inner expression_selected_{label}_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner ({raw})) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_inner 18 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_selected_{label},porigin_base) = {"(" + value + ")" if value else "eps"}
~$string_read_raw_known_base(S_selected_{label},porigin_base,pvalue_base)
''')
        if value is not None:
            checks.append(f'$string_read_raw_known_base(S_selected_{label},porigin_base,{value})')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
