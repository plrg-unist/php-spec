"""Quiet XOR demands both truth values and its selected fallback before rebinding."""

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
expression_cond = NExprBinaryOpLogicalXor expression_left expression_right metadata_cond
expression_left = NExprCastDouble expression_atom metadata_left
expression_atom = NScalarInt (INTEGER 0) metadata_atom
expression_right = NExprConstFetch (NName (BYTES text_false_keyword) metadata_name) metadata_right
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_false_keyword) = $ptascii("false")
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_name)
$origin_node(S_capture.SOURCES,porigin_name) = (NName (BYTES text_false_keyword) metadata_name)
porigin_name = PORIGIN n_unit pcpath_name
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_atom) = (PINT 0)
$compiled_read(S_capture,porigin_right) = (PBOOL false)
$string_read_runtime_value(S_capture,porigin_left) = (PFLOAT 0)
$string_read_runtime_value(S_capture,porigin_right) = (PBOOL false)
$truth_value(S_capture,PFLOAT 0,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$truth_value(S_capture,PBOOL false,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL false)
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
S_budget_xor_peer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_runtime_value(S_budget_xor_peer,porigin_base) = eps
$string_read_raw_known_base(S_budget_xor_peer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_xor_peer,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
''')
    nodes = {
        'cond': 'NExprBinaryOpLogicalXor expression_left expression_right eps',
        'left': 'NExprCastDouble expression_atom eps',
        'atom': 'NScalarInt (INTEGER 0) eps',
        'right': 'NExprConstFetch (NName (BYTES text_false_keyword) metadata_name) eps',
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
            state = f'S_bad_xor_peer_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('atom', 'right', 'leaf'):
            state = f'S_zero_line_xor_peer_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in nodes:
            state = f'S_bad_xor_peer_{label}_source'
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for at, label, value in (('atom', 'value', 'PINT 1'),
                             ('right', 'nan', 'PFLOAT 9221120237041090560'),
                             ('leaf', 'type', 'PINT 0'),
                             ('leaf', 'header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        state = f'S_bad_xor_peer_{at}_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{at} ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_forged_budget_xor_peer = S_bad_xor_peer_atom_value[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_xor_peer,porigin_base,pvalue_base)
S_attested_xor_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PINT 0)) :: ppool.CONSTANTS]]]
$compiled_identity_value(S_attested_xor_peer,porigin_right) = (PINT 0)
$string_read_runtime_value(S_attested_xor_peer,porigin_right) = (PINT 0)
$string_read_runtime_value(S_attested_xor_peer,porigin_cond) = (PBOOL false)
$string_read_runtime_value(S_attested_xor_peer,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_attested_xor_peer,porigin_base,pvalue_base)
''')
    for label, left, right in (('left_true', 1, False), ('right_true', 0, True), ('both_true', 1, True)):
        truth = bool(left) != right
        name = 'dHJ1ZQ==' if right else 'ZmFsc2U='
        state = f'S_{label}_xor_peer'
        checks += [f'expression_{label}_atom = NScalarInt (INTEGER {left}) metadata_atom',
                   f'expression_{label}_left = NExprCastDouble expression_{label}_atom metadata_left',
                   f'name_{label} = NName (BYTES "{name}") metadata_name',
                   f'expression_{label}_right = NExprConstFetch name_{label} metadata_right',
                   f'expression_{label}_cond = NExprBinaryOpLogicalXor expression_{label}_left expression_{label}_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_false metadata_base',
                   f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_left expression_{label}_left) :: (PCOCCURRENCE pcpath_atom expression_{label}_atom) :: (PCOCCURRENCE pcpath_right expression_{label}_right) :: (PCOCCURRENCE pcpath_name name_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT {left})) :: (PCONSTANT pcpath_right (PBOOL {str(right).lower()})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_cond) = (PBOOL {str(truth).lower()})',
                   f'$string_read_runtime_value({state},porigin_base) = ' + ('(PBOOL true)' if truth else '(pvalue_base)'),
                   f'{"~" if truth else ""}$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_skipped_xor_peer = S_left_true_xor_peer[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_skipped_xor_peer,porigin_false) = eps
$string_read_runtime_value(S_skipped_xor_peer,porigin_base) = (PBOOL true)
~$string_read_raw_known_base(S_skipped_xor_peer,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
