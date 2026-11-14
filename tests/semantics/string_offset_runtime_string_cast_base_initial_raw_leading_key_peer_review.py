"""A direct nested string cast preserves its header and the initial reference key."""

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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprCastString expression_inner metadata_base)
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = $ptascii("abc")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_inner) = (expression_inner)
$origin_node(S_capture.SOURCES,porigin_leaf) = (expression_leaf)
$compiled_read(S_capture,porigin_inner) = eps
$compiled_read(S_capture,porigin_leaf) = (PSTRING ($ptascii("abc")))
$compiled_precision(S_capture,(porigin_base)) = (14)
$compiled_precision(S_capture,(porigin_inner)) = (14)
$compiled_precision(S_capture,(porigin_leaf)) = (14)
$string_read_runtime_value(S_capture,porigin_inner) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_leaf) = (pvalue_base)
$cast_apply(S_capture,CASTSTRING,pvalue_base,18) = S_capture[.RESULT = KNOWN pvalue_base]
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
$string_read_raw_known_base(S_capture,porigin_inner,pvalue_base)
porigin_base = PORIGIN n_unit pcpath_base
porigin_inner = PORIGIN n_unit pcpath_inner
porigin_leaf = PORIGIN n_unit pcpath_leaf
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_unused_cast_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PINT 999)) :: (PCONSTANT pcpath_inner (PBOOL false)) :: ppool.CONSTANTS]]]
$compiled_read(S_unused_cast_pool,porigin_base) = eps
$compiled_read(S_unused_cast_pool,porigin_inner) = eps
$string_read_raw_known_base(S_unused_cast_pool,porigin_base,pvalue_base)
S_budget_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))]
$string_read_runtime_value(S_budget_cast,porigin_base) = eps
$string_read_raw_known_base(S_budget_cast,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_budget_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 18 true) :: pcode.EXPRESSIONS]]'),
            ('inner_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_inner 0 false) :: pcode.EXPRESSIONS]]'),
            ('inner_constant', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_inner 18 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base 17) :: ppool.CONSTANTS]]'),
            ('inner_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_inner 17) :: ppool.CONSTANTS]]'),
            ('leaf_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_leaf 17) :: ppool.CONSTANTS]]'),
            ('leaf_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('leaf_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 1)) :: ppool.CONSTANTS]]'),
            ('source', '.SOURCES = eps'),
            ('code', '.CODE = eps'),
            ('pool', '.POOLS = eps')):
        checks += [f'S_bad_cast_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_cast_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_cast_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('kind', 'pcpath_base', 'NExprCastBool expression_inner metadata_base'),
            ('inner', 'pcpath_inner', 'NExprCastString expression_leaf eps'),
            ('leaf', 'pcpath_leaf', 'NScalarString (BYTES text_leaf) eps')):
        checks += [f'S_bad_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_cast_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_budget_forged_cast = S_bad_cast_leaf_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_base]
~$string_read_raw_known_base(S_budget_forged_cast,porigin_base,pvalue_base)
''')
    for label, child, raw, value in (
            ('digit_zero', 'NScalarInt (INTEGER 0) metadata_inner', 'PINT 0', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            ('digit_one', 'NScalarInt (INTEGER 1) metadata_inner', 'PINT 1', 'PSTRING_CARRIER INTERNED_STRING ([49])'),
            ('digit_nine', 'NScalarInt (INTEGER 9) metadata_inner', 'PINT 9', 'PSTRING_CARRIER INTERNED_STRING ([57])'),
            ('integer_ten', 'NScalarInt (INTEGER 10) metadata_inner', 'PINT 10', None),
            ('float_one', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_inner', 'PFLOAT 4607182418800017408', None),
            ('empty', 'NScalarString (BYTES "") metadata_inner', 'PSTRING ([])', 'PSTRING_CARRIER INTERNED_STRING ([])'),
            ('zero', 'NScalarString (BYTES "MA==") metadata_inner', 'PSTRING ([48])', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            ('two_zeroes', 'NScalarString (BYTES "MDA=") metadata_inner', 'PSTRING ([48,48])', 'PSTRING_CARRIER INTERNED_STRING ([48,48])'),
            ('nul', 'NScalarString (BYTES "AA==") metadata_inner', 'PSTRING ([0])', None)):
        checks += lines(f'''
expression_cast_{label}_child = {child}
expression_cast_{label} = NExprCastString expression_cast_{label}_child metadata_base
S_cast_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_cast_{label}) :: (PCOCCURRENCE pcpath_inner expression_cast_{label}_child) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner ({raw})) :: (PCCPRECISION pcpath_base 14) :: (PCCPRECISION pcpath_inner 14) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 18 false) :: (CODEEXPR pcpath_inner 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_cast_{label},porigin_base) = eps
$string_read_runtime_value(S_cast_{label},porigin_base) = {"(" + value + ")" if value else "eps"}
~$string_read_raw_known_base(S_cast_{label},porigin_base,pvalue_base)
''')
        if value is not None:
            checks += [f'$string_read_raw_known_base(S_cast_{label},porigin_base,{value})',
                       f'$string_read_raw_leading({value},pvalue_raw) = (1)',
                       f'$string_read_in_range({value},1) = {str(label == "two_zeroes").lower()}']
    for n in (0, 1):
        checks += lines(f'''
expression_bool_{n}_leaf = NScalarString (BYTES "{('MA==', 'MQ==')[n]}") metadata_leaf
expression_bool_{n} = NExprCastBool expression_bool_{n}_leaf metadata_inner
expression_bool_{n}_base = NExprCastString expression_bool_{n} metadata_base
S_bool_{n} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bool_{n}_base) :: (PCOCCURRENCE pcpath_inner expression_bool_{n}) :: (PCOCCURRENCE pcpath_leaf expression_bool_{n}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PSTRING ([{48+n}]))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_bool_{n},porigin_inner) = (PBOOL {str(n == 1).lower()})
$string_read_runtime_value(S_bool_{n},porigin_base) = (PSTRING_CARRIER INTERNED_STRING ({'[49]' if n else '[]'}))
$string_read_raw_known_base(S_bool_{n},porigin_base,PSTRING_CARRIER INTERNED_STRING ({'[49]' if n else '[]'}))
''')
    for raw in ('word', '1.5x'):
        checks.append(f'$string_read_raw_leading(pvalue_base,PSTRING ($ptascii("{raw}"))) = eps')
    checks += lines(r'''
$string_read_raw_leading(pvalue_base,PSTRING ($ptascii("3x"))) = (3)
$string_read_raw_leading(pvalue_base,PSTRING ($ptascii("-4x"))) = (-4)
$string_read_raw_leading(pvalue_base,PSTRING ($ptascii("-1x"))) = (-1)
~$string_read_in_range(pvalue_base,3)
~$string_read_in_range(pvalue_base,-4)
$string_read_in_range(pvalue_base,-1)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
