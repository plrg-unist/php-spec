"""Nonconstant empty CONCAT preserves its header and the initial reference key."""

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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpConcat expression_left expression_right metadata_base)
expression_left = NExprCastString expression_left_leaf metadata_left
expression_left_leaf = NScalarString (BYTES text_left_leaf) metadata_left_leaf
expression_right = NExprCastString expression_right_inner metadata_right
expression_right_inner = NExprCastString expression_right_leaf metadata_right_inner
expression_right_leaf = NScalarString (BYTES text_right_leaf) metadata_right_leaf
$base64(text_left_leaf) = $ptascii("abc")
$base64(text_right_leaf) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_left_leaf)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_inner)
$origin_child((porigin_right_inner),[PCFIELD 0]) = (porigin_right_leaf)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_left_leaf) = (expression_left_leaf)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$origin_node(S_capture.SOURCES,porigin_right_inner) = (expression_right_inner)
$origin_node(S_capture.SOURCES,porigin_right_leaf) = (expression_right_leaf)
$compiled_read(S_capture,porigin_left) = eps
$compiled_read(S_capture,porigin_right) = eps
$compiled_read(S_capture,porigin_right_inner) = eps
$compiled_read(S_capture,porigin_left_leaf) = (PSTRING ($ptascii("abc")))
$compiled_read(S_capture,porigin_right_leaf) = (PSTRING ([]))
$string_read_runtime_value(S_capture,porigin_left) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_right) = (PSTRING_CARRIER INTERNED_STRING ([]))
$string_read_runtime_value(S_capture,porigin_right_inner) = (PSTRING_CARRIER INTERNED_STRING ([]))
~$concat_constant(S_capture,(porigin_left))
~$concat_constant(S_capture,(porigin_right))
$concat_constant(S_capture,(porigin_left_leaf))
$concat_constant(S_capture,(porigin_right_leaf))
$string_concat(S_capture,pvalue_base,PSTRING_CARRIER INTERNED_STRING ([]),false,false) = S_capture[.RESULT = KNOWN pvalue_base]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
porigin_base = PORIGIN n_unit pcpath_base
porigin_left = PORIGIN n_unit pcpath_left
porigin_left_leaf = PORIGIN n_unit pcpath_left_leaf
porigin_right = PORIGIN n_unit pcpath_right
porigin_right_inner = PORIGIN n_unit pcpath_right_inner
porigin_right_leaf = PORIGIN n_unit pcpath_right_leaf
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_budget_concat = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_budget_concat,porigin_base) = eps
$string_read_raw_known_base(S_budget_concat,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_concat,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_unused_concat_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PINT 999)) :: (PCONSTANT pcpath_left (PBOOL false)) :: (PCONSTANT pcpath_right (PBOOL true)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_concat_pool,porigin_base) = eps
$string_read_runtime_value(S_unused_concat_pool,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_unused_concat_pool,porigin_base,pvalue_base)
''')
    for label in ('base', 'left', 'left_leaf', 'right', 'right_inner', 'right_leaf'):
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label not in ('left_leaf', 'right_leaf'):
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            name = f'S_bad_concat_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, update in (
            ('source', '.SOURCES = eps'), ('code', '.CODE = eps'), ('pool', '.POOLS = eps'),
            ('left_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left_leaf (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('right_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right_leaf (PSTRING ([120]))) :: ppool.CONSTANTS]]'),
            ('left_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left_leaf (PINT 0)) :: ppool.CONSTANTS]]'),
            ('right_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right_leaf (PNULL)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_concat_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_concat_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_concat_{label},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprBinaryOpCoalesce expression_left expression_right metadata_base'),
            ('left', 'NExprCastString expression_left_leaf eps'),
            ('left_leaf', 'NScalarString (BYTES text_left_leaf) eps'),
            ('right', 'NExprCastString expression_right_inner eps'),
            ('right_inner', 'NExprCastString expression_right_leaf eps'),
            ('right_leaf', 'NScalarString (BYTES text_right_leaf) eps')):
        checks += [f'S_bad_concat_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_concat_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_budget_forged_concat = S_bad_concat_right_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_concat,porigin_base,pvalue_base)
expression_empty = NScalarString (BYTES "") metadata_right_leaf
expression_raw_abc = NScalarString (BYTES "YWJj") metadata_left_leaf
expression_reverse_left = NExprCastString expression_empty metadata_left
expression_reverse = NExprBinaryOpConcat expression_reverse_left expression_raw_abc metadata_base
S_reverse = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_reverse) :: (PCOCCURRENCE pcpath_left expression_reverse_left) :: (PCOCCURRENCE pcpath_left_leaf expression_empty) :: (PCOCCURRENCE pcpath_right expression_raw_abc) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left_leaf (PSTRING ([]))) :: (PCONSTANT pcpath_right (PSTRING ($ptascii("abc")))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 true) :: pcode.EXPRESSIONS]]]
~$concat_constant(S_reverse,(porigin_left))
$concat_constant(S_reverse,(porigin_right))
$string_read_runtime_value(S_reverse,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_reverse,porigin_base,pvalue_base)
expression_const_empty_left = NExprBinaryOpConcat expression_empty expression_left metadata_base
S_const_empty_left = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_const_empty_left) :: (PCOCCURRENCE pcpath_left expression_empty) :: (PCOCCURRENCE pcpath_right expression_left) :: (PCOCCURRENCE pcpath_right_inner expression_raw_abc) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ([]))) :: (PCONSTANT pcpath_right_inner (PSTRING ($ptascii("abc")))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: (CODEEXPR pcpath_right_inner 18 true) :: pcode.EXPRESSIONS]]]
$concat_constant(S_const_empty_left,(porigin_left))
~$concat_constant(S_const_empty_left,(porigin_right))
$string_read_runtime_value(S_const_empty_left,porigin_left) = (PSTRING_CARRIER INTERNED_STRING ([]))
$string_read_runtime_value(S_const_empty_left,porigin_right) = (pvalue_base)
$string_read_runtime_value(S_const_empty_left,porigin_base) = eps
~$string_read_raw_known_base(S_const_empty_left,porigin_base,pvalue_base)
expression_const_empty_right = NExprBinaryOpConcat expression_left expression_empty metadata_base
S_const_empty_right = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_const_empty_right) :: (PCOCCURRENCE pcpath_right expression_empty) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING ([]))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 true) :: pcode.EXPRESSIONS]]]
~$concat_constant(S_const_empty_right,(porigin_left))
$concat_constant(S_const_empty_right,(porigin_right))
$string_read_runtime_value(S_const_empty_right,porigin_left) = (pvalue_base)
$string_read_runtime_value(S_const_empty_right,porigin_right) = (PSTRING_CARRIER INTERNED_STRING ([]))
$string_read_runtime_value(S_const_empty_right,porigin_base) = eps
~$string_read_raw_known_base(S_const_empty_right,porigin_base,pvalue_base)
$string_concat(S_capture,PSTRING_CARRIER INTERNED_STRING ([]),pvalue_base,true,false) = $string_request(S_capture,$ptascii("abc"))
$string_concat(S_capture,pvalue_base,PSTRING_CARRIER INTERNED_STRING ([]),false,true) = $string_request(S_capture,$ptascii("abc"))
''')
    for label, text, raw, value in (
            ('all_empty', '', 'PSTRING ([])', 'PSTRING_CARRIER INTERNED_STRING ([])'),
            ('zero', 'MA==', 'PSTRING ([48])', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            ('nul', 'AA==', 'PSTRING ([0])', None)):
        checks += lines(f'''
expression_{label}_leaf = NScalarString (BYTES "{text}") metadata_left_leaf
expression_{label}_left = NExprCastString expression_{label}_leaf metadata_left
expression_{label}_base = NExprBinaryOpConcat expression_{label}_left expression_right metadata_base
S_concat_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_left expression_{label}_left) :: (PCOCCURRENCE pcpath_left_leaf expression_{label}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left_leaf ({raw})) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_concat_{label},porigin_base) = {"(" + value + ")" if value else "eps"}
~$string_read_raw_known_base(S_concat_{label},porigin_base,pvalue_base)
''')
        if value is not None:
            checks.append(f'$string_read_raw_known_base(S_concat_{label},porigin_base,{value})')
    checks += lines(r'''
expression_alloc_leaf = NScalarString (BYTES "WFla") metadata_right_leaf
expression_alloc_inner = NExprCastString expression_alloc_leaf metadata_right_inner
expression_alloc_right = NExprCastString expression_alloc_inner metadata_right
expression_alloc_base = NExprBinaryOpConcat expression_left expression_alloc_right metadata_base
S_alloc_concat = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_alloc_base) :: (PCOCCURRENCE pcpath_right expression_alloc_right) :: (PCOCCURRENCE pcpath_right_inner expression_alloc_inner) :: (PCOCCURRENCE pcpath_right_leaf expression_alloc_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right_leaf (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_alloc_concat,porigin_base) = eps
~$string_read_raw_known_base(S_alloc_concat,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
