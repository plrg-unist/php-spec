"""Mixed numeric cancellation keeps the false arm across raw-key reference rebinding."""

from string_offset_float_conditional_base_initial_raw_leading_key_peer_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def _projection(label, tree, accepted, *, not_shorthand=False):
    checks, occurrences, constants, paths = [], [], [], []

    def visit(node, suffix, path):
        name = 'expression_projected_' + label + suffix
        if len(node) == 2:
            constructor, value = node
            checks.append(f'{name} = {constructor} metadata_cond')
            if constructor.startswith('NExprConstFetch'):
                raw = constructor[len('NExprConstFetch '):]
                occurrences.append(f'(PCOCCURRENCE ({path} ++ [PCFIELD 0]) {raw})')
        else:
            constructor, value, left, right = node
            left_name = visit(left, suffix + '_l', f'({path} ++ [PCFIELD 0])')
            right_name = visit(right, suffix + '_r', f'({path} ++ [PCFIELD 1])')
            checks.append(f'{name} = NExprBinaryOp{constructor} {left_name} {right_name} metadata_cond')
        occurrences.append(f'(PCOCCURRENCE {path} {name})')
        constants.append(f'(PCONSTANT {path} ({value}))')
        paths.append(path)
        return name

    root_path = '(pcpath_left ++ [PCFIELD 0])' if not_shorthand else 'pcpath_left'
    expression = visit(tree, '', root_path)
    state = 'S_projected_' + label
    if not_shorthand:
        checks += [f'expression_not_{label} = NExprBooleanNot {expression} metadata_cond',
                   f'expression_base_{label} = NExprTernary expression_not_{label} ABSENT (NScalarString (BYTES text_right) metadata_right) metadata']
        occurrences += [f'(PCOCCURRENCE pcpath_left expression_not_{label})']
        constants += ['(PCONSTANT pcpath_right (PSTRING ($ptascii("abc"))))']
        constants += [f'(PCCPRECISION {path} 14)' for path in ['pcpath_left', 'pcpath_right'] + paths]
        pool_tail = 'eps'
    else:
        checks.append(f'expression_base_{label} = NExprTernary {expression} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata')
        pool_tail = 'ppool.CONSTANTS'
    occurrences.insert(0, f'(PCOCCURRENCE pcpath_base expression_base_{label})')
    checks.append(f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = ' + ' :: '.join(occurrences + ['pcunit.OCCURRENCES']) + ']]][.POOLS = [ppool[.CONSTANTS = ' + ' :: '.join(constants + [pool_tail]) + ']]]')
    if not_shorthand:
        checks[-1] += '[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: ' + ' :: '.join(f'(CODEEXPR {path} 18 true)' for path in paths) + ' :: pcode.EXPRESSIONS]]]'
        checks += [f'$compiled_read({state},porigin_left) = eps',
                   f'$string_read_raw_truth({state},PORIGIN n_unit {root_path},{tree[1]})',
                   f'$string_read_runtime_value({state},porigin_left) = (PBOOL false)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)',
                   f'~$string_read_raw_known_base({state}[.CODE = eps],porigin_base,pvalue_base)']
    else:
        checks += [f'$origin_node({state}.SOURCES,porigin_left) = ({expression})',
                   f'$compiled_read({state},porigin_left) = ({tree[1]})',
                   f'{"" if accepted else "~"}$string_read_raw_truth({state},porigin_left,{tree[1]})']
        if accepted:
            selected = 'pvalue_base' if tree[1] in ('PFLOAT 0', 'PFLOAT 9223372036854775808') else 'pvalue_wrong'
            checks.append(f'$string_read_raw_known_base({state},porigin_base,{selected})')
        else:
            checks += [f'~$string_read_raw_known_base({state},porigin_base,{value})'
                       for value in ('pvalue_base', 'pvalue_wrong')]
    return checks


