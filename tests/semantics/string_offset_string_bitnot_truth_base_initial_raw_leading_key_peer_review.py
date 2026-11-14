"""One-byte string complements preserve frozen reference-key selection."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    condition = 'NExprBitwiseNot expression_string_not metadata_cond'
    body = body.replace(old, 'NExprTernary (' + condition + ')')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = (PSTRING ([48]))')
    body = body.replace('~$truth(S_capture,PINT 0)', '~$truth(S_capture,PSTRING ([48]))')
    early = lines(r'''
expression_string_not = NScalarString (BYTES text_string_not) metadata_string_not
$base64(text_string_not) = [207]
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_string_not)
$origin_node(S_capture.SOURCES,porigin_string_not) = (expression_string_not)
$compiled_read(S_capture,porigin_string_not) = (PSTRING ([207]))
$string_read_raw_truth(S_capture,porigin_string_not,PSTRING ([207]))
$string_not([207]) = [48]
$bitnot_value(S_capture,PSTRING ([207]),0) = S_capture[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([48]))]
$string_read_raw_truth(S_capture,porigin_left,PSTRING ([48]))
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PSTRING ([48]))\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_string_not = PORIGIN n_unit pcpath_string_not
S_budget_string_not = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING ([0]))]
$string_read_raw_truth(S_budget_string_not,porigin_left,PSTRING ([48]))
$string_read_raw_known_base(S_budget_string_not,porigin_base,pvalue_base)
''')
    checks += [f'S_shorthand_string_not = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary ({condition}) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]',
               '~$string_read_raw_known_base(S_shorthand_string_not,porigin_base,pvalue_base)',
               '~$string_read_raw_known_base(S_shorthand_string_not,porigin_base,pvalue_wrong)']
    for label, path, value in (
            ('own_byte', 'pcpath_left', 'PSTRING ([49])'), ('own_int', 'pcpath_left', 'PINT 0'),
            ('own_bool', 'pcpath_left', 'PBOOL false'),
            ('own_carrier', 'pcpath_left', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
            ('child_byte', 'pcpath_string_not', 'PSTRING ([206])'),
            ('child_int', 'pcpath_string_not', 'PINT 207'),
            ('child_carrier', 'pcpath_string_not', 'PSTRING_CARRIER INTERNED_STRING ([207])')):
        own = value if label.startswith('own') else 'PSTRING ([48])'
        checks += [f'S_bad_string_not_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_string_not_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_string_not_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('root', 'pcpath_left', 'NExprBitwiseNot expression_string_not eps'),
            ('child', 'pcpath_string_not', 'NScalarString (BYTES text_string_not) eps')):
        checks += [f'S_bad_string_not_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'{"" if label == "root" else "~"}$string_read_raw_truth(S_bad_string_not_{label}_source,porigin_left,PSTRING ([48]))',
                   f'~$string_read_raw_known_base(S_bad_string_not_{label}_source,porigin_base,pvalue_base)']
    for label, path in (('root', 'pcpath_left'), ('child', 'pcpath_string_not')):
        checks += [f'S_bad_string_not_{label}_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 false) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_truth(S_bad_string_not_{label}_code,porigin_left,PSTRING ([48]))',
                   f'~$string_read_raw_known_base(S_bad_string_not_{label}_code,porigin_base,pvalue_base)']

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        return f'NScalarInt (INTEGER {i})', f'PINT {i}'
    false = ('BitwiseNot', 'PSTRING ([48])', string(b'\xcf'))
    true = ('BitwiseNot', 'PSTRING ([49])', string(b'\xce'))
    matrices = [
        ('source', false, True), ('truthy', true, True),
        ('nul_result', ('BitwiseNot', 'PSTRING ([0])', string(b'\xff')), True),
        ('ff_result', ('BitwiseNot', 'PSTRING ([255])', string(b'\0')), True),
        ('double_complement', ('BitwiseNot', 'PSTRING ([207])', false), True),
        ('not_zero_string', ('BooleanNot', 'PBOOL true', false), True),
        ('not_one_string', ('BooleanNot', 'PBOOL false', true), True),
        ('equal_parent', ('Equal', 'PBOOL true', false, string(b'0')), True),
        ('strict_parent', ('Identical', 'PBOOL false', false, integer(0)), True),
        ('spaceship_parent', ('Spaceship', 'PINT 0', false, integer(0)), True),
        ('arithmetic_parent', ('Plus', 'PINT 2', true, integer(1)), True),
        ('short_parent', ('LogicalOr', 'PBOOL true', false, string(b'word')), True),
        ('wrong_byte', ('BitwiseNot', 'PSTRING ([49])', string(b'\xcf')), False),
        ('integer_forgery', ('BitwiseNot', 'PINT 0', string(b'\xcf')), False),
        ('bool_forgery', ('BitwiseNot', 'PBOOL false', string(b'\xcf')), False),
        ('carrier_forgery', ('BitwiseNot', 'PSTRING_CARRIER INTERNED_STRING ([48])', string(b'\xcf')), False),
        ('empty_string', ('BitwiseNot', 'PSTRING ([])', string(b'')), False),
        ('multibyte_string', ('BitwiseNot', 'PSTRING ([48,47])', string(b'\xcf\xd0')), False),
        ('multibyte_forgery', ('BitwiseNot', 'PSTRING ([48])', string(b'\xcf\xd0')), False),
        ('child_forgery', ('BitwiseNot', 'PSTRING ([48])', ('NScalarString (BYTES "zw==")', 'PINT 207')), False),
    ]
    for label, tree, accepted in matrices:
        projected = _projection('string_not_' + label, tree, accepted)
        if accepted and tree[1] == 'PSTRING ([48])':
            assert projected[-1].endswith(',porigin_base,pvalue_wrong)')
            projected[-1] = projected[-1].replace(',porigin_base,pvalue_wrong)', ',porigin_base,pvalue_base)')
        checks += projected
    checks += lines(r'''
S_budget_wrong_string_not = S_sign_string_not_wrong_byte[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING ([49]))]
~$string_read_raw_truth(S_budget_wrong_string_not,porigin_left,PSTRING ([49]))
~$string_read_raw_known_base(S_budget_wrong_string_not,porigin_base,pvalue_wrong)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
