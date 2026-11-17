"""An empty cast condition selects the fallback's distinct immutable header."""

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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond ABSENT expression_false metadata_base)
expression_cond = NExprCastString expression_cond_inner metadata_cond
expression_cond_inner = NExprCastString expression_cond_leaf metadata_cond_inner
expression_cond_leaf = NScalarString (BYTES text_cond_leaf) metadata_cond_leaf
expression_false = NExprCastString expression_leaf metadata_false
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_cond_leaf) = eps
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cond_inner)
$origin_child((porigin_cond_inner),[PCFIELD 0]) = (porigin_cond_leaf)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$string_read_runtime_value(S_capture,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([]))
$truth_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([]),18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
S_budget_shorthand = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([]))]
$string_read_runtime_value(S_budget_shorthand,porigin_base) = eps
$string_read_raw_known_base(S_budget_shorthand,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_shorthand,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
''')
    for label in ('base', 'cond', 'cond_inner', 'cond_leaf', 'false', 'leaf'):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label not in ('cond_leaf', 'leaf'):
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            raw = '[]' if label == 'cond_leaf' else '[48]'
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = (PSTRING ({raw}))')
            updates += [('pool', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PSTRING ([49]))) :: ppool.CONSTANTS]]'),
                        ('request', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PSTRING_CARRIER (REQUEST_STRING 99) ({raw}))) :: ppool.CONSTANTS]]')]
        for kind, update in updates:
            name = f'S_bad_shorthand_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprTernary expression_cond ABSENT (NExprCastBool expression_leaf metadata_false) metadata_base'),
            ('cond', 'NExprCastString expression_cond_inner eps'),
            ('cond_inner', 'NExprCastString expression_cond_leaf eps'),
            ('cond_leaf', 'NScalarString (BYTES text_cond_leaf) eps'),
            ('false', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_shorthand_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_shorthand_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_shorthand_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
expression_truthy_leaf = NScalarString (BYTES "Yg==") metadata_cond_leaf
expression_truthy_inner = NExprCastString expression_truthy_leaf metadata_cond_inner
expression_truthy_cond = NExprCastString expression_truthy_inner metadata_cond
expression_truthy_root = NExprTernary expression_truthy_cond ABSENT expression_false metadata_base
S_truthy = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_truthy_root) :: (PCOCCURRENCE pcpath_cond expression_truthy_cond) :: (PCOCCURRENCE pcpath_cond_inner expression_truthy_inner) :: (PCOCCURRENCE pcpath_cond_leaf expression_truthy_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_leaf (PSTRING ([98]))) :: ppool.CONSTANTS]]]
S_truthy.POOLS = [ppool_truthy]
S_truthy.SOURCES = [pcunit_truthy]
$string_read_runtime_value(S_truthy,porigin_base) = (PSTRING_CARRIER INTERNED_STRING ([98]))
$string_read_raw_known_base(S_truthy,porigin_base,PSTRING_CARRIER INTERNED_STRING ([98]))
~$string_read_raw_known_base(S_truthy,porigin_base,pvalue_base)
S_truthy_bad_source = S_truthy[.SOURCES = [pcunit_truthy[.OCCURRENCES = (PCOCCURRENCE pcpath_false (NExprCastString expression_leaf eps)) :: pcunit_truthy.OCCURRENCES]]]
$string_read_runtime_value(S_truthy_bad_source,porigin_base) = eps
~$string_read_raw_known_base(S_truthy_bad_source,porigin_base,PSTRING_CARRIER INTERNED_STRING ([98]))
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 18 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool_truthy[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool_truthy.CONSTANTS]]'),
            ('pool', '.POOLS = [ppool_truthy[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING_CARRIER (REQUEST_STRING 99) ([48]))) :: ppool_truthy.CONSTANTS]]'),
            ('descendant', '.SOURCES = [pcunit_truthy[.OCCURRENCES = (PCOCCURRENCE pcpath_leaf (NScalarString (BYTES "AA==") metadata_leaf)) :: pcunit_truthy.OCCURRENCES]]')):
        checks += [f'S_skipped_shorthand_{label} = S_truthy[{update}]',
                   f'$string_read_runtime_value(S_skipped_shorthand_{label},porigin_base) = (PSTRING_CARRIER INTERNED_STRING ([98]))',
                   f'$string_read_raw_known_base(S_skipped_shorthand_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ([98]))']
    for label, text, raw in (('empty', '', '[]'), ('two_zeroes', 'MDA=', '[48,48]'), ('nul', 'AA==', '[0]')):
        checks += lines(f'''
expression_shorthand_{label}_leaf = NScalarString (BYTES "{text}") metadata_leaf
expression_shorthand_{label}_false = NExprCastString expression_shorthand_{label}_leaf metadata_false
expression_shorthand_{label}_root = NExprTernary expression_cond ABSENT expression_shorthand_{label}_false metadata_base
S_shorthand_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_shorthand_{label}_root) :: (PCOCCURRENCE pcpath_false expression_shorthand_{label}_false) :: (PCOCCURRENCE pcpath_leaf expression_shorthand_{label}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ({raw}))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_shorthand_{label},porigin_base) = {"eps" if label == "nul" else "(PSTRING_CARRIER INTERNED_STRING (" + raw + "))"}
~$string_read_raw_known_base(S_shorthand_{label},porigin_base,pvalue_base)
''')
        if label != 'nul':
            checks.append(f'$string_read_raw_known_base(S_shorthand_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ({raw}))')
    checks += lines(r'''
expression_bool_cond = NExprCastBool expression_cond_inner metadata_cond
expression_bool_root = NExprTernary expression_bool_cond ABSENT expression_false metadata_base
S_cond_bool = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bool_root) :: (PCOCCURRENCE pcpath_cond expression_bool_cond) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_cond_bool,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_cond_bool,porigin_base,pvalue_base)
S_budget_forged_shorthand = S_bad_shorthand_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_shorthand,porigin_base,pvalue_base)
~$string_read_in_range(PSTRING_CARRIER INTERNED_STRING ([]),0)
$string_read_in_range(PSTRING_CARRIER INTERNED_STRING ([48,48]),0)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
