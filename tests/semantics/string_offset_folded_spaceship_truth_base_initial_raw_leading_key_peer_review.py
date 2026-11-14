"""Scalar spaceship orders preserve frozen reference-key selection."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    condition = 'NExprBinaryOpSpaceship expression_spaceship_float expression_spaceship_null metadata_cond'
    body = body.replace(old, 'NExprTernary (' + condition + ')')
    early = lines(r'''
expression_spaceship_float = NScalarFloat (FLOAT text_spaceship_float) metadata_spaceship_float
expression_spaceship_null = NExprConstFetch (NName (BYTES text_spaceship_null) metadata_spaceship_name) metadata_spaceship_null
text_spaceship_float = "0000000000000000"
$ptlc($base64(text_spaceship_null)) = $ptascii("null")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_spaceship_float)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_spaceship_null)
$origin_child((porigin_spaceship_null),[PCFIELD 0]) = (porigin_spaceship_name)
$origin_node(S_capture.SOURCES,porigin_spaceship_name) = (NName (BYTES text_spaceship_null) metadata_spaceship_name)
''')
    for child, value in (('float', 'PFLOAT 0'), ('null', 'PNULL')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_spaceship_{child}) = (expression_spaceship_{child})',
                  f'$compiled_read(S_capture,porigin_spaceship_{child}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_spaceship_{child},{value})']
    early += lines(r'''
$binary_apply(S_capture,SPACESHIP,PFLOAT 0,PNULL,0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_spaceship_float = PORIGIN n_unit pcpath_spaceship_float
porigin_spaceship_null = PORIGIN n_unit pcpath_spaceship_null
porigin_spaceship_name = PORIGIN n_unit pcpath_spaceship_name
S_budget_spaceship = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
$string_read_raw_truth(S_budget_spaceship,porigin_left,PINT 0)
$string_read_raw_known_base(S_budget_spaceship,porigin_base,pvalue_base)
''')
    checks += [f'S_shorthand_spaceship = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary ({condition}) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]',
               '$string_read_raw_known_base(S_shorthand_spaceship,porigin_base,pvalue_base)',
               '~$string_read_raw_known_base(S_shorthand_spaceship,porigin_base,pvalue_wrong)']
    for label, path, value in (
            ('own_order', 'pcpath_left', 'PINT 1'), ('own_tag', 'pcpath_left', 'PBOOL false'),
            ('float_bits', 'pcpath_spaceship_float', 'PFLOAT 9223372036854775808'),
            ('float_tag', 'pcpath_spaceship_float', 'PINT 0'),
            ('null_bool', 'pcpath_spaceship_null', 'PBOOL false'),
            ('null_int', 'pcpath_spaceship_null', 'PINT 0')):
        own = value if label.startswith('own') else 'PINT 0'
        checks += [f'S_bad_spaceship_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_spaceship_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_spaceship_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('root', 'pcpath_left', 'NExprBinaryOpSpaceship expression_spaceship_float expression_spaceship_null eps'),
            ('float', 'pcpath_spaceship_float', 'NScalarFloat (FLOAT text_spaceship_float) eps'),
            ('null', 'pcpath_spaceship_null', 'NExprConstFetch (NName (BYTES text_spaceship_null) metadata_spaceship_name) eps'),
            ('name', 'pcpath_spaceship_name', 'NName (BYTES text_spaceship_null) eps')):
        checks += [f'S_bad_spaceship_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'{"" if label == "root" else "~"}$string_read_raw_truth(S_bad_spaceship_{label}_source,porigin_left,PINT 0)',
                   f'~$string_read_raw_known_base(S_bad_spaceship_{label}_source,porigin_base,pvalue_base)']
    for label, path in (('root', 'pcpath_left'), ('float', 'pcpath_spaceship_float'), ('null', 'pcpath_spaceship_null')):
        checks += [f'S_bad_spaceship_{label}_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 false) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_truth(S_bad_spaceship_{label}_code,porigin_left,PINT 0)',
                   f'~$string_read_raw_known_base(S_bad_spaceship_{label}_code,porigin_base,pvalue_base)']

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        value = str(i) if i >= 0 else f'$({i})'
        return f'NScalarInt (INTEGER {value})', f'PINT {value}'
    def floating(bits):
        return f'NScalarFloat (FLOAT "{bits:016x}")', f'PFLOAT {bits}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    false, true, null = constant('false', 'PBOOL false'), constant('true', 'PBOOL true'), constant('null', 'PNULL')
    zero, negative_zero = floating(0), floating(9223372036854775808)
    negative = ('Spaceship', 'PINT $(-1)', string(b'2.0'), integer(3))
    equal = ('Spaceship', 'PINT 0', zero, null)
    matrices = [
        ('source', equal, True), ('negative', negative, True),
        ('positive', ('Spaceship', 'PINT 1', integer(3), string(b'2.0')), True),
        ('numeric_strings', ('Spaceship', 'PINT 0', string(b'2.0'), string(b'2')), True),
        ('leading_string', ('Spaceship', 'PINT 1', string(b'2x'), integer(2)), True),
        ('nonnumeric_string', ('Spaceship', 'PINT 1', string(b'word'), integer(0)), True),
        ('null_string', ('Spaceship', 'PINT $(-1)', null, string(b'0')), True),
        ('false_zero_string', ('Spaceship', 'PINT 0', false, string(b'0')), True),
        ('true_nonnumeric', ('Spaceship', 'PINT 0', true, string(b'word')), True),
        ('negative_zero_null', ('Spaceship', 'PINT 0', negative_zero, null), True),
        ('signed_zeros', ('Spaceship', 'PINT 0', negative_zero, zero), True),
        ('subnormal', ('Spaceship', 'PINT 1', floating(1), integer(0)), True),
        ('unary_parent', ('UnaryMinus', 'PINT 1', negative), True),
        ('not_parent', ('BooleanNot', 'PBOOL false', negative), True),
        ('bitnot_parent', ('BitwiseNot', 'PINT $(-1)', equal), True),
        ('arithmetic_parent', ('Plus', 'PINT 0', negative, integer(1)), True),
        ('comparison_parent', ('Identical', 'PBOOL true', equal, integer(0)), True),
        ('short_parent', ('LogicalOr', 'PBOOL true', equal, string(b'word')), True),
        ('wrong_order', ('Spaceship', 'PINT 1', zero, null), False),
        ('wrong_tag', ('Spaceship', 'PBOOL false', zero, null), False),
        ('wrong_float_tag', ('Spaceship', 'PFLOAT 0', zero, null), False),
        ('forged_child', ('Spaceship', 'PINT 0', ('NScalarFloat (FLOAT "0000000000000000")', 'PINT 0'), null), False),
        ('infinity', ('Spaceship', 'PINT 1', floating(9218868437227405312), integer(0)), False),
        ('nan', ('Spaceship', 'PINT 1', floating(9221120237041090560), integer(0)), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection('spaceship_' + label, tree, accepted)
    for label, value in (('infinity', 'PINT 1'), ('nan', 'PINT 1')):
        checks += [f'S_budget_spaceship_{label} = S_sign_spaceship_{label}[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]',
                   f'~$string_read_raw_truth(S_budget_spaceship_{label},porigin_left,{value})']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
