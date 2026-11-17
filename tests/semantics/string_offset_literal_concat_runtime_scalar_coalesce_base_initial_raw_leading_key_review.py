"""A folded raw-STRING CONCAT retains its falsey header and raw CV offset."""

from string_offset_literal_string_runtime_scalar_coalesce_base_initial_raw_leading_key_review import render as render_raw
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_raw(program, filename_b64)
    for old, new in (
            ('expression_left = NScalarString (BYTES text_left) metadata_left',
             'expression_left = NExprBinaryOpConcat expression_prefix expression_suffix metadata_left'),
            ('$base64(text_left) = $ptascii("0")',
             '$string_read_literal_bytes(expression_left) = ($ptascii("0"))'),
            ('NScalarString (BYTES text_left) eps',
             'NExprBinaryOpConcat expression_prefix expression_suffix eps')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    checks = lines(r'''
expression_prefix = NScalarString (BYTES text_prefix) metadata_prefix
expression_suffix = NScalarString (BYTES text_suffix) metadata_suffix
$base64(text_prefix) = eps
$base64(text_suffix) = $ptascii("0")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_prefix)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_suffix)
$origin_node(S_capture.SOURCES,porigin_prefix) = (expression_prefix)
$origin_node(S_capture.SOURCES,porigin_suffix) = (expression_suffix)
porigin_prefix = PORIGIN n_unit pcpath_prefix
porigin_suffix = PORIGIN n_unit pcpath_suffix
$pcwalk([PCOCCURRENCE pcpath_left expression_left]) = [PCOCCURRENCE pcpath_left expression_left,PCOCCURRENCE pcpath_prefix expression_prefix,PCOCCURRENCE pcpath_suffix expression_suffix]
$compiled_read(S_capture,porigin_prefix) = eps
$compiled_read(S_capture,porigin_suffix) = eps
$code_expression(pcode.EXPRESSIONS,pcpath_prefix) = eps
$code_expression(pcode.EXPRESSIONS,pcpath_suffix) = eps
$constant_at(ppool.CONSTANTS,pcpath_prefix) = eps
$constant_at(ppool.CONSTANTS,pcpath_suffix) = eps
$constant_precision_at(ppool.CONSTANTS,pcpath_prefix) = eps
$constant_precision_at(ppool.CONSTANTS,pcpath_suffix) = eps
$compiled_precision(S_capture,(porigin_prefix)) = (z_precision)
$compiled_precision(S_capture,(porigin_suffix)) = (z_precision)
$compiled_identity_value(S_capture,porigin_left) = (PSTRING ($ptascii("0")))
$string_read_runtime_value(S_capture,porigin_prefix) = eps
$string_read_runtime_value(S_capture,porigin_suffix) = eps
''')
    for label, update in (
            ('prefix_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_prefix (NScalarString (BYTES text_prefix) eps)) :: pcunit.OCCURRENCES]]'),
            ('suffix_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_suffix (NScalarString (BYTES text_suffix) eps)) :: pcunit.OCCURRENCES]]'),
            ('left_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 0 true) :: pcode.EXPRESSIONS]]')):
        state = 'S_bad_literal_concat_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_left) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_pruned_literal_concat = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_prefix 17) :: (PCCPRECISION pcpath_suffix 18) :: (PCONSTANT pcpath_prefix (PINT 9223372036854775808)) :: (PCONSTANT pcpath_suffix (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_prefix 0 false) :: (CODEEXPR pcpath_suffix 0 false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_pruned_literal_concat,porigin_prefix) = eps
$compiled_read(S_pruned_literal_concat,porigin_suffix) = eps
$string_read_runtime_value(S_pruned_literal_concat,porigin_left) = (pkeyread.BASE)
$string_read_runtime_value(S_pruned_literal_concat,porigin_base) = (pkeyread.BASE)
$string_read_raw_known_base(S_pruned_literal_concat,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
