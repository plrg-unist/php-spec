"""Folded scalar CONCAT suffixes keep exact allocated headers and saved offsets."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain


def render(program, filename_b64, reference=False):
    body, _, _ = render_chain(program, filename_b64, reference=reference)
    inner = 'b23-41' if reference else 'b02-31'
    suffix = '' if reference else 'c1-10000'
    base = '10' + inner + suffix
    for old, new in [('10bcde', base), ('10bc', '10' + inner), ('bc', inner), ('de', suffix)]:
        body = body.replace('$ptascii("' + old + '")', '$ptascii("' + new + '")')
    if reference:
        body = body.replace('([99])', '([50])').replace('([100])', '([51])')
        body = body.replace('R:c;K:4;', 'R:2;K:4;')
    for node in ('inner_suffix', 'suffix'):
        old = f'expression_{node} = NScalarString (BYTES text_{node}) metadata_{node}'
        new = f'expression_{node} = NExprBinaryOpConcat expression_{node}_left expression_{node}_right metadata_{node}'
        assert body.count(old) == 1
        body = body.replace(old, new)
        body = body.replace(f'NScalarString (BYTES text_{node}) eps',
                            f'NExprBinaryOpConcat expression_{node}_left expression_{node}_right eps')
        body = '\n'.join(line for line in body.split('\n')
                         if not line.startswith('  -- if $base64(text_' + node + ')'))
    checks = []
    for node, value in (('inner_suffix', inner), ('suffix', suffix)):
        checks += [f'$string_read_literal_bytes(expression_{node}) = eps',
                   f'$string_read_folded_concat_bytes(expression_{node}) = ($ptascii("{value}"))',
                   f'$string_read_runtime_value(S_capture,porigin_{node}) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("{value}")))']
    checks += lines(r'''
$string_read_folded_concat_bytes(expression_integer) = ($ptascii("10"))
$string_read_runtime_value(S_capture,porigin_integer) = (PINT 10)
$string_read_folded_concat_bytes(NScalarFloat (FLOAT "4000000000000000") metadata_integer) = eps
$string_read_folded_concat_bytes(NExprCastString expression_integer metadata_cast) = eps
$origin_child((porigin_suffix),[PCFIELD 1]) = (porigin_suffix_right)
porigin_suffix_right = PORIGIN n_unit pcpath_suffix_right
''')
    if reference:
        checks += lines(r'''
expression_suffix_right = NExprConstFetch (NNameFullyQualified (BYTES text_suffix_name) metadata_suffix_name) metadata_suffix_const
porigin_suffix_const = porigin_suffix_right
''')
    else:
        checks += lines(r'''
expression_suffix_right = NExprUnaryMinus (NExprConstFetch (NNameFullyQualified (BYTES text_suffix_name) metadata_suffix_name) metadata_suffix_const) metadata_suffix_sign
$origin_child((porigin_suffix_right),[PCFIELD 0]) = (porigin_suffix_const)
''')
    checks += lines(r'''
$ptlc($base64(text_suffix_name)) = $ptascii("null")
$origin_child((porigin_suffix_const),[PCFIELD 0]) = (porigin_suffix_name)
porigin_suffix_name = PORIGIN n_unit pcpath_suffix_name
$origin_node(S_capture.SOURCES,porigin_suffix_name) = (NNameFullyQualified (BYTES text_suffix_name) metadata_suffix_name)
$compiled_read(S_capture,porigin_suffix_name) = eps
$compiled_identity_value(S_capture,porigin_suffix_name) = eps
$code_expression(pcode.EXPRESSIONS,pcpath_suffix_name) = eps
$constant_at(ppool.CONSTANTS,pcpath_suffix_name) = eps
''')
    if reference:
        checks += lines(r'''
$string_same(pvalue_inner,pvalue_base) = (false)
S_empty_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:3]]
$string_concat(S_empty_prefix,pvalue_inner,PSTRING_CARRIER INTERNED_STRING eps,false,true) = S_empty_prefix[.STRINGDATA = S_capture.STRINGDATA][.RESULT = KNOWN pvalue_base]
$string_concat(S_empty_prefix,pvalue_inner,PSTRING_CARRIER INTERNED_STRING eps,false,false) = S_empty_prefix[.RESULT = KNOWN pvalue_inner]
''')
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = lines(r'''
S_name_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_suffix_name 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_name_precision,porigin_base,pvalue_base)
$string_read_raw_capture(S_name_precision,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
S_name_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_suffix_name (NNameFullyQualified (BYTES text_suffix_name) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_base(S_name_shadow,porigin_base,pvalue_base)
$string_read_plan(S_name_shadow) = eps
S_scalar_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_suffix_right (PINT 7)) :: ppool.CONSTANTS]]]
~$string_read_allocated_base(S_scalar_pool,porigin_base,pvalue_base)
$string_read_plan(S_scalar_pool) = eps
S_string_pool_type = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_suffix (PINT 10)) :: ppool.CONSTANTS]]]
~$string_read_allocated_base(S_string_pool_type,porigin_base,pvalue_base)
''')
    integer_bytes = '10' + inner + '10'
    derived += [f'pvalue_integer_rhs = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("{integer_bytes}"))']
    derived += lines(r'''
S_integer_rhs = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_chain (NExprBinaryOpConcat expression_inner expression_integer metadata_chain)) :: (PCOCCURRENCE pcpath_suffix expression_integer) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_suffix (PINT 10)) :: ppool.CONSTANTS]]][.STRINGDATA = S_capture.STRINGDATA[0:3] ++ [$echo_value(pvalue_integer_rhs)]][.RESULT = KNOWN pvalue_integer_rhs]
$string_carrier_valid(S_integer_rhs,pvalue_integer_rhs)
$concat_constant(S_integer_rhs,(porigin_suffix)) = true
$string_read_runtime_value(S_integer_rhs,porigin_suffix) = (PINT 10)
~$string_read_allocated_value(S_integer_rhs,porigin_chain,pvalue_integer_rhs)
$string_read_raw_capture(S_integer_rhs,poperand,pvalue_integer_rhs) = eps
$string_read_plan(S_integer_rhs) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    assert 'text_inner_suffix' not in main and 'text_suffix)' not in main
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())


def render_reference(program, filename_b64):
    return render(program, filename_b64, reference=True)
