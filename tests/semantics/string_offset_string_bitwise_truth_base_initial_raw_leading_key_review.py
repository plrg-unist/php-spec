"""One-byte string bitwise truth preserves exact tags, bytes and frozen keys."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpBitwiseXor expression_byte_left expression_byte_right metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_cond) = (PINT 1)', '$compiled_read(S_capture,porigin_cond) = (PSTRING ([0]))')
    body = body.replace('$truth(S_capture,PINT 1)', '$truth(S_capture,PSTRING ([0]))')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpBitwiseXor expression_byte_left expression_byte_right metadata_cond)
expression_byte_left = NScalarString (BYTES text_byte_left) metadata_byte_left
expression_byte_right = NScalarString (BYTES text_byte_right) metadata_byte_right
$base64(text_byte_left) = [48]
$base64(text_byte_right) = [48]
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_byte_left)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_byte_right)
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for child in ('left', 'right'):
        checks += lines(f'''
$origin_node(S_capture.SOURCES,porigin_byte_{child}) = (expression_byte_{child})
$compiled_read(S_capture,porigin_byte_{child}) = (PSTRING ([48]))
$string_read_raw_truth(S_capture,porigin_byte_{child},PSTRING ([48]))
porigin_byte_{child} = PORIGIN n_unit pcpath_byte_{child}
''')
    checks += lines(r'''
$binary_apply(S_capture,BITXOR,PSTRING ([48]),PSTRING ([48]),0) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([0]))]
$string_read_raw_truth(S_capture,porigin_cond,PSTRING ([0]))
S_budget_byte_binary = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_budget_byte_binary,porigin_cond,PSTRING ([0]))
$string_read_raw_known_base(S_budget_byte_binary,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own_byte', 'pcpath_cond', 'PSTRING ([48])'),
            ('own_tag', 'pcpath_cond', 'PINT 0'),
            ('own_carrier', 'pcpath_cond', 'PSTRING_CARRIER INTERNED_STRING ([0])'),
            ('left_byte', 'pcpath_byte_left', 'PSTRING ([49])'),
            ('left_tag', 'pcpath_byte_left', 'PINT 0'),
            ('right_byte', 'pcpath_byte_right', 'PSTRING ([49])'),
            ('right_tag', 'pcpath_byte_right', 'PINT 0')):
        own = value if path == 'pcpath_cond' else 'PSTRING ([0])'
        checks += [f'S_bad_byte_binary_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_byte_binary_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_byte_binary_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('root', 'pcpath_cond', 'NExprBinaryOpBitwiseXor expression_byte_left expression_byte_right eps'),
            ('left', 'pcpath_byte_left', 'NScalarString (BYTES text_byte_left) eps'),
            ('right', 'pcpath_byte_right', 'NScalarString (BYTES text_byte_right) eps')):
        checks += [f'S_bad_byte_binary_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'{"" if label == "root" else "~"}$string_read_raw_truth(S_bad_byte_binary_{label}_source,porigin_cond,PSTRING ([0]))',
                   f'~$string_read_raw_known_base(S_bad_byte_binary_{label}_source,porigin_base,pkeyread.BASE)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
