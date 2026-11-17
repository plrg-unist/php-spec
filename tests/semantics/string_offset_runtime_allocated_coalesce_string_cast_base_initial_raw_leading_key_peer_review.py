"""A STRING cast copies the exact REQUEST certified by its COALESCE child."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_peer_review import render as render_reference


def render(program, filename_b64):
    body, _, _ = render_reference(program, filename_b64)
    old = '$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_chain expression_right metadata_base)'
    assert body.count(old) == 1
    body = body.replace(old,
        '$origin_node(S_capture.SOURCES,porigin_base) = (NExprCastString expression_coalesce metadata_base)\n'
        '  -- if expression_coalesce = NExprBinaryOpCoalesce expression_chain expression_right metadata_coalesce')
    old = '$origin_child((porigin_base),[PCFIELD 0]) = (porigin_chain)'
    assert body.count(old) == 1
    body = body.replace(old,
        '$origin_child((porigin_base),[PCFIELD 0]) = (porigin_coalesce)\n'
        '  -- if $origin_child((porigin_coalesce),[PCFIELD 0]) = (porigin_chain)')
    old = '$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)'
    assert body.count(old) == 1
    body = body.replace(old, '$origin_child((porigin_coalesce),[PCFIELD 1]) = (porigin_right)')
    old = '~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)'
    assert body.count(old) == 1
    body = body.replace(old, old[1:])
    for name in ('promoted', 'digit', 'infinity', 'nan', 'digit_integer'):
        old = f'expression_{name}_base = NExprBinaryOpCoalesce expression_{name}_chain expression_right metadata_base'
        assert body.count(old) == 1
        body = body.replace(old,
            f'expression_{name}_coalesce = NExprBinaryOpCoalesce expression_{name}_chain expression_right metadata_coalesce\n'
            f'  -- if expression_{name}_base = NExprCastString expression_{name}_coalesce metadata_base')
    checks = lines(r'''
porigin_coalesce = PORIGIN n_unit pcpath_coalesce
$origin_node(S_capture.SOURCES,porigin_coalesce) = (expression_coalesce)
$code_expression(pcode.EXPRESSIONS,pcpath_coalesce) = ((z_coalesce,false))
$(z_coalesce > 0)
$compiled_precision(S_capture,(porigin_coalesce)) = (14)
$compiled_read(S_capture,porigin_coalesce) = eps
$compiled_identity_value(S_capture,porigin_coalesce) = eps
$constant_at(ppool.CONSTANTS,pcpath_coalesce) = eps
$string_read_runtime_value(S_capture,porigin_coalesce) = eps
~$string_read_allocated_value(S_capture,porigin_coalesce,pvalue_base)
$string_read_allocated_base(S_capture,porigin_coalesce,pvalue_base)
|S_capture.STRINGDATA| = 4
$cast_apply(S_capture,CASTSTRING,pvalue_base,z_base) = S_capture[.RESULT = KNOWN pvalue_base]
$cast_apply(S_suffix_entry,CASTSTRING,pvalue_base,z_base) = S_suffix_entry[.RESULT = KNOWN pvalue_base]
$string_read_allocated_value(S_suffix_entry,porigin_base,pvalue_base)
$cast_apply(S_clone,CASTSTRING,pvalue_clone,z_base) = S_clone[.RESULT = KNOWN pvalue_clone]
~$string_read_allocated_value(S_clone,porigin_base,pvalue_clone)
~$string_read_allocated_value(S_capture,porigin_base,PSTRING ($ptascii("-10.5bcde")))
~$string_read_allocated_value(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("-10.5bcde")))
S_child_unused = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_coalesce (PSTRING ($ptascii("unused")))) :: ppool.CONSTANTS]]]
$compiled_read(S_child_unused,porigin_coalesce) = eps
$string_read_allocated_base(S_child_unused,porigin_coalesce,pvalue_base)
$string_read_allocated_value(S_child_unused,porigin_base,pvalue_base)
$string_read_plan(S_child_unused) = (pstringread)
S_fallback_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_guard (NScalarInt (INTEGER 777) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_fallback_source,porigin_coalesce,pvalue_base)
~$string_read_allocated_value(S_fallback_source,porigin_base,pvalue_base)
$string_read_plan(S_fallback_source) = eps
$origin_node(S_capture.SOURCES,porigin_key) = (expression_cv)
expression_cv_coalesce = NExprBinaryOpCoalesce expression_cv expression_right metadata_coalesce
expression_cv_base = NExprCastString expression_cv_coalesce metadata_base
pcoccurrence_cv* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_base])
S_uncertified = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv* ++ pcunit.OCCURRENCES]]][.STORE[n_old] = DEFINED pvalue_base]
S_cv_read = $resolve_at(S_uncertified,VARIABLE ($ptascii("key")) 18,18)
S_cv_read.RESULT = KNOWN pvalue_base
$cast_apply(S_uncertified,CASTSTRING,pvalue_base,z_base) = S_uncertified[.RESULT = KNOWN pvalue_base]
~$string_read_allocated_base(S_uncertified,porigin_coalesce,pvalue_base)
~$string_read_allocated_value(S_uncertified,porigin_base,pvalue_base)
S_abrupt_copy = S_capture[.COMPLETION = UNSUPPORTED "control"]
$string_read_allocated_base(S_abrupt_copy,porigin_coalesce,pvalue_base)
$cast_apply(S_abrupt_copy,CASTSTRING,pvalue_base,z_base) = S_abrupt_copy
~$string_read_allocated_value(S_abrupt_copy,porigin_base,pvalue_base)
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_coalesce 0 false) :: pcode.EXPRESSIONS]]'),
            ('folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_coalesce z_coalesce true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_coalesce 17) :: ppool.CONSTANTS]]'),
            ('source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_coalesce (NExprBinaryOpCoalesce expression_chain expression_right eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_coalesce_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'~$string_read_allocated_value({state},porigin_base,pvalue_base)',
                   f'$string_read_plan({state}) = eps']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    main = body.split('def $main() = true\n', 1)[1]
    assert program in body
    derived_start = main.index('  -- if S_unmarked =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
