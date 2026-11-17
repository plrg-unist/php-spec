"""One-byte NOT through nested casts preserves the base and initial reference key."""

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
            ('$string_read_raw_saved(S,pstringread) = (1)', '$string_read_raw_saved(S,pstringread) = (0)')):
        assert old in body
        body = body.replace(old, new)
    body = body.replace('abc', 'b').replace('1x', '0x').replace('-0x', '-1x')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBitwiseNot expression_child metadata_base)
expression_child = NExprCastString expression_inner metadata_child
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [157]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_child)
$origin_child((porigin_child),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
porigin_base = PORIGIN n_unit pcpath_base
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$string_read_runtime_value(S_capture,porigin_child) = (PSTRING_CARRIER INTERNED_STRING ([157]))
$string_read_runtime_value(S_capture,porigin_inner) = (PSTRING_CARRIER INTERNED_STRING ([157]))
$string_read_runtime_value(S_capture,porigin_leaf) = (PSTRING_CARRIER INTERNED_STRING ([157]))
$bitnot_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([157]),18) = S_capture[.RESULT = KNOWN pvalue_base]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([157]))
S_budget_bitnot = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([157]))]
$string_read_runtime_value(S_budget_bitnot,porigin_base) = eps
$string_read_raw_known_base(S_budget_bitnot,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_bitnot,porigin_base,PSTRING_CARRIER INTERNED_STRING ([157]))
S_unused_bitnot_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PINT 999)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_bitnot_pool,porigin_base) = eps
$string_read_raw_known_base(S_unused_bitnot_pool,porigin_base,pvalue_base)
''')
    for label in ('base', 'child', 'inner', 'leaf'):
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
            checks.append('$compiled_read(S_capture,porigin_leaf) = (PSTRING ([157]))')
            updates += [('pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ([51]))) :: ppool.CONSTANTS]]'),
                        ('tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 157)) :: ppool.CONSTANTS]]'),
                        ('request', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING_CARRIER (REQUEST_STRING 0) ([157]))) :: ppool.CONSTANTS]]')]
        for kind, update in updates:
            name = f'S_bad_bitnot_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprBooleanNot expression_child metadata_base'),
            ('child', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_bitnot_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_bitnot_{label}_source,porigin_base,pvalue_base)']
    for label, text, raw, result in (
            ('empty', '', '[]', None), ('multibyte', 'nZ0=', '[157,157]', None),
            ('nul_operand', 'AA==', '[0]', None), ('nul_result', '/w==', '[255]', None),
            ('low', 'AQ==', '[1]', '[254]'), ('high', '/g==', '[254]', '[1]')):
        checks += lines(f'''
expression_bitnot_{label}_leaf = NScalarString (BYTES "{text}") metadata_leaf
expression_bitnot_{label}_inner = NExprCastString expression_bitnot_{label}_leaf metadata_inner
expression_bitnot_{label}_child = NExprCastString expression_bitnot_{label}_inner metadata_child
expression_bitnot_{label}_root = NExprBitwiseNot expression_bitnot_{label}_child metadata_base
S_bitnot_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bitnot_{label}_root) :: (PCOCCURRENCE pcpath_child expression_bitnot_{label}_child) :: (PCOCCURRENCE pcpath_inner expression_bitnot_{label}_inner) :: (PCOCCURRENCE pcpath_leaf expression_bitnot_{label}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ({raw}))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_bitnot_{label},porigin_base) = {"(PSTRING_CARRIER INTERNED_STRING (" + result + "))" if result else "eps"}
~$string_read_raw_known_base(S_bitnot_{label},porigin_base,pvalue_base)
''')
        if result is not None:
            checks.append(f'$string_read_raw_known_base(S_bitnot_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ({result}))')
    checks += lines(r'''
expression_old_binary_leaf = NScalarString (BYTES "Mw==") metadata_inner
expression_old_binary_child = NExprCastString expression_old_binary_leaf metadata_child
expression_old_binary_root = NExprBitwiseNot expression_old_binary_child metadata_base
S_old_binary_unary = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_old_binary_root) :: (PCOCCURRENCE pcpath_child expression_old_binary_child) :: (PCOCCURRENCE pcpath_inner expression_old_binary_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner (PSTRING ([51]))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_inner 18 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_old_binary_unary,porigin_base) = (PSTRING_CARRIER INTERNED_STRING ([204]))
$string_read_raw_known_base(S_old_binary_unary,porigin_base,PSTRING_CARRIER INTERNED_STRING ([204]))
S_budget_forged_bitnot = S_bad_bitnot_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_bitnot,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
