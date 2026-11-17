"""Completed negative-zero powers retain exact bits and the falsey fallback."""

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
expression_cond = NExprBinaryOpPow expression_left expression_right metadata_cond
expression_left = NExprUnaryMinus expression_cast metadata_left
expression_cast = NExprCastDouble expression_atom metadata_cast
expression_atom = NScalarInt (INTEGER 0) metadata_atom
expression_right = NScalarInt (INTEGER 3) metadata_right
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_atom) = (PINT 0)
$compiled_read(S_capture,porigin_right) = (PINT 3)
$string_read_runtime_value(S_capture,porigin_cast) = (PFLOAT 0)
$string_read_runtime_value(S_capture,porigin_left) = (PFLOAT 9223372036854775808)
$power_prepare(NFLOAT 9223372036854775808,NINT 3) = POWERDONE (NFLOAT 9223372036854775808) false
$binary_apply(S_capture,POWER,PFLOAT 9223372036854775808,PINT 3,18) = S_capture[.RESULT = KNOWN (PFLOAT 9223372036854775808)]
$string_read_runtime_value(S_capture,porigin_cond) = (PFLOAT 9223372036854775808)
$truth_value(S_capture,PFLOAT 9223372036854775808,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$truth_value(S_capture,pvalue_base,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
S_budget_power = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_runtime_value(S_budget_power,porigin_base) = eps
$string_read_raw_known_base(S_budget_power,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_power,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
''')
    nodes = {
        'cond': 'NExprBinaryOpPow expression_left expression_right eps',
        'left': 'NExprUnaryMinus expression_cast eps',
        'cast': 'NExprCastDouble expression_atom eps',
        'atom': 'NScalarInt (INTEGER 0) eps',
        'right': 'NScalarInt (INTEGER 3) eps',
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
            state = f'S_bad_power_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('atom', 'right', 'leaf'):
            state = f'S_zero_line_power_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in nodes:
            state = f'S_bad_power_{label}_source'
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, value in (('type', 'PINT 0'), ('bytes', 'PSTRING ([49])'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        state = f'S_bad_power_leaf_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_forged_budget_power = S_bad_power_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_power,porigin_base,pvalue_base)
''')
    for label, exponent, bits in (('even', 2, 0), ('zero', 0, 4607182418800017408)):
        checks += [f'expression_{label}_right = NScalarInt (INTEGER {exponent}) metadata_right',
                   f'expression_{label}_cond = NExprBinaryOpPow expression_left expression_{label}_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata_base',
                   f'S_{label}_power = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_right expression_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PINT {exponent})) :: ppool.CONSTANTS]]]',
                   f'$power_prepare(NFLOAT 9223372036854775808,NINT {exponent}) = POWERDONE (NFLOAT {bits}) false',
                   f'$string_read_runtime_value(S_{label}_power,porigin_cond) = (PFLOAT {bits})',
                   f'$string_read_runtime_value(S_{label}_power,porigin_base) = ' + ('(pvalue_base)' if label == 'even' else f'(PFLOAT {bits})'),
                   f'{"" if label == "even" else "~"}$string_read_raw_known_base(S_{label}_power,porigin_base,pvalue_base)']
    checks += lines(r'''
S_skip_power = S_zero_power[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PINT 0)) :: (PCCPRECISION pcpath_false 17) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_skip_power,porigin_false) = eps
$string_read_runtime_value(S_skip_power,porigin_base) = (PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_skip_power,porigin_base,pvalue_base)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_negative_leaf)
porigin_negative_leaf = PORIGIN n_unit pcpath_negative_leaf
expression_negative_right = NExprUnaryMinus expression_right metadata_right
expression_negative_cond = NExprBinaryOpPow expression_left expression_negative_right metadata_cond
expression_negative_base = NExprTernary expression_negative_cond ABSENT expression_false metadata_base
S_negative_power = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_negative_base) :: (PCOCCURRENCE pcpath_cond expression_negative_cond) :: (PCOCCURRENCE pcpath_right expression_negative_right) :: (PCOCCURRENCE pcpath_negative_leaf expression_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_negative_leaf (PINT 3)) :: (PCCPRECISION pcpath_negative_leaf 14) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 false) :: (CODEEXPR pcpath_negative_leaf 18 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_negative_power,porigin_right) = (PINT (-3))
$power_prepare(NFLOAT 9223372036854775808,NINT (-3)) = POWERDONE (NFLOAT 18442240474082181120) true
$string_read_runtime_value(S_negative_power,porigin_cond) = eps
$string_read_runtime_value(S_negative_power,porigin_base) = eps
~$string_read_raw_known_base(S_negative_power,porigin_base,pvalue_base)
S_negative_budget_power = S_negative_power[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_negative_budget_power,porigin_base,pvalue_base)
expression_general_atom = NScalarInt (INTEGER 2) metadata_atom
expression_general_cast = NExprCastDouble expression_general_atom metadata_cast
expression_general_left = NExprUnaryPlus expression_general_cast metadata_left
expression_general_right = NScalarFloat (FLOAT "3fe0000000000000") metadata_right
expression_general_cond = NExprBinaryOpPow expression_general_left expression_general_right metadata_cond
expression_general_base = NExprTernary expression_general_cond ABSENT expression_false metadata_base
S_general_power = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_general_base) :: (PCOCCURRENCE pcpath_cond expression_general_cond) :: (PCOCCURRENCE pcpath_left expression_general_left) :: (PCOCCURRENCE pcpath_cast expression_general_cast) :: (PCOCCURRENCE pcpath_atom expression_general_atom) :: (PCOCCURRENCE pcpath_right expression_general_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 2)) :: (PCONSTANT pcpath_right (PFLOAT 4602678819172646912)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_general_power,porigin_left) = (PFLOAT 4611686018427387904)
$string_read_runtime_value(S_general_power,porigin_right) = (PFLOAT 4602678819172646912)
$power_prepare(NFLOAT 4611686018427387904,NFLOAT 4602678819172646912) = POWERGENERAL 4607182418800017408 4611686018427387904 4602678819172646912 0 false
$string_read_runtime_value(S_general_power,porigin_cond) = eps
$string_read_runtime_value(S_general_power,porigin_base) = eps
~$string_read_raw_known_base(S_general_power,porigin_base,pvalue_base)
S_general_budget_power = S_general_power[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_general_budget_power,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
