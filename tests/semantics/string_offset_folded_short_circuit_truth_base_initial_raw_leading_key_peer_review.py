"""Quiet short circuits retain the selected base and frozen reference-key offset."""

import base64

from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import _projection
from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpLogicalAnd expression_short_and expression_short_skip metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_left) = (PINT 0)', '$compiled_read(S_capture,porigin_left) = (PBOOL false)')
    body = body.replace('~$truth(S_capture,PINT 0)', '~$truth(S_capture,PBOOL false)')
    old_wrong = 'S_wrong_left = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: ppool.CONSTANTS]]]'
    assert body.count(old_wrong) == 1
    body = body.replace(old_wrong, old_wrong.replace('PBOOL false', 'PBOOL true'))
    early = lines(r'''
expression_short_and = NExprBinaryOpBooleanAnd expression_short_or expression_short_false metadata_short_and
expression_short_or = NExprBinaryOpLogicalOr expression_short_zero expression_short_negative metadata_short_or
expression_short_negative = NExprUnaryMinus expression_short_zero_string metadata_short_negative
expression_short_zero = NScalarString (BYTES text_short_zero) metadata_short_zero
expression_short_zero_string = NScalarString (BYTES text_short_zero_string) metadata_short_zero_string
expression_short_false = NExprConstFetch (NName (BYTES text_short_false) metadata_short_false_name) metadata_short_false
expression_short_skip = NExprConstFetch (NName (BYTES text_short_skip) metadata_short_skip_name) metadata_short_skip
$base64(text_short_zero) = $ptascii("0")
$base64(text_short_zero_string) = $ptascii("0.0")
$ptlc($base64(text_short_false)) = $ptascii("false")
$base64(text_short_skip) = $ptascii("NEVER_EVALUATED_B")
''')
    children = (
        ('left', 0, 'and', 'PBOOL false'),
        ('short_and', 0, 'or', 'PBOOL false'),
        ('short_or', 0, 'zero', 'PSTRING ($ptascii("0"))'),
        ('short_or', 1, 'negative', 'PFLOAT 9223372036854775808'),
        ('short_negative', 0, 'zero_string', 'PSTRING ($ptascii("0.0"))'))
    for parent, field, child, value in children:
        early += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_short_{child})',
                  f'$origin_node(S_capture.SOURCES,porigin_short_{child}) = (expression_short_{child})',
                  f'$compiled_read(S_capture,porigin_short_{child}) = ({value})',
                  f'$string_read_raw_truth(S_capture,porigin_short_{child},{value})']
    early += lines(r'''
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_short_skip)
$origin_node(S_capture.SOURCES,porigin_short_skip) = (expression_short_skip)
$compiled_read(S_capture,porigin_short_skip) = eps
$origin_child((porigin_short_and),[PCFIELD 1]) = (porigin_short_false)
$origin_node(S_capture.SOURCES,porigin_short_false) = (expression_short_false)
$truth_value(S_capture,PSTRING ($ptascii("0")),0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$truth_value(S_capture[.RESULT = KNOWN (PBOOL false)],PFLOAT 9223372036854775808,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_truth(S_capture,porigin_left,PBOOL false)
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PBOOL false)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + check + '\n' for check in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_short_skip = PORIGIN n_unit pcpath_short_skip
porigin_short_false = PORIGIN n_unit pcpath_short_false
S_budget_short = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
$string_read_raw_truth(S_budget_short,porigin_left,PBOOL false)
$string_read_raw_known_base(S_budget_short,porigin_base,pvalue_base)
S_shorthand_short = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprBinaryOpLogicalAnd expression_short_and expression_short_skip metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_short,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_short,porigin_base,pvalue_wrong)
''')
    for _, _, child, _ in children:
        checks.append(f'porigin_short_{child} = PORIGIN n_unit pcpath_short_{child}')
    for label, path, value in (
            ('own', 'pcpath_left', 'PBOOL true'), ('own_tag', 'pcpath_left', 'PINT 0'),
            ('and', 'pcpath_short_and', 'PBOOL true'), ('or', 'pcpath_short_or', 'PBOOL true'),
            ('negative', 'pcpath_short_negative', 'PFLOAT 0'),
            ('zero_string', 'pcpath_short_zero_string', 'PSTRING ($ptascii("0"))')):
        own = value if label in ('own', 'own_tag') else 'PBOOL false'
        checks += [f'S_bad_short_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_short_{label},porigin_left,{own})',
                   f'~$string_read_raw_known_base(S_bad_short_{label},porigin_base,pvalue_base)']
    for label, path, node in (
            ('and', 'pcpath_short_and', 'NExprBinaryOpBooleanAnd expression_short_or expression_short_false eps'),
            ('negative', 'pcpath_short_negative', 'NExprUnaryMinus expression_short_zero_string eps'),
            ('skipped', 'pcpath_short_skip', 'NExprConstFetch (NName (BYTES text_short_skip) metadata_short_skip_name) eps'),
            ('false', 'pcpath_short_false', 'NExprConstFetch (NName (BYTES text_short_false) metadata_short_false_name) eps')):
        checks += [f'S_bad_short_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_short_{label}_source,porigin_left,PBOOL false)',
                   f'~$string_read_raw_known_base(S_bad_short_{label}_source,porigin_base,pvalue_base)']
    checks += lines(r'''
S_bad_short_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_short_negative 18 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_short_code,porigin_left,PBOOL false)
~$string_read_raw_known_base(S_bad_short_code,porigin_base,pvalue_base)
''')

    def string(raw):
        return 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '")', 'PSTRING ([' + ','.join(map(str, raw)) + '])'
    def integer(i):
        return f'NScalarInt (INTEGER {i})', f'PINT {i}'
    def floating(bits):
        return f'NScalarFloat (FLOAT "{bits:016x}")', f'PFLOAT {bits}'
    def constant(name, value):
        return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") metadata_cond)', value
    true, false, null = constant('true', 'PBOOL true'), constant('false', 'PBOOL false'), constant('null', 'PNULL')
    unknown = constant('NEVER_EVALUATED_B', 'PNULL')
    one, zero, negative_zero = floating(4607182418800017408), floating(0), floating(9223372036854775808)
    nan, infinity = floating(9221120237041090560), floating(9218868437227405312)
    bad_division = ('Div', 'PINT 1', integer(1), integer(0))
    nested_false = ('LogicalOr', 'PBOOL false', string(b'0'), ('UnaryMinus', 'PFLOAT 9223372036854775808', string(b'0.0')))
    matrices = []
    for form, is_or in (('BooleanOr', True), ('LogicalOr', True), ('BooleanAnd', False), ('LogicalAnd', False)):
        decisive, other = (true, false) if is_or else (false, true)
        result = 'PBOOL true' if is_or else 'PBOOL false'
        matrices += [
            (form + '_decisive', (form, result, decisive, unknown), True),
            (form + '_rhs_true', (form, 'PBOOL true', other, true), True),
            (form + '_rhs_false', (form, 'PBOOL false', other, false), True),
            (form + '_missing_demanded', (form, 'PBOOL false', other, unknown), False),
            (form + '_wrong_result', (form, 'PBOOL false' if is_or else 'PBOOL true', decisive, unknown), False)]
    matrices += [
        ('float_decisive', ('BooleanOr', 'PBOOL true', one, unknown), True),
        ('float_zero', ('LogicalOr', 'PBOOL true', zero, string(b'word')), True),
        ('float_negative_zero', ('BooleanAnd', 'PBOOL false', negative_zero, unknown), True),
        ('float_subnormal', ('LogicalAnd', 'PBOOL true', floating(1), true), True),
        ('null_left', ('BooleanOr', 'PBOOL true', null, one), True),
        ('integer_left', ('LogicalAnd', 'PBOOL false', integer(0), unknown), True),
        ('string_empty', ('LogicalOr', 'PBOOL false', string(b''), negative_zero), True),
        ('string_zero', ('BooleanOr', 'PBOOL true', string(b'0'), true), True),
        ('nested', ('LogicalAnd', 'PBOOL false', ('BooleanAnd', 'PBOOL false', nested_false, false), unknown), True),
        ('xor_child', ('BooleanAnd', 'PBOOL true', ('LogicalXor', 'PBOOL true', one, false), true), True),
        ('not_parent', ('BooleanNot', 'PBOOL true', ('LogicalAnd', 'PBOOL false', false, unknown)), True),
        ('skip_division', ('LogicalOr', 'PBOOL true', true, bad_division), True),
        ('skip_nan', ('BooleanOr', 'PBOOL true', true, nan), True),
        ('skip_infinity', ('LogicalAnd', 'PBOOL false', false, infinity), True),
        ('nan_left', ('LogicalOr', 'PBOOL true', nan, false), False),
        ('nan_right', ('BooleanOr', 'PBOOL true', false, nan), False),
        ('infinite_left', ('LogicalAnd', 'PBOOL true', infinity, true), False),
        ('infinite_right', ('BooleanAnd', 'PBOOL true', true, infinity), False),
        ('cached_left', ('BooleanOr', 'PBOOL true', bad_division, unknown), False),
        ('cached_right', ('LogicalAnd', 'PBOOL true', true, bad_division), False),
        ('wrong_tag', ('BooleanOr', 'PINT 1', true, unknown), False),
    ]
    for label, tree, accepted in matrices:
        checks += _projection('short_' + label, tree, accepted)
    for form, left, result, accepted in (
            ('BooleanOr', 'true', 'true', True), ('LogicalOr', 'false', 'false', False),
            ('BooleanAnd', 'false', 'false', True), ('LogicalAnd', 'true', 'false', False)):
        label = 'short_' + form + ('_decisive' if accepted else '_missing_demanded')
        state = 'S_short_no_rhs_' + form
        checks += [f'{state} = S_sign_{label}[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL {result})) :: (PCONSTANT (pcpath_left ++ [PCFIELD 0]) (PBOOL {left})) :: ppool.CONSTANTS]]]',
                   f'$compiled_read({state},PORIGIN n_unit (pcpath_left ++ [PCFIELD 1])) = eps',
                   f'{"" if accepted else "~"}$string_read_raw_truth({state},porigin_left,PBOOL {result})']
    checks += lines(r'''
S_budget_cached_short_left = S_sign_short_cached_left[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
~$string_read_raw_truth(S_budget_cached_short_left,porigin_left,PBOOL true)
S_budget_cached_short_right = S_sign_short_cached_right[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL true)]
~$string_read_raw_truth(S_budget_cached_short_right,porigin_left,PBOOL true)
S_masked_short_nan_left = S_sign_short_nan_left[.REPORTING = 0]
~$string_read_raw_truth(S_masked_short_nan_left,porigin_left,PBOOL true)
S_masked_short_nan_right = S_sign_short_nan_right[.REPORTING = 0]
~$string_read_raw_truth(S_masked_short_nan_right,porigin_left,PBOOL true)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
