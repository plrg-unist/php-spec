"""An emitted NULL left value selects a certified string-cast RHS header."""

from string_offset_runtime_scalar_coalesce_base_initial_raw_leading_key_review import render as render_raw
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_raw(program, filename_b64)
    old = 'NExprBinaryOpCoalesce expression_cond (NScalarString (BYTES text_selected) metadata_selected)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprBinaryOpCoalesce expression_cond (NExprCastString (NScalarString (BYTES text_selected) metadata_selected) metadata_cast)')
    old = '$origin_child((porigin_base),[PCFIELD 1]) = (porigin_selected)'
    assert body.count(old) == 1
    body = body.replace(old, '$origin_child((porigin_base),[PCFIELD 1]) = (porigin_cast)\n  -- if $origin_child((porigin_cast),[PCFIELD 0]) = (porigin_selected)')
    assert body.count('pcpath_base ++ [PCFIELD 1]') >= 1
    body = body.replace('pcpath_base ++ [PCFIELD 1]', 'pcpath_base ++ [PCFIELD 1, PCFIELD 0]')
    checks = lines(r'''
porigin_cast = PORIGIN n_unit pcpath_cast
$origin_node(S_capture.SOURCES,porigin_cast) = (NExprCastString (NScalarString (BYTES text_selected) metadata_selected) metadata_cast)
$compiled_read(S_capture,porigin_cast) = eps
$compiled_precision(S_capture,(porigin_cast)) = (z_precision)
$string_read_runtime_value(S_capture,porigin_cast) = (pkeyread.BASE)
''')
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cast 0 false) :: pcode.EXPRESSIONS]]'),
            ('folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cast 12 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cast $(z_precision + 1)) :: ppool.CONSTANTS]]')):
        state = 'S_bad_coalesce_cast_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_spurious_coalesce_cast_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cast (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
$compiled_read(S_spurious_coalesce_cast_pool,porigin_cast) = eps
$string_read_runtime_value(S_spurious_coalesce_cast_pool,porigin_base) = (pkeyread.BASE)
$string_read_raw_known_base(S_spurious_coalesce_cast_pool,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + 1 + len(checks), derived + len(checks)
