"""Mixed arms authenticate either selected carrier without demanding the other."""

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
expression_true = NScalarString (BYTES text_true) metadata_true
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_true) = $ptascii("unused")
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cond_leaf)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_true)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL false)
$truth_value(S_capture,PBOOL false,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$compiled_read(S_capture,porigin_true) = (PSTRING ($ptascii("unused")))
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))
S_budget_mixed = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))]
$string_read_runtime_value(S_budget_mixed,porigin_base) = eps
$string_read_raw_known_base(S_budget_mixed,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_mixed,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))
''')
    for label in ('base', 'cond', 'cond_leaf', 'true', 'false', 'inner', 'leaf'):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        if label == 'true':
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
            name = f'S_bad_mixed_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprTernary expression_cond expression_true (NExprCastBool expression_inner metadata_false) metadata_base'),
            ('cond', 'NExprCastBool expression_cond_leaf eps'),
            ('cond_leaf', 'NScalarInt (INTEGER 0) eps'),
            ('true', 'NScalarString (BYTES text_true) eps'),
            ('false', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_mixed_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_mixed_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_mixed_{label}_source,porigin_base,pvalue_base)']
    for label, update in (
            ('code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_true 0 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_true 17) :: ppool.CONSTANTS]]'),
            ('pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_true (PSTRING_CARRIER (REQUEST_STRING 99) ([88]))) :: ppool.CONSTANTS]]')):
        checks += [f'S_skipped_raw_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_skipped_raw_{label},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base(S_skipped_raw_{label},porigin_base,pvalue_base)']
    checks += lines(r'''
expression_selected_cond_leaf = NScalarInt (INTEGER 1) metadata_cond_leaf
expression_selected_cond = NExprCastBool expression_selected_cond_leaf metadata_cond
expression_selected_root = NExprTernary expression_selected_cond expression_true expression_false metadata_base
S_selected_raw = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_selected_root) :: (PCOCCURRENCE pcpath_cond expression_selected_cond) :: (PCOCCURRENCE pcpath_cond_leaf expression_selected_cond_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_leaf (PINT 1)) :: ppool.CONSTANTS]]]
S_selected_raw.SOURCES = [pcunit_selected]
S_selected_raw.POOLS = [ppool_selected]
$string_read_runtime_value(S_selected_raw,porigin_base) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))
$string_read_raw_known_base(S_selected_raw,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))
~$string_read_raw_known_base(S_selected_raw,porigin_base,pvalue_base)
''')
    for label, update in (
            ('precision', '.POOLS = [ppool_selected[.CONSTANTS = (PCCPRECISION pcpath_true 17) :: ppool_selected.CONSTANTS]]'),
            ('emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_true 18 false) :: pcode.EXPRESSIONS]]'),
            ('pool', '.POOLS = [ppool_selected[.CONSTANTS = (PCONSTANT pcpath_true (PSTRING ([48]))) :: ppool_selected.CONSTANTS]]'),
            ('request', '.POOLS = [ppool_selected[.CONSTANTS = (PCONSTANT pcpath_true (PSTRING_CARRIER (REQUEST_STRING 99) ($ptascii("unused")))) :: ppool_selected.CONSTANTS]]')):
        checks += [f'S_bad_raw_{label} = S_selected_raw[{update}]',
                   f'$string_read_runtime_value(S_bad_raw_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_raw_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))']
    for label, update in (
            ('code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool_selected[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool_selected.CONSTANTS]]'),
            ('pool', '.POOLS = [ppool_selected[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING_CARRIER (REQUEST_STRING 99) ([48]))) :: ppool_selected.CONSTANTS]]'),
            ('descendant', '.SOURCES = [pcunit_selected[.OCCURRENCES = (PCOCCURRENCE pcpath_leaf (NScalarString (BYTES "AA==") metadata_leaf)) :: pcunit_selected.OCCURRENCES]]')):
        checks += [f'S_skipped_cast_{label} = S_selected_raw[{update}]',
                   f'$string_read_runtime_value(S_skipped_cast_{label},porigin_base) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))',
                   f'$string_read_raw_known_base(S_skipped_cast_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))']
    for label, text, raw in (('empty', '', '[]'), ('nul', 'AA==', '[0]')):
        checks += lines(f'''
expression_mixed_{label}_true = NScalarString (BYTES "{text}") metadata_true
expression_mixed_{label}_root = NExprTernary expression_selected_cond expression_mixed_{label}_true expression_false metadata_base
S_mixed_{label} = S_selected_raw[.SOURCES = [pcunit_selected[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_mixed_{label}_root) :: (PCOCCURRENCE pcpath_true expression_mixed_{label}_true) :: pcunit_selected.OCCURRENCES]]][.POOLS = [ppool_selected[.CONSTANTS = (PCONSTANT pcpath_true (PSTRING ({raw}))) :: ppool_selected.CONSTANTS]]]
$string_read_runtime_value(S_mixed_{label},porigin_base) = {"eps" if label == "nul" else "(PSTRING_CARRIER INTERNED_STRING ([]))"}
~$string_read_raw_known_base(S_mixed_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("unused")))
''')
        if label == 'empty':
            checks.append('$string_read_raw_known_base(S_mixed_empty,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))')
    checks += lines(r'''
expression_true_bool = NExprCastBool expression_cond_leaf metadata_true
expression_bool_root = NExprTernary expression_cond expression_true_bool expression_false metadata_base
S_true_bool = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bool_root) :: (PCOCCURRENCE pcpath_true expression_true_bool) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_true_bool,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_true_bool,porigin_base,pvalue_base)
S_budget_forged_mixed = S_bad_mixed_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_mixed,porigin_base,pvalue_base)
~$string_read_in_range(PSTRING_CARRIER INTERNED_STRING ([]),0)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
