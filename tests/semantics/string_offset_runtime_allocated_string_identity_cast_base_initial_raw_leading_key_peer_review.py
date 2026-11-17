"""An outer STRING cast copies only the exact proven REQUEST child header."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_peer_review import render as render_reference


def render(program, filename_b64):
    body, _, _ = render_reference(program, filename_b64)
    old = '$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_chain expression_right metadata_base)'
    assert body.count(old) == 1
    body = body.replace(old,
        '$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_identity expression_right metadata_base)\n'
        '  -- if expression_identity = NExprCastString expression_chain metadata_identity')
    old = '$origin_child((porigin_base),[PCFIELD 0]) = (porigin_chain)'
    assert body.count(old) == 1
    body = body.replace(old,
        '$origin_child((porigin_base),[PCFIELD 0]) = (porigin_identity)\n'
        '  -- if $origin_child((porigin_identity),[PCFIELD 0]) = (porigin_chain)')
    # Keep the inherited synthetic producers at the fresh source's deeper paths.
    for name in ('promoted', 'digit', 'infinity', 'nan', 'digit_integer'):
        old = f'expression_{name}_base = NExprBinaryOpCoalesce expression_{name}_chain expression_right metadata_base'
        assert body.count(old) == 1
        body = body.replace(old,
            f'expression_{name}_identity = NExprCastString expression_{name}_chain metadata_identity\n'
            f'  -- if expression_{name}_base = NExprBinaryOpCoalesce expression_{name}_identity expression_right metadata_base')
    checks = lines(r'''
porigin_identity = PORIGIN n_unit pcpath_identity
$origin_node(S_capture.SOURCES,porigin_identity) = (expression_identity)
$compiled_precision(S_capture,(porigin_identity)) = (14)
$code_expression(pcode.EXPRESSIONS,pcpath_identity) = ((z_identity,false))
$(z_identity > 0)
$compiled_read(S_capture,porigin_identity) = eps
$compiled_identity_value(S_capture,porigin_identity) = eps
$constant_at(ppool.CONSTANTS,pcpath_identity) = eps
$string_read_runtime_value(S_capture,porigin_identity) = eps
$string_read_allocated_value(S_capture,porigin_identity,pvalue_base)
$string_read_allocated_value(S_capture,porigin_chain,pvalue_base)
|S_capture.STRINGDATA| = 4
$cast_apply(S_capture,CASTSTRING,pvalue_base,z_identity) = S_capture[.RESULT = KNOWN pvalue_base]
$cast_apply(S_suffix_entry,CASTSTRING,pvalue_base,z_identity) = S_suffix_entry[.RESULT = KNOWN pvalue_base]
$string_read_allocated_value(S_suffix_entry,porigin_identity,pvalue_base)
$cast_apply(S_clone,CASTSTRING,pvalue_clone,z_identity) = S_clone[.RESULT = KNOWN pvalue_clone]
~$string_read_allocated_value(S_clone,porigin_identity,pvalue_clone)
~$string_read_allocated_value(S_capture,porigin_identity,PSTRING ($ptascii("-10.5bcde")))
~$string_read_allocated_value(S_capture,porigin_identity,PSTRING_CARRIER INTERNED_STRING ($ptascii("-10.5bcde")))
S_identity_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:3]]
~$string_carrier_valid(S_identity_prefix,pvalue_base)
~$string_read_allocated_value(S_identity_prefix,porigin_identity,pvalue_base)
S_identity_unused = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_identity (PSTRING ($ptascii("unused")))) :: ppool.CONSTANTS]]]
$compiled_read(S_identity_unused,porigin_identity) = eps
$string_read_allocated_value(S_identity_unused,porigin_identity,pvalue_base)
$string_read_raw_capture(S_identity_unused,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
$string_read_plan(S_identity_unused) = (pstringread)
$origin_node(S_capture.SOURCES,porigin_key) = (expression_cv)
expression_cv_identity = NExprCastString expression_cv metadata_identity
expression_cv_base = NExprBinaryOpCoalesce expression_cv_identity expression_right metadata_base
pcoccurrence_cv* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_base])
S_uncertified = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv* ++ pcunit.OCCURRENCES]]][.STORE[n_old] = DEFINED pvalue_base]
$origin_node(S_uncertified.SOURCES,porigin_chain) = (expression_cv)
$string_carrier_valid(S_uncertified,pvalue_base)
S_cv_read = $resolve_at(S_uncertified,VARIABLE ($ptascii("key")) 18,18)
S_cv_read.RESULT = KNOWN pvalue_base
$cast_apply(S_uncertified,CASTSTRING,pvalue_base,z_identity) = S_uncertified[.RESULT = KNOWN pvalue_base]
~$string_read_allocated_value(S_uncertified,porigin_chain,pvalue_base)
~$string_read_allocated_value(S_uncertified,porigin_identity,pvalue_base)
~$string_read_allocated_base(S_uncertified,porigin_base,pvalue_base)
''')
    updates = (
        ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_identity 0 false) :: pcode.EXPRESSIONS]]'),
        ('folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_identity z_identity true) :: pcode.EXPRESSIONS]]'),
        ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_identity 17) :: ppool.CONSTANTS]]'),
        ('shape', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_identity (NScalarInt (INTEGER 10) metadata_identity)) :: pcunit.OCCURRENCES]]'),
        ('child_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_chain (NExprBinaryOpConcat expression_inner expression_de eps)) :: pcunit.OCCURRENCES]]'))
    for label, update in updates:
        state = 'S_identity_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'~$string_read_allocated_value({state},porigin_identity,pvalue_base)',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_plan({state}) = eps']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    main = body.split('def $main() = true\n', 1)[1]
    assert program in body
    derived_start = main.index('  -- if S_unmarked =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
