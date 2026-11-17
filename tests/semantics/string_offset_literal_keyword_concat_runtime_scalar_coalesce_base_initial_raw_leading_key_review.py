"""Reserved false/null CONCAT produces a nonnull falsey STRING coalesce base."""

from string_offset_literal_concat_runtime_scalar_coalesce_base_initial_raw_leading_key_review import render as render_string
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_string(program, filename_b64)
    replacements = (
        ('$string_read_literal_bytes(expression_left) = ($ptascii("0"))',
         '$string_read_folded_concat_bytes(expression_left) = ($ptascii("0"))'),
        ('expression_prefix = NScalarString (BYTES text_prefix) metadata_prefix',
         'expression_prefix = NExprBinaryOpConcat expression_keyword_false expression_keyword_null metadata_prefix\n'
         '  -- if expression_keyword_false = NExprConstFetch name_keyword_false metadata_keyword_false\n'
         '  -- if name_keyword_false = NName (BYTES text_keyword_false) metadata_name_false\n'
         '  -- if expression_keyword_null = NExprConstFetch name_keyword_null metadata_keyword_null\n'
         '  -- if name_keyword_null = NName (BYTES text_keyword_null) metadata_name_null\n'
         '  -- if $base64(text_keyword_false) = $ptascii("false")\n'
         '  -- if $base64(text_keyword_null) = $ptascii("null")'),
        ('$base64(text_prefix) = eps',
         '$string_read_folded_concat_bytes(expression_prefix) = (eps)'),
        ('NScalarString (BYTES text_prefix) eps)) :: pcunit.OCCURRENCES',
         'NExprBinaryOpConcat expression_keyword_false expression_keyword_null eps)) :: pcunit.OCCURRENCES'),
        ('PCOCCURRENCE pcpath_prefix expression_prefix,PCOCCURRENCE pcpath_suffix expression_suffix]',
         'PCOCCURRENCE pcpath_prefix expression_prefix,PCOCCURRENCE pcpath_keyword_false expression_keyword_false,PCOCCURRENCE pcpath_name_false name_keyword_false,PCOCCURRENCE pcpath_keyword_null expression_keyword_null,PCOCCURRENCE pcpath_name_null name_keyword_null,PCOCCURRENCE pcpath_suffix expression_suffix]'),
        ('$compiled_read(S_capture,porigin_prefix) = eps',
         '$compiled_read(S_capture,porigin_prefix) = (PSTRING eps)'),
        ('$compiled_read(S_capture,porigin_suffix) = eps',
         '$compiled_read(S_capture,porigin_suffix) = (PSTRING ($ptascii("0")))'),
        ('$code_expression(pcode.EXPRESSIONS,pcpath_prefix) = eps',
         '$code_expression(pcode.EXPRESSIONS,pcpath_prefix) = ((z_keyword_prefix,true))'),
        ('$code_expression(pcode.EXPRESSIONS,pcpath_suffix) = eps',
         '$code_expression(pcode.EXPRESSIONS,pcpath_suffix) = ((z_keyword_suffix,true))'),
        ('$constant_at(ppool.CONSTANTS,pcpath_prefix) = eps',
         '$constant_at(ppool.CONSTANTS,pcpath_prefix) = (PSTRING eps)'),
        ('$constant_at(ppool.CONSTANTS,pcpath_suffix) = eps',
         '$constant_at(ppool.CONSTANTS,pcpath_suffix) = (PSTRING ($ptascii("0")))'),
        ('$string_read_runtime_value(S_capture,porigin_prefix) = eps',
         '$string_read_runtime_value(S_capture,porigin_prefix) = (PSTRING_CARRIER INTERNED_STRING eps)'),
        ('$string_read_runtime_value(S_capture,porigin_suffix) = eps',
         '$string_read_runtime_value(S_capture,porigin_suffix) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))'),
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
$origin_child((porigin_prefix),[PCFIELD 1]) = (porigin_keyword_null)
$origin_child((porigin_keyword_false),[PCFIELD 0]) = (porigin_name_false)
$origin_child((porigin_keyword_null),[PCFIELD 0]) = (porigin_name_null)
porigin_keyword_false = PORIGIN n_unit pcpath_keyword_false
porigin_keyword_null = PORIGIN n_unit pcpath_keyword_null
porigin_name_false = PORIGIN n_unit pcpath_name_false
porigin_name_null = PORIGIN n_unit pcpath_name_null
$origin_node(S_capture.SOURCES,porigin_keyword_false) = (expression_keyword_false)
$origin_node(S_capture.SOURCES,porigin_keyword_null) = (expression_keyword_null)
$origin_node(S_capture.SOURCES,porigin_name_false) = (name_keyword_false)
$origin_node(S_capture.SOURCES,porigin_name_null) = (name_keyword_null)
$compiled_read(S_capture,porigin_keyword_false) = (PBOOL false)
$compiled_read(S_capture,porigin_keyword_null) = (PNULL)
$compiled_identity_value(S_capture,porigin_keyword_false) = (PBOOL false)
$compiled_identity_value(S_capture,porigin_keyword_null) = (PNULL)
$code_expression(pcode.EXPRESSIONS,pcpath_keyword_false) = ((z_keyword_false,true))
$code_expression(pcode.EXPRESSIONS,pcpath_keyword_null) = ((z_keyword_null,true))
$(z_keyword_prefix > 0 /\ z_keyword_suffix > 0 /\ z_keyword_false > 0 /\ z_keyword_null > 0)
$constant_at(ppool.CONSTANTS,pcpath_keyword_false) = (PBOOL false)
$constant_at(ppool.CONSTANTS,pcpath_keyword_null) = (PNULL)
$compiled_precision(S_capture,(porigin_keyword_false)) = (z_precision)
$compiled_precision(S_capture,(porigin_keyword_null)) = (z_precision)
$constant_precision_at(ppool.CONSTANTS,pcpath_keyword_false) = eps
$constant_precision_at(ppool.CONSTANTS,pcpath_keyword_null) = eps
$compiled_read(S_pruned_literal_concat,porigin_left) = (PSTRING ($ptascii("0")))
$compiled_string_value(S_pruned_literal_concat,porigin_left,PSTRING ($ptascii("0"))) = PSTRING ($ptascii("0"))
$string_read_folded_concat_bytes(NExprConstFetch (NName (BYTES "VFJVRQ==") eps) eps) = ($ptascii("1"))
$string_read_folded_concat_bytes(NExprConstFetch (NName (BYTES "RkFMU0U=") eps) eps) = (eps)
$string_read_folded_concat_bytes(NExprConstFetch (NName (BYTES "TlVMTA==") eps) eps) = (eps)
$string_read_folded_concat_bytes(NExprConstFetch (NName (BYTES "Zm9v") eps) eps) = eps
$string_read_folded_concat_bytes(NExprConstFetch (NNameFullyQualified (BYTES "dHJ1ZQ==") eps) eps) = ($ptascii("1"))
$string_read_folded_concat_bytes(NExprConstFetch (NNameRelative (BYTES "dHJ1ZQ==") eps) eps) = eps
''')
    for label in ('false', 'null'):
        checks += [f'$compiled_read(S_capture,porigin_name_{label}) = eps',
                   f'$code_expression(pcode.EXPRESSIONS,pcpath_name_{label}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_name_{label}) = eps',
                   f'$constant_precision_at(ppool.CONSTANTS,pcpath_name_{label}) = eps',
                   f'$compiled_precision(S_capture,(porigin_name_{label})) = (z_precision)',
                   f'S_keyword_name_shadow_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_name_{label} (NName (BYTES text_keyword_{label}) eps)) :: pcunit.OCCURRENCES]]]',
                   f'$compiled_read(S_keyword_name_shadow_{label},porigin_left) = (PSTRING ($ptascii("0")))',
                   f'$compiled_string_value(S_keyword_name_shadow_{label},porigin_left,PSTRING ($ptascii("0"))) = pkeyread.BASE',
                   f'$string_read_runtime_value(S_keyword_name_shadow_{label},porigin_left) = eps',
                   f'~$string_read_raw_known_base(S_keyword_name_shadow_{label},porigin_base,pkeyread.BASE)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + added + len(checks), derived + added + len(checks)
