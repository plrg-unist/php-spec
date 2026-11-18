"""Proper FLOAT full ternaries retain quiet truth, bits and one-row RHS allocation."""

import string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_review as minus
import string_offset_runtime_allocated_float_coalesce_tree_rhs_concat_base_initial_raw_leading_key_review as coalesce
from string_offset_retained_carrier_protocol import lines


def ternary_tree(text, reference):
    text = coalesce.coalesce_tree(text, reference)
    selected = ('NExprCastDouble (NExprUnaryMinus '
        '(NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_negative) metadata_rhs_selected')
    skipped = ('NExprCastDouble (NExprBinaryOpDiv '
        '(NScalarFloat (FLOAT "3ff0000000000000") metadata_rhs_skipped_one) '
        '(NScalarFloat (FLOAT "0000000000000000") metadata_rhs_skipped_zero) metadata_rhs_skipped_div) metadata_rhs_skipped')
    condition = ('NExprCastDouble (NScalarFloat (FLOAT "3ff0000000000000") metadata_rhs_condition_atom) metadata_rhs_condition') if reference else (
        'NExprCastDouble (NExprUnaryMinus (NScalarFloat (FLOAT "0000000000000000") metadata_rhs_condition_atom) metadata_rhs_condition_negative) metadata_rhs_condition')
    metadata = 'metadata_nn' if reference else 'metadata_right_number'
    before = f'NExprBinaryOpCoalesce ({selected}) ({skipped}) {metadata}'
    true, false = (selected, skipped) if reference else (skipped, selected)
    assert text.count(before) == 1
    text = text.replace(before, f'NExprTernary ({condition}) ({true}) ({false}) {metadata}')
    old_path = ','.join(['PCFIELD 0'] * (6 if reference else 3))
    new_path = ','.join(['PCFIELD 0'] * 3 + ['PCFIELD 1', 'PCFIELD 0', 'PCFIELD 0']) if reference else 'PCFIELD 2,PCFIELD 0,PCFIELD 0'
    before = f'$origin_child((porigin_right_number),[{old_path}]) = (porigin_atom)'
    assert text.count(before) == 1
    return text.replace(before, f'$origin_child((porigin_right_number),[{new_path}]) = (porigin_atom)')


def ternary_checks(reference):
    bits = 13851102128954671104 if reference else 9223372036854775808
    condition_bits = 4607182418800017408 if reference else 9223372036854775808
    path = '[PCFIELD 0,PCFIELD 0,PCFIELD 0]' if reference else 'eps'
    selected, skipped = ('true', 'false') if reference else ('false', 'true')
    return lines(f'''
$origin_child((porigin_right_number),{path}) = (porigin_ternary)
$origin_node(S_capture.SOURCES,porigin_ternary) = (NExprTernary expression_condition expression_true expression_false metadata_ternary)
$origin_child((porigin_ternary),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_ternary),[PCFIELD 1]) = (porigin_true)
$origin_child((porigin_ternary),[PCFIELD 2]) = (porigin_false)
$origin_node(S_capture.SOURCES,porigin_condition) = (expression_condition)
$origin_node(S_capture.SOURCES,porigin_true) = (expression_true)
$origin_node(S_capture.SOURCES,porigin_false) = (expression_false)
porigin_ternary = PORIGIN n_unit pcpath_ternary
$code_expression(pcode.EXPRESSIONS,pcpath_ternary) = ((z_ternary,false))
$(z_ternary > 0)
$compiled_read(S_capture,porigin_ternary) = eps
$compiled_read(S_capture,porigin_condition) = eps
$compiled_read(S_capture,porigin_{selected}) = eps
$compiled_precision(S_capture,(porigin_ternary)) = (14)
$compiled_precision(S_capture,(porigin_condition)) = (14)
$compiled_precision(S_capture,(porigin_{selected})) = (14)
$string_read_runtime_value(S_capture,porigin_condition) = (PFLOAT {condition_bits})
$truth_value(S_capture,PFLOAT {condition_bits},z_ternary) = S_capture[.RESULT = KNOWN (PBOOL {str(reference).lower()})]
$string_read_runtime_value(S_capture,porigin_{selected}) = (PFLOAT {bits})
$string_read_runtime_value(S_capture,porigin_{skipped}) = eps
$string_read_runtime_value(S_capture,porigin_ternary) = (PFLOAT {bits})
''')


