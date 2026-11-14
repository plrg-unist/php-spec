"""Folded comparisons retain typed operands and frozen reference-key offsets."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpNotIdentical expression_compare_notequal expression_compare_greater metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = (PBOOL false)')
    body = body.replace('~$truth(S_capture,PINT 0)', '~$truth(S_capture,PBOOL false)')
    old_wrong = 'S_wrong_left = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: ppool.CONSTANTS]]]'
    assert body.count(old_wrong) == 1
    body = body.replace(old_wrong, old_wrong.replace('PBOOL false', 'PBOOL true'))
    early = lines(r'''
expression_compare_notequal = NExprBinaryOpNotEqual expression_compare_null expression_compare_false metadata_compare_notequal
expression_compare_greater = NExprBinaryOpGreater expression_compare_greaterequal expression_compare_lessequal metadata_compare_greater
expression_compare_greaterequal = NExprBinaryOpGreaterOrEqual expression_compare_two_string expression_compare_two_int metadata_compare_greaterequal
expression_compare_lessequal = NExprBinaryOpSmallerOrEqual expression_compare_one_string expression_compare_true metadata_compare_lessequal
expression_compare_null = NExprConstFetch (NName (BYTES text_compare_null) metadata_compare_null_name) metadata_compare_null
expression_compare_false = NExprConstFetch (NName (BYTES text_compare_false) metadata_compare_false_name) metadata_compare_false
expression_compare_true = NExprConstFetch (NName (BYTES text_compare_true) metadata_compare_true_name) metadata_compare_true
expression_compare_two_string = NScalarString (BYTES text_compare_two_string) metadata_compare_two_string
expression_compare_two_int = NScalarInt (INTEGER 2) metadata_compare_two_int
expression_compare_one_string = NScalarString (BYTES text_compare_one_string) metadata_compare_one_string
$ptlc($base64(text_compare_null)) = $ptascii("null")
$ptlc($base64(text_compare_false)) = $ptascii("false")
$ptlc($base64(text_compare_true)) = $ptascii("true")
$base64(text_compare_two_string) = $ptascii("2")
$base64(text_compare_one_string) = $ptascii("1")
''')
    children = (
        ('left', 0, 'notequal', 'PBOOL false'), ('left', 1, 'greater', 'PBOOL false'),
        ('compare_notequal', 0, 'null', 'PNULL'), ('compare_notequal', 1, 'false', 'PBOOL false'),
        ('compare_greater', 0, 'greaterequal', 'PBOOL true'), ('compare_greater', 1, 'lessequal', 'PBOOL true'),
        ('compare_greaterequal', 0, 'two_string', 'PSTRING ($ptascii("2"))'), ('compare_greaterequal', 1, 'two_int', 'PINT 2'),
        ('compare_lessequal', 0, 'one_string', 'PSTRING ($ptascii("1"))'), ('compare_lessequal', 1, 'true', 'PBOOL true'))
    for parent, field, child, value in children:
        early += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_compare_{child})',
                  f'$origin_node(S_capture.SOURCES,porigin_compare_{child}) = (expression_compare_{child})',
                  f'$compiled_read(S_capture,porigin_compare_{child}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_compare_{child},{value})']
    for name in ('null', 'false', 'true'):
        early += [f'$origin_child((porigin_compare_{name}),[PCFIELD 0]) = (porigin_compare_{name}_name)',
                  f'$origin_node(S_capture.SOURCES,porigin_compare_{name}_name) = (NName (BYTES text_compare_{name}) metadata_compare_{name}_name)']
    early += lines(r'''
$binary_apply(S_capture,NOTEQUAL,PNULL,PBOOL false,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$binary_apply(S_capture,GREATEREQUAL,PSTRING ($ptascii("2")),PINT 2,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$binary_apply(S_capture,LESSEQUAL,PSTRING ($ptascii("1")),PBOOL true,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$binary_apply(S_capture,GREATER,PBOOL true,PBOOL true,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$binary_apply(S_capture,NOTIDENTICAL,PBOOL false,PBOOL false,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_truth(S_capture,porigin_left,PBOOL false)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PBOOL false)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for name in tuple(child for _, _, child, _ in children) + ('null_name', 'false_name', 'true_name'):
        checks.append(f'porigin_compare_{name} = PORIGIN n_unit pcpath_compare_{name}')
    checks += lines(r'''
S_budget_compare = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$string_read_raw_truth(S_budget_compare,porigin_left,PBOOL false)
$string_read_raw_known_base(S_budget_compare,porigin_base,pvalue_base)
S_shorthand_compare = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprBinaryOpNotIdentical expression_compare_notequal expression_compare_greater metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_compare,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_compare,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PBOOL true'), ('own_tag', 'pcpath_left', 'PINT 0'),
            ('greater', 'pcpath_compare_greater', 'PBOOL true'), ('null_tag', 'pcpath_compare_null', 'PBOOL false'),
            ('false_tag', 'pcpath_compare_false', 'PNULL'), ('string_tag', 'pcpath_compare_two_string', 'PINT 2')):
        own = value if label in ('own', 'own_tag') else 'PBOOL false'
        checks += [f'S_bad_compare_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_compare_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_compare_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('greater', 'pcpath_compare_greater', 'NExprBinaryOpGreater expression_compare_greaterequal expression_compare_lessequal eps'),
            ('name', 'pcpath_compare_false_name', 'NName (BYTES text_compare_false) eps'),
            ('swapped', 'pcpath_compare_greaterequal', 'NExprBinaryOpGreaterOrEqual expression_compare_two_int expression_compare_two_string metadata_compare_greaterequal')):
        checks += [f'S_bad_compare_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_compare_{label}_source,porigin_left,PBOOL false)']
    checks += lines(r'''
S_bad_compare_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_compare_notequal 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_compare_code,porigin_left,PBOOL false)
~$string_read_raw_known_base(S_bad_compare_code,porigin_base,pvalue_base)
''')

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        spelling = f'$({i})' if i < 0 else str(i)
        return f'NScalarInt (INTEGER {spelling})', f'PINT {spelling}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    two, three = integer(2), integer(3)
    equal = ('Equal', 'PBOOL true', string(b'2'), two)
    notequal = ('NotEqual', 'PBOOL false', null, false)
    bad_division = ('Div', 'PINT 0', integer(1), integer(0))
    matrices = [
        ('equal_true', equal, True), ('equal_false', ('Equal', 'PBOOL false', string(b'2'), three), True),
        ('notequal_true', ('NotEqual', 'PBOOL true', null, true), True), ('notequal_false', notequal, True),
        ('identical_true', ('Identical', 'PBOOL true', false, false), True), ('identical_false', ('Identical', 'PBOOL false', string(b'2'), two), True),
        ('notidentical_true', ('NotIdentical', 'PBOOL true', string(b'2'), two), True), ('notidentical_false', ('NotIdentical', 'PBOOL false', false, false), True),
        ('less_true', ('Smaller', 'PBOOL true', two, three), True), ('less_false', ('Smaller', 'PBOOL false', three, two), True),
        ('lessequal_true', ('SmallerOrEqual', 'PBOOL true', string(b'2'), two), True), ('lessequal_false', ('SmallerOrEqual', 'PBOOL false', three, two), True),
        ('greater_true', ('Greater', 'PBOOL true', three, two), True), ('greater_false', ('Greater', 'PBOOL false', two, three), True),
        ('greaterequal_true', ('GreaterOrEqual', 'PBOOL true', string(b'2'), two), True), ('greaterequal_false', ('GreaterOrEqual', 'PBOOL false', integer(1), two), True),
        ('nonnumeric_left', ('Greater', 'PBOOL true', string(b'word'), two), True),
        ('nonnumeric_right', ('Greater', 'PBOOL false', two, string(b'word')), True),
        ('decimal_string', ('Equal', 'PBOOL true', string(b'2.0'), two), True),
        ('leading_string', ('Equal', 'PBOOL false', string(b'2x'), two), True),
        ('null_empty', ('Equal', 'PBOOL true', null, string(b'')), True),
        ('bool_zero', ('Equal', 'PBOOL true', false, string(b'0')), True),
        ('nested', ('NotIdentical', 'PBOOL true', equal, notequal), True),
        ('not_parent', ('BooleanNot', 'PBOOL false', equal), True),
        ('signed_parent', ('UnaryMinus', 'PINT $(-1)', equal), True),
        ('wrong_result', ('Equal', 'PBOOL false', string(b'2'), two), False),
        ('wrong_type', ('Equal', 'PINT 1', string(b'2'), two), False),
        ('float_child', ('Equal', 'PBOOL true', ('NScalarFloat (FLOAT "3ff0000000000000")', 'PFLOAT 4607182418800017408'), integer(1)), False),
        ('nan_child', ('Identical', 'PBOOL false', ('NScalarFloat (FLOAT "7ff8000000000000")', 'PFLOAT 9221120237041090560'), integer(1)), False),
        ('spaceship', ('Spaceship', 'PBOOL false', two, two), False),
        ('outside_child', ('Equal', 'PBOOL true', integer(9223372036854775808), integer(9223372036854775808)), False),
        ('array_child', ('Identical', 'PBOOL true', ('NExprArray (SEQUENCE eps)', 'PARRAY 0'), ('NExprArray (SEQUENCE eps)', 'PARRAY 0')), False),
        ('object_child', ('Identical', 'PBOOL true', ('NExprArray (SEQUENCE eps)', 'POBJECT 0'), ('NExprArray (SEQUENCE eps)', 'POBJECT 0')), False),
        ('interned_child', ('Equal', 'PBOOL true', ('NScalarString (BYTES "Mg==")', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))'), two), False),
        ('cached_division', ('Equal', 'PBOOL true', bad_division, integer(0)), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection('compare_' + label, tree, accepted)
    checks += lines(r'''
S_cached_budget_compare = S_sign_compare_cached_division[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$binary_apply(S_cached_budget_compare,EQUAL,PINT 0,PINT 0,0) = S_cached_budget_compare
~$string_read_raw_truth(S_cached_budget_compare,PORIGIN n_unit (pcpath_left ++ [PCFIELD 0]),PINT 0)
~$string_read_raw_truth(S_cached_budget_compare,porigin_left,PBOOL true)
S_cached_child_budget_compare = S_sign_compare_cached_division[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_cached_child_budget_compare,PORIGIN n_unit (pcpath_left ++ [PCFIELD 0]),PINT 0)
~$string_read_raw_truth(S_cached_child_budget_compare,porigin_left,PBOOL true)
S_missing_budget_compare = S_sign_compare_equal_true[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR (pcpath_left ++ [PCFIELD 1]) 18 false) :: pcode.EXPRESSIONS]]]
$binary_apply(S_missing_budget_compare,EQUAL,PSTRING ($ptascii("2")),PINT 2,0) = S_missing_budget_compare
~$string_read_raw_truth(S_missing_budget_compare,porigin_left,PBOOL true)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
