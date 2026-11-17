"""Emitted STRING casts preserve certified REQUEST children and their owners."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_review import render as render_float


def render(program, filename_b64, reference=False):
    renderer = render_float if reference else render_chain
    body, _, _ = renderer(program, filename_b64, reference=reference)
    child = 'chain' if reference else 'inner'
    value = 'pvalue_base' if reference else 'pvalue_inner'
    text = '-10.5bcde' if reference else '10bc'
    identity = 3 if reference else 2
    if reference:
        old = 'NExprBinaryOpCoalesce expression_chain expression_skipped metadata_base'
        assert body.count(old) == 1
        body = body.replace(old + ')', 'NExprBinaryOpCoalesce expression_identity expression_skipped metadata_base)\n'
                            '  -- if expression_identity = NExprCastString expression_chain metadata_identity')
        old = '$origin_child((porigin_base),[PCFIELD 0]) = (porigin_chain)'
    else:
        old = 'expression_chain = NExprBinaryOpConcat expression_inner expression_suffix metadata_chain'
        assert body.count(old) == 1
        body = body.replace(old, 'expression_chain = NExprBinaryOpConcat expression_identity expression_suffix metadata_chain\n'
                            '  -- if expression_identity = NExprCastString expression_inner metadata_identity')
        old = '$origin_child((porigin_chain),[PCFIELD 0]) = (porigin_inner)'
    assert body.count(old) == 1
    body = body.replace(old, old.rsplit(' = ', 1)[0] + ' = (porigin_identity)\n'
                        f'  -- if $origin_child((porigin_identity),[PCFIELD 0]) = (porigin_{child})')
    checks = lines(f'''
porigin_identity = PORIGIN n_unit pcpath_identity
$origin_node(S_capture.SOURCES,porigin_identity) = (expression_identity)
$compiled_precision(S_capture,(porigin_identity)) = (14)
$compiled_read(S_capture,porigin_identity) = eps
$compiled_identity_value(S_capture,porigin_identity) = eps
$code_expression(pcode.EXPRESSIONS,pcpath_identity) = ((z_identity,false))
$(z_identity > 0)
pvalue_identity = {value}
pvalue_identity = PSTRING_CARRIER (REQUEST_STRING {identity}) ($ptascii("{text}"))
$string_read_runtime_value(S_capture,porigin_identity) = eps
$string_read_allocated_value(S_capture,porigin_identity,pvalue_identity)
$cast_apply(S_capture,CASTSTRING,pvalue_identity,z_identity) = S_capture[.RESULT = KNOWN pvalue_identity]
|S_capture.STRINGDATA| = 4
''')
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = lines(f'''
S_identity_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:{identity}]]
~$string_carrier_valid(S_identity_prefix,pvalue_identity)
~$string_read_allocated_value(S_identity_prefix,porigin_identity,pvalue_identity)
pvalue_identity_clone = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("{text}"))
S_identity_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("{text}")]]
$string_carrier_valid(S_identity_clone,pvalue_identity_clone)
$cast_apply(S_identity_clone,CASTSTRING,pvalue_identity_clone,z_identity) = S_identity_clone[.RESULT = KNOWN pvalue_identity_clone]
~$string_read_allocated_value(S_identity_clone,porigin_identity,pvalue_identity_clone)
~$string_read_allocated_value(S_capture,porigin_identity,PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}")))
~$string_read_allocated_value(S_capture,porigin_identity,PSTRING ($ptascii("{text}")))
S_identity_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_identity (PSTRING ($ptascii("{text}")))) :: ppool.CONSTANTS]]]
$compiled_read(S_identity_pool,porigin_identity) = eps
$string_read_allocated_base(S_identity_pool,porigin_base,pvalue_base)
$string_read_plan(S_identity_pool) = (pstringread)
S_identity_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_identity (NExprCastString expression_{child} eps)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_base(S_identity_shadow,porigin_base,pvalue_base)
$string_read_plan(S_identity_shadow) = eps
S_identity_abrupt = S_capture[.COMPLETION = UNSUPPORTED "control"]
~$string_read_allocated_value(S_identity_abrupt,porigin_identity,pvalue_identity)
''')
    for label, flag, line in [('line', 'false', '0'), ('folded', 'true', 'z_identity')]:
        state = 'S_identity_' + label
        derived += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_identity {line} {flag}) :: pcode.EXPRESSIONS]]]',
                    f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                    f'$string_read_plan({state}) = eps']
    derived += lines(r'''
S_identity_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_identity 17) :: ppool.CONSTANTS]]]
~$string_read_allocated_base(S_identity_precision,porigin_base,pvalue_base)
$string_read_plan(S_identity_precision) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())


def render_reference(program, filename_b64):
    return render(program, filename_b64, reference=True)
