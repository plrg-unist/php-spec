"""A truthy one-byte STRING bitwise NOT keeps its own shorthand header."""

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
expression_cond = NExprBitwiseNot expression_operand metadata_cond
expression_operand = NExprCastString expression_atom metadata_operand
expression_atom = NScalarString (BYTES text_atom) metadata_atom
$base64(text_atom) = [157]
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [88]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_operand)
$origin_child((porigin_operand),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_atom) = (PSTRING ([157]))
$compiled_read(S_capture,porigin_leaf) = (PSTRING ([88]))
$string_read_runtime_value(S_capture,porigin_operand) = (PSTRING_CARRIER INTERNED_STRING ([157]))
$bitnot_value(S_capture,PSTRING_CARRIER INTERNED_STRING ([157]),12) = S_capture[.RESULT = KNOWN pkeyread.BASE]
$string_read_runtime_value(S_capture,porigin_cond) = (pkeyread.BASE)
$truth_value(S_capture,pkeyread.BASE,12) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_capture,porigin_false) = (PSTRING_CARRIER INTERNED_STRING ([88]))
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([98]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([98]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([88]))
S_budget_string_bitnot = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([88]))]
$string_read_runtime_value(S_budget_string_bitnot,porigin_base) = eps
$string_read_raw_known_base(S_budget_string_bitnot,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_string_bitnot,porigin_base,PSTRING_CARRIER INTERNED_STRING ([88]))
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
            updates.append(('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 12 false) :: pcode.EXPRESSIONS]]'))
        else:
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 12 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_changed_string_bitnot_{label}_{kind}'
            skipped = label in ('false', 'inner', 'leaf')
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = ' + ('(pkeyread.BASE)' if skipped else 'eps'),
                       f'{"" if skipped else "~"}$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
        if label in ('atom', 'leaf'):
            state = f'S_zero_line_string_bitnot_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pkeyread.BASE)',
                       f'$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
        if label in nodes:
            state = f'S_changed_string_bitnot_{label}_source'
            skipped = label in ('inner', 'leaf')
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = ' + ('(pkeyread.BASE)' if skipped else 'eps'),
                       f'{"" if skipped else "~"}$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    for label, value in (('bytes', 'PSTRING ([158])'), ('type', 'PINT 157'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([157])')):
        state = f'S_bad_string_bitnot_atom_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_forged_budget_string_bitnot = S_bad_string_bitnot_atom_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_forged_budget_string_bitnot,porigin_base,pkeyread.BASE)
S_skipped_string_bitnot_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 7)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_skipped_string_bitnot_pool,porigin_false) = eps
$string_read_runtime_value(S_skipped_string_bitnot_pool,porigin_base) = (pkeyread.BASE)
$string_read_raw_known_base(S_skipped_string_bitnot_pool,porigin_base,pkeyread.BASE)
''')
    for label, encoded, payload in (('falsey', 'zw==', '[207]'),
                                     ('multibyte', 'nZ0=', '[157,157]'),
                                     ('nul_result', '/w==', '[255]')):
        checks += [f'expression_{label}_atom = NScalarString (BYTES "{encoded}") metadata_atom',
                   f'expression_{label}_operand = NExprCastString expression_{label}_atom metadata_operand',
                   f'expression_{label}_cond = NExprBitwiseNot expression_{label}_operand metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata',
                   f'S_{label}_string_bitnot = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_operand expression_{label}_operand) :: (PCOCCURRENCE pcpath_atom expression_{label}_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PSTRING ({payload}))) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_{label}_string_bitnot,porigin_base) = ' + ('(PSTRING_CARRIER INTERNED_STRING ([88]))' if label == 'falsey' else 'eps'),
                   f'~$string_read_raw_known_base(S_{label}_string_bitnot,porigin_base,pkeyread.BASE)']
        if label == 'falsey':
            checks += ['$string_read_runtime_value(S_falsey_string_bitnot,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ([48]))',
                       '$string_read_raw_known_base(S_falsey_string_bitnot,porigin_base,PSTRING_CARRIER INTERNED_STRING ([88]))']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
