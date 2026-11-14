"""Quiet emitted casts preserve literal ternary headers and frozen raw offsets."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprCastBool expression_cast_int metadata_cond)')
    anchor = '  -- if $compiled_read(S_capture,porigin_cond) = (PINT 1)\n'
    assert body.count(anchor) == 1
    early = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
S_capture.CODE = [pcode]
pcode.UNIT = n_unit
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprCastBool expression_cast_int metadata_cond)
expression_cast_int = NExprCastInt expression_cast_leaf metadata_cast_int
expression_cast_leaf = NScalarString (BYTES text_cast_leaf) metadata_cast_leaf
$base64(text_cast_leaf) = [49]
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cast_int)
$origin_child((porigin_cast_int),[PCFIELD 0]) = (porigin_cast_leaf)
$origin_node(S_capture.SOURCES,porigin_cast_int) = (expression_cast_int)
$origin_node(S_capture.SOURCES,porigin_cast_leaf) = (expression_cast_leaf)
$compiled_read(S_capture,porigin_cond) = eps
$compiled_read(S_capture,porigin_cast_int) = eps
$compiled_read(S_capture,porigin_cast_leaf) = (PSTRING ([49]))
$compiled_precision(S_capture,(porigin_cond)) = (z_cast_precision)
$compiled_precision(S_capture,(porigin_cast_int)) = (z_cast_precision)
$compiled_precision(S_capture,(porigin_cast_leaf)) = (z_cast_precision)
$string_read_runtime_value(S_capture,porigin_cast_int) = (PINT 1)
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL true)
$cast_apply(S_capture,CASTBOOL,PINT 1,12) = S_capture[.RESULT = KNOWN (PBOOL true)]
$truth_value(S_capture,PBOOL true,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
''')
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early))
    body = body.replace('$truth(S_capture,PINT 1)', '$truth(S_capture,PBOOL true)')
    for state in ('S_wrong_condition', 'S_wrong_condition_value'):
        start = body.index('  -- if ' + state + ' = ')
        end = body.index('\n', start)
        body = body[:end] + '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 12 true) :: pcode.EXPRESSIONS]]]' + body[end:]
    checks = lines(r'''
porigin_cast_int = PORIGIN n_unit pcpath_cast_int
porigin_cast_leaf = PORIGIN n_unit pcpath_cast_leaf
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_budget_cast,porigin_base,pkeyread.BASE)
S_unused_cast_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL false)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_cast_pool,porigin_cond) = eps
$string_read_runtime_value(S_unused_cast_pool,porigin_cond) = (PBOOL true)
$string_read_raw_known_base(S_unused_cast_pool,porigin_base,pkeyread.BASE)
''')
    for label, path, node in (
            ('condition', 'pcpath_cond', 'NExprCastBool expression_cast_int eps'),
            ('inner', 'pcpath_cast_int', 'NExprCastInt expression_cast_leaf eps'),
            ('leaf', 'pcpath_cast_leaf', 'NScalarString (BYTES text_cast_leaf) eps'),
            ('unselected', '(pcpath_base ++ [PCFIELD 2])', 'NScalarString (BYTES text_false) eps')):
        checks += [f'S_bad_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_source,porigin_base,pkeyread.BASE)']
    for label, path, line, constant in (
            ('zero_line', 'pcpath_cond', 0, 'false'),
            ('inner_line', 'pcpath_cast_int', 0, 'false'),
            ('folded_root', 'pcpath_cond', 12, 'true')):
        checks += [f'S_bad_cast_{label} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} {line} {constant}) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_bad_cast_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond $(z_cast_precision + 1)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_bad_cast_precision,porigin_base,pkeyread.BASE)
S_bad_cast_leaf = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cast_leaf (PSTRING ([48]))) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_bad_cast_leaf,porigin_base,pkeyread.BASE)
S_budget_forged_cast = S_bad_cast_leaf[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
~$string_read_raw_known_base(S_budget_forged_cast,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) - 1 + len(checks), derived + len(checks)
