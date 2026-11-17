"""Nonnull emitted STRING coalesce skips a complete emitted RHS ternary."""

from string_offset_runtime_scalar_coalesce_base_initial_raw_leading_key_peer_review import render as render_raw
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_raw(program, filename_b64)
    old = '(NScalarString (BYTES text_right) metadata_right)'
    right = '(NExprTernary expression_right_guard expression_right_selected expression_right_skipped metadata_right)'
    assert body.count(old) == 7
    body = body.replace(old, right)
    for old, new in (
            ('$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("XYZ")))', '$compiled_read(S_capture,porigin_right) = eps'),
            ('$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("XYZ"))) = pvalue_fallback', '$string_read_runtime_value(S_capture,porigin_right) = (pvalue_fallback)'),
            ('PCONSTANT pcpath_right (PSTRING ($ptascii("bad")))', 'PCONSTANT pcpath_right_selected (PSTRING ($ptascii("bad")))'),
            ('~$string_read_raw_known_base(S_coalesce_wrong_right,porigin_base,pvalue_base)', '$string_read_raw_known_base(S_coalesce_wrong_right,porigin_base,pvalue_base)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    bindings = lines(r'''
expression_right_guard = NExprCastInt expression_right_atom metadata_right_guard
expression_right_atom = NScalarInt (INTEGER 1) metadata_right_atom
expression_right_selected = NScalarString (BYTES text_right) metadata_right_selected
expression_right_skipped = NScalarString (BYTES text_right_skipped) metadata_right_skipped
$base64(text_right_skipped) = $ptascii("abc")
''')
    anchor = '  -- if $origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left ' + right + ' metadata_base)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, anchor + ''.join('  -- if ' + check + '\n' for check in bindings))
    children = lines(r'''
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_guard)
$origin_child((porigin_right),[PCFIELD 1]) = (porigin_right_selected)
$origin_child((porigin_right),[PCFIELD 2]) = (porigin_right_skipped)
$origin_child((porigin_right_guard),[PCFIELD 0]) = (porigin_right_atom)
porigin_right_guard = PORIGIN n_unit pcpath_right_guard
porigin_right_selected = PORIGIN n_unit pcpath_right_selected
porigin_right_skipped = PORIGIN n_unit pcpath_right_skipped
porigin_right_atom = PORIGIN n_unit pcpath_right_atom
$origin_node(S_capture.SOURCES,porigin_right_guard) = (expression_right_guard)
$origin_node(S_capture.SOURCES,porigin_right_selected) = (expression_right_selected)
$origin_node(S_capture.SOURCES,porigin_right_skipped) = (expression_right_skipped)
$origin_node(S_capture.SOURCES,porigin_right_atom) = (expression_right_atom)
$compiled_read(S_capture,porigin_right_guard) = eps
$compiled_read(S_capture,porigin_right_atom) = (PINT 1)
$compiled_read(S_capture,porigin_right_selected) = (PSTRING ($ptascii("XYZ")))
$string_read_runtime_value(S_capture,porigin_right_guard) = (PINT 1)
''')
    anchor = '  -- if $origin_node(S_capture.SOURCES,porigin_right) = ' + right + '\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, anchor + ''.join('  -- if ' + check + '\n' for check in children))
    checks = ['$string_read_runtime_value(S_coalesce_wrong_right,porigin_right) = eps']
    for label, update in (
            ('root_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('root_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 true) :: pcode.EXPRESSIONS]]'),
            ('root_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]'),
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_guard 0 false) :: pcode.EXPRESSIONS]]'),
            ('guard_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_guard 18 true) :: pcode.EXPRESSIONS]]'),
            ('guard_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right_guard 17) :: ppool.CONSTANTS]]'),
            ('atom_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_atom 18 false) :: pcode.EXPRESSIONS]]'),
            ('atom_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right_atom 17) :: ppool.CONSTANTS]]'),
            ('selected_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_selected 18 false) :: pcode.EXPRESSIONS]]'),
            ('selected_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right_selected 17) :: ppool.CONSTANTS]]'),
            ('guard_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_guard (NExprCastInt expression_right_atom eps)) :: pcunit.OCCURRENCES]]'),
            ('selected_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_selected (NScalarString (BYTES text_right) eps)) :: pcunit.OCCURRENCES]]'),
            ('skipped_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_skipped (NScalarString (BYTES text_right_skipped) eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_pair_skipped_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_right) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_fallback)']
    checks += lines(r'''
S_pair_ignored_right_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PINT 999)) :: ppool.CONSTANTS]]]
$compiled_read(S_pair_ignored_right_pool,porigin_right) = eps
$string_read_runtime_value(S_pair_ignored_right_pool,porigin_right) = (pvalue_fallback)
$string_read_raw_known_base(S_pair_ignored_right_pool,porigin_base,pvalue_base)
S_pair_wrong_immediate_right = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprTernary expression_right_guard expression_right_selected expression_right_skipped eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_pair_wrong_immediate_right,porigin_base) = eps
~$string_read_raw_known_base(S_pair_wrong_immediate_right,porigin_base,pvalue_base)
S_pair_folded_right = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_pair_folded_right,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_pair_folded_right,porigin_base,pvalue_base)
''')
    for label, right_node in (
            ('raw', 'NScalarString (BYTES text_right) metadata_right'),
            ('literal_concat', 'NExprBinaryOpConcat (NScalarString (BYTES "WA==") metadata_right_selected) (NScalarString (BYTES "WVo=") metadata_right_skipped) metadata_right')):
        checks += lines(f'''
expression_pair_{label}_right = {right_node}
expression_pair_{label}_base = NExprBinaryOpCoalesce expression_left expression_pair_{label}_right metadata_base
S_pair_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_pair_{label}_base) :: (PCOCCURRENCE pcpath_right expression_pair_{label}_right) :: pcunit.OCCURRENCES]]]
$string_read_literal_bytes(expression_pair_{label}_right) = ($ptascii("XYZ"))
$compiled_read(S_pair_{label},porigin_right) = eps
$string_read_runtime_value(S_pair_{label},porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_pair_{label},porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    extra = len(bindings) + len(children) + len(checks)
    return body, count + extra, derived + extra
