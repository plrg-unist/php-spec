"""Typed folded spaceship orders retain the selected base and frozen raw offset."""

import base64

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpSpaceship expression_decimal_ship expression_three_ship metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_cond) = (PINT 1)', '$compiled_read(S_capture,porigin_cond) = (PINT $(-1))')
    body = body.replace('$truth(S_capture,PINT 1)', '$truth(S_capture,PINT $(-1))')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpSpaceship expression_decimal_ship expression_three_ship metadata_cond)
expression_decimal_ship = NScalarString (BYTES text_decimal_ship) metadata_decimal_ship
expression_three_ship = NScalarInt (INTEGER 3) metadata_three_ship
$base64(text_decimal_ship) = $ptascii("2.0")
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_decimal_ship)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_three_ship)
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for name, value in (('decimal', 'PSTRING ($ptascii("2.0"))'), ('three', 'PINT 3')):
        checks += lines(f'''
$origin_node(S_capture.SOURCES,porigin_{name}_ship) = (expression_{name}_ship)
$compiled_read(S_capture,porigin_{name}_ship) = ({value})
$string_read_raw_truth(S_capture,porigin_{name}_ship,{value})
porigin_{name}_ship = PORIGIN n_unit pcpath_{name}_ship
''')
    checks += lines(r'''
$binary_apply(S_capture,SPACESHIP,PSTRING ($ptascii("2.0")),PINT 3,0) = S_capture[.RESULT = KNOWN (PINT $(-1))]
$string_read_raw_truth(S_capture,porigin_cond,PINT $(-1))
S_budget_ship = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
$string_read_raw_truth(S_budget_ship,porigin_cond,PINT $(-1))
$string_read_raw_known_base(S_budget_ship,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own_zero', 'pcpath_cond', 'PINT 0'), ('own_tag', 'pcpath_cond', 'PBOOL true'),
            ('decimal_bytes', 'pcpath_decimal_ship', 'PSTRING ($ptascii("3.0"))'),
            ('decimal_tag', 'pcpath_decimal_ship', 'PINT 2'),
            ('three_value', 'pcpath_three_ship', 'PINT 2'), ('three_tag', 'pcpath_three_ship', 'PFLOAT 4613937818241073152')):
        own = value if path == 'pcpath_cond' else 'PINT $(-1)'
        checks += [f'S_bad_ship_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_ship_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_ship_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('root', 'pcpath_cond', 'NExprBinaryOpSpaceship expression_decimal_ship expression_three_ship eps'),
            ('left', 'pcpath_decimal_ship', 'NScalarString (BYTES text_decimal_ship) eps'),
            ('right', 'pcpath_three_ship', 'NScalarInt (INTEGER 3) eps')):
        checks += [f'S_bad_ship_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'{"" if label == "root" else "~"}$string_read_raw_truth(S_bad_ship_{label}_source,porigin_cond,PINT $(-1))',
                   f'~$string_read_raw_known_base(S_bad_ship_{label}_source,porigin_base,pkeyread.BASE)']
    integer = lambda n, meta: (f'NScalarInt (INTEGER {n}) {meta}', f'PINT {n}')
    floating = lambda bits, meta: (f'NScalarFloat (FLOAT "{bits:016x}") {meta}', f'PFLOAT {bits}')
    string = lambda s, meta: (f'NScalarString (BYTES "{base64.b64encode(s.encode()).decode()}") {meta}', f'PSTRING ($ptascii("{s}"))')
    left_meta, right_meta = 'metadata_decimal_ship', 'metadata_three_ship'
    for label, left, right, result, accepted in (
            ('positive', integer(3, left_meta), string('2.0', right_meta), 1, True),
            ('equal', string('2.0', left_meta), integer(2, right_meta), 0, True),
            ('nonnumeric', string('word', left_meta), integer(2, right_meta), 1, True),
            ('leading', string('2x', left_meta), integer(2, right_meta), 1, True),
            ('signed_zero', floating(9223372036854775808, left_meta), floating(0, right_meta), 0, True),
            ('finite', floating(4602678819172646912, left_meta), integer(0, right_meta), 1, True),
            ('infinity', floating(9218868437227405312, left_meta), integer(0, right_meta), 1, False),
            ('nan', floating(9221120237041090560, left_meta), integer(0, right_meta), 1, False)):
        left_node, left_value = left
        right_node, right_value = right
        checks += lines(f'''
expression_{label}_ship_left = {left_node}
expression_{label}_ship_right = {right_node}
expression_{label}_ship = NExprBinaryOpSpaceship expression_{label}_ship_left expression_{label}_ship_right metadata_cond
expression_{label}_ship_base = NExprTernary expression_{label}_ship (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false) metadata
S_{label}_ship = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_ship_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_ship) :: (PCOCCURRENCE pcpath_decimal_ship expression_{label}_ship_left) :: (PCOCCURRENCE pcpath_three_ship expression_{label}_ship_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT {result})) :: (PCONSTANT pcpath_decimal_ship ({left_value})) :: (PCONSTANT pcpath_three_ship ({right_value})) :: ppool.CONSTANTS]]]
{'' if accepted else '~'}$string_read_raw_truth(S_{label}_ship,porigin_cond,PINT {result})
''')
        if accepted:
            selected = 'abc' if result else 'XYZ'
            checks += [f'$string_read_raw_known_base(S_{label}_ship,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("{selected}")))']
        else:
            checks += [f'~$string_read_raw_known_base(S_{label}_ship,porigin_base,{value})'
                       for value in ('pkeyread.BASE', 'pvalue_wrong')]
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
