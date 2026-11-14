"""Quiet original scalar integer arithmetic keeps the frozen raw-key reference path."""

import base64

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMinus expression_integer_left expression_integer_right metadata_cond)')
    early = lines(r'''
expression_integer_left = NExprBinaryOpDiv expression_integer_null expression_integer_string metadata_integer_left
expression_integer_right = NExprConstFetch (NName (BYTES text_false_name) metadata_false_name) metadata_integer_right
expression_integer_null = NExprConstFetch (NName (BYTES text_null_name) metadata_null_name) metadata_integer_null
expression_integer_string = NScalarString (BYTES text_integer_string) metadata_integer_string
$ptlc($base64(text_false_name)) = $ptascii("false")
$ptlc($base64(text_null_name)) = $ptascii("null")
$base64(text_integer_string) = $ptascii("2")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_integer_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_integer_right)
$origin_child((porigin_integer_left),[PCFIELD 0]) = (porigin_integer_null)
$origin_child((porigin_integer_left),[PCFIELD 1]) = (porigin_integer_string)
$origin_child((porigin_integer_null),[PCFIELD 0]) = (porigin_null_name)
$origin_child((porigin_integer_right),[PCFIELD 0]) = (porigin_false_name)
$origin_node(S_capture.SOURCES,porigin_null_name) = (NName (BYTES text_null_name) metadata_null_name)
$origin_node(S_capture.SOURCES,porigin_false_name) = (NName (BYTES text_false_name) metadata_false_name)
''')
    for name, value in (('integer_left', 'PINT 0'), ('integer_right', 'PBOOL false'),
                        ('integer_null', 'PNULL'), ('integer_string', 'PSTRING ($ptascii("2"))')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_{name}) = (expression_{name})',
                  f'$compiled_read(S_capture,porigin_{name}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_{name},{value})']
    early += lines(r'''
$compiled_string_value(S_capture,porigin_integer_string,PSTRING ($ptascii("2"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))
$coerce_number(PNULL) = COERCED (NINT 0) false
$coerce_number(PBOOL false) = COERCED (NINT 0) false
$coerce_number(PSTRING ($ptascii("2"))) = COERCED (NINT 2) false
~$string_read_raw_unary_integer(S_capture,porigin_integer_left,0)
~$string_read_raw_unary_integer(S_capture,porigin_left,0)
$binary_apply(S_capture,DIVIDE,PNULL,PSTRING ($ptascii("2")),0) = S_capture[.RESULT = KNOWN (PINT 0)]
$binary_apply(S_capture,SUBTRACT,PINT 0,PBOOL false,0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_integer_left = PORIGIN n_unit pcpath_integer_left
porigin_integer_right = PORIGIN n_unit pcpath_integer_right
porigin_integer_null = PORIGIN n_unit pcpath_integer_null
porigin_integer_string = PORIGIN n_unit pcpath_integer_string
porigin_null_name = PORIGIN n_unit pcpath_null_name
porigin_false_name = PORIGIN n_unit pcpath_false_name
expression_integer = NExprBinaryOpMinus expression_integer_left expression_integer_right metadata_cond
S_budget_integer = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
$string_read_raw_truth(S_budget_integer,porigin_left,PINT 0)
$string_read_raw_known_base(S_budget_integer,porigin_base,pvalue_base)
S_shorthand_integer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary expression_integer ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_integer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_integer,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PINT 1'),
            ('left_tag', 'pcpath_integer_null', 'PBOOL false'),
            ('right_tag', 'pcpath_integer_right', 'PNULL'),
            ('raw_bytes', 'pcpath_integer_string', 'PSTRING ($ptascii("3"))'),
            ('carrier', 'pcpath_integer_string', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))')):
        own = value if label == 'own' else 'PINT 0'
        checks += [f'S_bad_integer_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_integer_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_integer_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('division', 'pcpath_integer_left', 'NExprBinaryOpDiv expression_integer_null expression_integer_string eps'),
            ('literal', 'pcpath_integer_string', 'NScalarString (BYTES text_integer_string) eps'),
            ('null_name', 'pcpath_null_name', 'NName (BYTES text_null_name) eps'),
            ('false_name', 'pcpath_false_name', 'NName (BYTES text_false_name) eps')):
        checks += [f'S_bad_integer_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_integer_{label}_source,porigin_left,PINT 0)',
                   f'~$string_read_raw_known_base(S_bad_integer_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_bad_integer_read = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_integer_string 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_integer_read,porigin_left,PINT 0)
S_unary_integer = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprUnaryPlus expression_integer_left metadata_cond) (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata)) :: (PCOCCURRENCE pcpath_left (NExprUnaryPlus expression_integer_left metadata_cond)) :: pcunit.OCCURRENCES]]]
$string_read_raw_truth(S_unary_integer,porigin_left,PINT 0)
$string_read_raw_known_base(S_unary_integer,porigin_base,pvalue_base)
''')
    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        spelling = f'$({i})' if i < 0 else str(i)
        return f'NScalarInt (INTEGER {spelling})', f'PINT {spelling}'
    def constant(name, value):
        encoded = base64.b64encode(name.encode()).decode()
        return f'NExprConstFetch (NName (BYTES "{encoded}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    source_add = ('Plus', 'PINT 3', string(b'2'), true)
    bad_integer = ('Div', 'PINT 1', integer(1), integer(0))
    matrices = [
        ('source_a_integer', ('Mul', 'PINT 3', source_add, string(b'1')), True),
        ('old_string_division', ('Div', 'PINT 0', string(b'0'), integer(2)), True),
        ('literal_zero', integer(0), True),
        ('old_modulo', ('Mod', 'PINT 1', integer(3), integer(2)), True),
        ('nested_both_integer', ('Plus', 'PINT 4', source_add, integer(1)), True),
        ('float_parent', ('Plus', 'PFLOAT 4616189618054758400', source_add, string(b'1.0')), True),
        ('negative', ('Minus', 'PINT $(-1)', false, string(b'1')), True),
        ('both_strings', ('Plus', 'PINT 3', string(b'1'), string(b'2')), True),
        ('bool_null', ('Plus', 'PINT 1', true, null), True),
        ('null_bool', ('Mul', 'PINT 0', null, false), True),
        ('whitespace', ('Div', 'PINT 2', string(b'\t4 \n'), string(b'2')), True),
        ('fraction', ('Div', 'PINT 1', string(b'3'), string(b'2')), False),
        ('decimal_string', ('Plus', 'PINT 1', string(b'1.0'), false), False),
        ('float_child', ('Plus', 'PINT 1', ('NScalarFloat (FLOAT "3ff0000000000000")', 'PFLOAT 4607182418800017408'), false), False),
        ('overflow', ('Plus', 'PINT 9223372036854775807', string(b'9223372036854775807'), true), False),
        ('own_range', ('Plus', 'PINT 9223372036854775808', string(b'9223372036854775807'), true), False),
        ('child_range', ('Plus', 'PINT 0', integer(9223372036854775808), false), False),
        ('zero_divisor', ('Div', 'PINT 0', true, string(b'0')), False),
        ('leading_left', ('Plus', 'PINT 2', string(b'2x'), false), False),
        ('leading_right', ('Plus', 'PINT 2', false, string(b'2x')), False),
        ('nul_leading', ('Plus', 'PINT 2', string(b'2\0'), false), False),
        ('nonnumeric', ('Plus', 'PINT 0', string(b'x'), false), False),
        ('nonfinite', ('Div', 'PINT 0', null, string(b'1e309')), False),
        ('interned_carrier', ('Plus', 'PINT 2', ('NScalarString (BYTES "Mg==")', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))'), false), False),
        ('request_carrier', ('Plus', 'PINT 2', ('NScalarString (BYTES "Mg==")', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("2"))'), false), False),
        ('nested_zero', ('Plus', 'PINT 2', bad_integer, string(b'1')), False),
        ('modulo_gate', ('Mod', 'PINT 0', null, string(b'2')), False),
        ('shift_gate', ('ShiftLeft', 'PINT 0', null, string(b'2')), False),
        ('power_gate', ('Pow', 'PINT 0', null, string(b'2')), False),
    ]
    for label, tree, accepted in matrices:
        projected = _projection(label, tree, accepted)
        if accepted and tree[1] == 'PINT 0':
            assert projected[-1] == f'$string_read_raw_known_base(S_projected_{label},porigin_base,pvalue_wrong)'
            projected[-1] = f'$string_read_raw_known_base(S_projected_{label},porigin_base,pvalue_base)'
        checks += projected
    checks += lines(r'''
~$string_read_raw_unary_integer(S_projected_old_string_division,porigin_left,0)
S_zero_budget_integer = S_projected_zero_divisor[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
$binary_apply(S_zero_budget_integer,DIVIDE,PBOOL true,PSTRING ($ptascii("0")),0) = S_zero_budget_integer
~$string_read_raw_truth(S_zero_budget_integer,porigin_left,PINT 0)
S_fraction_budget_integer = S_projected_fraction[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
~$string_read_raw_truth(S_fraction_budget_integer,porigin_left,PINT 1)
S_leading_budget_integer = S_projected_leading_left[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 2)]
$coerce_number(PSTRING ($ptascii("2x"))) = COERCED (NINT 2) true
~$string_read_raw_truth(S_leading_budget_integer,porigin_left,PINT 2)
S_nested_budget_integer = S_projected_nested_zero[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
$string_read_raw_truth(S_nested_budget_integer,porigin_integer_left,PINT 1)
~$string_read_raw_truth(S_nested_budget_integer[.COMPLETION = NORMAL],porigin_integer_left,PINT 1)
~$string_read_raw_truth(S_nested_budget_integer,porigin_left,PINT 2)
~$string_read_raw_known_base(S_nested_budget_integer,porigin_base,pvalue_wrong)
''')
    not_checks = _projection('not_integer', ('Plus', 'PINT 1', null, true), True, not_shorthand=True)
    emitted_base = '$string_read_raw_known_base(S_projected_not_integer,porigin_base,pvalue_base)'
    assert not_checks.count(emitted_base) == 1
    not_checks[not_checks.index(emitted_base)] = '~' + emitted_base
    checks += not_checks + lines(r'''
S_projected_not_integer.POOLS = [ppool_integer_not]
S_projected_not_integer.CODE = [pcode_integer_not]
S_folded_not_integer = S_projected_not_integer[.POOLS = [ppool_integer_not[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: ppool_integer_not.CONSTANTS]]][.CODE = [pcode_integer_not[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: pcode_integer_not.EXPRESSIONS]]]
$compiled_read(S_folded_not_integer,porigin_left) = (PBOOL false)
$string_read_raw_truth(S_folded_not_integer,PORIGIN n_unit (pcpath_left ++ [PCFIELD 0]),PINT 1)
$string_read_raw_truth(S_folded_not_integer,porigin_left,PBOOL false)
$string_read_raw_known_base(S_folded_not_integer,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_folded_not_integer[.CODE = eps],porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    added = len(early) + len(checks)
    return body, count + added, derived + len(checks)
