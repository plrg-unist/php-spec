"""A falsey STRING bitwise NOT demands its fallback before key rebinding."""

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
expression_operand = NExprCastString expression_atom metadata_operand
expression_atom = NScalarString (BYTES text_atom) metadata_atom
$base64(text_atom) = [207]
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_operand)
$origin_child((porigin_operand),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_atom) = (PSTRING ([207]))
$compiled_read(S_capture,porigin_leaf) = (PSTRING ([48]))
$string_read_runtime_value(S_capture,porigin_operand) = (PSTRING_CARRIER INTERNED_STRING ([207]))
$bitnot_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([207]),18) = S_capture[.RESULT = KNOWN pvalue_base]
$string_read_runtime_value(S_capture,porigin_cond) = (pvalue_base)
$truth_value(S_capture,pvalue_base,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([98]))
S_budget_string_bitnot_peer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))]
$string_read_runtime_value(S_budget_string_bitnot_peer,porigin_base) = eps
$string_read_raw_known_base(S_budget_string_bitnot_peer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_string_bitnot_peer,porigin_base,PSTRING_CARRIER INTERNED_STRING ([98]))
''')
    nodes = {
        'cond': 'NExprBitwiseNot expression_operand eps',
        'operand': 'NExprCastString expression_atom eps',
        'atom': 'NScalarString (BYTES text_atom) eps',
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
            state = f'S_bad_string_bitnot_peer_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('atom', 'leaf'):
            state = f'S_zero_line_string_bitnot_peer_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in nodes:
            state = f'S_bad_string_bitnot_peer_{label}_source'
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, value in (('atom_type', 'PINT 207'), ('atom_bytes', 'PSTRING ([206])'),
                         ('atom_header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([207])'),
                         ('leaf_type', 'PINT 0'), ('leaf_bytes', 'PSTRING ([88])'),
                         ('leaf_header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        at = label.split('_')[0]
        state = f'S_bad_string_bitnot_peer_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{at} ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_forged_budget_string_bitnot_peer = S_bad_string_bitnot_peer_atom_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_string_bitnot_peer,porigin_base,pvalue_base)
expression_truthy_atom = NScalarString (BYTES "nQ==") metadata_atom
expression_truthy_operand = NExprCastString expression_truthy_atom metadata_operand
expression_truthy_cond = NExprBitwiseNot expression_truthy_operand metadata_cond
expression_truthy_base = NExprTernary expression_truthy_cond ABSENT expression_false metadata_base
S_truthy_string_bitnot_peer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_truthy_base) :: (PCOCCURRENCE pcpath_cond expression_truthy_cond) :: (PCOCCURRENCE pcpath_operand expression_truthy_operand) :: (PCOCCURRENCE pcpath_atom expression_truthy_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PSTRING ([157]))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_truthy_string_bitnot_peer,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([98]))
$string_read_runtime_value(S_truthy_string_bitnot_peer,porigin_base) = (PSTRING_CARRIER INTERNED_STRING ([98]))
~$string_read_raw_known_base(S_truthy_string_bitnot_peer,porigin_base,pvalue_base)
$string_read_raw_known_base(S_truthy_string_bitnot_peer,porigin_base,PSTRING_CARRIER INTERNED_STRING ([98]))
S_skip_string_bitnot_peer = S_truthy_string_bitnot_peer[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PSTRING ([157]))) :: (PCONSTANT pcpath_leaf (PINT 7)) :: (PCCPRECISION pcpath_false 17) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_skip_string_bitnot_peer,porigin_false) = eps
$string_read_runtime_value(S_skip_string_bitnot_peer,porigin_base) = (PSTRING_CARRIER INTERNED_STRING ([98]))
$string_read_raw_known_base(S_skip_string_bitnot_peer,porigin_base,PSTRING_CARRIER INTERNED_STRING ([98]))
''')
    for label, encoded, payload in (('empty', '', 'eps'), ('multibyte', 'z88=', '[207,207]'),
                                     ('nul_result', '/w==', '[255]')):
        checks += [f'expression_{label}_atom = NScalarString (BYTES "{encoded}") metadata_atom',
                   f'expression_{label}_operand = NExprCastString expression_{label}_atom metadata_operand',
                   f'expression_{label}_cond = NExprBitwiseNot expression_{label}_operand metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata_base',
                   f'S_{label}_string_bitnot_peer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_operand expression_{label}_operand) :: (PCOCCURRENCE pcpath_atom expression_{label}_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PSTRING ({payload}))) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_{label}_string_bitnot_peer,porigin_cond) = eps',
                   f'$string_read_runtime_value(S_{label}_string_bitnot_peer,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_{label}_string_bitnot_peer,porigin_base,pvalue_base)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
