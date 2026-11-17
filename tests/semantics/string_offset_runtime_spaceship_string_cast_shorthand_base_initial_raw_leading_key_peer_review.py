"""Zero spaceship retains signed-zero operands and the selected fallback header."""

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
expression_cond = NExprBinaryOpSpaceship expression_left expression_right metadata_cond
expression_left = NExprCastDouble expression_left_atom metadata_left
expression_left_atom = NScalarInt (INTEGER 0) metadata_left_atom
expression_right = NExprUnaryMinus expression_right_atom metadata_right
expression_right_atom = NScalarFloat (FLOAT text_right_atom) metadata_right_atom
text_right_atom = "0000000000000000"
expression_false = NExprCastString expression_inner metadata_false
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = [48]
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_left_atom)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_atom)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$compiled_read(S_capture,porigin_left_atom) = (PINT 0)
$compiled_read(S_capture,porigin_right_atom) = (PFLOAT 0)
$compiled_read(S_capture,porigin_right) = (PFLOAT 9223372036854775808)
$string_read_runtime_value(S_capture,porigin_left) = (PFLOAT 0)
$string_read_runtime_value(S_capture,porigin_right) = (PFLOAT 9223372036854775808)
$binary_apply(S_capture,SPACESHIP,PFLOAT 0,PFLOAT 9223372036854775808,18) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_runtime_value(S_capture,porigin_cond) = (PINT 0)
$string_read_runtime_value(S_capture,porigin_false) = (pvalue_base)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ([48]))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
S_budget_spaceship_peer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$string_read_runtime_value(S_budget_spaceship_peer,porigin_base) = eps
$string_read_raw_known_base(S_budget_spaceship_peer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_spaceship_peer,porigin_base,PSTRING_CARRIER INTERNED_STRING ([49]))
''')
    nodes = {
        'cond': 'NExprBinaryOpSpaceship expression_left expression_right eps',
        'left': 'NExprCastDouble expression_left_atom eps',
        'left_atom': 'NScalarInt (INTEGER 0) eps',
        'right': 'NExprUnaryMinus expression_right_atom eps',
        'right_atom': 'NScalarFloat (FLOAT text_right_atom) eps',
        'false': 'NExprCastString expression_inner eps',
        'inner': 'NExprCastString expression_leaf eps',
        'leaf': 'NScalarString (BYTES text_leaf) eps'}
    for label in ('base', *nodes):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                   f'$compiled_precision(S_capture,(porigin_{label})) = (14)']
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label in ('left_atom', 'right', 'right_atom', 'leaf'):
            updates.append(('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 false) :: pcode.EXPRESSIONS]]'))
        else:
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 18 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_changed_spaceship_peer_{label}_{kind}'
            valid = label == 'right_atom' or (label == 'right' and kind == 'emitted')
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = ' + ('(pvalue_base)' if valid else 'eps'),
                       f'{"" if valid else "~"}$string_read_raw_known_base({state},porigin_base,pvalue_base)']
        if label in ('left_atom', 'right', 'right_atom', 'leaf'):
            checks += [f'S_zero_line_spaceship_peer_{label} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value(S_zero_line_spaceship_peer_{label},porigin_base) = (pvalue_base)',
                       f'$string_read_raw_known_base(S_zero_line_spaceship_peer_{label},porigin_base,pvalue_base)']
        if label in nodes:
            state = f'S_changed_spaceship_peer_{label}_source'
            valid = label == 'right_atom'
            checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({nodes[label]})) :: pcunit.OCCURRENCES]]]',
                       f'$string_read_runtime_value({state},porigin_base) = ' + ('(pvalue_base)' if valid else 'eps'),
                       f'{"" if valid else "~"}$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_emitted_spaceship_peer = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_emitted_spaceship_peer,porigin_right) = eps
$string_read_runtime_value(S_emitted_spaceship_peer,porigin_right) = (PFLOAT 9223372036854775808)
$string_read_raw_known_base(S_emitted_spaceship_peer,porigin_base,pvalue_base)
S_child_pool_spaceship_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right_atom (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_child_pool_spaceship_peer,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_child_pool_spaceship_peer,porigin_base,pvalue_base)
''')
    for label, state in (('precision', 'S_changed_spaceship_peer_right_atom_precision'),
                         ('code', 'S_changed_spaceship_peer_right_atom_emitted'),
                         ('source', 'S_changed_spaceship_peer_right_atom_source'),
                         ('pool', 'S_child_pool_spaceship_peer')):
        checks += [f'S_demanded_spaceship_peer_{label} = {state}[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 false) :: ' + ('(CODEEXPR pcpath_right_atom 18 false) :: ' if label == 'code' else '') + 'pcode.EXPRESSIONS]]]',
                   f'$string_read_runtime_value(S_demanded_spaceship_peer_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_demanded_spaceship_peer_{label},porigin_base,pvalue_base)']
    for label, value in (('type', 'PINT 0'), ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])')):
        checks += [f'S_bad_spaceship_peer_leaf_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_spaceship_peer_leaf_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_spaceship_peer_leaf_{label},porigin_base,pvalue_base)']
    checks += lines(r'''
S_forged_budget_spaceship_peer = S_bad_spaceship_peer_leaf_type[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_spaceship_peer,porigin_base,pvalue_base)
''')
    for label, node, bits, result in (('lower', 'NExprUnaryPlus', 4607182418800017408, -1),
                                       ('upper', 'NExprUnaryMinus', 13830554455654793216, 1)):
        checks += [f'expression_{label}_spaceship_atom = NScalarFloat (FLOAT "3ff0000000000000") metadata_right_atom',
                   f'expression_{label}_spaceship_right = {node} expression_{label}_spaceship_atom metadata_right',
                   f'expression_{label}_spaceship_cond = NExprBinaryOpSpaceship expression_left expression_{label}_spaceship_right metadata_cond',
                   f'expression_{label}_spaceship_base = NExprTernary expression_{label}_spaceship_cond ABSENT expression_false metadata_base',
                   f'S_{label}_spaceship_peer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_spaceship_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_spaceship_cond) :: (PCOCCURRENCE pcpath_right expression_{label}_spaceship_right) :: (PCOCCURRENCE pcpath_right_atom expression_{label}_spaceship_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PFLOAT {bits})) :: (PCONSTANT pcpath_right_atom (PFLOAT 4607182418800017408)) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_{label}_spaceship_peer,porigin_cond) = (PINT ({result}))',
                   f'$string_read_runtime_value(S_{label}_spaceship_peer,porigin_base) = (PINT ({result}))',
                   f'~$string_read_raw_known_base(S_{label}_spaceship_peer,porigin_base,pvalue_base)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
