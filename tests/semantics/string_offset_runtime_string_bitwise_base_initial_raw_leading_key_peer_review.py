"""Nested XOR/OR preserves an exact one-byte base and the initial reference key."""

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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpBitwiseXor expression_left expression_right metadata_base)
expression_left = NExprCastString expression_left_leaf metadata_left
expression_left_leaf = NScalarString (BYTES text_left_leaf) metadata_left_leaf
expression_right = NExprBinaryOpBitwiseOr expression_right_left expression_right_right metadata_right
expression_right_left = NExprCastString expression_right_left_leaf metadata_right_left
expression_right_left_leaf = NScalarString (BYTES text_right_left_leaf) metadata_right_left_leaf
expression_right_right = NScalarString (BYTES text_right_right) metadata_right_right
$base64(text_left_leaf) = $ptascii("3")
$base64(text_right_left_leaf) = $ptascii("P")
$base64(text_right_right) = $ptascii("Q")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_left_leaf)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_left)
$origin_child((porigin_right_left),[PCFIELD 0]) = (porigin_right_left_leaf)
$origin_child((porigin_right),[PCFIELD 1]) = (porigin_right_right)
porigin_base = PORIGIN n_unit pcpath_base
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$string_read_runtime_value(S_capture,porigin_left) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("3")))
$string_read_runtime_value(S_capture,porigin_right_left) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("P")))
$string_read_runtime_value(S_capture,porigin_right_right) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")))
$string_read_runtime_value(S_capture,porigin_right) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")))
$binary_apply(S_capture,BITOR,PSTRING_CARRIER INTERNED_STRING ($ptascii("P")),PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")),18) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")))]
$binary_apply(S_capture,BITXOR,PSTRING_CARRIER INTERNED_STRING ($ptascii("3")),PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")),18) = S_capture[.RESULT = KNOWN pvalue_base]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
$string_read_raw_known_base(S_capture,porigin_right,PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")))
S_budget_bitwise = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")))]
$string_read_runtime_value(S_budget_bitwise,porigin_base) = eps
$string_read_raw_known_base(S_budget_bitwise,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_bitwise,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("Q")))
S_unused_bitwise_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PINT 999)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_bitwise_pool,porigin_base) = eps
$string_read_raw_known_base(S_unused_bitwise_pool,porigin_base,pvalue_base)
''')
    for label in ('base', 'left', 'left_leaf', 'right', 'right_left', 'right_left_leaf', 'right_right'):
        if label != 'base':
            checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                       f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})']
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label in ('base', 'left', 'right', 'right_left'):
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            text = {'left_leaf': '3', 'right_left_leaf': 'P', 'right_right': 'Q'}[label]
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = (PSTRING ($ptascii("{text}")))')
            updates += [('pool', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PSTRING ($ptascii("X")))) :: ppool.CONSTANTS]]'),
                        ('tag', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PINT 81)) :: ppool.CONSTANTS]]'),
                        ('request', f'.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{label} (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("{text}")))) :: ppool.CONSTANTS]]')]
        for kind, update in updates:
            name = f'S_bad_bitwise_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprBinaryOpPlus expression_left expression_right metadata_base'),
            ('left', 'NExprCastString expression_left_leaf eps'),
            ('left_leaf', 'NScalarString (BYTES text_left_leaf) eps'),
            ('right', 'NExprBinaryOpBitwiseXor expression_right_left expression_right_right metadata_right'),
            ('right_left', 'NExprCastString expression_right_left_leaf eps'),
            ('right_left_leaf', 'NScalarString (BYTES text_right_left_leaf) eps'),
            ('right_right', 'NScalarString (BYTES text_right_right) eps')):
        checks += [f'S_bad_bitwise_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_bitwise_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_bitwise_{label}_source,porigin_base,pvalue_base)']
    for label, text, raw in (
            ('empty', '', '[]'), ('multibyte', 'MzM=', '[51,51]'),
            ('nul_operand', 'AA==', '[0]'), ('nul_result', 'UQ==', '[81]')):
        checks += lines(f'''
expression_bitwise_{label}_leaf = NScalarString (BYTES "{text}") metadata_left_leaf
expression_bitwise_{label}_left = NExprCastString expression_bitwise_{label}_leaf metadata_left
expression_bitwise_{label}_root = NExprBinaryOpBitwiseXor expression_bitwise_{label}_left expression_right metadata_base
S_bitwise_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bitwise_{label}_root) :: (PCOCCURRENCE pcpath_left expression_bitwise_{label}_left) :: (PCOCCURRENCE pcpath_left_leaf expression_bitwise_{label}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left_leaf (PSTRING ({raw}))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_bitwise_{label},porigin_base) = eps
~$string_read_raw_known_base(S_bitwise_{label},porigin_base,pvalue_base)
''')
    checks += lines(r'''
S_unary_bitwise = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprBitwiseNot expression_left metadata_base)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_unary_bitwise,porigin_base) = (PSTRING_CARRIER INTERNED_STRING ([204]))
~$string_read_raw_known_base(S_unary_bitwise,porigin_base,PSTRING_CARRIER INTERNED_STRING ([204]))
S_budget_forged_bitwise = S_bad_bitwise_right_left_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_bitwise,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
