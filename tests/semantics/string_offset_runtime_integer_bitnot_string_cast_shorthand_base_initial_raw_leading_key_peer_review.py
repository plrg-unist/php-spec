"""An integral FLOAT bitwise NOT selects the exact falsey string fallback."""

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
expression_cond = NExprBitwiseNot expression_operand metadata_cond
expression_operand = NExprCastDouble expression_signed metadata_operand
expression_signed = NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_atom) metadata_signed
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_operand)
$origin_child((porigin_operand),[PCFIELD 0]) = (porigin_signed)
$origin_child((porigin_signed),[PCFIELD 0]) = (porigin_atom)
porigin_atom = PORIGIN n_unit pcpath_atom
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_signed) = (PINT (-1))
$string_read_runtime_value(S_capture,porigin_signed) = (PINT (-1))
$string_read_runtime_value(S_capture,porigin_operand) = (PFLOAT 13830554455654793216)
$bitnot_value(S_capture,PFLOAT 13830554455654793216,18) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_runtime_value(S_capture,porigin_cond) = (PINT 0)
$truth_value(S_capture,PINT 0,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$truth_value(S_capture,pvalue_base,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
S_budget_bitnot = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_runtime_value(S_budget_bitnot,porigin_base) = eps
$string_read_raw_known_base(S_budget_bitnot,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_bitnot,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
''')
    nodes = {
        'cond': 'NExprBitwiseNot expression_operand eps',
        'operand': 'NExprCastDouble expression_signed eps',
        'signed': 'NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_atom) eps',
        'false': 'NExprCastString expression_inner eps',
        'inner': 'NExprCastString expression_leaf eps',
        'leaf': 'NScalarString (BYTES text_leaf) eps'}
    for label in ('base', *nodes):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                   f'$compiled_precision(S_capture,(porigin_{label})) = (14)']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label in ('signed', 'leaf'):
            updates.append(('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 false) :: pcode.EXPRESSIONS]]'))
        else:
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_bad_bitnot_{label}_{kind}'
            recomputed = label == 'signed' and kind == 'emitted'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = ' + ('(pvalue_base)' if recomputed else 'eps'),
                       f'{"" if recomputed else "~"}$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('signed', 'leaf'):
            state = f'S_zero_line_bitnot_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in nodes:
            state = f'S_bad_bitnot_{label}_source'
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, value in (('type', 'PINT 0'), ('bytes', 'PSTRING ([49])'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        state = f'S_bad_bitnot_leaf_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_forged_budget_bitnot = S_bad_bitnot_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_bitnot,porigin_base,pvalue_base)
expression_zero_signed = NScalarInt (INTEGER 0) metadata_signed
expression_zero_operand = NExprCastDouble expression_zero_signed metadata_operand
expression_zero_cond = NExprBitwiseNot expression_zero_operand metadata_cond
expression_zero_base = NExprTernary expression_zero_cond ABSENT expression_false metadata_base
S_nonzero_bitnot = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_zero_base) :: (PCOCCURRENCE pcpath_cond expression_zero_cond) :: (PCOCCURRENCE pcpath_operand expression_zero_operand) :: (PCOCCURRENCE pcpath_signed expression_zero_signed) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_signed (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_nonzero_bitnot,porigin_operand) = (PFLOAT 0)
$string_read_runtime_value(S_nonzero_bitnot,porigin_cond) = (PINT (-1))
$string_read_runtime_value(S_nonzero_bitnot,porigin_base) = (PINT (-1))
~$string_read_raw_known_base(S_nonzero_bitnot,porigin_base,pvalue_base)
S_skip_bitnot = S_nonzero_bitnot[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_signed (PINT 0)) :: (PCCPRECISION pcpath_false 17) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_skip_bitnot,porigin_false) = eps
$string_read_runtime_value(S_skip_bitnot,porigin_base) = (PINT (-1))
~$string_read_raw_known_base(S_skip_bitnot,porigin_base,pvalue_base)
expression_string_signed = NScalarString (BYTES "zw==") metadata_signed
expression_string_operand = NExprCastString expression_string_signed metadata_operand
expression_string_cond = NExprBitwiseNot expression_string_operand metadata_cond
expression_string_base = NExprTernary expression_string_cond ABSENT expression_false metadata_base
S_string_bitnot = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_string_base) :: (PCOCCURRENCE pcpath_cond expression_string_cond) :: (PCOCCURRENCE pcpath_operand expression_string_operand) :: (PCOCCURRENCE pcpath_signed expression_string_signed) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_signed (PSTRING ([207]))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_string_bitnot,porigin_operand) = (PSTRING_CARRIER INTERNED_STRING ([207]))
$string_read_runtime_value(S_string_bitnot,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([48]))
$string_read_runtime_value(S_string_bitnot,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_string_bitnot,porigin_base,pvalue_base)
expression_fractional_signed = NExprUnaryMinus (NScalarFloat (FLOAT "3ff8000000000000") metadata_atom) metadata_signed
expression_fractional_operand = NExprCastDouble expression_fractional_signed metadata_operand
expression_fractional_cond = NExprBitwiseNot expression_fractional_operand metadata_cond
expression_fractional_base = NExprTernary expression_fractional_cond ABSENT expression_false metadata_base
S_fractional_bitnot = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_fractional_base) :: (PCOCCURRENCE pcpath_cond expression_fractional_cond) :: (PCOCCURRENCE pcpath_operand expression_fractional_operand) :: (PCOCCURRENCE pcpath_signed expression_fractional_signed) :: (PCOCCURRENCE pcpath_atom (NScalarFloat (FLOAT "3ff8000000000000") metadata_atom)) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_signed (PFLOAT 13832806255468478464)) :: (PCONSTANT pcpath_atom (PFLOAT 4609434218613702656)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_fractional_bitnot,porigin_operand) = (PFLOAT 13832806255468478464)
~$string_read_runtime_integer_quiet(PFLOAT 13832806255468478464)
$string_read_runtime_value(S_fractional_bitnot,porigin_cond) = eps
$string_read_runtime_value(S_fractional_bitnot,porigin_base) = eps
~$string_read_raw_known_base(S_fractional_bitnot,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
