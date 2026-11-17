"""Folded direct integer negation retains its falsey INTERNED coalesce base."""

from string_offset_literal_integer_concat_runtime_scalar_coalesce_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    replacements = (
        ('expression_suffix = NScalarInt (INTEGER 0) metadata_suffix',
         'expression_suffix = NExprUnaryMinus expression_sign_atom metadata_suffix\n'
         '  -- if expression_sign_atom = NScalarInt (INTEGER 0) metadata_sign_atom'),
        ('NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES',
         'NExprUnaryMinus expression_sign_atom eps)) :: pcunit.OCCURRENCES'),
        ('$string_read_folded_concat_bytes(NExprUnaryMinus expression_suffix eps) = ($ptascii("0"))',
         '$string_read_folded_concat_bytes(NExprUnaryMinus expression_suffix eps) = eps'),
        ('PCOCCURRENCE pcpath_suffix expression_suffix]',
         'PCOCCURRENCE pcpath_suffix expression_suffix,PCOCCURRENCE pcpath_sign_atom expression_sign_atom]'),
        ('$compiled_read(S_capture,porigin_prefix) = eps',
         '$compiled_read(S_capture,porigin_prefix) = (PSTRING eps)'),
        ('$compiled_read(S_capture,porigin_suffix) = eps',
         '$compiled_read(S_capture,porigin_suffix) = (PINT 0)'),
        ('$code_expression(pcode.EXPRESSIONS,pcpath_prefix) = eps',
         '$code_expression(pcode.EXPRESSIONS,pcpath_prefix) = ((z_sign_prefix,true))'),
        ('$code_expression(pcode.EXPRESSIONS,pcpath_suffix) = eps',
         '$code_expression(pcode.EXPRESSIONS,pcpath_suffix) = ((z_sign_suffix,true))'),
        ('$constant_at(ppool.CONSTANTS,pcpath_prefix) = eps',
         '$constant_at(ppool.CONSTANTS,pcpath_prefix) = (PSTRING eps)'),
        ('$constant_at(ppool.CONSTANTS,pcpath_suffix) = eps',
         '$constant_at(ppool.CONSTANTS,pcpath_suffix) = (PINT 0)'),
        ('$string_read_runtime_value(S_capture,porigin_prefix) = eps',
         '$string_read_runtime_value(S_capture,porigin_prefix) = (PSTRING_CARRIER INTERNED_STRING eps)'),
        ('$string_read_runtime_value(S_capture,porigin_suffix) = eps',
         '$string_read_runtime_value(S_capture,porigin_suffix) = (PINT 0)'),
        ('$string_read_runtime_value(S_pruned_literal_concat,porigin_left) = (pkeyread.BASE)',
         '$string_read_runtime_value(S_pruned_literal_concat,porigin_left) = eps'),
        ('$string_read_runtime_value(S_pruned_literal_concat,porigin_base) = (pkeyread.BASE)',
         '$string_read_runtime_value(S_pruned_literal_concat,porigin_base) = eps'),
        ('$string_read_raw_known_base(S_pruned_literal_concat,porigin_base,pkeyread.BASE)',
         '~$string_read_raw_known_base(S_pruned_literal_concat,porigin_base,pkeyread.BASE)'),
    )
    for old, new in replacements:
        assert body.count(old) == 1, old
        body = body.replace(old, new)
    checks = lines(r'''
$origin_child((porigin_suffix),[PCFIELD 0]) = (porigin_sign_atom)
porigin_sign_atom = PORIGIN n_unit pcpath_sign_atom
$origin_node(S_capture.SOURCES,porigin_sign_atom) = (expression_sign_atom)
$compiled_read(S_capture,porigin_sign_atom) = (PINT 0)
$compiled_identity_value(S_capture,porigin_suffix) = (PINT 0)
$compiled_identity_value(S_capture,porigin_sign_atom) = (PINT 0)
$code_expression(pcode.EXPRESSIONS,pcpath_sign_atom) = ((z_sign_atom,true))
$(z_sign_prefix > 0 /\ z_sign_suffix > 0 /\ z_sign_atom > 0)
$constant_at(ppool.CONSTANTS,pcpath_sign_atom) = (PINT 0)
$constant_precision_at(ppool.CONSTANTS,pcpath_sign_atom) = eps
$compiled_precision(S_capture,(porigin_sign_atom)) = (z_precision)
$compiled_read(S_pruned_literal_concat,porigin_left) = (PSTRING ($ptascii("0")))
$compiled_string_value(S_pruned_literal_concat,porigin_left,PSTRING ($ptascii("0"))) = PSTRING ($ptascii("0"))
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarInt (INTEGER 1) eps) eps) = ($ptascii("-1"))
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarInt (INTEGER 9223372036854775807) eps) eps) = ($ptascii("-9223372036854775807"))
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarInt (INTEGER $(-9223372036854775807)) eps) eps) = ($ptascii("9223372036854775807"))
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarInt (INTEGER $(-9223372036854775808)) eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarInt (INTEGER 9223372036854775808) eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarInt (INTEGER $(-9223372036854775809)) eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarFloat (FLOAT "43e0000000000000") eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryPlus expression_sign_atom eps) = ($ptascii("0"))
$string_read_folded_concat_bytes(NExprUnaryMinus (NExprUnaryMinus expression_sign_atom eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryMinus expression_prefix eps) = eps
S_sign_atom_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_sign_atom (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]
$compiled_read(S_sign_atom_shadow,porigin_left) = (PSTRING ($ptascii("0")))
$string_read_runtime_value(S_sign_atom_shadow,porigin_left) = eps
~$string_read_raw_known_base(S_sign_atom_shadow,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks) + 1, derived + len(checks) + 1
