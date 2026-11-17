"""Selected NULL and skipped inner values preserve the reference-key history."""

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary expression_cond')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = eps')
    body = body.replace('~$truth(S_capture,PINT 0)', '$string_read_runtime_value(S_capture,porigin_left) = (PNULL)')
    anchor = '  -- if S_wrong_left = '
    assert body.count(anchor) == 1
    body = body.replace(anchor, '  -- if S_capture.CODE = [pcode]\n  -- if n_unit = pcode.UNIT\n' + anchor)
    for state in ('S_wrong_left', 'S_wrong_condition'):
        statement = next(line for line in body.splitlines() if line.startswith('  -- if ' + state + ' = '))
        body = body.replace(statement, statement + '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]]')
    checks = lines(r'''
expression_cond = NExprTernary expression_guard expression_positive expression_null metadata_cond
expression_guard = NExprCastInt expression_atom metadata_guard
expression_atom = NExprConstFetch name_atom metadata_atom
expression_positive = NScalarInt (INTEGER 1) metadata_positive
expression_null = NExprConstFetch name_null metadata_null
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_positive)
$origin_child((porigin_left),[PCFIELD 2]) = (porigin_null)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_cond)
$origin_node(S_capture.SOURCES,porigin_guard) = (expression_guard)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$origin_node(S_capture.SOURCES,porigin_positive) = (expression_positive)
$origin_node(S_capture.SOURCES,porigin_null) = (expression_null)
$compiled_read(S_capture,porigin_guard) = eps
$compiled_read(S_capture,porigin_atom) = (PNULL)
$compiled_read(S_capture,porigin_positive) = (PINT 1)
$compiled_read(S_capture,porigin_null) = (PNULL)
$string_read_runtime_value(S_capture,porigin_guard) = (PINT 0)
$truth_value(S_capture,PINT 0,18) = S_capture[.RESULT = KNOWN (PBOOL false)]
$truth_value(S_capture,PNULL,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
S_unused_null_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL true)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_null_peer,porigin_left) = eps
$string_read_raw_known_base(S_unused_null_peer,porigin_base,pvalue_base)
S_budget_null_peer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_wrong]
$string_read_runtime_value(S_budget_null_peer,porigin_left) = eps
$string_read_raw_known_base(S_budget_null_peer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_null_peer,porigin_base,pvalue_wrong)
''')
    for label in ('guard', 'atom', 'positive', 'null'):
        checks += [f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
                   f'$compiled_precision(S_capture,(porigin_{label})) = (14)']
    checks.append('$compiled_precision(S_capture,(porigin_left)) = (14)')
    for label, path, node in (
            ('condition', 'pcpath_left', 'NExprTernary expression_guard expression_positive expression_null eps'),
            ('guard', 'pcpath_guard', 'NExprCastInt expression_atom eps'),
            ('atom', 'pcpath_atom', 'NExprConstFetch name_atom eps'),
            ('unselected', 'pcpath_positive', 'NScalarInt (INTEGER 1) eps'),
            ('selected', 'pcpath_null', 'NExprConstFetch name_null eps'),
            ('true_arm', 'pcpath_true', 'NScalarString (BYTES text_true) eps'),
            ('false_arm', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        state = f'S_bad_null_peer_{label}_source'
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, path in (('condition', 'pcpath_left'), ('guard', 'pcpath_guard'),
                        ('atom', 'pcpath_atom'), ('selected', 'pcpath_null')):
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION {path} 17) :: ppool.CONSTANTS]]')]
        if label in ('condition', 'guard'):
            updates += [('zero_line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            updates += [('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_bad_null_peer_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, path in (('atom', 'pcpath_atom'), ('selected', 'pcpath_null'),
                        ('true_arm', 'pcpath_true'), ('false_arm', 'pcpath_right')):
        checks += [f'S_zero_line_null_peer_{label} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 0 true) :: pcode.EXPRESSIONS]]]',
                   f'$string_read_raw_known_base(S_zero_line_null_peer_{label},porigin_base,pvalue_base)']
    checks += lines(r'''
S_skipped_null_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_positive 17) :: (PCONSTANT pcpath_positive (PINT 9223372036854775808)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_positive 0 false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_skipped_null_peer,porigin_positive) = eps
$string_read_runtime_value(S_skipped_null_peer,porigin_positive) = eps
$string_read_runtime_value(S_skipped_null_peer,porigin_left) = (PNULL)
$string_read_raw_known_base(S_skipped_null_peer,porigin_base,pvalue_base)
S_selected_int_null_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_selected_int_null_peer,porigin_left) = (PINT 1)
$string_read_raw_known_base(S_selected_int_null_peer,porigin_base,pvalue_wrong)
~$string_read_raw_known_base(S_selected_int_null_peer,porigin_base,pvalue_base)
S_guard_int_null_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_guard_int_null_peer,porigin_left) = (PINT 1)
$string_read_raw_known_base(S_guard_int_null_peer,porigin_base,pvalue_wrong)
~$string_read_raw_known_base(S_guard_int_null_peer,porigin_base,pvalue_base)
S_range_null_peer = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null (PINT 9223372036854775808)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_range_null_peer,porigin_base,pvalue_base)
S_forged_budget_null_peer = S_range_null_peer[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_forged_budget_null_peer,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + 2 + len(checks), derived + 2 + len(checks)
