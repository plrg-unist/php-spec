"""Truthy one-byte STRING bitwise operators keep their own shorthand headers."""

from string_offset_initial_raw_leading_key_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)'),
            ('STRING_LEADING 1}', 'STRING_LEADING 0}'),
            ('$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (1)', '$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (0)'),
            ('$string_read_raw_saved(S_capture,pstringread) = (1)', '$string_read_raw_saved(S_capture,pstringread) = (0)'),
            ('$string_read_raw_saved(S,pstringread) = (1)', '$string_read_raw_saved(S,pstringread) = (0)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    body = body.replace('abc', 'b').replace('1x', '0x').replace('-0x', '-1x')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond ABSENT expression_false metadata)
expression_cond = NExprBinaryOpBitwiseAnd expression_left expression_right metadata_cond
expression_left = NExprCastString expression_left_leaf metadata_left
expression_right = NExprCastString expression_right_leaf metadata_right
expression_left_leaf = NScalarString (BYTES text_left_leaf) metadata_left_leaf
expression_right_leaf = NScalarString (BYTES text_right_leaf) metadata_right_leaf
$base64(text_left_leaf) = [99]
$base64(text_right_leaf) = [98]
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [88]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_left_leaf)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_leaf)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_left_leaf) = (PSTRING ([99]))
$compiled_read(S_capture,porigin_right_leaf) = (PSTRING ([98]))
$compiled_read(S_capture,porigin_leaf) = (PSTRING ([88]))
$string_read_runtime_value(S_capture,porigin_left) = (PSTRING_CARRIER INTERNED_STRING ([99]))
$string_read_runtime_value(S_capture,porigin_right) = (PSTRING_CARRIER INTERNED_STRING ([98]))
$binary_apply(S_capture,BITAND,PSTRING_CARRIER INTERNED_STRING ([99]),PSTRING_CARRIER INTERNED_STRING ([98]),12) = S_capture[.RESULT = KNOWN pkeyread.BASE]
$string_read_runtime_value(S_capture,porigin_cond) = (pkeyread.BASE)
$truth_value(S_capture,pkeyread.BASE,12) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_capture,porigin_false) = (PSTRING_CARRIER INTERNED_STRING ([88]))
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([98]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([98]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([88]))
S_budget_string_binary = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([88]))]
$string_read_runtime_value(S_budget_string_binary,porigin_base) = eps
$string_read_raw_known_base(S_budget_string_binary,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_string_binary,porigin_base,PSTRING_CARRIER INTERNED_STRING ([88]))
''')
    nodes = {
        'cond': 'NExprBinaryOpBitwiseAnd expression_left expression_right eps',
        'left': 'NExprCastString expression_left_leaf eps',
        'right': 'NExprCastString expression_right_leaf eps',
        'left_leaf': 'NScalarString (BYTES text_left_leaf) eps',
        'right_leaf': 'NScalarString (BYTES text_right_leaf) eps',
        'false': 'NExprCastString expression_inner eps',
        'inner': 'NExprCastString expression_leaf eps',
        'leaf': 'NScalarString (BYTES text_leaf) eps'}
    for label in ('base', *nodes):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                   f'$compiled_precision(S_capture,(porigin_{label})) = (14)']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label in ('left_leaf', 'right_leaf', 'leaf'):
            updates.append(('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 12 false) :: pcode.EXPRESSIONS]]'))
        else:
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 12 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_changed_string_binary_{label}_{kind}'
            skipped = label in ('false', 'inner', 'leaf')
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = ' + ('(pkeyread.BASE)' if skipped else 'eps'),
                       f'{"" if skipped else "~"}$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
        if label in ('left_leaf', 'right_leaf', 'leaf'):
            state = f'S_zero_line_string_binary_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pkeyread.BASE)',
                       f'$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
        if label in nodes:
            state = f'S_changed_string_binary_{label}_source'
            skipped = label in ('inner', 'leaf')
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = ' + ('(pkeyread.BASE)' if skipped else 'eps'),
                       f'{"" if skipped else "~"}$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    for at, value_bytes, wrong in (('left_leaf', 99, 100), ('right_leaf', 98, 99)):
        for label, value in (('bytes', f'PSTRING ([{wrong}])'), ('type', f'PINT {value_bytes}'),
                             ('header', f'PSTRING_CARRIER (REQUEST_STRING 0) ([{value_bytes}])')):
            state = f'S_bad_string_binary_{at}_{label}'
            checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{at} ({value})) :: ppool.CONSTANTS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_forged_budget_string_binary = S_bad_string_binary_left_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_forged_budget_string_binary,porigin_base,pkeyread.BASE)
S_skipped_string_binary_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 7)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_skipped_string_binary_pool,porigin_false) = eps
$string_read_runtime_value(S_skipped_string_binary_pool,porigin_base) = (pkeyread.BASE)
$string_read_raw_known_base(S_skipped_string_binary_pool,porigin_base,pkeyread.BASE)
''')
    for label, node, left_encoded, right_encoded, left, right, result in (
            ('falsey', 'NExprBinaryOpBitwiseAnd', 'MQ==', 'MA==', '[49]', '[48]', '[88]'),
            ('or', 'NExprBinaryOpBitwiseOr', 'Yw==', 'Yg==', '[99]', '[98]', '[99]'),
            ('xor', 'NExprBinaryOpBitwiseXor', 'Yw==', 'Yg==', '[99]', '[98]', '[1]'),
            ('nul_result', 'NExprBinaryOpBitwiseAnd', 'Yw==', 'BA==', '[99]', '[4]', None),
            ('multibyte', 'NExprBinaryOpBitwiseAnd', 'Y2M=', 'YmI=', '[99,99]', '[98,98]', None)):
        checks += [f'expression_{label}_left_leaf = NScalarString (BYTES "{left_encoded}") metadata_left_leaf',
                   f'expression_{label}_right_leaf = NScalarString (BYTES "{right_encoded}") metadata_right_leaf',
                   f'expression_{label}_left = NExprCastString expression_{label}_left_leaf metadata_left',
                   f'expression_{label}_right = NExprCastString expression_{label}_right_leaf metadata_right',
                   f'expression_{label}_cond = {node} expression_{label}_left expression_{label}_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata',
                   f'S_{label}_string_binary = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_left expression_{label}_left) :: (PCOCCURRENCE pcpath_right expression_{label}_right) :: (PCOCCURRENCE pcpath_left_leaf expression_{label}_left_leaf) :: (PCOCCURRENCE pcpath_right_leaf expression_{label}_right_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left_leaf (PSTRING ({left}))) :: (PCONSTANT pcpath_right_leaf (PSTRING ({right}))) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_{label}_string_binary,porigin_base) = ' + (f'(PSTRING_CARRIER INTERNED_STRING ({result}))' if result is not None else 'eps'),
                   f'~$string_read_raw_known_base(S_{label}_string_binary,porigin_base,pkeyread.BASE)']
        if result is not None:
            checks.append(f'$string_read_raw_known_base(S_{label}_string_binary,porigin_base,PSTRING_CARRIER INTERNED_STRING ({result}))')
        if label == 'falsey':
            checks.append('$string_read_runtime_value(S_falsey_string_binary,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([48]))')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
