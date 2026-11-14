"""A truthy emitted string cast keeps its own header and the captured reference key."""

from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_peer_review import render as render_zero
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_zero(program, filename_b64)
    for old, new in (
            ('NExprTernary (NScalarInt (INTEGER 0) metadata_cond)', 'NExprTernary (NExprCastString expression_inner metadata_cond)'),
            ('$base64(text_right) = $ptascii("abc")', '$base64(text_right) = $ptascii("XYZ")'),
            ('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = eps'),
            ('~$truth(S_capture,PINT 0)', '$string_read_runtime_value(S_capture,porigin_left) = (pvalue_base)'),
            ('$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("XYZ")))'),
            ('$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("abc"))) = pvalue_base', '$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("XYZ"))) = pvalue_wrong')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    anchor = '  -- if S_wrong_left = '
    assert body.count(anchor) == 1
    body = body.replace(anchor, '  -- if S_capture.CODE = [pcode]\n  -- if n_unit = pcode.UNIT\n' + anchor)
    for name in ('S_wrong_left', 'S_nonzero_pool', 'S_wrong_condition', 'S_nonzero_source'):
        statement = next(line for line in body.splitlines() if line.startswith('  -- if ' + name + ' = '))
        update = '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]]'
        if name == 'S_nonzero_source':
            update += '[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 0)) :: ppool.CONSTANTS]]]'
        body = body.replace(statement, statement + update)
    checks = lines(r'''
expression_cond = NExprCastString expression_inner metadata_cond
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = $ptascii("abc")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_inner)
$origin_node(S_capture.SOURCES,porigin_inner) = (expression_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (expression_leaf)
$compiled_read(S_capture,porigin_inner) = eps
$compiled_read(S_capture,porigin_leaf) = (PSTRING ($ptascii("abc")))
$compiled_precision(S_capture,(porigin_left)) = (14)
$compiled_precision(S_capture,(porigin_inner)) = (14)
$compiled_precision(S_capture,(porigin_leaf)) = (14)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_leaf) = (pvalue_base)
$cast_apply(S_capture,CASTSTRING,pvalue_base,18) = S_capture[.RESULT = KNOWN pvalue_base]
$truth_value(S_capture,pvalue_base,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
porigin_inner = PORIGIN n_unit pcpath_inner
porigin_leaf = PORIGIN n_unit pcpath_leaf
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
S_unused_cast_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_cast_pool,porigin_left) = eps
$string_read_raw_known_base(S_unused_cast_pool,porigin_base,pvalue_base)
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_wrong]
$string_read_runtime_value(S_budget_cast,porigin_left) = eps
$string_read_raw_known_base(S_budget_cast,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_cast,porigin_base,pvalue_wrong)
''')
    for label, update in (
            ('condition_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 0 false) :: pcode.EXPRESSIONS]]'),
            ('condition_constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode.EXPRESSIONS]]'),
            ('inner_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_inner 0 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]'),
            ('inner_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_inner 17) :: ppool.CONSTANTS]]'),
            ('leaf_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('leaf_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 1)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_cast_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_cast_{label},porigin_left) = eps',
                   f'~$string_read_raw_known_base(S_bad_cast_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('condition', 'pcpath_left', 'NExprCastString expression_inner eps'),
            ('inner', 'pcpath_inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'pcpath_leaf', 'NScalarString (BYTES text_leaf) eps'),
            ('fallback', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        checks += [f'S_bad_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_budget_forged_cast = S_bad_cast_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_cast,porigin_base,pvalue_base)
''')
    for label, child, raw, value, truth in (
            ('digit_zero', 'NScalarInt (INTEGER 0) metadata_inner', 'PINT 0', 'PSTRING_CARRIER INTERNED_STRING ([48])', False),
            ('digit_one', 'NScalarInt (INTEGER 1) metadata_inner', 'PINT 1', 'PSTRING_CARRIER INTERNED_STRING ([49])', True),
            ('digit_nine', 'NScalarInt (INTEGER 9) metadata_inner', 'PINT 9', 'PSTRING_CARRIER INTERNED_STRING ([57])', True),
            ('integer_ten', 'NScalarInt (INTEGER 10) metadata_inner', 'PINT 10', None, False),
            ('float_one', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_inner', 'PFLOAT 4607182418800017408', None, False),
            ('empty', 'NScalarString (BYTES "") metadata_inner', 'PSTRING ([])', 'PSTRING_CARRIER INTERNED_STRING ([])', False),
            ('zero', 'NScalarString (BYTES "MA==") metadata_inner', 'PSTRING ([48])', 'PSTRING_CARRIER INTERNED_STRING ([48])', False),
            ('two_zeroes', 'NScalarString (BYTES "MDA=") metadata_inner', 'PSTRING ([48,48])', 'PSTRING_CARRIER INTERNED_STRING ([48,48])', True),
            ('nul', 'NScalarString (BYTES "AA==") metadata_inner', 'PSTRING ([0])', None, False)):
        checks += lines(f'''
expression_string_cast_{label}_child = {child}
expression_string_cast_{label} = NExprCastString expression_string_cast_{label}_child metadata_cond
expression_string_cast_{label}_base = NExprTernary expression_string_cast_{label} ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_string_cast_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_string_cast_{label}_base) :: (PCOCCURRENCE pcpath_left expression_string_cast_{label}) :: (PCOCCURRENCE pcpath_inner expression_string_cast_{label}_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner ({raw})) :: (PCCPRECISION pcpath_left 14) :: (PCCPRECISION pcpath_inner 14) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: (CODEEXPR pcpath_inner 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_string_cast_{label},porigin_left) = eps
$string_read_runtime_value(S_string_cast_{label},porigin_left) = {"(" + value + ")" if value else "eps"}
$string_read_raw_known_base(S_string_cast_{label},porigin_base,pvalue_wrong) = {str(value is not None and not truth).lower()}
''')
        if value is not None:
            checks.append(f'$string_read_raw_known_base(S_string_cast_{label},porigin_base,{value}) = {str(truth).lower()}')
    for n in (0, 1):
        checks += lines(f'''
expression_bool_{n}_leaf = NScalarString (BYTES "{('MA==', 'MQ==')[n]}") metadata_leaf
expression_bool_{n} = NExprCastBool expression_bool_{n}_leaf metadata_inner
expression_bool_{n}_condition = NExprCastString expression_bool_{n} metadata_cond
expression_bool_{n}_base = NExprTernary expression_bool_{n}_condition ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_bool_{n} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bool_{n}_base) :: (PCOCCURRENCE pcpath_left expression_bool_{n}_condition) :: (PCOCCURRENCE pcpath_inner expression_bool_{n}) :: (PCOCCURRENCE pcpath_leaf expression_bool_{n}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ([{48+n}]))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_bool_{n},porigin_inner) = (PBOOL {str(n == 1).lower()})
$string_read_runtime_value(S_bool_{n},porigin_left) = (PSTRING_CARRIER INTERNED_STRING ({'[49]' if n else '[]'}))
$string_read_raw_known_base(S_bool_{n},porigin_base,pvalue_wrong) = {str(n == 0).lower()}
$string_read_raw_known_base(S_bool_{n},porigin_base,PSTRING_CARRIER INTERNED_STRING ({'[49]' if n else '[]'})) = {str(n == 1).lower()}
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + 2 + len(checks), derived + 2 + len(checks)
