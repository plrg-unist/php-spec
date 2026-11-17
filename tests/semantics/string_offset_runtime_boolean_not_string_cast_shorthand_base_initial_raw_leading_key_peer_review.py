"""Emitted NOT of a compiled negative FLOAT retains the frozen reference key."""

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
expression_cond = NExprBooleanNot expression_child metadata_cond
expression_child = NExprUnaryMinus expression_atom metadata_child
expression_atom = NScalarFloat (FLOAT text_atom) metadata_atom
text_atom = "3ff0000000000000"
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
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$compiled_read(S_capture,porigin_atom) = (PFLOAT 4607182418800017408)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_child) = (PFLOAT 13830554455654793216)
$compiled_identity_value(S_capture,porigin_child) = (PFLOAT 13830554455654793216)
$string_read_runtime_value(S_capture,porigin_child) = (PFLOAT 13830554455654793216)
$truth_value(S_capture,PFLOAT 13830554455654793216,18) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL false)
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
S_budget_not = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([]))]
$string_read_runtime_value(S_budget_not,porigin_base) = eps
$string_read_raw_known_base(S_budget_not,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_not,porigin_base,PSTRING_CARRIER INTERNED_STRING ([]))
''')
    for label in ('base', 'cond', 'child', 'false', 'inner', 'leaf'):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label not in ('child', 'leaf'):
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        elif label == 'leaf':
            updates += [('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_leaf 18 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            name = f'S_bad_not_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pvalue_base)']
        if label in ('child', 'leaf'):
            name = f'S_raw_zero_line_not_{label}'
            checks += [f'{name} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({name},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({name},porigin_base,pvalue_base)']
    for label, node in (
            ('base', 'NExprTernary expression_cond ABSENT (NExprCastBool expression_inner metadata_false) metadata_base'),
            ('cond', 'NExprBooleanNot expression_child eps'),
            ('child', 'NExprUnaryMinus expression_atom eps'),
            ('false', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_not_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_bad_not_{label}_source,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_not_{label}_source,porigin_base,pvalue_base)']
    for label, value in (('bits', 'PFLOAT 4607182418800017408'), ('type', 'PINT $(0 - 1)'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        checks += [f'S_bad_not_child_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_not_child_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_not_child_{label},porigin_base,pvalue_base)']
    for label, value in (('bytes', 'PSTRING ([49])'), ('type', 'PBOOL false'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        checks += [f'S_bad_not_leaf_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_not_leaf_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_not_leaf_{label},porigin_base,pvalue_base)']
    checks += lines(r'''
S_budget_forged_not = S_bad_not_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_not,porigin_base,pvalue_base)
porigin_atom = PORIGIN n_unit pcpath_atom
S_deep_not = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_atom (NScalarFloat (FLOAT "0000000000000000") eps)) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_atom 17) :: (PCONSTANT pcpath_atom (PBOOL false)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_deep_not,porigin_cond) = (PBOOL false)
$string_read_runtime_value(S_deep_not,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_deep_not,porigin_base,pvalue_base)
expression_zero_atom = NScalarFloat (FLOAT "0000000000000000") metadata_atom
expression_zero_child = NExprUnaryMinus expression_zero_atom metadata_child
expression_zero_cond = NExprBooleanNot expression_zero_child metadata_cond
expression_zero_root = NExprTernary expression_zero_cond ABSENT expression_false metadata_base
ppool_zero_not = ppool[.CONSTANTS = (PCONSTANT pcpath_child (PFLOAT 9223372036854775808)) :: (PCONSTANT pcpath_atom (PFLOAT 0)) :: ppool.CONSTANTS]
S_zero_not = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_zero_root) :: (PCOCCURRENCE pcpath_cond expression_zero_cond) :: (PCOCCURRENCE pcpath_child expression_zero_child) :: (PCOCCURRENCE pcpath_atom expression_zero_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool_zero_not]]
$string_read_runtime_value(S_zero_not,porigin_cond) = (PBOOL true)
$string_read_runtime_value(S_zero_not,porigin_base) = (PBOOL true)
~$string_read_raw_known_base(S_zero_not,porigin_base,pvalue_base)
S_skip_not = S_zero_not[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool_zero_not[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool_zero_not.CONSTANTS]]]
$string_read_runtime_value(S_skip_not,porigin_base) = (PBOOL true)
~$string_read_raw_known_base(S_skip_not,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