def render(program, filename_b64):
    body, count, derived = render_float(program, filename_b64)
    old = 'NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpMinus expression_numeric_left expression_numeric_right metadata_cond)')
    old_hex = '  -- if $hex_bits(text_cond,0) = 0\n'
    assert body.count(old_hex) == 1
    body = body.replace(old_hex, '')
    count -= 1
    early = lines(r'''
expression_numeric_left = NExprBinaryOpDiv expression_div_left expression_div_right metadata_numeric_left
expression_numeric_right = NExprBinaryOpMinus expression_sub_left expression_sub_right metadata_numeric_right
expression_div_left = NScalarInt (INTEGER 1) metadata_div_left
expression_div_right = NScalarInt (INTEGER 2) metadata_div_right
expression_sub_left = NScalarInt (INTEGER 1) metadata_sub_left
expression_sub_right = NScalarFloat (FLOAT text_sub_right) metadata_sub_right
$hex_bits(text_sub_right,0) = 4602678819172646912
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_numeric_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_numeric_right)
$origin_child((porigin_numeric_left),[PCFIELD 0]) = (porigin_div_left)
$origin_child((porigin_numeric_left),[PCFIELD 1]) = (porigin_div_right)
$origin_child((porigin_numeric_right),[PCFIELD 0]) = (porigin_sub_left)
$origin_child((porigin_numeric_right),[PCFIELD 1]) = (porigin_sub_right)
''')
    for name, value in (('numeric_left', 'PFLOAT 4602678819172646912'),
                        ('numeric_right', 'PFLOAT 4602678819172646912'),
                        ('div_left', 'PINT 1'), ('div_right', 'PINT 2'),
                        ('sub_left', 'PINT 1'), ('sub_right', 'PFLOAT 4602678819172646912')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_{name}) = (expression_{name})',
                  f'$compiled_read(S_capture,porigin_{name}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_{name},{value})']
    early += lines(r'''
$binary_apply(S_capture,DIVIDE,PINT 1,PINT 2,0) = S_capture[.RESULT = KNOWN (PFLOAT 4602678819172646912)]
$binary_apply(S_capture,SUBTRACT,PINT 1,PFLOAT 4602678819172646912,0) = S_capture[.RESULT = KNOWN (PFLOAT 4602678819172646912)]
$binary_apply(S_capture,SUBTRACT,PFLOAT 4602678819172646912,PFLOAT 4602678819172646912,0) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_capture,porigin_left,PFLOAT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PFLOAT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
porigin_numeric_left = PORIGIN n_unit pcpath_numeric_left
porigin_numeric_right = PORIGIN n_unit pcpath_numeric_right
porigin_div_left = PORIGIN n_unit pcpath_div_left
porigin_div_right = PORIGIN n_unit pcpath_div_right
porigin_sub_left = PORIGIN n_unit pcpath_sub_left
porigin_sub_right = PORIGIN n_unit pcpath_sub_right
expression_numeric = NExprBinaryOpMinus expression_numeric_left expression_numeric_right metadata_cond
S_budget_numeric = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 4607182418800017408)]
$string_read_raw_truth(S_budget_numeric,porigin_left,PFLOAT 0)
$string_read_raw_known_base(S_budget_numeric,porigin_base,pvalue_base)
S_shorthand_numeric = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary expression_numeric ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_numeric,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_numeric,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own_sign', 'pcpath_left', 'PFLOAT 9223372036854775808'),
            ('left_type', 'pcpath_numeric_left', 'PINT 0'),
            ('right_bits', 'pcpath_numeric_right', 'PFLOAT 4607182418800017408'),
            ('leaf_value', 'pcpath_div_left', 'PINT 2')):
        own = value if label == 'own_sign' else 'PFLOAT 0'
        checks += [f'S_wrong_numeric_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_wrong_numeric_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_wrong_numeric_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('left', 'pcpath_numeric_left', 'NExprBinaryOpDiv expression_div_left expression_div_right eps'),
            ('right', 'pcpath_numeric_right', 'NExprBinaryOpMinus expression_sub_left expression_sub_right eps'),
            ('leaf', 'pcpath_sub_right', 'NScalarFloat (FLOAT text_sub_right) eps')):
        checks += [f'S_wrong_numeric_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_wrong_numeric_{label}_source,porigin_left,PFLOAT 0)',
                   f'~$string_read_raw_known_base(S_wrong_numeric_{label}_source,porigin_base,pvalue_base)']
    def integer(value):
        spelling = f'$({value})' if value < 0 else str(value)
        return f'NScalarInt (INTEGER {spelling})', f'PINT {spelling}'
    floating = lambda bits: (f'NScalarFloat (FLOAT "{bits:016x}")', f'PFLOAT {bits}')
    half, one, two, negative_zero = 4602678819172646912, 4607182418800017408, 4611686018427387904, 9223372036854775808
    promotion = ('Plus', 'PFLOAT 4890909195324358656', integer(9223372036854775807), integer(1))
    bad_integer = ('Div', 'PINT 1', integer(1), integer(0))
    bad_float = ('Div', 'PFLOAT 0', integer(1), integer(0))
    matrices = [
        ('mixed_int', ('Plus', 'PFLOAT 0', integer(0), floating(0)), True),
        ('promotion', promotion, True),
        ('int_left_sub', ('Minus', f'PFLOAT {half}', integer(1), floating(half)), True),
        ('float_left_sub', ('Minus', 'PFLOAT 13826050856027422720', floating(half), integer(1)), True),
        ('mixed_right_div', ('Div', f'PFLOAT {half}', floating(one), integer(2)), True),
        ('mixed_left_div', ('Div', f'PFLOAT {half}', integer(1), floating(two)), True),
        ('fraction', ('Div', f'PFLOAT {half}', integer(1), integer(2)), True),
        ('min_divide', ('Div', 'PFLOAT 4890909195324358656', integer(-9223372036854775808), integer(-1)), True),
        ('signed_zero', ('Mul', f'PFLOAT {negative_zero}', floating(negative_zero), integer(2)), True),
        ('signed_zero_div', ('Div', f'PFLOAT {negative_zero}', floating(negative_zero), integer(2)), True),
        ('fake_exact_div', ('Div', f'PFLOAT {two}', integer(4), integer(2)), False),
        ('fake_cancellation', ('Minus', 'PFLOAT 0', integer(1), integer(1)), False),
        ('wrong_zero_sign', ('Mul', 'PFLOAT 0', floating(negative_zero), integer(2)), False),
        ('zero_divisor', bad_float, False),
        ('float_zero_divisor', ('Div', 'PFLOAT 0', integer(1), floating(0)), False),
        ('negative_zero_divisor', ('Div', 'PFLOAT 0', integer(1), floating(negative_zero)), False),
        ('nested_integer_zero', ('Plus', f'PFLOAT {one}', bad_integer, floating(0)), False),
        ('nested_float_zero', ('Plus', 'PFLOAT 0', bad_float, floating(0)), False),
        ('infinite_denominator', ('Div', 'PFLOAT 0', integer(0), floating(9218868437227405312)), False),
        ('overflow', ('Mul', 'PFLOAT 9218868437227405312', floating(9218868437227405311), integer(2)), False),
        ('fake_finite_overflow', ('Mul', 'PFLOAT 0', floating(9218868437227405311), integer(2)), False),
        ('modulo_gate', ('Mod', f'PFLOAT {one}', integer(3), integer(2)), False),
    ]
    for label, constructor, value, right in (
            ('bool_left', 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_cond)', 'PBOOL true', False),
            ('bool_right', 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_cond)', 'PBOOL true', True),
            ('null_right', 'NExprConstFetch (NName (BYTES "bnVsbA==") metadata_cond)', 'PNULL', True),
            ('numeric_string', 'NScalarString (BYTES "MA==")', 'PSTRING ($ptascii("0"))', False)):
        child = (constructor, value)
        result = f'PFLOAT {one}' if value.startswith('PBOOL') else 'PFLOAT 0'
        matrices.append((label, ('Plus', result, floating(0) if right else child, child if right else floating(0)), True))
    for label, tree, accepted in matrices:
        checks += _projection(label, tree, accepted)
    checks += lines(r'''
S_zero_budget_numeric = S_projected_zero_divisor[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
$binary_apply(S_zero_budget_numeric,DIVIDE,PINT 1,PINT 0,0) = S_zero_budget_numeric
~$string_read_raw_truth(S_zero_budget_numeric,porigin_left,PFLOAT 0)
~$string_read_raw_known_base(S_zero_budget_numeric,porigin_base,pvalue_base)
S_nested_budget_numeric = S_projected_nested_integer_zero[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 1)]
$string_read_raw_truth(S_nested_budget_numeric,porigin_numeric_left,PINT 1)
~$string_read_raw_truth(S_nested_budget_numeric[.COMPLETION = NORMAL],porigin_numeric_left,PINT 1)
~$string_read_raw_truth(S_nested_budget_numeric,porigin_left,PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_nested_budget_numeric,porigin_base,pvalue_wrong)
S_nested_float_budget_numeric = S_projected_nested_float_zero[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
~$string_read_raw_truth(S_nested_float_budget_numeric,porigin_left,PFLOAT 0)
$binary_apply(S_projected_infinite_denominator,DIVIDE,PINT 0,PFLOAT 9218868437227405312,0) = S_projected_infinite_denominator[.RESULT = KNOWN (PFLOAT 0)]
~$string_read_raw_truth(S_projected_infinite_denominator,porigin_numeric_right,PFLOAT 9218868437227405312)
$string_read_raw_truth(S_projected_bool_left,porigin_numeric_left,PBOOL true)
$string_read_raw_truth(S_projected_bool_right,porigin_numeric_right,PBOOL true)
$string_read_raw_truth(S_projected_null_right,porigin_numeric_right,PNULL)
$string_read_raw_truth(S_projected_numeric_string,porigin_numeric_left,PSTRING ($ptascii("0")))
$binary_apply(S_projected_bool_left,ADD,PBOOL true,PFLOAT 0,0) = S_projected_bool_left[.RESULT = KNOWN (PFLOAT 4607182418800017408)]
$binary_apply(S_projected_null_right,ADD,PFLOAT 0,PNULL,0) = S_projected_null_right[.RESULT = KNOWN (PFLOAT 0)]
$binary_apply(S_projected_numeric_string,ADD,PSTRING ($ptascii("0")),PFLOAT 0,0) = S_projected_numeric_string[.RESULT = KNOWN (PFLOAT 0)]
''')
    checks += _projection('not_promotion', promotion, True, not_shorthand=True)
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    added = len(early) + len(checks)
    return body, count + added, derived + len(checks)
