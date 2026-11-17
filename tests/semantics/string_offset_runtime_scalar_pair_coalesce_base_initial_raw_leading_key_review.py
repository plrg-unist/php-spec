"""An emitted NULL left value selects the exact emitted ternary RHS header."""

from string_offset_runtime_scalar_coalesce_string_cast_base_initial_raw_leading_key_review import render as render_cast
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_cast(program, filename_b64)
    for old, new in (
            ('NExprCastString (NScalarString (BYTES text_selected) metadata_selected) metadata_cast',
             'NExprTernary expression_right_guard (NScalarString (BYTES text_selected) metadata_selected) expression_right_unused metadata_cast'),
            ('$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_selected)',
             '$origin_child((porigin_cast),[PCFIELD 1]) = (porigin_selected)'),
            ('pcpath_base ++ [PCFIELD 1, PCFIELD 0]', 'pcpath_base ++ [PCFIELD 1, PCFIELD 1]')):
        assert body.count(old) >= 1
        body = body.replace(old, new)
    checks = lines(r'''
expression_right_guard = NExprCastInt expression_right_atom metadata_right_guard
expression_right_atom = NScalarInt (INTEGER 1) metadata_right_atom
expression_right_unused = NScalarString (BYTES text_right_unused) metadata_right_unused
$base64(text_right_unused) = $ptascii("XYZ")
$string_read_literal_bytes(NExprTernary expression_right_guard (NScalarString (BYTES text_selected) metadata_selected) expression_right_unused metadata_cast) = eps
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_right_guard)
$origin_child((porigin_cast),[PCFIELD 2]) = (porigin_right_unused)
$origin_child((porigin_right_guard),[PCFIELD 0]) = (porigin_right_atom)
$origin_node(S_capture.SOURCES,porigin_right_guard) = (expression_right_guard)
$origin_node(S_capture.SOURCES,porigin_right_atom) = (expression_right_atom)
$origin_node(S_capture.SOURCES,porigin_right_unused) = (expression_right_unused)
porigin_right_guard = PORIGIN n_unit pcpath_right_guard
porigin_right_atom = PORIGIN n_unit pcpath_right_atom
porigin_right_unused = PORIGIN n_unit pcpath_right_unused
$compiled_read(S_capture,porigin_right_guard) = eps
$compiled_read(S_capture,porigin_right_atom) = (PINT 1)
$compiled_read(S_capture,porigin_right_unused) = (PSTRING ($ptascii("XYZ")))
$compiled_precision(S_capture,(porigin_right_guard)) = (z_precision)
$compiled_precision(S_capture,(porigin_right_atom)) = (z_precision)
$compiled_precision(S_capture,(porigin_right_unused)) = (z_precision)
$string_read_runtime_value(S_capture,porigin_right_guard) = (PINT 1)
$truth_value(S_capture,PINT 1,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
''')
    for label, update in (
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_guard 0 false) :: pcode.EXPRESSIONS]]'),
            ('guard_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_guard 12 true) :: pcode.EXPRESSIONS]]'),
            ('guard_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right_guard $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('atom_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_atom 12 false) :: pcode.EXPRESSIONS]]'),
            ('atom_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right_atom $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('atom_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]'),
            ('guard_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_guard (NExprCastInt expression_right_atom eps)) :: pcunit.OCCURRENCES]]'),
            ('unused_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_unused (NScalarString (BYTES text_right_unused) eps)) :: pcunit.OCCURRENCES]]'),
            ('right_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_cast (NExprTernary expression_right_guard (NScalarString (BYTES text_selected) metadata_selected) expression_right_unused eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_bad_pair_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_pair_skipped = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right_unused 17) :: (PCONSTANT pcpath_right_unused (PINT 9223372036854775808)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_unused 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_pair_skipped,porigin_right_unused) = eps
$string_read_runtime_value(S_pair_skipped,porigin_base) = (pkeyread.BASE)
$string_read_raw_known_base(S_pair_skipped,porigin_base,pkeyread.BASE)
S_pair_redirected = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right_atom (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_pair_redirected,porigin_right_guard) = eps
$string_read_runtime_value(S_pair_redirected,porigin_base) = eps
~$string_read_raw_known_base(S_pair_redirected,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
