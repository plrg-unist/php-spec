"""A direct +false CONCAT retains nonnull falsey STRING0 and the captured key."""

from string_offset_literal_concat_runtime_scalar_coalesce_base_initial_raw_leading_key_review import render as render_string
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_string(program, filename_b64)
    replacements = (
        ('$string_read_literal_bytes(expression_left) = ($ptascii("0"))',
         '$string_read_folded_concat_bytes(expression_left) = ($ptascii("0"))'),
        ('expression_prefix = NScalarString (BYTES text_prefix) metadata_prefix',
         'expression_prefix = NExprUnaryPlus expression_keyword_false metadata_prefix\n'
         '  -- if expression_keyword_false = NExprConstFetch name_keyword_false metadata_keyword_false\n'
         '  -- if name_keyword_false = NName (BYTES text_keyword_false) metadata_name_false\n'
         '  -- if $base64(text_keyword_false) = $ptascii("false")'),
        ('$base64(text_prefix) = eps',
         '$string_read_folded_concat_bytes(expression_prefix) = ($ptascii("0"))'),
        ('$base64(text_suffix) = $ptascii("0")', '$base64(text_suffix) = eps'),
        ('NScalarString (BYTES text_prefix) eps)) :: pcunit.OCCURRENCES',
         'NExprUnaryPlus expression_keyword_false eps)) :: pcunit.OCCURRENCES'),
        ('PCOCCURRENCE pcpath_prefix expression_prefix,PCOCCURRENCE pcpath_suffix expression_suffix]',
         'PCOCCURRENCE pcpath_prefix expression_prefix,PCOCCURRENCE pcpath_keyword_false expression_keyword_false,PCOCCURRENCE pcpath_name_false name_keyword_false,PCOCCURRENCE pcpath_suffix expression_suffix]'),
        ('$compiled_read(S_capture,porigin_prefix) = eps',
         '$compiled_read(S_capture,porigin_prefix) = (PINT 0)'),
        ('$compiled_read(S_capture,porigin_suffix) = eps',
         '$compiled_read(S_capture,porigin_suffix) = (PSTRING eps)'),
        ('$code_expression(pcode.EXPRESSIONS,pcpath_prefix) = eps',
         '$code_expression(pcode.EXPRESSIONS,pcpath_prefix) = ((z_unary_prefix,true))'),
        ('$code_expression(pcode.EXPRESSIONS,pcpath_suffix) = eps',
         '$code_expression(pcode.EXPRESSIONS,pcpath_suffix) = ((z_empty_suffix,true))'),
        ('$constant_at(ppool.CONSTANTS,pcpath_prefix) = eps',
         '$constant_at(ppool.CONSTANTS,pcpath_prefix) = (PINT 0)'),
        ('$constant_at(ppool.CONSTANTS,pcpath_suffix) = eps',
         '$constant_at(ppool.CONSTANTS,pcpath_suffix) = (PSTRING eps)'),
        ('$string_read_runtime_value(S_capture,porigin_prefix) = eps',
         '$string_read_runtime_value(S_capture,porigin_prefix) = (PINT 0)'),
        ('$string_read_runtime_value(S_capture,porigin_suffix) = eps',
         '$string_read_runtime_value(S_capture,porigin_suffix) = (PSTRING_CARRIER INTERNED_STRING eps)'),
        ('$string_read_runtime_value(S_pruned_literal_concat,porigin_left) = (pkeyread.BASE)',
         '$string_read_runtime_value(S_pruned_literal_concat,porigin_left) = eps'),
        ('$string_read_runtime_value(S_pruned_literal_concat,porigin_base) = (pkeyread.BASE)',
         '$string_read_runtime_value(S_pruned_literal_concat,porigin_base) = eps'),
        ('$string_read_raw_known_base(S_pruned_literal_concat,porigin_base,pkeyread.BASE)',
         '~$string_read_raw_known_base(S_pruned_literal_concat,porigin_base,pkeyread.BASE)'),
    )
    added = 0
    for old, new in replacements:
        assert body.count(old) == 1, old
        body = body.replace(old, new)
        added += new.count('\n') - old.count('\n')
    assert 'text_prefix' not in body
    checks = lines(r'''
$string_read_literal_bytes(expression_left) = eps
$origin_child((porigin_prefix),[PCFIELD 0]) = (porigin_keyword_false)
$origin_child((porigin_keyword_false),[PCFIELD 0]) = (porigin_name_false)
porigin_keyword_false = PORIGIN n_unit pcpath_keyword_false
porigin_name_false = PORIGIN n_unit pcpath_name_false
$origin_node(S_capture.SOURCES,porigin_keyword_false) = (expression_keyword_false)
$origin_node(S_capture.SOURCES,porigin_name_false) = (name_keyword_false)
$compiled_read(S_capture,porigin_keyword_false) = (PBOOL false)
$compiled_identity_value(S_capture,porigin_keyword_false) = (PBOOL false)
$compiled_identity_value(S_capture,porigin_prefix) = (PINT 0)
$code_expression(pcode.EXPRESSIONS,pcpath_keyword_false) = ((z_keyword_false,true))
$(z_unary_prefix > 0 /\ z_empty_suffix > 0 /\ z_keyword_false > 0)
$constant_at(ppool.CONSTANTS,pcpath_keyword_false) = (PBOOL false)
$compiled_precision(S_capture,(porigin_keyword_false)) = (z_precision)
$constant_precision_at(ppool.CONSTANTS,pcpath_keyword_false) = eps
$compiled_read(S_capture,porigin_name_false) = eps
$code_expression(pcode.EXPRESSIONS,pcpath_name_false) = eps
$constant_at(ppool.CONSTANTS,pcpath_name_false) = eps
$constant_precision_at(ppool.CONSTANTS,pcpath_name_false) = eps
$compiled_precision(S_capture,(porigin_name_false)) = (z_precision)
$compiled_read(S_pruned_literal_concat,porigin_left) = (PSTRING ($ptascii("0")))
$compiled_string_value(S_pruned_literal_concat,porigin_left,PSTRING ($ptascii("0"))) = PSTRING ($ptascii("0"))
$string_read_folded_concat_bytes(NExprUnaryPlus (NExprConstFetch (NName (BYTES "dHJ1ZQ==") eps) eps) eps) = ($ptascii("1"))
$string_read_folded_concat_bytes(NExprUnaryPlus (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) eps) = ($ptascii("0"))
S_unary_keyword_name_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_name_false (NName (BYTES text_keyword_false) eps)) :: pcunit.OCCURRENCES]]]
$compiled_read(S_unary_keyword_name_shadow,porigin_left) = (PSTRING ($ptascii("0")))
$compiled_string_value(S_unary_keyword_name_shadow,porigin_left,PSTRING ($ptascii("0"))) = pkeyread.BASE
$string_read_runtime_value(S_unary_keyword_name_shadow,porigin_left) = eps
~$string_read_raw_known_base(S_unary_keyword_name_shadow,porigin_base,pkeyread.BASE)
''')
    for constructor, sign in (('NExprUnaryPlus', ''), ('NExprUnaryMinus', '-')):
        for encoded, value in (('VFJVRQ==', sign + '1'), ('RkFMU0U=', '0'), ('TlVMTA==', '0')):
            checks.append(f'$string_read_folded_concat_bytes({constructor} (NExprConstFetch (NName (BYTES "{encoded}") eps) eps) eps) = ($ptascii("{value}"))')
        for name in ('NNameFullyQualified', 'NNameRelative'):
            checks.append(f'$string_read_folded_concat_bytes({constructor} (NExprConstFetch ({name} (BYTES "dHJ1ZQ==") eps) eps) eps) = eps')
        checks.append(f'$string_read_folded_concat_bytes({constructor} (NExprConstFetch (NName (BYTES "Zm9v") eps) eps) eps) = eps')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + added + len(checks), derived + added + len(checks)
