"""A truthy emitted string ternary retains its own INTERNED shorthand header."""

from string_offset_shorthand_base_initial_raw_leading_key_review import render as render_shorthand
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_shorthand(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_cond) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_cond) = eps'),
            ('$compiled_string_value(S_capture,porigin_cond,PSTRING ($ptascii("abc"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_cond) = (pkeyread.BASE)'),
            ('$truth(S_capture,PSTRING ($ptascii("abc")))', '$truth_value(S_capture,pkeyread.BASE,0) = S_capture[.RESULT = KNOWN (PBOOL true)]')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    early = lines(r'''
expression_cond = NExprTernary expression_guard expression_selected expression_unused metadata_cond
expression_guard = NExprCastInt expression_leaf metadata_guard
expression_leaf = NScalarInt (INTEGER 1) metadata_leaf
expression_selected = NScalarString (BYTES text_selected) metadata_selected
expression_unused = NScalarString (BYTES text_unused) metadata_unused
$base64(text_selected) = $ptascii("abc")
$base64(text_unused) = $ptascii("XYZ")
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_guard)
$origin_node(S_capture.SOURCES,porigin_guard) = (expression_guard)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (expression_leaf)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_selected)
$origin_node(S_capture.SOURCES,porigin_selected) = (expression_selected)
$origin_child((porigin_cond),[PCFIELD 2]) = (porigin_unused)
$origin_node(S_capture.SOURCES,porigin_unused) = (expression_unused)
$compiled_read(S_capture,porigin_guard) = eps
$compiled_read(S_capture,porigin_leaf) = (PINT 1)
$compiled_read(S_capture,porigin_selected) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_selected,PSTRING ($ptascii("abc"))) = pkeyread.BASE
$compiled_precision(S_capture,(porigin_cond)) = (z_precision)
$compiled_precision(S_capture,(porigin_guard)) = (z_precision)
$compiled_precision(S_capture,(porigin_leaf)) = (z_precision)
$compiled_precision(S_capture,(porigin_selected)) = (z_precision)
$string_read_runtime_value(S_capture,porigin_guard) = (PINT 1)
$truth_value(S_capture,PINT 1,12) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_capture,porigin_selected) = (pkeyread.BASE)
S_capture.CODE = [pcode]
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_cond) = eps\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    for state in ('S_wrong_condition', 'S_wrong_selected'):
        statement = next(line for line in body.splitlines() if line.startswith('  -- if ' + state + ' = '))
        body = body.replace(statement, statement + '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR (pcpath_base ++ [PCFIELD 0]) 12 true) :: pcode.EXPRESSIONS]]]')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
porigin_guard = PORIGIN n_unit pcpath_guard
porigin_leaf = PORIGIN n_unit pcpath_leaf
porigin_selected = PORIGIN n_unit pcpath_selected
porigin_unused = PORIGIN n_unit pcpath_unused
S_capture.SOURCES = [pcunit]
S_budget_string = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_budget_string,porigin_cond) = eps
$string_read_raw_known_base(S_budget_string,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_string,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_unused_string_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_string_pool,porigin_cond) = eps
$string_read_raw_known_base(S_unused_string_pool,porigin_base,pkeyread.BASE)
''')
    for label, path in (('condition', 'pcpath_cond'), ('guard', 'pcpath_guard'),
                        ('leaf', 'pcpath_leaf'), ('selected', 'pcpath_selected')):
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION {path} $(z_precision + 1)) :: ppool.CONSTANTS]]')]
        if label in ('condition', 'guard'):
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 12 true) :: pcode.EXPRESSIONS]]')]
        else:
            updates += [('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 12 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            state = f'S_bad_string_{label}_{kind}'
            checks += [f'{state} = S_capture[{update}]',
                       f'$string_read_runtime_value({state},porigin_cond) = eps',
                       f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('condition', 'pcpath_cond', 'NExprTernary expression_guard expression_selected expression_unused eps'),
            ('guard', 'pcpath_guard', 'NExprCastInt expression_leaf eps'),
            ('leaf', 'pcpath_leaf', 'NScalarInt (INTEGER 1) eps'),
            ('selected', 'pcpath_selected', 'NScalarString (BYTES text_selected) eps'),
            ('unused', 'pcpath_unused', 'NScalarString (BYTES text_unused) eps'),
            ('fallback', '(pcpath_base ++ [PCFIELD 2])', 'NScalarString (BYTES "WFla") eps')):
        checks += [f'S_bad_string_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_string_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_skipped_string = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_unused $(z_precision + 1)) :: (PCONSTANT pcpath_unused (PINT 9223372036854775808)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_unused 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_skipped_string,porigin_unused) = eps
$string_read_runtime_value(S_skipped_string,porigin_cond) = (pkeyread.BASE)
$string_read_raw_known_base(S_skipped_string,porigin_base,pkeyread.BASE)
S_wrong_guard_literal_string = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_wrong_guard_literal_string,porigin_cond) = eps
~$string_read_raw_known_base(S_wrong_guard_literal_string,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
~$string_read_raw_known_base(S_wrong_guard_literal_string,porigin_base,pkeyread.BASE)
S_wrong_string_leaf = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_wrong_string_leaf,porigin_cond) = eps
~$string_read_raw_known_base(S_wrong_string_leaf,porigin_base,pkeyread.BASE)
S_forged_string = S_wrong_string_leaf[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_forged_string,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
