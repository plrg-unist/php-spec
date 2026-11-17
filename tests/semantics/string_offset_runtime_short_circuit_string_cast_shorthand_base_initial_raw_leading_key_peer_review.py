"""False OR demands its RHS; decisive AND retains only its immediate source."""

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
expression_cond = NExprBinaryOpBooleanOr expression_left expression_right metadata_cond
expression_left = NExprCastInt expression_left_atom metadata_left
expression_left_atom = NExprConstFetch name_left_atom metadata_left_atom
expression_right = NExprCastBool expression_right_inner metadata_right
expression_right_inner = NExprCastInt expression_right_atom metadata_right_inner
expression_right_atom = NExprConstFetch name_right_atom metadata_right_atom
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_left_atom)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_inner)
$origin_child((porigin_right_inner),[PCFIELD 0]) = (porigin_right_atom)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_left_atom) = (PNULL)
$compiled_read(S_capture,porigin_right_atom) = (PNULL)
$string_read_runtime_value(S_capture,porigin_left) = (PINT 0)
$string_read_runtime_value(S_capture,porigin_right_inner) = (PINT 0)
$string_read_runtime_value(S_capture,porigin_right) = (PBOOL false)
$truth_value(S_capture,PINT 0,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL false)
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
S_budget_short_peer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_runtime_value(S_budget_short_peer,porigin_base) = eps
$string_read_raw_known_base(S_budget_short_peer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_short_peer,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
''')
    nodes = {
        'cond': 'NExprBinaryOpBooleanOr expression_left expression_right eps',
        'left': 'NExprCastInt expression_left_atom eps',
        'left_atom': 'NExprConstFetch name_left_atom eps',
        'right': 'NExprCastBool expression_right_inner eps',
        'right_inner': 'NExprCastInt expression_right_atom eps',
        'right_atom': 'NExprConstFetch name_right_atom eps',
        'false': 'NExprCastString expression_inner eps',
        'inner': 'NExprCastString expression_leaf eps',
        'leaf': 'NScalarString (BYTES text_leaf) eps'}
    for label in ('base', *nodes):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                   f'$compiled_precision(S_capture,(porigin_{label})) = (14)']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label in ('left_atom', 'right_atom', 'leaf'):
            updates.append(('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 false) :: pcode.EXPRESSIONS]]'))
        else:
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_bad_short_peer_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('left_atom', 'right_atom', 'leaf'):
            state = f'S_zero_line_short_peer_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in nodes:
            checks += [f'S_bad_short_peer_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value(S_bad_short_peer_{label}_source,porigin_base) = eps',
                       f'~$string_read_raw_known_base(S_bad_short_peer_{label}_source,porigin_base,pvalue_base)']
    for label, node in (('keyword_or', 'NExprBinaryOpLogicalOr'),
                        ('boolean_and', 'NExprBinaryOpBooleanAnd'),
                        ('keyword_and', 'NExprBinaryOpLogicalAnd')):
        checks += [f'expression_{label}_cond = {node} expression_left expression_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata_base',
                   f'S_{label}_short_peer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_{label}_short_peer,porigin_cond) = (PBOOL false)',
                   f'$string_read_runtime_value(S_{label}_short_peer,porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base(S_{label}_short_peer,porigin_base,pvalue_base)']
    for label in ('right', 'right_inner', 'right_atom'):
        kinds = ('precision', 'emitted') if label == 'right_atom' else ('precision', 'line', 'folded')
        for kind in kinds:
            field = 'POOLS' if kind == 'precision' else 'CODE'
            checks += [f'S_skipped_short_peer_{label}_{kind} = S_boolean_and_short_peer[.{field} = S_bad_short_peer_{label}_{kind}.{field}]',
                       f'$string_read_runtime_value(S_skipped_short_peer_{label}_{kind},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base(S_skipped_short_peer_{label}_{kind},porigin_base,pvalue_base)']
        state = f'S_skipped_short_peer_{label}_source'
        valid = label != 'right'
        checks += [f'{state} = S_boolean_and_short_peer[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_boolean_and_base) :: (PCOCCURRENCE pcpath_cond expression_boolean_and_cond) :: (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value({state},porigin_base) = ' + ('(pvalue_base)' if valid else 'eps'),
                   f'{"" if valid else "~"}$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for at, label, value in (('right_atom', 'range', 'PINT 9223372036854775808'),
                            ('leaf', 'type', 'PINT 0'),
                            ('leaf', 'header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        state = f'S_bad_short_peer_{at}_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{at} ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_skipped_range_short_peer = S_boolean_and_short_peer[.POOLS = S_bad_short_peer_right_atom_range.POOLS]
$string_read_runtime_value(S_skipped_range_short_peer,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_skipped_range_short_peer,porigin_base,pvalue_base)
S_forged_budget_short_peer = S_bad_short_peer_right_atom_range[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_short_peer,porigin_base,pvalue_base)
S_true_rhs_short_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right_atom (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_true_rhs_short_peer,porigin_right) = (PBOOL true)
$string_read_runtime_value(S_true_rhs_short_peer,porigin_cond) = (PBOOL true)
$string_read_runtime_value(S_true_rhs_short_peer,porigin_base) = (PBOOL true)
~$string_read_raw_known_base(S_true_rhs_short_peer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_true_rhs_short_peer,porigin_base,PBOOL true)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
