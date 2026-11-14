"""Completed finite FLOAT powers preserve frozen reference-key selection."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpPow expression_power_negative expression_power_three metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = (PFLOAT 9223372036854775808)')
    body = body.replace('~$truth(S_capture,PINT 0)', '~$truth(S_capture,PFLOAT 9223372036854775808)')
    early = lines(r'''
expression_power_negative = NExprUnaryMinus expression_power_zero metadata_power_negative
expression_power_zero = NScalarFloat (FLOAT text_power_zero) metadata_power_zero
expression_power_three = NScalarInt (INTEGER 3) metadata_power_three
text_power_zero = "0000000000000000"
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_power_negative)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_power_three)
$origin_child((porigin_power_negative),[PCFIELD 0]) = (porigin_power_zero)
''')
    for child, value in (('negative', 'PFLOAT 9223372036854775808'), ('zero', 'PFLOAT 0'), ('three', 'PINT 3')):
        early += [f'$origin_node(S_capture.SOURCES,porigin_power_{child}) = (expression_power_{child})',
                  f'$compiled_read(S_capture,porigin_power_{child}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_power_{child},{value})']
    early += lines(r'''
$coerce_number(PFLOAT 9223372036854775808) = COERCED (NFLOAT 9223372036854775808) false
$coerce_number(PINT 3) = COERCED (NINT 3) false
$power_prepare(NFLOAT 9223372036854775808,NINT 3) = POWERDONE (NFLOAT 9223372036854775808) false
$binary_apply(S_capture,POWER,PFLOAT 9223372036854775808,PINT 3,0) = S_capture[.RESULT = KNOWN (PFLOAT 9223372036854775808)]
$string_read_raw_truth(S_capture,porigin_left,PFLOAT 9223372036854775808)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PFLOAT 9223372036854775808)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_power_negative = PORIGIN n_unit pcpath_power_negative
porigin_power_zero = PORIGIN n_unit pcpath_power_zero
porigin_power_three = PORIGIN n_unit pcpath_power_three
S_budget_power = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
$string_read_raw_truth(S_budget_power,porigin_left,PFLOAT 9223372036854775808)
$string_read_raw_known_base(S_budget_power,porigin_base,pvalue_base)
S_shorthand_power = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprBinaryOpPow expression_power_negative expression_power_three metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_power,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_power,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own_bits', 'pcpath_left', 'PFLOAT 0'), ('own_tag', 'pcpath_left', 'PINT 0'),
            ('negative_bits', 'pcpath_power_negative', 'PFLOAT 0'),
            ('zero_bits', 'pcpath_power_zero', 'PFLOAT 9223372036854775808'),
            ('three_tag', 'pcpath_power_three', 'PFLOAT 4613937818241073152')):
        own = value if label.startswith('own') else 'PFLOAT 9223372036854775808'
        checks += [f'S_bad_power_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_power_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_power_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('negative', 'pcpath_power_negative', 'NExprUnaryMinus expression_power_zero eps'),
            ('zero', 'pcpath_power_zero', 'NScalarFloat (FLOAT text_power_zero) eps'),
            ('three', 'pcpath_power_three', 'NScalarInt (INTEGER 3) eps')):
        checks += [f'S_bad_power_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_power_{label}_source,porigin_left,PFLOAT 9223372036854775808)',
                   f'~$string_read_raw_known_base(S_bad_power_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_bad_power_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_power_negative 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_power_code,porigin_left,PFLOAT 9223372036854775808)
~$string_read_raw_known_base(S_bad_power_code,porigin_base,pvalue_base)
''')

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        value = str(i) if i >= 0 else f'$({i})'
        return f'NScalarInt (INTEGER {value})', f'PINT {value}'
    def floating(bits):
        return f'NScalarFloat (FLOAT "{bits:016x}")', f'PFLOAT {bits}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    false, null = constant('false', 'PBOOL false'), constant('null', 'PNULL')
    one, two, zero, negative_zero = floating(4607182418800017408), floating(4611686018427387904), floating(0), floating(9223372036854775808)
    positive = ('Pow', 'PFLOAT 4607182418800017408', string(b'2.0'), false)
    negative = ('Pow', 'PFLOAT 9223372036854775808', ('UnaryMinus', 'PFLOAT 9223372036854775808', zero), integer(3))
    matrices = [
        ('source', negative, True), ('positive_source', positive, True),
        ('null_exponent', ('Pow', 'PFLOAT 4607182418800017408', two, null), True),
        ('integer_zero_exponent', ('Pow', 'PFLOAT 4607182418800017408', string(b'2.0'), integer(0)), True),
        ('positive_zero', ('Pow', 'PFLOAT 0', zero, integer(3)), True),
        ('negative_zero_even', ('Pow', 'PFLOAT 0', negative_zero, integer(2)), True),
        ('integer_zero_float_exponent', ('Pow', 'PFLOAT 0', integer(0), floating(4609434218613702656)), True),
        ('null_base', ('Pow', 'PFLOAT 0', null, string(b'2.0')), True),
        ('false_base', ('Pow', 'PFLOAT 0', false, floating(4609434218613702656)), True),
        ('unary_parent', ('UnaryMinus', 'PFLOAT 13830554455654793216', positive), True),
        ('arithmetic_parent', ('Plus', 'PFLOAT 4607182418800017408', negative, one), True),
        ('comparison_parent', ('Equal', 'PBOOL true', negative, integer(0)), True),
        ('short_parent', ('LogicalOr', 'PBOOL true', negative, string(b'word')), True),
        ('integer_prior', ('Pow', 'PINT 8', integer(2), integer(3)), True),
        ('wrong_result_bits', ('Pow', 'PFLOAT 0', negative_zero, integer(3)), False),
        ('wrong_result_tag', ('Pow', 'PINT 0', negative_zero, integer(3)), False),
        ('integer_float_forgery', ('Pow', 'PFLOAT 4620693217682128896', integer(2), integer(3)), False),
        ('general', ('Pow', 'PFLOAT 4620693217682128896', two, integer(3)), False),
        ('nan_child', ('Pow', 'PFLOAT 4607182418800017408', floating(9221120237041090560), integer(0)), False),
        ('infinity_child', ('Pow', 'PFLOAT 4607182418800017408', floating(9218868437227405312), integer(0)), False),
        ('nonfinite_result', ('Pow', 'PFLOAT 9218868437227405312', zero, integer(-1)), False),
        ('deprecated_finite_forgery', ('Pow', 'PFLOAT 0', zero, integer(-1)), False),
        ('leading_string', ('Pow', 'PFLOAT 4607182418800017408', string(b'2.0x'), false), False),
        ('nonnumeric_string', ('Pow', 'PFLOAT 4607182418800017408', string(b'word'), false), False),
        ('forged_child', ('Pow', 'PFLOAT 4607182418800017408', ('NScalarString (BYTES "Mi4w")', 'PFLOAT 4611686018427387904'), false), False),
        ('float_not_unfolded', ('BooleanNot', 'PBOOL true', negative), False),
    ]
    for label, tree, accepted in matrices:
        projected = _projection('completed_power_' + label, tree, accepted)
        if accepted and tree[1] in ('PFLOAT 0', 'PFLOAT 9223372036854775808'):
            assert projected[-1].endswith(',porigin_base,pvalue_wrong)')
            projected[-1] = projected[-1].replace(',porigin_base,pvalue_wrong)', ',porigin_base,pvalue_base)')
        checks += projected
    checks += lines(r'''
$power_prepare(NFLOAT 4611686018427387904,NINT 3) = POWERGENERAL n_factor_power n_x_power n_y_power n_sign_power false
S_budget_general_power = S_sign_completed_power_general[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 4620693217682128896)]
~$string_read_raw_truth(S_budget_general_power,porigin_left,PFLOAT 4620693217682128896)
S_budget_deprecated_power = S_sign_completed_power_deprecated_finite_forgery[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT 0)]
~$string_read_raw_truth(S_budget_deprecated_power,porigin_left,PFLOAT 0)
S_masked_deprecated_power = S_sign_completed_power_deprecated_finite_forgery[.REPORTING = 0]
~$string_read_raw_truth(S_masked_deprecated_power,porigin_left,PFLOAT 0)
S_masked_leading_power = S_sign_completed_power_leading_string[.REPORTING = 0]
~$string_read_raw_truth(S_masked_leading_power,porigin_left,PFLOAT 4607182418800017408)
S_masked_nan_power = S_sign_completed_power_nan_child[.REPORTING = 0]
~$string_read_raw_truth(S_masked_nan_power,porigin_left,PFLOAT 4607182418800017408)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
