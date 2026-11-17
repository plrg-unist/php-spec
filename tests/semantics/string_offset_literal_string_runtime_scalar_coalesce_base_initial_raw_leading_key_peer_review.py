"""A literal nonnull STRING keeps its header and skips emitted coalesce RHS."""

from string_offset_initial_raw_leading_key_peer_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pvalue_base', '$string_read_runtime_value(S_capture,porigin_base) = (pvalue_base)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
expression_left = NScalarString (BYTES text_left) metadata_left
expression_right = NExprTernary expression_guard expression_selected expression_unused metadata_right
expression_guard = NExprCastInt expression_atom metadata_guard
expression_atom = NScalarInt (INTEGER 1) metadata_atom
expression_selected = NScalarString (BYTES text_selected) metadata_selected
expression_unused = NScalarString (BYTES text_unused) metadata_unused
$base64(text_left) = $ptascii("abc")
$base64(text_selected) = $ptascii("XYZ")
$base64(text_unused) = $ptascii("abc")
pvalue_fallback = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_right),[PCFIELD 1]) = (porigin_selected)
$origin_child((porigin_right),[PCFIELD 2]) = (porigin_unused)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$origin_node(S_capture.SOURCES,porigin_guard) = (expression_guard)
$origin_node(S_capture.SOURCES,porigin_selected) = (expression_selected)
$origin_node(S_capture.SOURCES,porigin_unused) = (expression_unused)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$compiled_read(S_capture,porigin_left) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_left,PSTRING ($ptascii("abc"))) = pvalue_base
$compiled_read(S_capture,porigin_right) = eps
$string_read_literal_bytes(expression_right) = eps
$string_read_runtime_value(S_capture,porigin_right) = (pvalue_fallback)
porigin_base = PORIGIN n_unit pcpath_base
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
porigin_guard = PORIGIN n_unit pcpath_guard
porigin_selected = PORIGIN n_unit pcpath_selected
porigin_unused = PORIGIN n_unit pcpath_unused
porigin_atom = PORIGIN n_unit pcpath_atom
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_fallback)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
S_literal_coalesce_budget = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_fallback]
$string_read_runtime_value(S_literal_coalesce_budget,porigin_base) = eps
$string_read_raw_known_base(S_literal_coalesce_budget,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_literal_coalesce_budget,porigin_base,pvalue_fallback)
''')
    for label, update in (
            ('root_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('root_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 true) :: pcode.EXPRESSIONS]]'),
            ('root_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]'),
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_guard 0 false) :: pcode.EXPRESSIONS]]'),
            ('guard_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_guard 17) :: ppool.CONSTANTS]]'),
            ('atom_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_atom 18 false) :: pcode.EXPRESSIONS]]'),
            ('selected_value', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PSTRING ($ptascii("bad")))) :: ppool.CONSTANTS]]'),
            ('selected_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_selected 17) :: ppool.CONSTANTS]]'),
            ('guard_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_guard (NExprCastInt expression_atom eps)) :: pcunit.OCCURRENCES]]'),
            ('selected_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_selected (NScalarString (BYTES text_selected) eps)) :: pcunit.OCCURRENCES]]'),
            ('unused_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused (NScalarString (BYTES text_unused) eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_literal_skipped_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_right) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_fallback)']
    for label, update in (
            ('root_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('left_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: pcode.EXPRESSIONS]]'),
            ('left_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]'),
            ('left_value', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('left_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left (NScalarString (BYTES text_left) eps)) :: pcunit.OCCURRENCES]]'),
            ('right_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprTernary expression_guard expression_selected expression_unused eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_literal_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, node in (
            ('raw', 'NScalarString (BYTES text_selected) metadata_right'),
            ('concat', 'NExprBinaryOpConcat (NScalarString (BYTES "WA==") metadata_selected) (NScalarString (BYTES "WVo=") metadata_unused) metadata_right')):
        checks += lines(f'''
expression_literal_{label}_right = {node}
expression_literal_{label}_base = NExprBinaryOpCoalesce expression_left expression_literal_{label}_right metadata_base
S_literal_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_literal_{label}_base) :: (PCOCCURRENCE pcpath_right expression_literal_{label}_right) :: pcunit.OCCURRENCES]]]
$string_read_literal_bytes(expression_literal_{label}_right) = ($ptascii("XYZ"))
$compiled_read(S_literal_{label},porigin_right) = eps
$string_read_runtime_value(S_literal_{label},porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_literal_{label},porigin_base,pvalue_base)
''')
    for label, node, raw, value in (
            ('empty', 'NScalarString (BYTES "") metadata_left', 'PSTRING ([])', 'PSTRING_CARRIER INTERNED_STRING ([])'),
            ('zero', 'NScalarString (BYTES "MA==") metadata_left', 'PSTRING ([48])', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            ('nul', 'NScalarString (BYTES "AA==") metadata_left', 'PSTRING ([0])', None)):
        checks += lines(f'''
expression_literal_{label}_left = {node}
expression_literal_{label}_base = NExprBinaryOpCoalesce expression_literal_{label}_left expression_right metadata_base
S_literal_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_literal_{label}_base) :: (PCOCCURRENCE pcpath_left expression_literal_{label}_left) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left ({raw})) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_literal_{label},porigin_base) = {"(" + value + ")" if value else "eps"}
~$string_read_raw_known_base(S_literal_{label},porigin_base,pvalue_fallback)
''')
        checks.append(f'$string_read_raw_known_base(S_literal_{label},porigin_base,{value or "pvalue_base"}) = {str(value is not None).lower()}')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
