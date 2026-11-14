"""Falsey emitted scalar casts preserve the fallback and frozen raw CV offset."""

from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_review import render as render_zero
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_zero(program, filename_b64)
    for old, new in (
            ('NExprTernary (NScalarInt (INTEGER 0) metadata_cond)', 'NExprTernary (NExprCastDouble expression_cast_int metadata_cond)'),
            ('$compiled_read(S_capture,porigin_cond) = (PINT 0)', '$compiled_read(S_capture,porigin_cond) = eps'),
            ('~$truth(S_capture,PINT 0)', '$string_read_runtime_value(S_capture,porigin_cond) = (PFLOAT 0)'),
            ('pvalue_condition = PINT 0', 'pvalue_condition = PFLOAT 0')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    early = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
S_capture.CODE = [pcode]
pcode.UNIT = n_unit
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprCastDouble expression_cast_int metadata_cond)
expression_cast_int = NExprCastInt expression_cast_bool metadata_cast_int
expression_cast_bool = NExprCastBool expression_cast_leaf metadata_cast_bool
expression_cast_leaf = NScalarString (BYTES text_cast_leaf) metadata_cast_leaf
$base64(text_cast_leaf) = [48]
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cast_int)
$origin_child((porigin_cast_int),[PCFIELD 0]) = (porigin_cast_bool)
$origin_child((porigin_cast_bool),[PCFIELD 0]) = (porigin_cast_leaf)
$origin_node(S_capture.SOURCES,porigin_cast_int) = (expression_cast_int)
$origin_node(S_capture.SOURCES,porigin_cast_bool) = (expression_cast_bool)
$origin_node(S_capture.SOURCES,porigin_cast_leaf) = (expression_cast_leaf)
$compiled_read(S_capture,porigin_cast_int) = eps
$compiled_read(S_capture,porigin_cast_bool) = eps
$compiled_read(S_capture,porigin_cast_leaf) = (PSTRING ([48]))
$compiled_precision(S_capture,(porigin_cond)) = (z_cast_precision)
$compiled_precision(S_capture,(porigin_cast_int)) = (z_cast_precision)
$compiled_precision(S_capture,(porigin_cast_bool)) = (z_cast_precision)
$compiled_precision(S_capture,(porigin_cast_leaf)) = (z_cast_precision)
$string_read_runtime_value(S_capture,porigin_cast_bool) = (PBOOL false)
$string_read_runtime_value(S_capture,porigin_cast_int) = (PINT 0)
$cast_apply(S_capture,CASTFLOAT,PINT 0,12) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$truth_value(S_capture,PFLOAT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_cond) = eps\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    for state in ('S_wrong_condition', 'S_boolean_condition', 'S_other'):
        statement = next(line for line in body.splitlines() if line.startswith('  -- if ' + state + ' = '))
        update = '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 12 true) :: pcode.EXPRESSIONS]]]'
        if state == 'S_other':
            update += '[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT 0)) :: ppool.CONSTANTS]]]'
        body = body.replace(statement, statement + update)
    checks = lines(r'''
porigin_cast_int = PORIGIN n_unit pcpath_cast_int
porigin_cast_bool = PORIGIN n_unit pcpath_cast_bool
porigin_cast_leaf = PORIGIN n_unit pcpath_cast_leaf
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_budget_cast,porigin_cond) = eps
$string_read_raw_known_base(S_budget_cast,porigin_base,pkeyread.BASE)
S_unused_cast_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL true)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_cast_pool,porigin_cond) = eps
$string_read_raw_known_base(S_unused_cast_pool,porigin_base,pkeyread.BASE)
S_bad_cast_leaf = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cast_leaf (PSTRING ([49]))) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_bad_cast_leaf,porigin_base,pkeyread.BASE)
S_bad_budget_cast = S_bad_cast_leaf[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
~$string_read_raw_known_base(S_bad_budget_cast,porigin_base,pkeyread.BASE)
S_bad_cast_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cond $(z_cast_precision + 1)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_bad_cast_precision,porigin_base,pkeyread.BASE)
''')
    for label, path, node in (
            ('condition', 'pcpath_cond', 'NExprCastDouble expression_cast_int eps'),
            ('inner', 'pcpath_cast_int', 'NExprCastInt expression_cast_bool eps'),
            ('bool', 'pcpath_cast_bool', 'NExprCastBool expression_cast_leaf eps'),
            ('leaf', 'pcpath_cast_leaf', 'NScalarString (BYTES text_cast_leaf) eps'),
            ('fallback', '(pcpath_base ++ [PCFIELD 2])', 'NScalarString (BYTES text_false) eps')):
        checks += [f'S_bad_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_source,porigin_base,pkeyread.BASE)']
    for label, path in (('root', 'pcpath_cond'), ('int', 'pcpath_cast_int'), ('bool', 'pcpath_cast_bool')):
        checks += [f'S_bad_cast_{label}_line = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_line,porigin_base,pkeyread.BASE)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
