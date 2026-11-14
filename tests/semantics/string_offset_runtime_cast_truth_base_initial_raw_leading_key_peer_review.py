"""Emitted primitive casts preserve literal bases and the captured reference key."""

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary expression_cond')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = eps')
    body = body.replace('~$truth(S_capture,PINT 0)', '$string_read_runtime_value(S_capture,porigin_left) = (PFLOAT 0)')
    anchor = '  -- if S_wrong_left = '
    assert body.count(anchor) == 1
    body = body.replace(anchor, '  -- if S_capture.CODE = [pcode]\n  -- if n_unit = pcode.UNIT\n' + anchor)
    for name in ('S_wrong_left', 'S_wrong_condition'):
        statement = next(line for line in body.splitlines() if line.startswith('  -- if ' + name + ' = '))
        body = body.replace(statement, statement + '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]]')
    checks = lines(r'''
expression_cond = NExprCastDouble expression_bool metadata_cond
expression_bool = NExprCastBool expression_text metadata_bool
expression_text = NScalarString (BYTES text_zero) metadata_text
$base64(text_zero) = [48]
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_bool)
$origin_node(S_capture.SOURCES,porigin_bool) = (expression_bool)
$origin_child((porigin_bool),[PCFIELD 0]) = (porigin_text)
$origin_node(S_capture.SOURCES,porigin_text) = (expression_text)
$compiled_read(S_capture,porigin_bool) = eps
$compiled_read(S_capture,porigin_text) = (PSTRING ([48]))
$compiled_precision(S_capture,(porigin_left)) = (14)
$compiled_precision(S_capture,(porigin_bool)) = (14)
$compiled_precision(S_capture,(porigin_text)) = (14)
$string_read_runtime_value(S_capture,porigin_bool) = (PBOOL false)
$string_read_runtime_value(S_capture,porigin_text) = (PSTRING_CARRIER INTERNED_STRING ([48]))
$cast_apply(S_capture,CASTFLOAT,PBOOL false,18) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$truth_value(S_capture,PFLOAT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_bool = PORIGIN n_unit pcpath_bool
porigin_text = PORIGIN n_unit pcpath_text
$origin_node(S_capture.SOURCES,porigin_true) = (expression_true)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_false)
S_unused_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL true)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_pool,porigin_left) = eps
$string_read_runtime_value(S_unused_pool,porigin_left) = (PFLOAT 0)
$string_read_raw_known_base(S_unused_pool,porigin_base,pvalue_base)
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_budget_cast,porigin_left) = eps
$string_read_raw_known_base(S_budget_cast,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_cast,porigin_base,pvalue_wrong)
''')
    for label, update in (
            ('condition_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 0 false) :: pcode.EXPRESSIONS]]'),
            ('condition_constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]'),
            ('child_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_bool 0 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]'),
            ('child_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_bool 17) :: ppool.CONSTANTS]]'),
            ('leaf_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_text (PSTRING ([49]))) :: ppool.CONSTANTS]]'),
            ('leaf_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_text (PINT 0)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_cast_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_cast_{label},porigin_left) = eps',
                   f'~$string_read_raw_known_base(S_bad_cast_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('condition', 'pcpath_left', 'NExprCastDouble expression_bool eps'),
            ('child', 'pcpath_bool', 'NExprCastBool expression_text eps'),
            ('leaf', 'pcpath_text', 'NScalarString (BYTES text_zero) eps'),
            ('unselected', 'pcpath_true', 'NScalarString (BYTES text_true) eps')):
        checks += [f'S_bad_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_source,porigin_base,pvalue_base)']
    for kind, scalar, values in (
            ('Bool', 'NScalarInt (INTEGER {n}) metadata_text', ('PBOOL false', 'PBOOL true')),
            ('Int', 'NScalarString (BYTES "{text}") metadata_text', ('PINT 0', 'PINT 1')),
            ('Double', 'NScalarInt (INTEGER {n}) metadata_text', ('PFLOAT 0', 'PFLOAT 4607182418800017408')),
            ('String', 'NScalarInt (INTEGER {n}) metadata_text', ('PSTRING_CARRIER INTERNED_STRING ([48])', 'PSTRING_CARRIER INTERNED_STRING ([49])'))):
        for n, value in enumerate(values):
            label = kind.lower() + str(n)
            child = scalar.format(n=n, text=('MA==', 'MQ==')[n])
            raw = 'PSTRING ([' + str(48 + n) + '])' if kind == 'Int' else 'PINT ' + str(n)
            checks += lines(f'''
expression_cast_{label}_child = {child}
expression_cast_{label} = NExprCast{kind} expression_cast_{label}_child metadata_cond
expression_cast_{label}_base = NExprTernary expression_cast_{label} expression_true expression_false metadata
S_cast_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_cast_{label}_base) :: (PCOCCURRENCE pcpath_left expression_cast_{label}) :: (PCOCCURRENCE pcpath_bool expression_cast_{label}_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_bool ({raw})) :: (PCCPRECISION pcpath_left 14) :: (PCCPRECISION pcpath_bool 14) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: (CODEEXPR pcpath_bool 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_cast_{label},porigin_left) = eps
$string_read_runtime_value(S_cast_{label},porigin_left) = ({value})
$string_read_raw_known_base(S_cast_{label},porigin_base,pvalue_wrong) = {str(kind != 'String' and n == 1).lower()}
$string_read_raw_known_base(S_cast_{label},porigin_base,pvalue_base) = {str(kind != 'String' and n == 0).lower()}
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + 2 + len(checks), derived + 2 + len(checks)
