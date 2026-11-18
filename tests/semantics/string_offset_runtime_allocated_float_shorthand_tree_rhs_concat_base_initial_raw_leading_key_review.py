"""Proper FLOAT shorthands retain selected bits and one-row RHS allocation."""

import string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_review as minus
import string_offset_runtime_allocated_float_coalesce_tree_rhs_concat_base_initial_raw_leading_key_review as coalesce
from string_offset_retained_carrier_protocol import lines


def shorthand_tree(text, reference):
    text = coalesce.coalesce_tree(text, reference)
    selected = ('NExprCastDouble (NExprUnaryMinus '
        '(NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_negative) metadata_rhs_selected')
    skipped = ('NExprCastDouble (NExprBinaryOpDiv '
        '(NScalarFloat (FLOAT "3ff0000000000000") metadata_rhs_skipped_one) '
        '(NScalarFloat (FLOAT "0000000000000000") metadata_rhs_skipped_zero) metadata_rhs_skipped_div) metadata_rhs_skipped')
    condition = selected if reference else ('NExprCastDouble '
        '(NScalarFloat (FLOAT "0000000000000000") metadata_sh_condition_float) metadata_sh_condition')
    fallback = skipped if reference else selected
    metadata = 'metadata_nn' if reference else 'metadata_right_number'
    before = f'NExprBinaryOpCoalesce ({selected}) ({skipped}) {metadata}'
    assert text.count(before) == 1
    text = text.replace(before, f'NExprTernary ({condition}) ABSENT ({fallback}) {metadata}')
    if not reference:
        before = '$origin_child((porigin_right_number),[PCFIELD 0,PCFIELD 0,PCFIELD 0]) = (porigin_atom)'
        assert text.count(before) == 1
        text = text.replace(before, before.replace('[PCFIELD 0,', '[PCFIELD 2,', 1))
    return text


def shorthand_checks(reference):
    bits = 13851102128954671104 if reference else 9223372036854775808
    condition_bits = bits if reference else 0
    path = '[PCFIELD 0,PCFIELD 0,PCFIELD 0]' if reference else 'eps'
    checks = lines(f'''
$origin_child((porigin_right_number),{path}) = (porigin_shorthand)
$origin_node(S_capture.SOURCES,porigin_shorthand) = (NExprTernary expression_condition ABSENT expression_fallback metadata_shorthand)
$origin_child((porigin_shorthand),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_shorthand),[PCFIELD 1]) = (porigin_absent)
$origin_child((porigin_shorthand),[PCFIELD 2]) = (porigin_fallback)
$origin_node(S_capture.SOURCES,porigin_condition) = (expression_condition)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$origin_node(S_capture.SOURCES,porigin_fallback) = (expression_fallback)
porigin_shorthand = PORIGIN n_unit pcpath_shorthand
porigin_condition = PORIGIN n_unit pcpath_condition
porigin_fallback = PORIGIN n_unit pcpath_fallback
$code_expression(pcode.EXPRESSIONS,pcpath_shorthand) = ((z_shorthand,false))
$(z_shorthand > 0)
$compiled_read(S_capture,porigin_shorthand) = eps
$compiled_read(S_capture,porigin_condition) = eps
$compiled_read(S_capture,porigin_fallback) = eps
$compiled_precision(S_capture,(porigin_shorthand)) = (14)
$compiled_precision(S_capture,(porigin_condition)) = (14)
$compiled_precision(S_capture,(porigin_fallback)) = (14)
$string_read_runtime_value(S_capture,porigin_condition) = (PFLOAT {condition_bits})
$truth_value(S_capture,PFLOAT {condition_bits},z_shorthand) = S_capture[.RESULT = KNOWN (PBOOL {str(reference).lower()})]
$string_read_runtime_value(S_capture,porigin_shorthand) = (PFLOAT {bits})
''')
    checks += [f'$string_read_runtime_value(S_capture,porigin_fallback) = {"eps" if reference else "(PFLOAT 9223372036854775808)"}']
    return checks


def front(program, filename_b64, reference=False):
    prefix, checks = minus.front(program, filename_b64, reference=reference)
    return prefix, shorthand_tree('\n'.join(checks), reference).splitlines() + shorthand_checks(reference)


def render(program, filename_b64, reference=False):
    body, count, derived = minus.render(program, filename_b64, reference=reference)
    body = shorthand_tree(body, reference)
    before_pool = '~$string_read_allocated_value(S_number_pool,porigin_base,pvalue_base)'
    assert body.count(before_pool) == 1
    body = body.replace(before_pool, before_pool[1:])
    before_fold = '''S_unary_fold = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_number z_unary false) :: pcode.EXPRESSIONS]]]
  -- if $string_read_allocated_value(S_unary_fold,porigin_base,pvalue_base)
  -- if $string_read_plan(S_unary_fold) = (pstringread)'''
    assert body.count(before_fold) == 1
    body = body.replace(before_fold, before_fold.replace('z_unary false', 'z_unary true').replace(
        '  -- if $string_read_allocated_value', '  -- if ~$string_read_allocated_value').replace('= (pstringread)', '= eps'))
    checks = shorthand_checks(reference) + lines(r'''
$string_read_raw_float_sign_tree(expression_right_number)
$string_read_raw_float_sign_tree(NExprTernary expression_right_number ABSENT expression_right_number eps)
$string_read_raw_float_sign_tree(NExprTernary expression_right_number expression_right_number expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprTernary (NScalarInt (INTEGER 1) eps) ABSENT expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprTernary expression_right_number ABSENT (NScalarString (BYTES "MQ==") eps) eps)
~$string_read_raw_float_sign_tree(NExprTernary expression_right_number ABSENT (NExprCastDouble (NScalarString (BYTES "LTEyLjU=") eps) eps) eps)
''')
    for node in ('shorthand', 'condition', *(() if reference else ('fallback',))):
        checks += [f'S_bad_{node} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_{node},porigin_shorthand) = eps',
                   f'~$string_read_allocated_value(S_bad_{node},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_bad_{node}) = eps']
    if reference:
        checks += lines(r'''
expression_fallback = NExprCastDouble expression_skipped_div metadata_skipped_cast
$origin_child((porigin_fallback),[PCFIELD 0]) = (porigin_skipped_div)
$origin_node(S_capture.SOURCES,porigin_skipped_div) = (expression_skipped_div)
porigin_skipped_div = PORIGIN n_unit pcpath_skipped_div
S_skipped = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_fallback 17) :: (PCCPRECISION pcpath_skipped_div 17) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_fallback 0 true) :: (CODEEXPR pcpath_skipped_div 0 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_skipped,porigin_shorthand) = (PFLOAT 13851102128954671104)
$string_read_allocated_value(S_skipped,porigin_base,pvalue_base)
$string_read_plan(S_skipped) = (pstringread)
S_skipped_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_skipped_div (NScalarFloat (FLOAT "0000000000000000") eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_skipped_source,porigin_shorthand) = (PFLOAT 13851102128954671104)
~$string_read_allocated_value(S_skipped_source,porigin_base,pvalue_base)
$string_read_plan(S_skipped_source) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
