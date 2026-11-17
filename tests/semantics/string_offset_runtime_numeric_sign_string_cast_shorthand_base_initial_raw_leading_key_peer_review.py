"""An emitted negative-zero sign retains the selected falsey string and key."""

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
expression_cond = NExprUnaryMinus expression_child metadata_cond
expression_child = NExprCastDouble expression_atom metadata_child
expression_atom = NScalarInt (INTEGER 0) metadata_atom
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_child)
$origin_child((porigin_child),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_atom) = (PINT 0)
$compiled_identity_value(S_capture,porigin_atom) = (PINT 0)
$string_read_runtime_value(S_capture,porigin_atom) = (PINT 0)
$cast_apply(S_capture,CASTFLOAT,PINT 0,18) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$string_read_runtime_value(S_capture,porigin_child) = (PFLOAT 0)
$unary_apply(S_capture,NEGATIVE,PFLOAT 0,18) = S_capture[.RESULT = KNOWN (PFLOAT 9223372036854775808)]
$string_read_runtime_value(S_capture,porigin_cond) = (PFLOAT 9223372036854775808)
$truth_value(S_capture,PFLOAT 9223372036854775808,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$truth_value(S_capture,pvalue_base,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
S_budget_sign = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_runtime_value(S_budget_sign,porigin_base) = eps
$string_read_raw_known_base(S_budget_sign,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_sign,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
''')
    nodes = {
        'cond': 'NExprUnaryMinus expression_child eps',
        'child': 'NExprCastDouble expression_atom eps',
        'atom': 'NScalarInt (INTEGER 0) eps',
        'false': 'NExprCastString expression_inner eps',
        'inner': 'NExprCastString expression_leaf eps',
        'leaf': 'NScalarString (BYTES text_leaf) eps'}
    for label in ('base', *nodes):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                   f'$compiled_precision(S_capture,(porigin_{label})) = (14)']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label in ('atom', 'leaf'):
            updates.append(('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 false) :: pcode.EXPRESSIONS]]'))
        else:
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_bad_sign_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('atom', 'leaf'):
            state = f'S_zero_line_sign_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in nodes:
            state = f'S_bad_sign_{label}_source'
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, value in (('atom_type', 'PBOOL false'), ('atom_value', 'PINT 1'),
                         ('leaf_type', 'PINT 0'),
                         ('leaf_bytes', 'PSTRING ([49])'),
                         ('leaf_header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        path = 'atom' if label.startswith('atom_') else 'leaf'
        state = f'S_bad_sign_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{path} ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_forged_budget_sign = S_bad_sign_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_sign,porigin_base,pvalue_base)
S_raw_float_sign = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PFLOAT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_raw_float_sign,porigin_atom) = (PFLOAT 0)
$string_read_runtime_value(S_raw_float_sign,porigin_cond) = (PFLOAT 9223372036854775808)
$string_read_runtime_value(S_raw_float_sign,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_raw_float_sign,porigin_base,pvalue_base)
expression_plus_cond = NExprUnaryPlus expression_child metadata_cond
expression_plus_base = NExprTernary expression_plus_cond ABSENT expression_false metadata_base
S_plus_sign = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_plus_base) :: (PCOCCURRENCE pcpath_cond expression_plus_cond) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_plus_sign,porigin_cond) = (PFLOAT 0)
$string_read_runtime_value(S_plus_sign,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_plus_sign,porigin_base,pvalue_base)
expression_one_atom = NScalarInt (INTEGER 1) metadata_atom
expression_one_child = NExprCastDouble expression_one_atom metadata_child
expression_one_cond = NExprUnaryMinus expression_one_child metadata_cond
expression_one_base = NExprTernary expression_one_cond ABSENT expression_false metadata_base
ppool_one_sign = ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 1)) :: ppool.CONSTANTS]
S_one_sign = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_one_base) :: (PCOCCURRENCE pcpath_cond expression_one_cond) :: (PCOCCURRENCE pcpath_child expression_one_child) :: (PCOCCURRENCE pcpath_atom expression_one_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool_one_sign]]
$string_read_runtime_value(S_one_sign,porigin_child) = (PFLOAT 4607182418800017408)
$string_read_runtime_value(S_one_sign,porigin_cond) = (PFLOAT 13830554455654793216)
$truth_value(S_one_sign,PFLOAT 13830554455654793216,18) = S_one_sign[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_one_sign,porigin_base) = (PFLOAT 13830554455654793216)
~$string_read_raw_known_base(S_one_sign,porigin_base,pvalue_base)
S_skip_sign = S_one_sign[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool_one_sign[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool_one_sign.CONSTANTS]]]
$string_read_runtime_value(S_skip_sign,porigin_false) = eps
$string_read_runtime_value(S_skip_sign,porigin_base) = (PFLOAT 13830554455654793216)
~$string_read_raw_known_base(S_skip_sign,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
