"""Literal NULL selects the actual header of an emitted full ternary RHS."""

from string_offset_null_runtime_string_cast_coalesce_base_initial_raw_leading_key_review import render as render_cast
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_cast(program, filename_b64)
    for old, new in (
            ('expression_right = NExprCastString expression_child metadata_right', 'expression_right = NExprTernary expression_guard expression_child expression_unused metadata_right'),
            ('$origin_child((porigin_right),[PCFIELD 0]) = (porigin_child)', '$origin_child((porigin_right),[PCFIELD 1]) = (porigin_child)'),
            ('NExprCastString expression_child eps', 'NExprTernary expression_guard expression_child expression_unused eps')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    old = '  -- if $cast_apply(S_capture,CASTSTRING,pkeyread.BASE,12) = S_capture[.RESULT = KNOWN pkeyread.BASE]\n'
    assert body.count(old) == 1
    body = body.replace(old, '')
    checks = lines(r'''
expression_guard = NExprCastInt expression_atom metadata_guard
expression_atom = NScalarInt (INTEGER 1) metadata_atom
expression_unused = NScalarString (BYTES text_unused) metadata_unused
$base64(text_unused) = $ptascii("XYZ")
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_right),[PCFIELD 2]) = (porigin_unused)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_guard) = (expression_guard)
$origin_node(S_capture.SOURCES,porigin_unused) = (expression_unused)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
porigin_guard = PORIGIN n_unit pcpath_guard
porigin_unused = PORIGIN n_unit pcpath_unused
porigin_atom = PORIGIN n_unit pcpath_atom
$compiled_read(S_capture,porigin_guard) = eps
$compiled_read(S_capture,porigin_atom) = (PINT 1)
$string_read_runtime_value(S_capture,porigin_guard) = (PINT 1)
$truth_value(S_capture,PINT 1,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
''')
    for label in ('guard', 'atom', 'unused'):
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (z_precision)')
    for label, update in (
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_guard 0 false) :: pcode.EXPRESSIONS]]'),
            ('guard_fold', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_guard 12 true) :: pcode.EXPRESSIONS]]'),
            ('guard_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_guard $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('atom_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_atom $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('atom_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]'),
            ('unused_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused (NScalarString (BYTES text_unused) eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_bad_null_runtime_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_skipped_null_runtime = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_unused 17) :: (PCONSTANT pcpath_unused (PINT 9223372036854775808)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_unused 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_skipped_null_runtime,porigin_unused) = eps
$string_read_runtime_value(S_skipped_null_runtime,porigin_base) = (pkeyread.BASE)
$string_read_raw_known_base(S_skipped_null_runtime,porigin_base,pkeyread.BASE)
S_redirected_null_runtime = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_redirected_null_runtime,porigin_guard) = eps
$string_read_runtime_value(S_redirected_null_runtime,porigin_base) = eps
~$string_read_raw_known_base(S_redirected_null_runtime,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count - 1 + len(checks), derived - 1 + len(checks)
