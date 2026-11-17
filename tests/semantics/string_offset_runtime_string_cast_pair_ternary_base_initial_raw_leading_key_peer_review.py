"""Only the selected string-cast arm supplies the frozen raw-key base."""

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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond expression_true expression_false metadata_base)
expression_cond = NExprCastBool expression_cond_leaf metadata_cond
expression_cond_leaf = NScalarInt (INTEGER 0) metadata_cond_leaf
expression_true = NExprCastString expression_unused metadata_true
expression_unused = NExprConstFetch (NName (BYTES text_unused) metadata_name) metadata_unused
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_unused) = $ptascii("MissingFallback")
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cond_leaf)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_true)
$origin_child((porigin_true),[PCFIELD 0]) = (porigin_unused)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL false)
$truth_value(S_capture,PBOOL false,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_true) = eps
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([88]))
S_budget_ternary = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([88]))]
$string_read_runtime_value(S_budget_ternary,porigin_base) = eps
$string_read_raw_known_base(S_budget_ternary,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_ternary,porigin_base,PSTRING_CARRIER INTERNED_STRING ([88]))
''')
    for label in ('base', 'cond', 'cond_leaf', 'true', 'unused', 'false', 'inner', 'leaf'):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        if label in ('true', 'unused'):
            continue
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label not in ('cond_leaf', 'leaf'):
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            value = 'PINT 0' if label == 'cond_leaf' else 'PSTRING ([48])'
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = ({value})')
            updates += [('pool', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PSTRING ([49]))) :: ppool.CONSTANTS]]')]
        for kind, update in updates:
            name = f'S_bad_ternary_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprTernary expression_cond expression_true (NExprCastBool expression_inner metadata_false) metadata_base'),
            ('cond', 'NExprCastBool expression_cond_leaf eps'),
            ('cond_leaf', 'NScalarInt (INTEGER 0) eps'),
            ('true', 'NExprCastString expression_unused eps'),
            ('false', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_ternary_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_ternary_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_ternary_{label}_source,porigin_base,pvalue_base)']
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_true 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_true 18 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_true 17) :: ppool.CONSTANTS]]'),
            ('pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_true (PSTRING_CARRIER (REQUEST_STRING 99) ([88]))) :: ppool.CONSTANTS]]'),
            ('descendant', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused (NScalarString (BYTES "AA==") metadata_unused)) :: pcunit.OCCURRENCES]]')):
        checks += [f'S_skipped_ternary_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_skipped_ternary_{label},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base(S_skipped_ternary_{label},porigin_base,pvalue_base)']
    for label, text, raw in (('empty', '', '[]'), ('two_zeroes', 'MDA=', '[48,48]'), ('nul', 'AA==', '[0]')):
        checks += lines(f'''
expression_ternary_{label}_leaf = NScalarString (BYTES "{text}") metadata_leaf
expression_ternary_{label}_inner = NExprCastString expression_ternary_{label}_leaf metadata_inner
expression_ternary_{label}_false = NExprCastString expression_ternary_{label}_inner metadata_false
expression_ternary_{label}_root = NExprTernary expression_cond expression_true expression_ternary_{label}_false metadata_base
S_ternary_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_ternary_{label}_root) :: (PCOCCURRENCE pcpath_false expression_ternary_{label}_false) :: (PCOCCURRENCE pcpath_inner expression_ternary_{label}_inner) :: (PCOCCURRENCE pcpath_leaf expression_ternary_{label}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ({raw}))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_ternary_{label},porigin_base) = {"eps" if label == "nul" else "(PSTRING_CARRIER INTERNED_STRING (" + raw + "))"}
~$string_read_raw_known_base(S_ternary_{label},porigin_base,pvalue_base)
''')
        if label != 'nul':
            checks.append(f'$string_read_raw_known_base(S_ternary_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ({raw}))')
    checks += lines(r'''
~$string_read_in_range(PSTRING_CARRIER INTERNED_STRING ([]),0)
$string_read_in_range(PSTRING_CARRIER INTERNED_STRING ([48,48]),0)
expression_true_bool = NExprCastBool expression_unused metadata_true
expression_bool_root = NExprTernary expression_cond expression_true_bool expression_false metadata_base
S_true_bool = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bool_root) :: (PCOCCURRENCE pcpath_true expression_true_bool) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_true_bool,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_true_bool,porigin_base,pvalue_base)
expression_short_root = NExprTernary expression_cond ABSENT expression_false metadata_base
S_short = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_short_root) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_short,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_short,porigin_base,pvalue_base)
S_budget_forged_ternary = S_bad_ternary_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_ternary,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
