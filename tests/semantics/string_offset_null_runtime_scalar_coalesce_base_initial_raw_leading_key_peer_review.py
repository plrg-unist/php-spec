"""Literal NULL selects a certified emitted ternary and preserves the raw key."""
import re

from string_offset_runtime_scalar_coalesce_base_initial_raw_leading_key_peer_review import render as render_emitted_left


def render(program, filename_b64):
    body, count, derived = render_emitted_left(program, filename_b64)
    swaps = {'expression_left': 'expression_right', 'metadata_left': 'metadata_right',
             'metadata_right': 'metadata_left', 'text_right': 'text_left',
             'porigin_left': 'porigin_right', 'porigin_right': 'porigin_left',
             'pcpath_left': 'pcpath_right', 'pcpath_right': 'pcpath_left'}
    body = re.sub(r'\b(' + '|'.join(swaps) + r')\b', lambda m: swaps[m[0]], body)
    literal = '(NExprConstFetch (NName (BYTES text_left) metadata_left_name) metadata_left)'
    old = '(NScalarString (BYTES text_left) metadata_left)'
    assert body.count(old) == 7
    body = body.replace(old, literal)
    for expression in ['expression_right', *('expression_coalesce_' + label + '_left' for label in ('empty', 'zero', 'nul', 'int_zero', 'int_one'))]:
        old = 'NExprBinaryOpCoalesce ' + expression + ' ' + literal
        assert body.count(old) == 1
        body = body.replace(old, 'NExprBinaryOpCoalesce ' + literal + ' ' + expression)
    for old, new in (
            ('$origin_child((porigin_base),[PCFIELD 0]) = (porigin_right)', '$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)'),
            ('$origin_child((porigin_base),[PCFIELD 1]) = (porigin_left)', '$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)'),
            ('$base64(text_left) = $ptascii("XYZ")', '$ptlc($base64(text_left)) = $ptascii("null")'),
            ('pvalue_fallback = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))', 'pvalue_fallback = PNULL'),
            ('$compiled_read(S_capture,porigin_left) = (PSTRING ($ptascii("XYZ")))', '$compiled_read(S_capture,porigin_left) = (PNULL)'),
            ('$compiled_string_value(S_capture,porigin_left,PSTRING ($ptascii("XYZ"))) = pvalue_fallback', '$string_read_runtime_value(S_capture,porigin_left) = (PNULL)'),
            ('NScalarString (BYTES text_left) eps', 'NExprConstFetch (NName (BYTES text_left) metadata_left_name) eps'),
            ('$string_read_runtime_value(S_coalesce_wrong_right,porigin_base) = (pvalue_base)', '$string_read_runtime_value(S_coalesce_wrong_right,porigin_base) = eps')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    checks = []
    for label, update in (
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]'),
            ('emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: pcode.EXPRESSIONS]]')):
        state = 'S_null_left_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, value in (('false', 'PBOOL false'), ('zero', 'PINT 0')):
        state = 'S_null_left_' + label
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_base) = ({value})',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
