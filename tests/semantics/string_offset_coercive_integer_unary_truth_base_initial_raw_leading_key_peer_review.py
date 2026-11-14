"""Integer signs retain exact computed children across raw-key reference rebinding."""

import base64

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def _projection(label, tree, accepted):
    checks, occurrences, constants, code = [], [], [], []

    def visit(node, suffix, path):
        name, value = 'expression_sign_' + label + suffix, node[1]
        if len(node) == 2:
            constructor = node[0]
            expression = constructor + ' metadata_cond'
            if constructor.startswith('NExprConstFetch '):
                occurrences.append(f'(PCOCCURRENCE ({path} ++ [PCFIELD 0]) {constructor[len("NExprConstFetch "):]})')
        elif len(node) == 3:
            child = visit(node[2], suffix + '_c', f'({path} ++ [PCFIELD 0])')
            expression = f'NExpr{node[0]} {child} metadata_cond'
        else:
            left = visit(node[2], suffix + '_l', f'({path} ++ [PCFIELD 0])')
            right = visit(node[3], suffix + '_r', f'({path} ++ [PCFIELD 1])')
            expression = f'NExprBinaryOp{node[0]} {left} {right} metadata_cond'
        checks.append(f'{name} = {expression}')
        occurrences.append(f'(PCOCCURRENCE {path} {name})')
        constants.extend([f'(PCONSTANT {path} ({value}))', f'(PCCPRECISION {path} 14)'])
        code.append(f'(CODEEXPR {path} 18 true)')
        return name

    expression = visit(tree, '', 'pcpath_left')
    state = 'S_sign_' + label
    checks.append(f'expression_base_sign_{label} = NExprTernary {expression} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata')
    occurrences.insert(0, f'(PCOCCURRENCE pcpath_base expression_base_sign_{label})')
    checks.append(f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = ' + ' :: '.join(occurrences + ['pcunit.OCCURRENCES']) + ']]][.POOLS = [ppool[.CONSTANTS = ' + ' :: '.join(constants + ['ppool.CONSTANTS']) + ']]][.CODE = [pcode[.EXPRESSIONS = ' + ' :: '.join(code + ['pcode.EXPRESSIONS']) + ']]]')
    checks += [f'$compiled_read({state},porigin_left) = ({tree[1]})',
               f'{"" if accepted else "~"}$string_read_raw_truth({state},porigin_left,{tree[1]})']
    if accepted:
        selected = 'pvalue_base' if tree[1] in ('PINT 0', 'PBOOL false') else 'pvalue_wrong'
        checks.append(f'$string_read_raw_known_base({state},porigin_base,{selected})')
    else:
        checks += [f'~$string_read_raw_known_base({state},porigin_base,{value})' for value in ('pvalue_base', 'pvalue_wrong')]
    return checks


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprUnaryMinus expression_sign_child metadata_cond)')
    early = lines(r'''
expression_sign_child = NExprBinaryOpMinus expression_sign_division expression_sign_false metadata_sign_child
expression_sign_division = NExprBinaryOpDiv expression_sign_null expression_sign_string metadata_sign_division
expression_sign_false = NExprConstFetch (NName (BYTES text_sign_false) metadata_sign_false_name) metadata_sign_false
expression_sign_null = NExprConstFetch (NName (BYTES text_sign_null) metadata_sign_null_name) metadata_sign_null
expression_sign_string = NScalarString (BYTES text_sign_string) metadata_sign_string
$ptlc($base64(text_sign_false)) = $ptascii("false")
$ptlc($base64(text_sign_null)) = $ptascii("null")
$base64(text_sign_string) = $ptascii("2")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_sign_child)
$origin_child((porigin_sign_child),[PCFIELD 0]) = (porigin_sign_division)
$origin_child((porigin_sign_child),[PCFIELD 1]) = (porigin_sign_false)
$origin_child((porigin_sign_division),[PCFIELD 0]) = (porigin_sign_null)
$origin_child((porigin_sign_division),[PCFIELD 1]) = (porigin_sign_string)
$origin_child((porigin_sign_false),[PCFIELD 0]) = (porigin_sign_false_name)
$origin_child((porigin_sign_null),[PCFIELD 0]) = (porigin_sign_null_name)
$origin_node(S_capture.SOURCES,porigin_sign_false_name) = (NName (BYTES text_sign_false) metadata_sign_false_name)
$origin_node(S_capture.SOURCES,porigin_sign_null_name) = (NName (BYTES text_sign_null) metadata_sign_null_name)
''')
    for name, value in (('child', 'PINT 0'), ('division', 'PINT 0'), ('false', 'PBOOL false'),
                        ('null', 'PNULL'), ('string', 'PSTRING ($ptascii("2"))')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_sign_{name}) = (expression_sign_{name})',
                  f'$compiled_read(S_capture,porigin_sign_{name}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_sign_{name},{value})']
    early += lines(r'''
~$string_read_raw_unary_integer(S_capture,porigin_left,0)
$unary_apply(S_capture,NEGATIVE,PINT 0,0) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_sign_child = PORIGIN n_unit pcpath_sign_child
porigin_sign_division = PORIGIN n_unit pcpath_sign_division
porigin_sign_false = PORIGIN n_unit pcpath_sign_false
porigin_sign_null = PORIGIN n_unit pcpath_sign_null
porigin_sign_string = PORIGIN n_unit pcpath_sign_string
porigin_sign_false_name = PORIGIN n_unit pcpath_sign_false_name
porigin_sign_null_name = PORIGIN n_unit pcpath_sign_null_name
S_budget_sign = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
$string_read_raw_truth(S_budget_sign,porigin_left,PINT 0)
$string_read_raw_known_base(S_budget_sign,porigin_base,pvalue_base)
S_shorthand_sign = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprUnaryMinus expression_sign_child metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_sign,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_sign,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own', 'pcpath_left', 'PINT 1'),
            ('child', 'pcpath_sign_child', 'PINT 1'),
            ('child_tag', 'pcpath_sign_child', 'PFLOAT 0'),
            ('false_tag', 'pcpath_sign_false', 'PNULL')):
        own = value if label == 'own' else 'PINT 0'
        checks += [f'S_bad_sign_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_sign_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_sign_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('child', 'pcpath_sign_child', 'NExprBinaryOpMinus expression_sign_division expression_sign_false eps'),
            ('name', 'pcpath_sign_false_name', 'NName (BYTES text_sign_false) eps')):
        checks += [f'S_bad_sign_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_sign_{label}_source,porigin_left,PINT 0)']
    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        spelling = f'$({i})' if i < 0 else str(i)
        return f'NScalarInt (INTEGER {spelling})', f'PINT {spelling}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    add = ('Plus', 'PINT 3', string(b'2'), true)
    zero_division = ('Div', 'PINT 0', null, string(b'2'))
    plus = ('UnaryPlus', 'PINT 3', add)
    minimum = 'PINT $(-9223372036854775808)'
    minimum_child = ('Plus', minimum, integer(-9223372036854775808), false)
    bad_legacy = ('Div', 'PINT 1', integer(1), integer(0))
    matrices = [
        ('source_a', ('UnaryPlus', 'PINT 3', ('Mul', 'PINT 3', add, string(b'1'))), True),
        ('old_division_plus', ('UnaryPlus', 'PINT 0', zero_division), True),
        ('negative', ('UnaryMinus', 'PINT $(-3)', add), True),
        ('double_sign', ('UnaryMinus', 'PINT 3', ('UnaryMinus', 'PINT $(-3)', add)), True),
        ('double_zero', ('UnaryPlus', 'PINT 0', ('UnaryMinus', 'PINT 0', zero_division)), True),
        ('legacy_literal', ('UnaryPlus', 'PINT 3', integer(3)), True),
        ('legacy_true', ('UnaryMinus', 'PINT $(-1)', true), True),
        ('legacy_string', ('UnaryPlus', 'PINT 2', string(b'2')), True),
        ('integer_parent', ('Plus', 'PINT 4', plus, integer(1)), True),
        ('float_parent', ('Plus', 'PFLOAT 4616189618054758400', plus, string(b'1.0')), True),
        ('folded_not', ('BooleanNot', 'PBOOL false', plus), True),
        ('minimum_positive', ('UnaryPlus', minimum, minimum_child), True),
        ('minimum_float', ('UnaryMinus', 'PFLOAT 4890909195324358656', minimum_child), True),
        ('minimum_integer_forgery', ('UnaryMinus', minimum, minimum_child), False),
        ('wrong_result', ('UnaryPlus', 'PINT 4', add), False),
        ('wrong_child', ('UnaryPlus', 'PINT 4', ('Plus', 'PINT 4', string(b'2'), true)), False),
        ('outside_own', ('UnaryPlus', 'PINT 9223372036854775808', add), False),
        ('outside_child', ('UnaryPlus', 'PINT 0', integer(9223372036854775808)), False),
        ('null_first_sign', ('UnaryPlus', 'PINT 0', null), False),
        ('false_first_sign', ('UnaryMinus', 'PINT 0', false), False),
        ('decimal_first_sign', ('UnaryPlus', 'PINT 1', string(b'1.0')), False),
        ('bitnot_gate', ('BitwiseNot', 'PINT $(-4)', add), True),
        ('fraction', ('UnaryPlus', 'PINT 1', ('Div', 'PINT 1', string(b'3'), string(b'2'))), False),
        ('zero_divisor', ('UnaryPlus', 'PINT 0', ('Div', 'PINT 0', null, string(b'0'))), False),
        ('nested_zero', ('UnaryPlus', 'PINT 1', ('Plus', 'PINT 1', bad_legacy, false)), False),
        ('leading', ('UnaryPlus', 'PINT 2', ('Plus', 'PINT 2', string(b'2x'), false)), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection(label, tree, accepted)
    checks += lines(r'''
S_zero_budget_sign = S_sign_zero_divisor[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 0)]
$unary_apply(S_zero_budget_sign,POSITIVE,PINT 0,0) = S_zero_budget_sign
~$string_read_raw_truth(S_zero_budget_sign,porigin_left,PINT 0)
S_nested_budget_sign = S_sign_nested_zero[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
$string_read_raw_truth(S_nested_budget_sign,PORIGIN n_unit (pcpath_sign_child ++ [PCFIELD 0]),PINT 1)
~$string_read_raw_truth(S_nested_budget_sign,porigin_left,PINT 1)
S_minimum_budget_sign = S_sign_minimum_integer_forgery[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT $(-9223372036854775808))]
~$string_read_raw_truth(S_minimum_budget_sign,porigin_left,PINT $(-9223372036854775808))
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    added = len(early) + len(checks)
    return body, count + added, derived + len(checks)