def front(program, filename_b64, reference=False):
    prefix, checks = minus.front(program, filename_b64, reference=reference)
    return prefix, ternary_tree('\n'.join(checks), reference).splitlines() + ternary_checks(reference)


def render(program, filename_b64, reference=False):
    body, count, derived = minus.render(program, filename_b64, reference=reference)
    body = ternary_tree(body, reference)
    before_pool = '~$string_read_allocated_value(S_number_pool,porigin_base,pvalue_base)'
    assert body.count(before_pool) == 1
    body = body.replace(before_pool, before_pool[1:])
    before_fold = '''S_unary_fold = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_number z_unary false) :: pcode.EXPRESSIONS]]]
  -- if $string_read_allocated_value(S_unary_fold,porigin_base,pvalue_base)
  -- if $string_read_plan(S_unary_fold) = (pstringread)'''
    assert body.count(before_fold) == 1
    body = body.replace(before_fold, before_fold.replace('z_unary false', 'z_unary true').replace(
        '  -- if $string_read_allocated_value', '  -- if ~$string_read_allocated_value').replace('= (pstringread)', '= eps'))
    checks = ternary_checks(reference) + lines(r'''
$string_read_raw_float_sign_tree(expression_right_number)
$string_read_raw_float_sign_tree(NExprTernary expression_right_number expression_right_number expression_right_number eps)
$string_read_raw_float_sign_tree(NExprBinaryOpCoalesce expression_right_number expression_right_number eps)
$string_read_raw_float_sign_tree(NExprTernary expression_right_number ABSENT expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprTernary (NScalarInt (INTEGER 1) eps) expression_right_number expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprTernary expression_right_number (NScalarInt (INTEGER 1) eps) expression_right_number eps)
~$string_read_raw_float_sign_tree(NExprTernary expression_right_number expression_right_number (NScalarString (BYTES "MQ==") eps) eps)
porigin_condition = PORIGIN n_unit pcpath_condition
porigin_true = PORIGIN n_unit pcpath_true
porigin_false = PORIGIN n_unit pcpath_false
''')
    selected, skipped = ('true', 'false') if reference else ('false', 'true')
    checks += lines(f'''
expression_{skipped} = NExprCastDouble expression_skipped_div metadata_skipped_cast
$origin_child((porigin_{skipped}),[PCFIELD 0]) = (porigin_skipped_div)
$origin_node(S_capture.SOURCES,porigin_skipped_div) = (expression_skipped_div)
porigin_skipped_div = PORIGIN n_unit pcpath_skipped_div
$string_read_runtime_value(S_capture,porigin_skipped_div) = eps
S_skipped_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{skipped} 17) :: (PCCPRECISION pcpath_skipped_div 17) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_skipped_precision,porigin_ternary) = $string_read_runtime_value(S_capture,porigin_ternary)
$string_read_allocated_value(S_skipped_precision,porigin_base,pvalue_base)
$string_read_plan(S_skipped_precision) = (pstringread)
S_skipped_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{skipped} 0 true) :: (CODEEXPR pcpath_skipped_div 0 true) :: pcode.EXPRESSIONS]]]
$string_read_allocated_value(S_skipped_code,porigin_base,pvalue_base)
$string_read_plan(S_skipped_code) = (pstringread)
S_skipped_deep_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_skipped_div (NScalarFloat (FLOAT "0000000000000000") eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_skipped_deep_source,porigin_ternary) = $string_read_runtime_value(S_capture,porigin_ternary)
~$string_read_allocated_value(S_skipped_deep_source,porigin_base,pvalue_base)
$string_read_plan(S_skipped_deep_source) = eps
''')
    for node in ('ternary', 'condition', selected):
        checks += [f'S_bad_{node} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_{node},porigin_ternary) = eps',
                   f'~$string_read_allocated_value(S_bad_{node},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_bad_{node}) = eps']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
