"""Integer-zero shifts select the falsey string without weakening its authority."""

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
expression_cond = NExprBinaryOpShiftLeft expression_left expression_right metadata_cond
expression_left = NExprCastInt expression_atom metadata_left
expression_atom = NExprConstFetch (NName (BYTES text_null) metadata_null) metadata_atom
expression_right = NScalarInt (INTEGER 2) metadata_right
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_null) = $ptascii("null")
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_atom) = (PNULL)
$compiled_read(S_capture,porigin_right) = (PINT 2)
$string_read_runtime_value(S_capture,porigin_atom) = (PNULL)
$string_read_runtime_value(S_capture,porigin_left) = (PINT 0)
$string_read_runtime_value(S_capture,porigin_right) = (PINT 2)
$binary_apply(S_capture,SHIFTLEFT,PINT 0,PINT 2,18) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_runtime_value(S_capture,porigin_cond) = (PINT 0)
$truth_value(S_capture,PINT 0,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$truth_value(S_capture,pvalue_base,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
S_budget_integer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_runtime_value(S_budget_integer,porigin_base) = eps
$string_read_raw_known_base(S_budget_integer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_integer,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
''')
    nodes = {
        'cond': 'NExprBinaryOpShiftLeft expression_left expression_right eps',
        'left': 'NExprCastInt expression_atom eps',
        'atom': 'NExprConstFetch (NName (BYTES text_null) metadata_null) eps',
        'right': 'NScalarInt (INTEGER 2) eps',
        'false': 'NExprCastString expression_inner eps',
        'inner': 'NExprCastString expression_leaf eps',
        'leaf': 'NScalarString (BYTES text_leaf) eps'}
    for label in ('base', *nodes):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                   f'$compiled_precision(S_capture,(porigin_{label})) = (14)']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label in ('atom', 'right', 'leaf'):
            updates.append(('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 false) :: pcode.EXPRESSIONS]]'))
        else:
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_bad_integer_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('atom', 'right', 'leaf'):
            state = f'S_zero_line_integer_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in nodes:
            state = f'S_bad_integer_{label}_source'
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, value in (('type', 'PINT 0'), ('bytes', 'PSTRING ([49])'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        state = f'S_bad_integer_leaf_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_forged_budget_integer = S_bad_integer_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_integer,porigin_base,pvalue_base)
expression_true_atom = NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_null) metadata_atom
expression_true_left = NExprCastInt expression_true_atom metadata_left
expression_true_cond = NExprBinaryOpShiftLeft expression_true_left expression_right metadata_cond
expression_true_base = NExprTernary expression_true_cond ABSENT expression_false metadata_base
ppool_true_integer = ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PBOOL true)) :: ppool.CONSTANTS]
S_true_integer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_true_base) :: (PCOCCURRENCE pcpath_cond expression_true_cond) :: (PCOCCURRENCE pcpath_left expression_true_left) :: (PCOCCURRENCE pcpath_atom expression_true_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool_true_integer]]
$string_read_runtime_value(S_true_integer,porigin_left) = (PINT 1)
$string_read_runtime_value(S_true_integer,porigin_cond) = (PINT 4)
$string_read_runtime_value(S_true_integer,porigin_base) = (PINT 4)
~$string_read_raw_known_base(S_true_integer,porigin_base,pvalue_base)
S_skip_integer = S_true_integer[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool_true_integer[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool_true_integer.CONSTANTS]]]
$string_read_runtime_value(S_skip_integer,porigin_false) = eps
$string_read_runtime_value(S_skip_integer,porigin_base) = (PINT 4)
~$string_read_raw_known_base(S_skip_integer,porigin_base,pvalue_base)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_negative_leaf)
porigin_negative_leaf = PORIGIN n_unit pcpath_negative_leaf
expression_negative_right = NExprUnaryMinus expression_right metadata_right
expression_negative_cond = NExprBinaryOpShiftLeft expression_left expression_negative_right metadata_cond
expression_negative_base = NExprTernary expression_negative_cond ABSENT expression_false metadata_base
S_negative_integer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_negative_base) :: (PCOCCURRENCE pcpath_cond expression_negative_cond) :: (PCOCCURRENCE pcpath_right expression_negative_right) :: (PCOCCURRENCE pcpath_negative_leaf expression_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_negative_leaf (PINT 2)) :: (PCCPRECISION pcpath_negative_leaf 14) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 false) :: (CODEEXPR pcpath_negative_leaf 18 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_negative_integer,porigin_right) = (PINT (-2))
$string_read_runtime_value(S_negative_integer,porigin_cond) = eps
$string_read_runtime_value(S_negative_integer,porigin_base) = eps
~$string_read_raw_known_base(S_negative_integer,porigin_base,pvalue_base)
''')
    for label, node, integer in (
            ('mod', 'NExprBinaryOpMod', 2), ('right', 'NExprBinaryOpShiftRight', 2),
            ('and', 'NExprBinaryOpBitwiseAnd', 2), ('or', 'NExprBinaryOpBitwiseOr', 0),
            ('xor', 'NExprBinaryOpBitwiseXor', 0), ('wide', 'NExprBinaryOpShiftLeft', 64),
            ('power', 'NExprBinaryOpPow', 2)):
        checks += [f'expression_{label}_right = NScalarInt (INTEGER {integer}) metadata_right',
                   f'expression_{label}_cond = {node} expression_left expression_{label}_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata_base',
                   f'S_{label}_integer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_right expression_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PINT {integer})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_{label}_integer,porigin_cond) = (PINT 0)',
                   f'$string_read_runtime_value(S_{label}_integer,porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base(S_{label}_integer,porigin_base,pvalue_base)']
    for label, raw, value, quiet in (
            ('integral', 'NScalarFloat (FLOAT "4000000000000000") metadata_right', 'PFLOAT 4611686018427387904', True),
            ('fractional', 'NScalarFloat (FLOAT "3ff8000000000000") metadata_right', 'PFLOAT 4609434218613702656', False),
            ('leading', 'NScalarString (BYTES "Mng=") metadata_right', 'PSTRING ($ptascii("2x"))', False)):
        checks += [f'expression_{label}_right = {raw}',
                   f'expression_{label}_cond = NExprBinaryOpShiftLeft expression_left expression_{label}_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata_base',
                   f'S_{label}_integer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_right expression_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_{label}_integer,porigin_cond) = ' + ('(PINT 0)' if quiet else 'eps'),
                   f'$string_read_runtime_value(S_{label}_integer,porigin_base) = ' + ('(pvalue_base)' if quiet else 'eps'),
                   f'{"" if quiet else "~"}$string_read_raw_known_base(S_{label}_integer,porigin_base,pvalue_base)']
    checks += lines(r'''
expression_string_left = NScalarString (BYTES "MA==") metadata_left
expression_string_right = NScalarString (BYTES "MA==") metadata_right
expression_string_cond = NExprBinaryOpBitwiseAnd expression_string_left expression_string_right metadata_cond
expression_string_base = NExprTernary expression_string_cond ABSENT expression_false metadata_base
S_string_integer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_string_base) :: (PCOCCURRENCE pcpath_cond expression_string_cond) :: (PCOCCURRENCE pcpath_left expression_string_left) :: (PCOCCURRENCE pcpath_right expression_string_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ([48]))) :: (PCONSTANT pcpath_right (PSTRING ([48]))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_string_integer,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([48]))
$string_read_runtime_value(S_string_integer,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_string_integer,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
