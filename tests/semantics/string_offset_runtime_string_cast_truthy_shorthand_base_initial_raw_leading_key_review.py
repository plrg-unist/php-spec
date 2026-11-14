"""Truthy emitted string casts preserve their own INTERNED shorthand header."""

from string_offset_shorthand_base_initial_raw_leading_key_review import render as render_shorthand
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_shorthand(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_cond) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_cond) = eps'),
            ('$compiled_string_value(S_capture,porigin_cond,PSTRING ($ptascii("abc"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_cond) = (pkeyread.BASE)'),
            ('$truth(S_capture,PSTRING ($ptascii("abc")))', '$truth_value(S_capture,pkeyread.BASE,0) = S_capture[.RESULT = KNOWN (PBOOL true)]'),
            ('  -- if $string_read_raw_known_base(S_capture,porigin_cond,pkeyread.BASE)\n', '  -- if ~$string_read_raw_known_base(S_capture,porigin_cond,pkeyread.BASE)\n')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    early = lines(r'''
expression_cond = NExprCastString expression_child metadata_cond
expression_child = NScalarString (BYTES text_child) metadata_child
$base64(text_child) = $ptascii("abc")
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_child)
$origin_node(S_capture.SOURCES,porigin_child) = (expression_child)
$compiled_read(S_capture,porigin_child) = (PSTRING ($ptascii("abc")))
$compiled_precision(S_capture,(porigin_cond)) = (z_precision)
$compiled_precision(S_capture,(porigin_child)) = (z_precision)
$string_read_runtime_value(S_capture,porigin_child) = (pkeyread.BASE)
$cast_apply(S_capture,CASTSTRING,pkeyread.BASE,12) = S_capture[.RESULT = KNOWN pkeyread.BASE]
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
porigin_child = PORIGIN n_unit pcpath_child
S_capture.SOURCES = [pcunit]
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_budget_cast,porigin_cond) = eps
$string_read_raw_known_base(S_budget_cast,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_unused_cast_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_cast_pool,porigin_cond) = eps
$string_read_raw_known_base(S_unused_cast_pool,porigin_base,pkeyread.BASE)
''')
    for label, update in (
            ('condition_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 0 false) :: pcode.EXPRESSIONS]]'),
            ('condition_constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 12 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('child_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('child_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PINT 1)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_cast_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_cast_{label},porigin_cond) = eps',
                   f'~$string_read_raw_known_base(S_bad_cast_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('condition', 'pcpath_cond', 'NExprCastString expression_child eps'),
            ('child', 'pcpath_child', 'NScalarString (BYTES text_child) eps'),
            ('fallback', '(pcpath_base ++ [PCFIELD 2])', 'NScalarString (BYTES "WFla") eps')):
        checks += [f'S_bad_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_budget_forged_cast = S_bad_cast_child_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_budget_forged_cast,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
