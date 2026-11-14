"""Integer-negation overflow composes through cancellation and raw-key reference rebinding."""

from string_offset_float_conditional_base_initial_raw_leading_key_peer_review import render as render_float
from string_offset_retained_carrier_protocol import lines


def _projection(label, operator, child, value, bits, accepted, *, not_shorthand=False):
    child_path = '(pcpath_left ++ [PCFIELD 0,PCFIELD 0])' if not_shorthand else '(pcpath_left ++ [PCFIELD 0])'
    sign_path = '(pcpath_left ++ [PCFIELD 0])' if not_shorthand else 'pcpath_left'
    checks = [f'expression_child_{label} = {child} metadata_cond',
              f'expression_sign_{label} = NExprUnary{operator} expression_child_{label} metadata_cond']
    occurrences = [f'(PCOCCURRENCE {sign_path} expression_sign_{label})',
                   f'(PCOCCURRENCE {child_path} expression_child_{label})']
    if child.startswith('NExprConstFetch '):
        occurrences.append(f'(PCOCCURRENCE ({child_path} ++ [PCFIELD 0]) {child[len("NExprConstFetch "):]})')
    constants = [f'(PCONSTANT {sign_path} (PFLOAT {bits}))', f'(PCONSTANT {child_path} ({value}))']
    state = 'S_projected_' + label
    if not_shorthand:
        checks += [f'expression_not_{label} = NExprBooleanNot expression_sign_{label} metadata_cond',
                   f'expression_base_{label} = NExprTernary expression_not_{label} ABSENT (NScalarString (BYTES text_right) metadata_right) metadata']
        occurrences += [f'(PCOCCURRENCE pcpath_left expression_not_{label})']
        constants += ['(PCONSTANT pcpath_right (PSTRING ($ptascii("abc"))))']
        constants += [f'(PCCPRECISION {path} 14)' for path in ('pcpath_left', sign_path, child_path, 'pcpath_right')]
        tail = 'eps'
    else:
        checks.append(f'expression_base_{label} = NExprTernary expression_sign_{label} (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata')
        tail = 'ppool.CONSTANTS'
    occurrences.insert(0, f'(PCOCCURRENCE pcpath_base expression_base_{label})')
    checks.append(f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = ' + ' :: '.join(occurrences + ['pcunit.OCCURRENCES']) + ']]][.POOLS = [ppool[.CONSTANTS = ' + ' :: '.join(constants + [tail]) + ']]]')
    if not_shorthand:
        checks[-1] += f'[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 false) :: (CODEEXPR {sign_path} 18 true) :: (CODEEXPR {child_path} 18 true) :: pcode.EXPRESSIONS]]]'
        checks += [f'$compiled_read({state},porigin_left) = eps',
                   f'$string_read_raw_truth({state},PORIGIN n_unit {sign_path},PFLOAT {bits})',
                   f'$string_read_runtime_value({state},porigin_left) = (PBOOL false)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)',
                   f'~$string_read_raw_known_base({state}[.CODE = eps],porigin_base,pvalue_base)']
    else:
        checks += [f'$compiled_read({state},porigin_left) = (PFLOAT {bits})',
                   f'$compiled_read({state},porigin_numeric_left) = ({value})',
                   f'{"" if accepted else "~"}$string_read_raw_truth({state},porigin_left,PFLOAT {bits})']
        if accepted:
            selected = 'pvalue_base' if bits in (0, 9223372036854775808) else 'pvalue_wrong'
            checks.append(f'$string_read_raw_known_base({state},porigin_base,{selected})')
        else:
            checks += [f'~$string_read_raw_known_base({state},porigin_base,{selected})'
                       for selected in ('pvalue_base', 'pvalue_wrong')]
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
expression_numeric_left = NExprUnaryMinus expression_minimum metadata_numeric_left
expression_numeric_right = NExprBinaryOpPlus expression_right_max expression_right_one metadata_numeric_right
expression_minimum = NExprBinaryOpMinus expression_negative_max expression_min_one metadata_minimum
expression_negative_max = NExprUnaryMinus expression_max metadata_negative_max
expression_max = NScalarInt (INTEGER 9223372036854775807) metadata_max
expression_min_one = NScalarInt (INTEGER 1) metadata_min_one
expression_right_max = NScalarInt (INTEGER 9223372036854775807) metadata_right_max
expression_right_one = NScalarInt (INTEGER 1) metadata_right_one
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_numeric_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_numeric_right)
$origin_child((porigin_numeric_left),[PCFIELD 0]) = (porigin_minimum)
$origin_child((porigin_minimum),[PCFIELD 0]) = (porigin_negative_max)
$origin_child((porigin_minimum),[PCFIELD 1]) = (porigin_min_one)
$origin_child((porigin_negative_max),[PCFIELD 0]) = (porigin_max)
$origin_child((porigin_numeric_right),[PCFIELD 0]) = (porigin_right_max)
$origin_child((porigin_numeric_right),[PCFIELD 1]) = (porigin_right_one)
''')
    values = (('numeric_left', 'PFLOAT 4890909195324358656'),
              ('numeric_right', 'PFLOAT 4890909195324358656'),
              ('minimum', 'PINT $(-9223372036854775808)'),
              ('negative_max', 'PINT $(-9223372036854775807)'),
              ('max', 'PINT 9223372036854775807'), ('min_one', 'PINT 1'),
              ('right_max', 'PINT 9223372036854775807'), ('right_one', 'PINT 1'))
    for name, value in values:
        early += [f'$origin_node(S_capture.SOURCES,porigin_{name}) = (expression_{name})',
                  f'$compiled_read(S_capture,porigin_{name}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_{name},{value})']
    early += lines(r'''
