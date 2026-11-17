"""A falsey raw condition demands only its selected nested string-cast fallback."""

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
expression_cond = NScalarString (BYTES text_cond) metadata_cond
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_cond) = eps
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$string_read_runtime_value(S_capture,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([]))
$truth_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([]),18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
S_budget_raw_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([]))]
$string_read_runtime_value(S_budget_raw_cast,porigin_base) = eps
$string_read_raw_known_base(S_budget_raw_cast,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_raw_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
''')
    for label in ('base', 'cond', 'false', 'inner', 'leaf'):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label not in ('cond', 'leaf'):
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            raw = '[]' if label == 'cond' else '[48]'
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = (PSTRING ({raw}))')
            updates += [('pool', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PSTRING ([49]))) :: ppool.CONSTANTS]]'),
                        ('request', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PSTRING_CARRIER (REQUEST_STRING 99) ({raw}))) :: ppool.CONSTANTS]]'),
                        ('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            name = f'S_bad_raw_cast_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprTernary expression_cond ABSENT (NExprCastBool expression_inner metadata_false) metadata_base'),
            ('cond', 'NScalarString (BYTES text_cond) eps'),
            ('false', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_raw_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_raw_cast_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_raw_cast_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_cond_zero_line = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 0 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_cond_zero_line,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_cond_zero_line,porigin_base,pvalue_base)
S_budget_forged_raw_cast = S_bad_raw_cast_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_raw_cast,porigin_base,pvalue_base)
''')
    for label, text, raw, truth in (
            ('zero', 'MA==', '[48]', False),
            ('two_zeroes', 'MDA=', '[48,48]', True),
            ('nul', 'AA==', '[0]', None)):
        selected = raw if truth else '[48]'
        result = 'eps' if truth is None else f'(PSTRING_CARRIER INTERNED_STRING ({selected}))'
        checks += lines(f'''
expression_raw_{label}_cond = NScalarString (BYTES "{text}") metadata_cond
expression_raw_{label}_root = NExprTernary expression_raw_{label}_cond ABSENT expression_false metadata_base
S_raw_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_raw_{label}_root) :: (PCOCCURRENCE pcpath_cond expression_raw_{label}_cond) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PSTRING ({raw}))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_raw_{label},porigin_base) = {result}
''')
        if truth is None:
            checks.append(f'~$string_read_raw_known_base(S_raw_{label},porigin_base,pvalue_base)')
        else:
            checks.append(f'$string_read_raw_known_base(S_raw_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ({selected}))')
    checks += lines(r'''
S_raw_two_zeroes.SOURCES = [pcunit_truthy]
S_raw_two_zeroes.POOLS = [ppool_truthy]
S_truthy_bad_source = S_raw_two_zeroes[.SOURCES = [pcunit_truthy[.OCCURRENCES = (PCOCCURRENCE pcpath_false (NExprCastString expression_inner eps)) :: pcunit_truthy.OCCURRENCES]]]
$string_read_runtime_value(S_truthy_bad_source,porigin_base) = eps
~$string_read_raw_known_base(S_truthy_bad_source,porigin_base,PSTRING_CARRIER INTERNED_STRING ([48,48]))
''')
    for label, update in (
            ('code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool_truthy[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool_truthy.CONSTANTS]]'),
            ('pool', '.POOLS = [ppool_truthy[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING_CARRIER (REQUEST_STRING 99) ([48]))) :: ppool_truthy.CONSTANTS]]'),
            ('descendant', '.SOURCES = [pcunit_truthy[.OCCURRENCES = (PCOCCURRENCE pcpath_inner (NScalarString (BYTES "AA==") metadata_inner)) :: pcunit_truthy.OCCURRENCES]]')):
        checks += [f'S_skipped_raw_cast_{label} = S_raw_two_zeroes[{update}]',
                   f'$string_read_runtime_value(S_skipped_raw_cast_{label},porigin_base) = (PSTRING_CARRIER INTERNED_STRING ([48,48]))',
                   f'$string_read_raw_known_base(S_skipped_raw_cast_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ([48,48]))']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
