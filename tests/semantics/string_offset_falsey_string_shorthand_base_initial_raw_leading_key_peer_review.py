"""Certified falsey string conditions preserve shorthand reference-key fallbacks."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_peer_review import render as render_zero
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_zero(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    condition = 'NExprBinaryOpBitwiseAnd expression_shorthand_left expression_shorthand_right metadata_cond'
    body = body.replace(old, 'NExprTernary (' + condition + ')')
    body = body.replace('porigin_left) = (PINT 0)', 'porigin_left) = (PSTRING ([48]))')
    body = body.replace('~$truth(S_capture,PINT 0)', '~$truth(S_capture,PSTRING ([48]))')
    early = lines(r'''
$string_read_raw_truth(S_capture,porigin_left,PSTRING ([48]))
$truth_value(S_capture,PSTRING ([48]),0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_shorthand_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_shorthand_right)
$compiled_read(S_capture,porigin_shorthand_left) = (PSTRING ([48]))
$compiled_read(S_capture,porigin_shorthand_right) = (PSTRING ([49]))
$string_read_raw_truth(S_capture,porigin_shorthand_left,PSTRING ([48]))
$string_read_raw_truth(S_capture,porigin_shorthand_right,PSTRING ([49]))
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PSTRING ([48]))\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ([48]))
S_budget_string_shorthand = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 7)]
$string_read_raw_truth(S_budget_string_shorthand,porigin_left,PSTRING ([48]))
$string_read_raw_known_base(S_budget_string_shorthand,porigin_base,pvalue_base)
S_wrong_condition_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left (NExprBinaryOpBitwiseAnd expression_shorthand_left expression_shorthand_right eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_wrong_condition_source,porigin_base,pvalue_base)
S_wrong_fallback_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NScalarString (BYTES text_right) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_wrong_fallback_source,porigin_base,pvalue_base)
S_condition_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_known_base(S_condition_code,porigin_base,pvalue_base)
S_fallback_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_known_base(S_fallback_code,porigin_base,pvalue_base)
''')

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'

    zero, one = string(b'0'), string(b'1')
    complement = ('BitwiseNot', 'PSTRING ([48])', string(b'\xcf'))
    binary = ('BitwiseAnd', 'PSTRING ([48])', zero, ('BitwiseOr', 'PSTRING ([49])', one, zero))
    nul = ('BitwiseXor', 'PSTRING ([0])', zero, zero)
    matrices = [
        ('source', binary, True, True), ('complement', complement, True, True),
        ('xor', ('BitwiseXor', 'PSTRING ([48])', one, string(b'\x01')), True, True),
        ('nul_child', ('BitwiseOr', 'PSTRING ([48])', nul, zero), True, True),
        ('double_complement', ('BitwiseNot', 'PSTRING ([48])', ('BitwiseNot', 'PSTRING ([207])', zero)), True, True),
        ('literal_zero', zero, True, True), ('literal_empty', string(b''), True, True),
        ('integer_zero', ('NScalarInt (INTEGER 0)', 'PINT 0'), True, True),
        ('truthy_nul', nul, True, False),
        ('truthy_one', ('BitwiseOr', 'PSTRING ([49])', one, zero), True, False),
        ('truthy_ff', ('BitwiseNot', 'PSTRING ([255])', string(b'\0')), True, False),
        ('wrong_byte', ('BitwiseAnd', 'PSTRING ([49])', zero, one), False, False),
        ('wrong_tag', ('BitwiseAnd', 'PINT 0', zero, one), False, False),
        ('carrier_tag', ('BitwiseAnd', 'PSTRING_CARRIER INTERNED_STRING ([48])', zero, one), False, False),
        ('empty_computed', ('BitwiseXor', 'PSTRING ([])', string(b''), string(b'')), False, False),
        ('multibyte', ('BitwiseAnd', 'PSTRING ([48])', zero, string(b'13')), False, False),
    ]
    for label, tree, raw_accepted, fallback_accepted in matrices:
        projected = _projection('string_shorthand_' + label, tree, raw_accepted)
        selected = ' (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right)'
        assert sum(selected in check for check in projected) == 1
        projected = [check.replace(selected, ' ABSENT (NScalarString (BYTES text_right) metadata_right)') for check in projected]
        if raw_accepted:
            assert projected[-1].startswith('$string_read_raw_known_base(')
            state = 'S_sign_string_shorthand_' + label
            projected[-1:] = [f'{"" if fallback_accepted else "~"}$string_read_raw_known_base({state},porigin_base,pvalue_base)',
                              f'~$string_read_raw_known_base({state},porigin_base,pvalue_wrong)']
            if not fallback_accepted:
                byte = tree[1].removeprefix('PSTRING (').removesuffix(')')
                projected.append(f'~$string_read_raw_known_base({state},porigin_base,PSTRING_CARRIER INTERNED_STRING ({byte}))')
        checks += projected
    checks += lines(r'''
S_budget_wrong_string_shorthand = S_sign_string_shorthand_wrong_byte[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL false)]
~$string_read_raw_truth(S_budget_wrong_string_shorthand,porigin_left,PSTRING ([49]))
~$string_read_raw_known_base(S_budget_wrong_string_shorthand,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