$unary_apply(S_capture,NEGATIVE,PINT $(-9223372036854775808),0) = S_capture[.RESULT = KNOWN (PFLOAT 4890909195324358656)]
$binary_apply(S_capture,ADD,PINT 9223372036854775807,PINT 1,0) = S_capture[.RESULT = KNOWN (PFLOAT 4890909195324358656)]
$binary_apply(S_capture,SUBTRACT,PFLOAT 4890909195324358656,PFLOAT 4890909195324358656,0) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_capture,porigin_left,PFLOAT 0)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PFLOAT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = [f'porigin_{name} = PORIGIN n_unit pcpath_{name}' for name, _ in values]
    checks += lines(r'''
expression_numeric = NExprBinaryOpMinus expression_numeric_left expression_numeric_right metadata_cond
S_budget_numeric = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 7)]
$string_read_raw_truth(S_budget_numeric,porigin_left,PFLOAT 0)
$string_read_raw_known_base(S_budget_numeric,porigin_base,pvalue_base)
S_shorthand_numeric = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary expression_numeric ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_numeric,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_numeric,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('minimum_type', 'pcpath_minimum', 'PFLOAT 14114281232179134464'),
            ('minimum_value', 'pcpath_minimum', 'PINT $(-9223372036854775807)'),
            ('max_leaf', 'pcpath_max', 'PINT 1'),
            ('left_bits', 'pcpath_numeric_left', 'PFLOAT 0')):
        checks += [f'S_bad_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_{label},porigin_numeric_left,PFLOAT 4890909195324358656)',
                   f'~$string_read_raw_known_base(S_bad_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('unary', 'pcpath_numeric_left', 'NExprUnaryMinus expression_minimum eps'),
            ('integer_child', 'pcpath_minimum', 'NExprBinaryOpMinus expression_negative_max expression_min_one eps'),
            ('integer_leaf', 'pcpath_max', 'NScalarInt (INTEGER 9223372036854775807) eps')):
        checks += [f'S_bad_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_{label}_source,porigin_left,PFLOAT 0)',
                   f'~$string_read_raw_known_base(S_bad_{label}_source,porigin_base,pvalue_base)']
    minimum = 'NScalarInt (INTEGER $(-9223372036854775808))'
    one = 'NScalarInt (INTEGER 1)'
    floating = lambda bits: f'NScalarFloat (FLOAT "{bits:016x}")'
    for label, operator, child, value, bits, accepted in (
            ('min_overflow', 'Minus', minimum, 'PINT $(-9223372036854775808)', 4890909195324358656, True),
            ('min_plus_fake_float', 'Plus', minimum, 'PINT $(-9223372036854775808)', 14114281232179134464, False),
            ('exact_integer', 'Plus', one, 'PINT 1', 4607182418800017408, False),
            ('integer_zero', 'Minus', 'NScalarInt (INTEGER 0)', 'PINT 0', 9223372036854775808, False),
            ('float_positive_zero', 'Plus', floating(0), 'PFLOAT 0', 0, True),
            ('float_negative_zero', 'Minus', floating(0), 'PFLOAT 0', 9223372036854775808, True),
            ('keep_negative_zero', 'Plus', floating(9223372036854775808), 'PFLOAT 9223372036854775808', 9223372036854775808, True),
            ('flip_negative_zero', 'Minus', floating(9223372036854775808), 'PFLOAT 9223372036854775808', 0, True),
            ('wrong_zero_sign', 'Plus', floating(9223372036854775808), 'PFLOAT 9223372036854775808', 0, False),
            ('float_large', 'Minus', floating(4890909195324358656), 'PFLOAT 4890909195324358656', 14114281232179134464, True),
            ('string_half', 'Plus', 'NScalarString (BYTES "MC41")', 'PSTRING ($ptascii("0.5"))', 4602678819172646912, True),
            ('bool', 'Plus', 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_cond)', 'PBOOL true', 4607182418800017408, False),
            ('null', 'Minus', 'NExprConstFetch (NName (BYTES "bnVsbA==") metadata_cond)', 'PNULL', 0, False),
            ('undefined', 'Plus', one, 'PUNDEFINED', 0, False),
            ('array', 'Plus', one, 'PARRAY 0', 0, False),
            ('object', 'Plus', one, 'POBJECT 0', 0, False),
            ('out_of_range', 'Minus', 'NScalarInt (INTEGER $(-9223372036854775809))', 'PINT $(-9223372036854775809)', 4890909195324358656, False),
            ('infinite_result', 'Plus', floating(9218868437227405312), 'PFLOAT 9218868437227405312', 9218868437227405312, False),
            ('fake_finite_infinite', 'Plus', floating(9218868437227405312), 'PFLOAT 9218868437227405312', 0, False)):
        checks += _projection(label, operator, child, value, bits, accepted)
    checks += lines(r'''
$string_read_raw_truth(S_projected_string_half,porigin_numeric_left,PSTRING ($ptascii("0.5")))
$unary_apply(S_projected_string_half,POSITIVE,PSTRING ($ptascii("0.5")),0) = S_projected_string_half[.RESULT = KNOWN (PFLOAT 4602678819172646912)]
$unary_apply(S_projected_exact_integer,POSITIVE,PINT 1,0) = S_projected_exact_integer[.RESULT = KNOWN (PINT 1)]
S_projected_min_overflow.SOURCES = [pcunit_error]
S_projected_min_overflow.POOLS = [ppool_error]
expression_error_left = NScalarInt (INTEGER 1) metadata_cond
expression_error_right = NScalarInt (INTEGER 0) metadata_cond
expression_error_child = NExprBinaryOpDiv expression_error_left expression_error_right metadata_cond
expression_error_sign = NExprUnaryMinus expression_error_child metadata_cond
expression_error_base = NExprTernary expression_error_sign (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_error = S_projected_min_overflow[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT $(-9223372036854775808))][.SOURCES = [pcunit_error[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_error_base) :: (PCOCCURRENCE pcpath_left expression_error_sign) :: (PCOCCURRENCE pcpath_numeric_left expression_error_child) :: (PCOCCURRENCE (pcpath_numeric_left ++ [PCFIELD 0]) expression_error_left) :: (PCOCCURRENCE (pcpath_numeric_left ++ [PCFIELD 1]) expression_error_right) :: pcunit_error.OCCURRENCES]]][.POOLS = [ppool_error[.CONSTANTS = (PCONSTANT (pcpath_numeric_left ++ [PCFIELD 0]) (PINT 1)) :: (PCONSTANT (pcpath_numeric_left ++ [PCFIELD 1]) (PINT 0)) :: ppool_error.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_numeric_left 18 true) :: (CODEEXPR (pcpath_numeric_left ++ [PCFIELD 0]) 18 true) :: (CODEEXPR (pcpath_numeric_left ++ [PCFIELD 1]) 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_error,porigin_numeric_left) = (PINT $(-9223372036854775808))
$compiled_read(S_error,PORIGIN n_unit (pcpath_numeric_left ++ [PCFIELD 0])) = (PINT 1)
$compiled_read(S_error,PORIGIN n_unit (pcpath_numeric_left ++ [PCFIELD 1])) = (PINT 0)
$string_read_raw_truth(S_error,porigin_numeric_left,PINT $(-9223372036854775808))
~$string_read_raw_truth(S_error[.COMPLETION = NORMAL],porigin_numeric_left,PINT $(-9223372036854775808))
$unary_apply(S_error,NEGATIVE,PINT $(-9223372036854775808),0) = S_error[.RESULT = KNOWN (PFLOAT 4890909195324358656)]
~$string_read_raw_truth(S_error,porigin_left,PFLOAT 4890909195324358656)
~$string_read_raw_known_base(S_error,porigin_base,pvalue_wrong)
expression_nested_child = NExprBinaryOpPlus expression_error_child expression_error_right metadata_cond
expression_nested_sign = NExprUnaryMinus expression_nested_child metadata_cond
expression_nested_base = NExprTernary expression_nested_sign (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_nested_error = S_error[.SOURCES = [pcunit_error[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_nested_base) :: (PCOCCURRENCE pcpath_left expression_nested_sign) :: (PCOCCURRENCE pcpath_numeric_left expression_nested_child) :: (PCOCCURRENCE (pcpath_numeric_left ++ [PCFIELD 0]) expression_error_child) :: (PCOCCURRENCE (pcpath_numeric_left ++ [PCFIELD 1]) expression_error_right) :: (PCOCCURRENCE (pcpath_numeric_left ++ [PCFIELD 0,PCFIELD 0]) expression_error_left) :: (PCOCCURRENCE (pcpath_numeric_left ++ [PCFIELD 0,PCFIELD 1]) expression_error_right) :: pcunit_error.OCCURRENCES]]][.POOLS = [ppool_error[.CONSTANTS = (PCONSTANT (pcpath_numeric_left ++ [PCFIELD 0]) (PINT $(-9223372036854775808))) :: (PCONSTANT (pcpath_numeric_left ++ [PCFIELD 1]) (PINT 0)) :: (PCONSTANT (pcpath_numeric_left ++ [PCFIELD 0,PCFIELD 0]) (PINT 1)) :: (PCONSTANT (pcpath_numeric_left ++ [PCFIELD 0,PCFIELD 1]) (PINT 0)) :: ppool_error.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_numeric_left 18 true) :: (CODEEXPR (pcpath_numeric_left ++ [PCFIELD 0]) 18 true) :: (CODEEXPR (pcpath_numeric_left ++ [PCFIELD 1]) 18 true) :: (CODEEXPR (pcpath_numeric_left ++ [PCFIELD 0,PCFIELD 0]) 18 true) :: (CODEEXPR (pcpath_numeric_left ++ [PCFIELD 0,PCFIELD 1]) 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_nested_error,PORIGIN n_unit (pcpath_numeric_left ++ [PCFIELD 0])) = (PINT $(-9223372036854775808))
$compiled_read(S_nested_error,PORIGIN n_unit (pcpath_numeric_left ++ [PCFIELD 0,PCFIELD 0])) = (PINT 1)
$compiled_read(S_nested_error,PORIGIN n_unit (pcpath_numeric_left ++ [PCFIELD 0,PCFIELD 1])) = (PINT 0)
$string_read_raw_truth(S_nested_error,porigin_numeric_left,PINT $(-9223372036854775808))
~$string_read_raw_truth(S_nested_error[.COMPLETION = NORMAL],porigin_numeric_left,PINT $(-9223372036854775808))
~$string_read_raw_truth(S_nested_error,porigin_left,PFLOAT 4890909195324358656)
~$string_read_raw_known_base(S_nested_error,porigin_base,pvalue_wrong)
''')
    checks += _projection('not_min_overflow', 'Minus', minimum, 'PINT $(-9223372036854775808)', 4890909195324358656, True, not_shorthand=True)
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    added = len(early) + len(checks)
    return body, count + added, derived + len(checks)
