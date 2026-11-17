"""An emitted NULL left value selects the exact raw coalesce fallback header."""

from string_offset_runtime_null_shorthand_base_initial_raw_leading_key_review import render as render_null
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_null(program, filename_b64)
    old = 'NExprTernary expression_cond ABSENT (NScalarString (BYTES text_selected) metadata_selected)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprBinaryOpCoalesce expression_cond (NScalarString (BYTES text_selected) metadata_selected)')
    removed = [line for line in body.splitlines(keepends=True) if 'porigin_absent' in line]
    assert len(removed) == 3
    body = ''.join(line for line in body.splitlines(keepends=True) if 'porigin_absent' not in line)
    old = '$origin_child((porigin_base),[PCFIELD 2]) = (porigin_selected)'
    assert body.count(old) == 1
    body = body.replace(old, '$origin_child((porigin_base),[PCFIELD 1]) = (porigin_selected)')
    assert body.count('pcpath_base ++ [PCFIELD 2]') >= 1
    body = body.replace('pcpath_base ++ [PCFIELD 2]', 'pcpath_base ++ [PCFIELD 1]')
    early = lines(r'''
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)
''')
    anchor = '  -- if $string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = []
    for label, update in (
            ('line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 12 true) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base $(z_precision + 1)) :: ppool.CONSTANTS]]')):
        state = 'S_bad_coalesce_root_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    for label, value in (('false', 'PBOOL false'), ('zero', 'PINT 0')):
        state = 'S_nonnull_coalesce_' + label
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = ({value})',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count - len(removed) + len(early) + len(checks), derived + len(checks)
