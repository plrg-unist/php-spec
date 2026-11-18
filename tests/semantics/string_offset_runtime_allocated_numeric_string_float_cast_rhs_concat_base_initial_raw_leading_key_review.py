"""Raw numeric STRING casts retain exact FLOAT bits and one RHS allocation."""

import base64
import json

import string_offset_runtime_allocated_unary_minus_float_rhs_concat_base_initial_raw_leading_key_review as minus
from string_offset_retained_carrier_protocol import lines


def numeric_string_cast(text, reference):
    before = 'NExprUnaryMinus (NScalarFloat (FLOAT text_right_bits) metadata_atom) metadata_right_number'
    assert text.count(before) == 1
    text = text.replace(before, 'NExprCastDouble (NScalarString (BYTES text_number_bytes) metadata_atom) metadata_right_number')
    text = text.replace('NScalarFloat (FLOAT text_right_bits)', 'NScalarString (BYTES text_number_bytes)')
    number = ' -12.50 ' if reference else '-0.0'
    bits = 13846598529327300608 if reference else 9223372036854775808
    atom_bits = '4029000000000000' if reference else '0000000000000000'
    before = f'text_right_bits = "{atom_bits}"'
    assert text.count(before) == 1
    text = text.replace(before, 'text_number_bytes = ' + json.dumps(base64.b64encode(number.encode()).decode()))
    before = '$code_expression(pcode.EXPRESSIONS,pcpath_right_number) = ((z_unary,true))'
    assert text.count(before) == 1
    text = text.replace(before, before.replace('true', 'false'))
    before = f'$compiled_read(S_capture,porigin_right_number) = (PFLOAT {bits})'
    assert text.count(before) == 1
    return text.replace(before, '$compiled_read(S_capture,porigin_right_number) = eps')


def cast_checks(reference):
    number = ' -12.50 ' if reference else '-0.0'
    bits = 13846598529327300608 if reference else 9223372036854775808
    return lines(f'''
$compiled_read(S_capture,porigin_atom) = (PSTRING ($ptascii({json.dumps(number)})))
$string_read_runtime_value(S_capture,porigin_atom) = (PSTRING_CARRIER INTERNED_STRING ($ptascii({json.dumps(number)})))
$compiled_precision(S_capture,(porigin_atom)) = (14)
$c_string($ptascii({json.dumps(number)})) = $ptascii({json.dumps(number)})
$numeric_string($ptascii({json.dumps(number)})) = FULLNUM (NFLOAT {bits})
$cast_apply(S_capture,CASTFLOAT,PSTRING_CARRIER INTERNED_STRING ($ptascii({json.dumps(number)})),z_unary) = S_capture[.RESULT = KNOWN (PFLOAT {bits})]
$truth_value(S_capture,PFLOAT {bits},z_unary) = S_capture[.RESULT = KNOWN (PBOOL {str(reference).lower()})]
''')


def front(program, filename_b64, reference=False):
    prefix, checks = minus.front(program, filename_b64, reference=reference)
    return prefix, numeric_string_cast('\n'.join(checks), reference).splitlines() + cast_checks(reference)


def render(program, filename_b64, reference=False):
    body, count, derived = minus.render(program, filename_b64, reference=reference)
    body = numeric_string_cast(body, reference)
    before_pool = '~$string_read_allocated_value(S_number_pool,porigin_base,pvalue_base)'
    assert body.count(before_pool) == 1
    body = body.replace(before_pool, before_pool[1:])
    before_atom = '''$string_read_allocated_value(S_atom_pool,porigin_base,pvalue_base)
  -- if $string_read_plan(S_atom_pool) = (pstringread)'''
    assert body.count(before_atom) == 1
    body = body.replace(before_atom, before_atom.replace('$string_read_allocated_value', '~$string_read_allocated_value').replace('= (pstringread)', '= eps'))
    before_fold = '''S_unary_fold = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right_number z_unary false) :: pcode.EXPRESSIONS]]]
  -- if $string_read_allocated_value(S_unary_fold,porigin_base,pvalue_base)
  -- if $string_read_plan(S_unary_fold) = (pstringread)'''
    assert body.count(before_fold) == 1
    body = body.replace(before_fold, before_fold.replace('z_unary false', 'z_unary true').replace(
        '  -- if $string_read_allocated_value', '  -- if ~$string_read_allocated_value').replace('= (pstringread)', '= eps'))
    checks = cast_checks(reference) + lines(r'''
$string_read_raw_numeric_string(NScalarString (BYTES text_number_bytes) metadata_atom)
~$string_read_raw_float_sign_tree(NScalarString (BYTES text_number_bytes) metadata_atom)
$string_read_raw_float_sign_tree(expression_right_number)
$string_read_raw_float_sign_tree(NExprUnaryPlus expression_right_number eps)
$string_read_raw_float_sign_tree(NExprBinaryOpPlus expression_right_number expression_right_number eps)
$string_read_raw_float_sign_tree(NExprTernary expression_right_number ABSENT (NExprCastDouble (NScalarString (BYTES "LTEyLjU=") eps) eps) eps)
~$string_read_raw_numeric_string(NScalarString (BYTES "") eps)
~$string_read_raw_numeric_string(NScalarString (BYTES "eA==") eps)
~$string_read_raw_numeric_string(NScalarString (BYTES "MXg=") eps)
~$string_read_raw_numeric_string(NScalarString (BYTES "MQAx") eps)
~$string_read_raw_numeric_string(NScalarInt (INTEGER 1) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarString (BYTES "eA==") eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarString (BYTES "MXg=") eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarString (BYTES "MQAx") eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarInt (INTEGER 1) eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NExprUnaryMinus (NScalarInt (INTEGER 25) eps) eps) eps)
$compiled_read(S_number_pool,porigin_right_number) = eps
$string_read_runtime_value(S_number_pool,porigin_right_number) = $string_read_runtime_value(S_capture,porigin_right_number)
$string_read_runtime_value(S_atom_pool,porigin_right_number) = eps
S_atom_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_atom 17) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_atom_precision,porigin_right_number) = eps
~$string_read_allocated_value(S_atom_precision,porigin_base,pvalue_base)
$string_read_plan(S_atom_precision) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
