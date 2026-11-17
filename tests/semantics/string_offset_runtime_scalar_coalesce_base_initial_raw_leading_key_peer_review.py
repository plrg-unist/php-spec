"""A nonnull emitted STRING coalesce retains its header and saved reference key."""

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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left (NScalarString (BYTES text_right) metadata_right) metadata_base)
expression_left = NExprTernary expression_guard expression_skipped expression_selected metadata_left
expression_guard = NExprCastInt expression_atom metadata_guard
expression_atom = NExprConstFetch name_atom metadata_atom
expression_skipped = NScalarString (BYTES text_skipped) metadata_skipped
expression_selected = NScalarString (BYTES text_selected) metadata_selected
$base64(text_selected) = $ptascii("abc")
$base64(text_skipped) = $ptascii("XYZ")
$base64(text_right) = $ptascii("XYZ")
pvalue_fallback = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_skipped)
$origin_child((porigin_left),[PCFIELD 2]) = (porigin_selected)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_guard) = (expression_guard)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
$origin_node(S_capture.SOURCES,porigin_selected) = (expression_selected)
$origin_node(S_capture.SOURCES,porigin_right) = (NScalarString (BYTES text_right) metadata_right)
$compiled_read(S_capture,porigin_left) = eps
$compiled_read(S_capture,porigin_guard) = eps
$compiled_read(S_capture,porigin_atom) = (PNULL)
$compiled_read(S_capture,porigin_selected) = (PSTRING ($ptascii("abc")))
$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("XYZ")))
$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("XYZ"))) = pvalue_fallback
$string_read_runtime_value(S_capture,porigin_guard) = (PINT 0)
$string_read_runtime_value(S_capture,porigin_left) = (pvalue_base)
porigin_base = PORIGIN n_unit pcpath_base
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
porigin_guard = PORIGIN n_unit pcpath_guard
porigin_atom = PORIGIN n_unit pcpath_atom
porigin_skipped = PORIGIN n_unit pcpath_skipped
porigin_selected = PORIGIN n_unit pcpath_selected
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_fallback)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
S_budget_coalesce = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_fallback]
$string_read_runtime_value(S_budget_coalesce,porigin_base) = eps
$string_read_raw_known_base(S_budget_coalesce,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_coalesce,porigin_base,pvalue_fallback)
''')
    for label, path in (('root', 'pcpath_base'), ('left', 'pcpath_left'),
                        ('guard', 'pcpath_guard'), ('atom', 'pcpath_atom'),
                        ('selected', 'pcpath_selected')):
        checks.append(f'$compiled_precision(S_capture,(PORIGIN n_unit {path})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION {path} 17) :: ppool.CONSTANTS]]')]
        if label in ('root', 'left', 'guard'):
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 true) :: pcode.EXPRESSIONS]]')]
        else:
            updates += [('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_coalesce_bad_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_base) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, path, node in (
            ('left', 'pcpath_left', 'NExprTernary expression_guard expression_skipped expression_selected eps'),
            ('guard', 'pcpath_guard', 'NExprCastInt expression_atom eps'),
            ('atom', 'pcpath_atom', 'NExprConstFetch name_atom eps'),
            ('skipped', 'pcpath_skipped', 'NScalarString (BYTES text_skipped) eps'),
            ('selected', 'pcpath_selected', 'NScalarString (BYTES text_selected) eps'),
            ('right', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        checks += [f'S_coalesce_bad_source_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_coalesce_bad_source_{label},porigin_base,pvalue_base)']
    checks += lines(r'''
S_coalesce_skipped = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_skipped 17) :: (PCONSTANT pcpath_skipped (PINT 9223372036854775808)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_skipped 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_coalesce_skipped,porigin_skipped) = eps
$string_read_runtime_value(S_coalesce_skipped,porigin_base) = (pvalue_base)
$string_read_raw_known_base(S_coalesce_skipped,porigin_base,pvalue_base)
S_coalesce_wrong_right = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING ($ptascii("bad")))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_coalesce_wrong_right,porigin_base) = (pvalue_base)
~$string_read_raw_known_base(S_coalesce_wrong_right,porigin_base,pvalue_base)
S_coalesce_wrong_selected = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_coalesce_wrong_selected,porigin_base) = eps
~$string_read_raw_known_base(S_coalesce_wrong_selected,porigin_base,pvalue_base)
S_coalesce_forged = S_coalesce_wrong_selected[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_coalesce_forged,porigin_base,pvalue_base)
''')
    for label, node, raw, value, admit in (
            ('empty', 'NScalarString (BYTES "") metadata_selected', 'PSTRING ([])', 'PSTRING_CARRIER INTERNED_STRING ([])', True),
            ('zero', 'NScalarString (BYTES "MA==") metadata_selected', 'PSTRING ([48])', 'PSTRING_CARRIER INTERNED_STRING ([48])', True),
            ('nul', 'NScalarString (BYTES "AA==") metadata_selected', 'PSTRING ([0])', None, False),
            ('int_zero', 'NScalarInt (INTEGER 0) metadata_selected', 'PINT 0', 'PINT 0', False),
            ('int_one', 'NScalarInt (INTEGER 1) metadata_selected', 'PINT 1', 'PINT 1', False)):
        checks += lines(f'''
expression_coalesce_{label}_selected = {node}
expression_coalesce_{label}_left = NExprTernary expression_guard expression_skipped expression_coalesce_{label}_selected metadata_left
expression_coalesce_{label}_base = NExprBinaryOpCoalesce expression_coalesce_{label}_left (NScalarString (BYTES text_right) metadata_right) metadata_base
S_coalesce_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_coalesce_{label}_base) :: (PCOCCURRENCE pcpath_left expression_coalesce_{label}_left) :: (PCOCCURRENCE pcpath_selected expression_coalesce_{label}_selected) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected ({raw})) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_coalesce_{label},porigin_left) = {"(" + value + ")" if value else "eps"}
$string_read_runtime_value(S_coalesce_{label},porigin_base) = {"(" + value + ")" if value else "eps"}
~$string_read_raw_known_base(S_coalesce_{label},porigin_base,pvalue_fallback)
''')
        if value is not None:
            checks.append(f'$string_read_raw_known_base(S_coalesce_{label},porigin_base,{value}) = {str(admit).lower()}')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
