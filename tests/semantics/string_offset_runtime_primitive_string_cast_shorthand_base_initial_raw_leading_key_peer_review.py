"""A compiled NULL condition selects a certified nested string-cast fallback."""

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
expression_cond = NExprConstFetch (NName (BYTES text_cond) metadata_name) metadata_cond
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_cond) = $ptascii("null")
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cond_child)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
porigin_cond_child = PORIGIN n_unit pcpath_cond_child
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_cond) = (PNULL)
$type_bytes(PNULL) = $ptascii("null")
$string_read_runtime_value(S_capture,porigin_cond) = (PNULL)
$truth_value(S_capture,PNULL,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
S_budget_primitive = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([]))]
$string_read_runtime_value(S_budget_primitive,porigin_base) = eps
$string_read_raw_known_base(S_budget_primitive,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_primitive,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
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
            raw = 'PNULL' if label == 'cond' else 'PSTRING ([48])'
            pool = 'PSTRING ([49])' if label == 'cond' else 'PBOOL false'
            updates += [('pool', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} ({pool})) :: ppool.CONSTANTS]]'),
                        ('request', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PSTRING_CARRIER (REQUEST_STRING 99) ([48]))) :: ppool.CONSTANTS]]'),
                        ('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 false) :: pcode.EXPRESSIONS]]')]
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = ({raw})')
        for kind, update in updates:
            name = f'S_bad_primitive_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprTernary expression_cond ABSENT (NExprCastBool expression_inner metadata_false) metadata_base'),
            ('cond', 'NExprConstFetch (NName (BYTES text_cond) metadata_name) eps'),
            ('false', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_primitive_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_primitive_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_primitive_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_primitive_zero_line = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 0 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_primitive_zero_line,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_primitive_zero_line,porigin_base,pvalue_base)
S_budget_forged_primitive = S_bad_primitive_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_primitive,porigin_base,pvalue_base)
S_false_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL false)) :: ppool.CONSTANTS]]]
$compiled_identity_value(S_false_pool,porigin_cond) = (PBOOL false)
$string_read_runtime_value(S_false_pool,porigin_cond) = (PBOOL false)
$string_read_runtime_value(S_false_pool,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_false_pool,porigin_base,pvalue_base)
S_true_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL true)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_true_pool,porigin_base) = (PBOOL true)
~$string_read_raw_known_base(S_true_pool,porigin_base,pvalue_base)
''')
    for label, node, value in (
            ('bool', 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_name) metadata_cond', 'PBOOL true'),
            ('int', 'NScalarInt (INTEGER 1) metadata_cond', 'PINT 1'),
            ('float', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_cond', 'PFLOAT 4607182418800017408')):
        name_source = '(PCOCCURRENCE pcpath_cond_child (NName (BYTES "dHJ1ZQ==") metadata_name)) :: ' if label == 'bool' else ''
        checks += lines(f'''
expression_truthy_{label}_cond = {node}
expression_truthy_{label}_root = NExprTernary expression_truthy_{label}_cond ABSENT expression_false metadata_base
S_truthy_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_truthy_{label}_root) :: (PCOCCURRENCE pcpath_cond expression_truthy_{label}_cond) :: {name_source}pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond ({value})) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_truthy_{label},porigin_base) = ({value})
~$string_read_raw_known_base(S_truthy_{label},porigin_base,pvalue_base)
''')
    checks += lines(r'''
expression_legacy_cond = NScalarString (BYTES "MA==") metadata_cond
expression_legacy_root = NExprTernary expression_legacy_cond ABSENT expression_false metadata_base
S_legacy_string = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_legacy_root) :: (PCOCCURRENCE pcpath_cond expression_legacy_cond) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PSTRING ([48]))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_legacy_string,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_legacy_string,porigin_base,pvalue_base)
expression_emitted_child = NScalarInt (INTEGER 0) metadata_name
expression_emitted_cond = NExprCastBool expression_emitted_child metadata_cond
expression_emitted_root = NExprTernary expression_emitted_cond ABSENT expression_false metadata_base
S_emitted_cond = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_emitted_root) :: (PCOCCURRENCE pcpath_cond expression_emitted_cond) :: (PCOCCURRENCE pcpath_cond_child expression_emitted_child) :: pcunit.OCCURRENCES]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 18 false) :: (CODEEXPR pcpath_cond_child 18 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond_child 14) :: (PCONSTANT pcpath_cond_child (PINT 0)) :: ppool.CONSTANTS]]]
$compiled_read(S_emitted_cond,porigin_cond) = eps
$string_read_runtime_value(S_emitted_cond,porigin_cond) = (PBOOL false)
$string_read_runtime_value(S_emitted_cond,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_emitted_cond,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
