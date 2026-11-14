"""One-byte string binary truth retains source tags and frozen reference keys."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    condition = 'NExprBinaryOpBitwiseAnd expression_byte_left expression_byte_right metadata_cond'
    body = body.replace(old, 'NExprTernary (' + condition + ')')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = (PSTRING ([48]))')
    body = body.replace('~$truth(S_capture,PINT 0)', '~$truth(S_capture,PSTRING ([48]))')
    early = lines(r'''
expression_byte_left = NScalarString (BYTES text_byte_left) metadata_byte_left
expression_byte_right = NExprBinaryOpBitwiseOr expression_byte_inner_left expression_byte_inner_right metadata_byte_right
expression_byte_inner_left = NScalarString (BYTES text_byte_inner_left) metadata_byte_inner_left
expression_byte_inner_right = NScalarString (BYTES text_byte_inner_right) metadata_byte_inner_right
$base64(text_byte_left) = [48]
$base64(text_byte_inner_left) = [49]
$base64(text_byte_inner_right) = [48]
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_byte_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_byte_right)
$origin_child((porigin_byte_right),[PCFIELD 0]) = (porigin_byte_inner_left)
$origin_child((porigin_byte_right),[PCFIELD 1]) = (porigin_byte_inner_right)
''')
    for child, value in (('left', 48), ('inner_left', 49), ('inner_right', 48), ('right', 49)):
        early += [f'$origin_node(S_capture.SOURCES,porigin_byte_{child}) = (expression_byte_{child})',
                  f'$compiled_read(S_capture,porigin_byte_{child}) = (PSTRING ([{value}]))',
                  f'$string_read_raw_truth(S_capture,porigin_byte_{child},PSTRING ([{value}]))']
    early += lines(r'''
$byte_binary(BITOR,[49],[48]) = [49]
$byte_binary(BITAND,[48],[49]) = [48]
$binary_apply(S_capture,BITOR,PSTRING ([49]),PSTRING ([48]),0) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([49]))]
$binary_apply(S_capture,BITAND,PSTRING ([48]),PSTRING ([49]),0) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))]
$string_read_raw_truth(S_capture,porigin_left,PSTRING ([48]))
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PSTRING ([48]))\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    checks += [f'porigin_byte_{child} = PORIGIN n_unit pcpath_byte_{child}'
               for child in ('left', 'right', 'inner_left', 'inner_right')]
    checks += lines(r'''
S_budget_byte_binary = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_budget_byte_binary,porigin_left,PSTRING ([48]))
$string_read_raw_known_base(S_budget_byte_binary,porigin_base,pvalue_base)
''')
    checks += [f'S_shorthand_byte_binary = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary ({condition}) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]',
               '$string_read_raw_known_base(S_shorthand_byte_binary,porigin_base,pvalue_base)',
               '~$string_read_raw_known_base(S_shorthand_byte_binary,porigin_base,pvalue_wrong)']
    for label, path, value in (
            ('own_byte', 'pcpath_left', 'PSTRING ([49])'),
            ('own_int', 'pcpath_left', 'PINT 0'),
            ('own_bool', 'pcpath_left', 'PBOOL false'),
            ('own_carrier', 'pcpath_left', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            ('left_byte', 'pcpath_byte_left', 'PSTRING ([49])'),
            ('left_int', 'pcpath_byte_left', 'PINT 48'),
            ('right_byte', 'pcpath_byte_right', 'PSTRING ([48])'),
            ('right_carrier', 'pcpath_byte_right', 'PSTRING_CARRIER INTERNED_STRING ([49])'),
            ('inner_byte', 'pcpath_byte_inner_left', 'PSTRING ([48])'),
            ('inner_int', 'pcpath_byte_inner_right', 'PINT 48')):
        own = value if label.startswith('own') else 'PSTRING ([48])'
        checks += [f'S_bad_byte_binary_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_byte_binary_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_byte_binary_{label},porigin_base,pvalue_base)']
    for child, path, node in (
            ('root', 'pcpath_left', 'NExprBinaryOpBitwiseAnd expression_byte_left expression_byte_right eps'),
            ('left', 'pcpath_byte_left', 'NScalarString (BYTES text_byte_left) eps'),
            ('right', 'pcpath_byte_right', 'NExprBinaryOpBitwiseOr expression_byte_inner_left expression_byte_inner_right eps'),
            ('inner_left', 'pcpath_byte_inner_left', 'NScalarString (BYTES text_byte_inner_left) eps'),
            ('inner_right', 'pcpath_byte_inner_right', 'NScalarString (BYTES text_byte_inner_right) eps')):
        checks += [f'S_bad_byte_binary_{child}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'{"" if child == "root" else "~"}$string_read_raw_truth(S_bad_byte_binary_{child}_source,porigin_left,PSTRING ([48]))',
                   f'~$string_read_raw_known_base(S_bad_byte_binary_{child}_source,porigin_base,pvalue_base)']
        checks += [f'S_bad_byte_binary_{child}_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 false) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_truth(S_bad_byte_binary_{child}_code,porigin_left,PSTRING ([48]))',
                   f'~$string_read_raw_known_base(S_bad_byte_binary_{child}_code,porigin_base,pvalue_base)']

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'

    zero = string(b'0')
    one = string(b'1')
    nul = ('BitwiseXor', 'PSTRING ([0])', zero, zero)
    ascii_zero = ('BitwiseAnd', 'PSTRING ([48])', zero, ('BitwiseOr', 'PSTRING ([49])', one, zero))
    matrices = [
        ('source', ascii_zero, True), ('nul_truth', nul, True),
        ('and_truthy', ('BitwiseAnd', 'PSTRING ([49])', one, string(b'3')), True),
        ('or_zero', ('BitwiseOr', 'PSTRING ([48])', zero, zero), True),
        ('xor_zero', ('BitwiseXor', 'PSTRING ([48])', string(b'1'), string(b'\x01')), True),
        ('ff', ('BitwiseOr', 'PSTRING ([255])', string(b'\x80'), string(b'\x7f')), True),
        ('nul_child', ('BitwiseOr', 'PSTRING ([48])', nul, zero), True),
        ('not_child', ('BitwiseAnd', 'PSTRING ([48])', ('BitwiseNot', 'PSTRING ([48])', string(b'\xcf')), string(b'\xff')), True),
        ('not_parent', ('BitwiseNot', 'PSTRING ([255])', nul), True),
        ('boolean_parent', ('BooleanNot', 'PBOOL false', nul), True),
        ('equal_parent', ('Equal', 'PBOOL true', ascii_zero, zero), True),
        ('strict_parent', ('Identical', 'PBOOL false', ascii_zero, ('NScalarInt (INTEGER 0)', 'PINT 0')), True),
        ('spaceship_parent', ('Spaceship', 'PINT 0', ascii_zero, ('NScalarInt (INTEGER 0)', 'PINT 0')), True),
        ('short_parent', ('LogicalOr', 'PBOOL true', nul, string(b'word')), True),
        ('wrong_byte', ('BitwiseAnd', 'PSTRING ([49])', zero, one), False),
        ('integer_forgery', ('BitwiseAnd', 'PINT 0', zero, one), False),
        ('bool_forgery', ('BitwiseOr', 'PBOOL false', zero, zero), False),
        ('carrier_forgery', ('BitwiseXor', 'PSTRING_CARRIER INTERNED_STRING ([0])', zero, zero), False),
        ('empty_left', ('BitwiseAnd', 'PSTRING ([])', string(b''), one), False),
        ('empty_right', ('BitwiseOr', 'PSTRING ([49])', one, string(b'')), False),
        ('multibyte', ('BitwiseXor', 'PSTRING ([0,0])', string(b'01'), string(b'01')), False),
        ('short_left', ('BitwiseAnd', 'PSTRING ([48])', zero, string(b'13')), False),
        ('short_right', ('BitwiseOr', 'PSTRING ([49,51])', string(b'13'), zero), False),
        ('mixed_left', ('BitwiseAnd', 'PSTRING ([48])', ('NScalarInt (INTEGER 48)', 'PINT 48'), one), False),
        ('mixed_right', ('BitwiseXor', 'PSTRING ([0])', zero, ('NScalarInt (INTEGER 0)', 'PINT 0')), False),
    ]
    for label, tree, accepted in matrices:
        projected = _projection('byte_binary_' + label, tree, accepted)
        if accepted and tree[1] == 'PSTRING ([48])':
            assert projected[-1].endswith(',porigin_base,pvalue_wrong)')
            projected[-1] = projected[-1].replace(',porigin_base,pvalue_wrong)', ',porigin_base,pvalue_base)')
        checks += projected
    checks += lines(r'''
S_budget_wrong_byte_binary = S_sign_byte_binary_wrong_byte[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING ([49]))]
~$string_read_raw_truth(S_budget_wrong_byte_binary,porigin_left,PSTRING ([49]))
~$string_read_raw_known_base(S_budget_wrong_byte_binary,porigin_base,pvalue_wrong)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
