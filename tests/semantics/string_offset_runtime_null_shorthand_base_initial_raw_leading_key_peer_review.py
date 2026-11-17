"""A selected NULL shorthand fallback keeps the saved reference-key history."""

from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_peer_review import render as render_zero
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_zero(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary expression_cond')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = eps')
    body = body.replace('~$truth(S_capture,PINT 0)', '$string_read_runtime_value(S_capture,porigin_left) = (PNULL)')
    anchor = '  -- if S_wrong_left = '
    assert body.count(anchor) == 1
    body = body.replace(anchor, '  -- if S_capture.CODE = [pcode]\n  -- if n_unit = pcode.UNIT\n' + anchor)
    for state in ('S_wrong_left', 'S_nonzero_pool', 'S_wrong_condition'):
        statement = next(line for line in body.splitlines() if line.startswith('  -- if ' + state + ' = '))
        body = body.replace(statement, statement + '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]]')
    statement = next(line for line in body.splitlines() if line.startswith('  -- if S_nonzero_source = '))
    body = body.replace(statement, statement + '[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 0)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]]')
    checks = lines(r'''
expression_cond = NExprTernary expression_guard expression_skipped expression_selected metadata_cond
expression_guard = NExprCastInt expression_atom metadata_guard
expression_atom = NExprConstFetch name_atom metadata_atom
expression_skipped = NScalarInt (INTEGER 1) metadata_skipped
expression_selected = NExprConstFetch name_selected metadata_selected
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_skipped)
$origin_child((porigin_left),[PCFIELD 2]) = (porigin_selected)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_guard) = (expression_guard)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
$origin_node(S_capture.SOURCES,porigin_selected) = (expression_selected)
$compiled_read(S_capture,porigin_guard) = eps
$compiled_read(S_capture,porigin_atom) = (PNULL)
$compiled_read(S_capture,porigin_selected) = (PNULL)
$compiled_read(S_capture,porigin_skipped) = (PINT 1)
$string_read_runtime_value(S_capture,porigin_guard) = (PINT 0)
$truth_value(S_capture,PNULL,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_base) = (pvalue_base)
porigin_guard = PORIGIN n_unit pcpath_guard
porigin_atom = PORIGIN n_unit pcpath_atom
porigin_selected = PORIGIN n_unit pcpath_selected
porigin_skipped = PORIGIN n_unit pcpath_skipped
S_budget_null_shorthand = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_budget_null_shorthand,porigin_left) = eps
$string_read_raw_known_base(S_budget_null_shorthand,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_null_shorthand,porigin_base,pvalue_wrong)
''')
    binding = checks.pop(0)
    anchor = '  -- if $base64(text_right) = $ptascii("abc")\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, '  -- if ' + binding + '\n' + anchor)
    for label, path in (('condition', 'pcpath_left'), ('guard', 'pcpath_guard'),
                        ('atom', 'pcpath_atom'), ('selected', 'pcpath_selected')):
        checks += [f'$compiled_precision(S_capture,(PORIGIN n_unit {path})) = (14)']
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION {path} 17) :: ppool.CONSTANTS]]')]
        if label in ('condition', 'guard'):
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            updates += [('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_null_shorthand_bad_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_left) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, path, node in (
            ('condition', 'pcpath_left', 'NExprTernary expression_guard expression_skipped expression_selected eps'),
            ('guard', 'pcpath_guard', 'NExprCastInt expression_atom eps'),
            ('atom', 'pcpath_atom', 'NExprConstFetch name_atom eps'),
            ('skipped', 'pcpath_skipped', 'NScalarInt (INTEGER 1) eps'),
            ('selected', 'pcpath_selected', 'NExprConstFetch name_selected eps'),
            ('fallback', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        checks += [f'S_null_shorthand_bad_source_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_null_shorthand_bad_source_{label},porigin_base,pvalue_base)']
    checks += lines(r'''
S_null_shorthand_skipped = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_skipped 17) :: (PCONSTANT pcpath_skipped (PINT 9223372036854775808)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_skipped 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_null_shorthand_skipped,porigin_skipped) = eps
$string_read_runtime_value(S_null_shorthand_skipped,porigin_left) = (PNULL)
$string_read_raw_known_base(S_null_shorthand_skipped,porigin_base,pvalue_base)
S_null_shorthand_guard_true = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_null_shorthand_guard_true,porigin_left) = (PINT 1)
~$string_read_raw_known_base(S_null_shorthand_guard_true,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_null_shorthand_guard_true,porigin_base,pvalue_wrong)
S_null_shorthand_selected_true = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PINT 1)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_null_shorthand_selected_true,porigin_left) = (PINT 1)
~$string_read_raw_known_base(S_null_shorthand_selected_true,porigin_base,pvalue_base)
S_null_shorthand_range = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PINT 9223372036854775808)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_null_shorthand_range,porigin_left) = eps
~$string_read_raw_known_base(S_null_shorthand_range,porigin_base,pvalue_base)
S_null_shorthand_forged = S_null_shorthand_range[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_null_shorthand_forged,porigin_base,pvalue_base)
S_null_shorthand_false_bool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PBOOL false)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_null_shorthand_false_bool,porigin_left) = (PBOOL false)
$string_read_raw_known_base(S_null_shorthand_false_bool,porigin_base,pvalue_base)
S_null_shorthand_zero_int = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_null_shorthand_zero_int,porigin_left) = (PINT 0)
$string_read_raw_known_base(S_null_shorthand_zero_int,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + 3 + len(checks), derived + 3 + len(checks)
