"""Quiet FLOAT subtraction selects the falsey string and preserves the old key."""

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
expression_cond = NExprBinaryOpMinus expression_left expression_right metadata_cond
expression_left = NExprCastDouble expression_atom metadata_left
expression_atom = NScalarInt (INTEGER 1) metadata_atom
expression_right = NScalarFloat (FLOAT "3ff0000000000000") metadata_right
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
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
$compiled_read(S_capture,porigin_atom) = (PINT 1)
$compiled_read(S_capture,porigin_right) = (PFLOAT 4607182418800017408)
$string_read_runtime_value(S_capture,porigin_atom) = (PINT 1)
$string_read_runtime_value(S_capture,porigin_left) = (PFLOAT 4607182418800017408)
$string_read_runtime_value(S_capture,porigin_right) = (PFLOAT 4607182418800017408)
$binary_apply(S_capture,SUBTRACT,PFLOAT 4607182418800017408,PFLOAT 4607182418800017408,18) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$string_read_runtime_value(S_capture,porigin_cond) = (PFLOAT 0)
$truth_value(S_capture,PFLOAT 0,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$truth_value(S_capture,pvalue_base,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
S_budget_arithmetic = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_runtime_value(S_budget_arithmetic,porigin_base) = eps
$string_read_raw_known_base(S_budget_arithmetic,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_arithmetic,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
''')
    nodes = {
        'cond': 'NExprBinaryOpMinus expression_left expression_right eps',
        'left': 'NExprCastDouble expression_atom eps',
        'atom': 'NScalarInt (INTEGER 1) eps',
        'right': 'NScalarFloat (FLOAT "3ff0000000000000") eps',
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
            state = f'S_bad_arithmetic_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('atom', 'right', 'leaf'):
            state = f'S_zero_line_arithmetic_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in nodes:
            state = f'S_bad_arithmetic_{label}_source'
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, path, value in (('atom_type', 'atom', 'PBOOL true'), ('atom_value', 'atom', 'PINT 2'),
                               ('right_type', 'right', 'PINT 1'), ('leaf_type', 'leaf', 'PINT 0'),
                               ('leaf_bytes', 'leaf', 'PSTRING ([49])'),
                               ('leaf_header', 'leaf', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        state = f'S_bad_arithmetic_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{path} ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_forged_budget_arithmetic = S_bad_arithmetic_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_arithmetic,porigin_base,pvalue_base)
S_raw_zero_arithmetic = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PFLOAT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_raw_zero_arithmetic,porigin_right) = (PFLOAT 0)
$string_read_runtime_value(S_raw_zero_arithmetic,porigin_cond) = (PFLOAT 4607182418800017408)
$string_read_runtime_value(S_raw_zero_arithmetic,porigin_base) = (PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_raw_zero_arithmetic,porigin_base,pvalue_base)
expression_two_atom = NScalarInt (INTEGER 2) metadata_atom
expression_two_left = NExprCastDouble expression_two_atom metadata_left
expression_two_cond = NExprBinaryOpMinus expression_two_left expression_right metadata_cond
expression_two_base = NExprTernary expression_two_cond ABSENT expression_false metadata_base
ppool_two_arithmetic = ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 2)) :: ppool.CONSTANTS]
S_two_arithmetic = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_two_base) :: (PCOCCURRENCE pcpath_cond expression_two_cond) :: (PCOCCURRENCE pcpath_left expression_two_left) :: (PCOCCURRENCE pcpath_atom expression_two_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool_two_arithmetic]]
$string_read_runtime_value(S_two_arithmetic,porigin_cond) = (PFLOAT 4607182418800017408)
$string_read_runtime_value(S_two_arithmetic,porigin_base) = (PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_two_arithmetic,porigin_base,pvalue_base)
S_skip_arithmetic = S_two_arithmetic[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool_two_arithmetic[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool_two_arithmetic.CONSTANTS]]]
$string_read_runtime_value(S_skip_arithmetic,porigin_false) = eps
$string_read_runtime_value(S_skip_arithmetic,porigin_base) = (PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_skip_arithmetic,porigin_base,pvalue_base)
expression_zero_right = NScalarFloat (FLOAT "0000000000000000") metadata_right
expression_divzero_cond = NExprBinaryOpDiv expression_left expression_zero_right metadata_cond
expression_divzero_base = NExprTernary expression_divzero_cond ABSENT expression_false metadata_base
S_divzero_arithmetic = S_raw_zero_arithmetic[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_divzero_base) :: (PCOCCURRENCE pcpath_cond expression_divzero_cond) :: (PCOCCURRENCE pcpath_right expression_zero_right) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_divzero_arithmetic,porigin_cond) = eps
$string_read_runtime_value(S_divzero_arithmetic,porigin_base) = eps
~$string_read_raw_known_base(S_divzero_arithmetic,porigin_base,pvalue_base)
''')
    for label, node, bits in (('add', 'NExprBinaryOpPlus', 4611686018427387904),
                               ('mul', 'NExprBinaryOpMul', 4607182418800017408),
                               ('div', 'NExprBinaryOpDiv', 4607182418800017408)):
        checks += [f'expression_{label}_cond = {node} expression_left expression_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata_base',
                   f'S_{label}_arithmetic = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_{label}_arithmetic,porigin_cond) = (PFLOAT {bits})',
                   f'$string_read_runtime_value(S_{label}_arithmetic,porigin_base) = (PFLOAT {bits})',
                   f'~$string_read_raw_known_base(S_{label}_arithmetic,porigin_base,pvalue_base)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
