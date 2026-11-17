"""A falsey nonnull cast skips its RHS and preserves the initial reference key."""

from string_offset_initial_raw_leading_key_peer_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pvalue_base', '$string_read_runtime_value(S_capture,porigin_base) = (pvalue_base)'),
            ('STRING_LEADING 1', 'STRING_LEADING 0'),
            ('$string_read_raw_leading(pvalue_base,pvalue_raw) = (1)', '$string_read_raw_leading(pvalue_base,pvalue_raw) = (0)'),
            ('$string_read_raw_saved(S_capture,pstringread) = (1)', '$string_read_raw_saved(S_capture,pstringread) = (0)'),
            ('$string_read_raw_saved(S,pstringread) = (1)', '$string_read_raw_saved(S,pstringread) = (0)'),
            ('PSTRING_CARRIER INTERNED_STRING ([98])', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            (';R:b;K:', ';R:0;K:')):
        assert old in body
        body = body.replace(old, new)
    body = body.replace('abc', '0').replace('1x', '0x').replace('-0x', '-1x')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
expression_left = NExprCastString expression_inner metadata_left
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
expression_right = NExprCastString expression_right_child metadata_right
expression_right_child = NExprConstFetch (NName (BYTES text_name) metadata_name) metadata_right_child
$base64(text_leaf) = [48]
$base64(text_name) = $ptascii("MissingFallback")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_child)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$origin_node(S_capture.SOURCES,porigin_right_child) = (expression_right_child)
porigin_base = PORIGIN n_unit pcpath_base
porigin_right = PORIGIN n_unit pcpath_right
porigin_right_child = PORIGIN n_unit pcpath_right_child
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$string_read_runtime_value(S_capture,porigin_left) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_leaf) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_right) = eps
$truth_value(S_capture,pvalue_base,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
pvalue_base =/= PNULL
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
S_budget_pair = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))]
$string_read_runtime_value(S_budget_pair,porigin_base) = eps
$string_read_raw_known_base(S_budget_pair,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_pair,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
S_unused_pair_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PINT 999)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_pair_pool,porigin_base) = eps
$string_read_raw_known_base(S_unused_pair_pool,porigin_base,pvalue_base)
''')
    for label in ('base', 'left', 'inner', 'leaf'):
        if label != 'base':
            checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                       f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})']
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label != 'leaf':
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            checks.append('$compiled_read(S_capture,porigin_leaf) = (PSTRING ([48]))')
            updates += [('pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ([49]))) :: ppool.CONSTANTS]]'),
                        ('tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 0)) :: ppool.CONSTANTS]]'),
                        ('request', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING_CARRIER (REQUEST_STRING 0) ([48]))) :: ppool.CONSTANTS]]')]
        for kind, update in updates:
            name = f'S_bad_pair_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprBinaryOpPlus expression_left expression_right metadata_base'),
            ('left', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps'),
            ('right', 'NExprCastString expression_right_child eps')):
        checks += [f'S_bad_pair_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_pair_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_pair_{label}_source,porigin_base,pvalue_base)']
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]'),
            ('pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING_CARRIER (REQUEST_STRING 99) ([88]))) :: ppool.CONSTANTS]]'),
            ('child_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_child (NScalarString (BYTES "AA==") metadata_right_child)) :: pcunit.OCCURRENCES]]')):
        checks += [f'S_skipped_pair_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_skipped_pair_{label},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base(S_skipped_pair_{label},porigin_base,pvalue_base)']
    for label, text, raw in (('empty', '', '[]'), ('two_zeroes', 'MDA=', '[48,48]'), ('nul', 'AA==', '[0]')):
        checks += lines(f'''
expression_pair_{label}_leaf = NScalarString (BYTES "{text}") metadata_leaf
expression_pair_{label}_inner = NExprCastString expression_pair_{label}_leaf metadata_inner
expression_pair_{label}_left = NExprCastString expression_pair_{label}_inner metadata_left
expression_pair_{label}_root = NExprBinaryOpCoalesce expression_pair_{label}_left expression_right metadata_base
S_pair_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_pair_{label}_root) :: (PCOCCURRENCE pcpath_left expression_pair_{label}_left) :: (PCOCCURRENCE pcpath_inner expression_pair_{label}_inner) :: (PCOCCURRENCE pcpath_leaf expression_pair_{label}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ({raw}))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_pair_{label},porigin_base) = {"eps" if label == "nul" else "(PSTRING_CARRIER INTERNED_STRING (" + raw + "))"}
~$string_read_raw_known_base(S_pair_{label},porigin_base,pvalue_base)
''')
        if label != 'nul':
            checks.append(f'$string_read_raw_known_base(S_pair_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ({raw}))')
    checks += lines(r'''
~$string_read_in_range(PSTRING_CARRIER INTERNED_STRING ([]),0)
$string_read_in_range(PSTRING_CARRIER INTERNED_STRING ([48,48]),0)
expression_pair_bool_right = NExprCastBool expression_right_child metadata_right
expression_pair_bool_root = NExprBinaryOpCoalesce expression_left expression_pair_bool_right metadata_base
S_pair_bool_right = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_pair_bool_root) :: (PCOCCURRENCE pcpath_right expression_pair_bool_right) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_pair_bool_right,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_pair_bool_right,porigin_base,pvalue_base)
S_budget_forged_pair = S_bad_pair_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_pair,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
