"""False emitted equality authenticates both raw arms before reference rebinding."""

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary expression_cond')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = eps')
    body = body.replace('~$truth(S_capture,PINT 0)', '$string_read_runtime_value(S_capture,porigin_left) = (PBOOL false)')
    anchor = '  -- if S_wrong_left = '
    assert body.count(anchor) == 1
    body = body.replace(anchor, '  -- if S_capture.CODE = [pcode]\n  -- if n_unit = pcode.UNIT\n' + anchor)
    for state in ('S_wrong_left', 'S_wrong_condition'):
        statement = next(line for line in body.splitlines() if line.startswith('  -- if ' + state + ' = '))
        body = body.replace(statement, statement + '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]]')
    checks = lines(r'''
expression_cond = NExprBinaryOpEqual expression_cast expression_compare metadata_cond
expression_cast = NExprCastInt expression_atom metadata_cast
expression_atom = NExprConstFetch name_atom metadata_atom
expression_compare = NScalarInt (INTEGER 1) metadata_compare
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_compare)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_cond)
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$origin_node(S_capture.SOURCES,porigin_compare) = (expression_compare)
$origin_node(S_capture.SOURCES,porigin_true) = (expression_true)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_false)
$compiled_read(S_capture,porigin_cast) = eps
$compiled_read(S_capture,porigin_atom) = (PNULL)
$compiled_read(S_capture,porigin_compare) = (PINT 1)
$string_read_runtime_value(S_capture,porigin_cast) = (PINT 0)
$string_read_runtime_value(S_capture,porigin_compare) = (PINT 1)
$binary_apply(S_capture,EQUAL,PINT 0,PINT 1,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$truth_value(S_capture,PBOOL false,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
S_unused_scalar_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL true)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_scalar_peer,porigin_left) = eps
$string_read_raw_known_base(S_unused_scalar_peer,porigin_base,pvalue_base)
S_budget_scalar_peer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_wrong]
$string_read_runtime_value(S_budget_scalar_peer,porigin_left) = eps
$string_read_raw_known_base(S_budget_scalar_peer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_scalar_peer,porigin_base,pvalue_wrong)
''')
    for label in ('cast', 'atom', 'compare'):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                   f'$compiled_precision(S_capture,(porigin_{label})) = (14)']
    checks.append('$compiled_precision(S_capture,(porigin_left)) = (14)')
    for label, path, node in (
            ('cond', 'pcpath_left', 'NExprBinaryOpEqual expression_cast expression_compare eps'),
            ('cast', 'pcpath_cast', 'NExprCastInt expression_atom eps'),
            ('atom', 'pcpath_atom', 'NExprConstFetch name_atom eps'),
            ('compare', 'pcpath_compare', 'NScalarInt (INTEGER 1) eps'),
            ('true_arm', 'pcpath_true', 'NScalarString (BYTES text_true) eps'),
            ('false_arm', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        state = f'S_bad_scalar_peer_{label}_source'
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, path in (('cond', 'pcpath_left'), ('cast', 'pcpath_cast'),
                        ('atom', 'pcpath_atom'), ('compare', 'pcpath_compare')):
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION {path} 17) :: ppool.CONSTANTS]]')]
        if label in ('cond', 'cast'):
            updates += [('zero_line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            updates += [('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_bad_scalar_peer_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, path in (('atom', 'pcpath_atom'), ('compare', 'pcpath_compare'),
                        ('true_arm', 'pcpath_true'), ('false_arm', 'pcpath_right')):
        state = f'S_zero_line_scalar_peer_{label}'
        checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 0 true) :: pcode.EXPRESSIONS]]]',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, path, value in (('range', 'pcpath_atom', 'PINT 9223372036854775808'),
                              ('compare_type', 'pcpath_compare', 'PBOOL true'),
                              ('true_header', 'pcpath_true', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("XYZ"))'),
                              ('false_header', 'pcpath_right', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))')):
        state = f'S_bad_scalar_peer_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
expression_flip_cond = NExprBinaryOpNotEqual expression_cast expression_compare metadata_cond
expression_flip_base = NExprTernary expression_flip_cond expression_true expression_false metadata
S_flip_scalar_peer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_flip_base) :: (PCOCCURRENCE pcpath_left expression_flip_cond) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_flip_scalar_peer,porigin_left) = (PBOOL true)
$string_read_raw_known_base(S_flip_scalar_peer,porigin_base,pvalue_wrong)
~$string_read_raw_known_base(S_flip_scalar_peer,porigin_base,pvalue_base)
S_attested_scalar_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_attested_scalar_peer,porigin_cast) = (PINT 1)
$string_read_runtime_value(S_attested_scalar_peer,porigin_left) = (PBOOL true)
$string_read_raw_known_base(S_attested_scalar_peer,porigin_base,pvalue_wrong)
~$string_read_raw_known_base(S_attested_scalar_peer,porigin_base,pvalue_base)
S_forged_budget_scalar_peer = S_bad_scalar_peer_range[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_scalar_peer,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + 2 + len(checks), derived + 2 + len(checks)
