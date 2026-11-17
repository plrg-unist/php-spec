"""An emitted INT cast preserves the selected fallback and frozen reference key."""

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
expression_cond = NExprCastInt expression_cond_leaf metadata_cond
expression_cond_leaf = NExprConstFetch (NName (BYTES text_cond) metadata_name) metadata_cond_leaf
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_cond) = $ptascii("null")
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cond_leaf)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_cond_leaf) = (PNULL)
$compiled_identity_value(S_capture,porigin_cond_leaf) = (PNULL)
$cast_apply(S_capture,CASTINT,PNULL,18) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_runtime_value(S_capture,porigin_cond) = (PINT 0)
$truth_value(S_capture,PINT 0,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([]))]
$string_read_runtime_value(S_budget_cast,porigin_base) = eps
$string_read_raw_known_base(S_budget_cast,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
''')
    for label in ('base', 'cond', 'cond_leaf', 'false', 'inner', 'leaf'):
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
            updates += [('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            name = f'S_bad_cast_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
        if label in ('cond_leaf', 'leaf'):
            name = f'S_raw_zero_line_cast_{label}'
            checks += [f'{name} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({name},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprTernary expression_cond ABSENT (NExprCastBool expression_inner metadata_false) metadata_base'),
            ('cond', 'NExprCastInt expression_cond_leaf eps'),
            ('cond_leaf', 'NExprConstFetch (NName (BYTES text_cond) metadata_name) eps'),
            ('false', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_cast_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_source,porigin_base,pvalue_base)']
    for label, value in (('bytes', 'PSTRING ([49])'), ('type', 'PBOOL false'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        checks += [f'S_bad_cast_leaf_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_cast_leaf_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_cast_leaf_{label},porigin_base,pvalue_base)']
    checks += lines(r'''
S_budget_forged_cast = S_bad_cast_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_cast,porigin_base,pvalue_base)
S_false_pool_cast = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_leaf (PBOOL false)) :: ppool.CONSTANTS]]]
$compiled_identity_value(S_false_pool_cast,porigin_cond_leaf) = (PBOOL false)
$string_read_runtime_value(S_false_pool_cast,porigin_cond) = (PINT 0)
$string_read_runtime_value(S_false_pool_cast,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_false_pool_cast,porigin_base,pvalue_base)
ppool_true_cast = ppool[.CONSTANTS = (PCONSTANT pcpath_cond_leaf (PBOOL true)) :: ppool.CONSTANTS]
S_true_pool_cast = S_capture[.POOLS = [ppool_true_cast]]
$string_read_runtime_value(S_true_pool_cast,porigin_cond) = (PINT 1)
$string_read_runtime_value(S_true_pool_cast,porigin_base) = (PINT 1)
~$string_read_raw_known_base(S_true_pool_cast,porigin_base,pvalue_base)
S_skipped_fallback_cast = S_true_pool_cast[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool_true_cast[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool_true_cast.CONSTANTS]]]
$string_read_runtime_value(S_skipped_fallback_cast,porigin_base) = (PINT 1)
~$string_read_raw_known_base(S_skipped_fallback_cast,porigin_base,pvalue_base)
''')
    for label, constructor, value in (('bool', 'NExprCastBool', 'PBOOL false'),
                                       ('float', 'NExprCastDouble', 'PFLOAT 0')):
        checks += lines(f'''
expression_other_{label}_cond = {constructor} expression_cond_leaf metadata_cond
expression_other_{label}_root = NExprTernary expression_other_{label}_cond ABSENT expression_false metadata_base
S_other_{label}_cast = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_other_{label}_root) :: (PCOCCURRENCE pcpath_cond expression_other_{label}_cond) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_other_{label}_cast,porigin_cond) = ({value})
$string_read_runtime_value(S_other_{label}_cast,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_other_{label}_cast,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
