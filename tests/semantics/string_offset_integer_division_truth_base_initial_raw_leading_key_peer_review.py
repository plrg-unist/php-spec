"""Exact integer division preserves the false arm across raw-key reference rebinding."""

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpDiv expression_numerator expression_denominator metadata_cond)')
    early = lines(r'''
$origin_node(S_capture.SOURCES,porigin_left) = (NExprBinaryOpDiv expression_numerator expression_denominator metadata_cond)
expression_numerator = NScalarInt (INTEGER 0) metadata_numerator
expression_denominator = NScalarInt (INTEGER 2) metadata_denominator
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_numerator)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_denominator)
$origin_node(S_capture.SOURCES,porigin_numerator) = (expression_numerator)
$origin_node(S_capture.SOURCES,porigin_denominator) = (expression_denominator)
$compiled_read(S_capture,porigin_numerator) = (PINT 0)
$compiled_read(S_capture,porigin_denominator) = (PINT 2)
$string_read_raw_unary_integer(S_capture,porigin_left,0)
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
$binary_apply(S_capture,DIVIDE,PINT 0,PINT 2,0) = S_capture[.RESULT = KNOWN (PINT 0)]
''')
    anchor = '  -- if $compiled_read(S_capture,porigin_left) = (PINT 0)\n'
    assert body.count(anchor) == 1
    body = body.replace(anchor, ''.join('  -- if ' + x + '\n' for x in early) + anchor)
    checks = lines(r'''
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_numerator = PORIGIN n_unit pcpath_numerator
porigin_denominator = PORIGIN n_unit pcpath_denominator
S_budget_division = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget_division,porigin_left,PINT 0)
$string_read_raw_known_base(S_budget_division,porigin_base,pvalue_base)
S_precision_division = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_precision_division,porigin_left,PINT 0)
$string_read_raw_known_base(S_precision_division,porigin_base,pvalue_base)
S_shorthand_division = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprTernary (NExprBinaryOpDiv expression_numerator expression_denominator metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)) :: pcunit.OCCURRENCES]]]
$string_read_raw_known_base(S_shorthand_division,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand_division,porigin_base,pvalue_wrong)
''')
    for label, path, value in (
            ('own_type', 'pcpath_left', 'PFLOAT 0'),
            ('numerator_value', 'pcpath_numerator', 'PINT 2'),
            ('denominator_value', 'pcpath_denominator', 'PINT 0'),
            ('numerator_type', 'pcpath_numerator', 'PFLOAT 0'),
            ('denominator_type', 'pcpath_denominator', 'PFLOAT 4611686018427387904')):
        checks += lines(f'''
S_pool_{label}_division = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_pool_{label}_division,porigin_left,{value if label == 'own_type' else 'PINT 0'})
~$string_read_raw_known_base(S_pool_{label}_division,porigin_base,pvalue_base)
''')
    for label, path, node in (
            ('numerator_metadata', 'pcpath_numerator', 'NScalarInt (INTEGER 0) eps'),
            ('denominator_metadata', 'pcpath_denominator', 'NScalarInt (INTEGER 2) eps'),
            ('numerator_position', 'pcpath_numerator', 'expression_denominator'),
            ('denominator_position', 'pcpath_denominator', 'expression_numerator')):
        checks += lines(f'''
S_source_{label}_division = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_source_{label}_division,porigin_left,PINT 0)
~$string_read_raw_known_base(S_source_{label}_division,porigin_base,pvalue_base)
''')
    # Raw negative and out-of-range leaves here are constructed controls, not source credit.
    for label, numerator, denominator, quotient, accepted in (
            ('positive', 6, 3, 2, True),
            ('prior_two_one', 2, 1, 2, True),
            ('prior_four_two', 4, 2, 2, True),
            ('negative', 6, -3, -2, True),
            ('zero_negative_denominator', 0, -2, 0, True),
            ('min_identity', -9223372036854775808, 1, -9223372036854775808, True),
            ('min_same', -9223372036854775808, -9223372036854775808, 1, True),
            ('max_same', 9223372036854775807, 9223372036854775807, 1, True),
            ('division_zero', 0, 0, 0, False),
            ('fraction', 1, 2, 0, False),
            ('overflow', -9223372036854775808, -1, -9223372036854775808, False),
            ('wrong_quotient', 6, 3, 3, False),
            ('child_range', 9223372036854775808, 2, 4611686018427387904, False),
            ('own_range', 9223372036854775808, 1, 9223372036854775808, False)):
        selected = 'pvalue_base' if quotient == 0 else 'pvalue_wrong'
        numerator, denominator, quotient = [str(n) if n >= 0 else f'$({n})'
                                           for n in (numerator, denominator, quotient)]
        checks += lines(f'''
expression_{label}_numerator = NScalarInt (INTEGER {numerator}) metadata_numerator
expression_{label}_denominator = NScalarInt (INTEGER {denominator}) metadata_denominator
expression_{label}_division = NExprBinaryOpDiv expression_{label}_numerator expression_{label}_denominator metadata_cond
expression_{label}_base = NExprTernary expression_{label}_division (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_{label}_division = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_left expression_{label}_division) :: (PCOCCURRENCE pcpath_numerator expression_{label}_numerator) :: (PCOCCURRENCE pcpath_denominator expression_{label}_denominator) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT {quotient})) :: (PCONSTANT pcpath_numerator (PINT {numerator})) :: (PCONSTANT pcpath_denominator (PINT {denominator})) :: ppool.CONSTANTS]]]
$compiled_read(S_{label}_division,porigin_left) = (PINT {quotient})
{'' if accepted else '~'}$string_read_raw_unary_integer(S_{label}_division,porigin_left,{quotient})
{'' if accepted else '~'}$string_read_raw_truth(S_{label}_division,porigin_left,PINT {quotient})
''')
        if accepted:
            checks += [f'$binary_apply(S_{label}_division,DIVIDE,PINT {numerator},PINT {denominator},0) = S_{label}_division[.RESULT = KNOWN (PINT {quotient})]',
                       f'$string_read_raw_known_base(S_{label}_division,porigin_base,{selected})']
        else:
            checks += [f'~$string_read_raw_known_base(S_{label}_division,porigin_base,{value})'
                       for value in ('pvalue_base', 'pvalue_wrong')]
    for label, constructor, numerator, numerator_value, denominator, denominator_value, quotient in (
            ('numeric_string', 'NExprBinaryOpDiv', 'NScalarString (BYTES "MA==")', 'PSTRING ($ptascii("0"))', 'NScalarInt (INTEGER 2)', 'PINT 2', 0),
            ('float_pair', 'NExprBinaryOpDiv', 'NScalarFloat (FLOAT "0000000000000000")', 'PFLOAT 0', 'NScalarFloat (FLOAT "4000000000000000")', 'PFLOAT 4611686018427387904', 0),
            ('power', 'NExprBinaryOpPow', 'NScalarInt (INTEGER 2)', 'PINT 2', 'NScalarInt (INTEGER 1)', 'PINT 1', 2)):
        checks += lines(f'''
expression_{label}_numerator = {numerator} metadata_numerator
expression_{label}_denominator = {denominator} metadata_denominator
expression_{label}_division = {constructor} expression_{label}_numerator expression_{label}_denominator metadata_cond
expression_{label}_base = NExprTernary expression_{label}_division (NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_right) metadata_right) metadata
S_{label}_division = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_left expression_{label}_division) :: (PCOCCURRENCE pcpath_numerator expression_{label}_numerator) :: (PCOCCURRENCE pcpath_denominator expression_{label}_denominator) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT {quotient})) :: (PCONSTANT pcpath_numerator ({numerator_value})) :: (PCONSTANT pcpath_denominator ({denominator_value})) :: ppool.CONSTANTS]]]
$compiled_read(S_{label}_division,porigin_left) = (PINT {quotient})
$string_read_raw_truth(S_{label}_division,porigin_numerator,{numerator_value})
$string_read_raw_truth(S_{label}_division,porigin_denominator,{denominator_value})
~$string_read_raw_unary_integer(S_{label}_division,porigin_left,{quotient})
~$string_read_raw_truth(S_{label}_division,porigin_left,PINT {quotient})
~$string_read_raw_known_base(S_{label}_division,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_{label}_division,porigin_base,pvalue_wrong)
''')
    checks += lines(r'''
$binary_apply(S_fraction_division,DIVIDE,PINT 1,PINT 2,0) = S_fraction_division[.RESULT = KNOWN (PFLOAT 4602678819172646912)]
$binary_apply(S_overflow_division,DIVIDE,PINT $(-9223372036854775808),PINT $(-1),0) = S_overflow_division[.RESULT = KNOWN (PFLOAT 4890909195324358656)]
$origin_child((porigin_numerator),[PCFIELD 0]) = (porigin_not_numerator)
$origin_child((porigin_numerator),[PCFIELD 1]) = (porigin_not_denominator)
porigin_not_numerator = PORIGIN n_unit pcpath_not_numerator
porigin_not_denominator = PORIGIN n_unit pcpath_not_denominator
expression_not_numerator = NScalarInt (INTEGER 6) metadata_numerator
expression_not_denominator = NScalarInt (INTEGER 3) metadata_denominator
expression_not_division = NExprBinaryOpDiv expression_not_numerator expression_not_denominator metadata_numerator
expression_not = NExprBooleanNot expression_not_division metadata_cond
expression_not_base = NExprTernary expression_not ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_not_division = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_not_base) :: (PCOCCURRENCE pcpath_left expression_not) :: (PCOCCURRENCE pcpath_numerator expression_not_division) :: (PCOCCURRENCE pcpath_not_numerator expression_not_numerator) :: (PCOCCURRENCE pcpath_not_denominator expression_not_denominator) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL false)) :: (PCONSTANT pcpath_numerator (PINT 2)) :: (PCONSTANT pcpath_not_numerator (PINT 6)) :: (PCONSTANT pcpath_not_denominator (PINT 3)) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 18 true) :: (CODEEXPR pcpath_numerator 18 true) :: (CODEEXPR pcpath_not_numerator 18 true) :: (CODEEXPR pcpath_not_denominator 18 true) :: pcode.EXPRESSIONS]]]
$string_read_raw_truth(S_not_division,porigin_numerator,PINT 2)
$string_read_raw_truth(S_not_division,porigin_left,PBOOL false)
$string_read_raw_known_base(S_not_division,porigin_base,pvalue_base)
S_not_division.POOLS = [ppool_not]
S_wrong_not_division = S_not_division[.POOLS = [ppool_not[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL true)) :: ppool_not.CONSTANTS]]]
~$string_read_raw_truth(S_wrong_not_division,porigin_left,PBOOL true)
~$string_read_raw_known_base(S_wrong_not_division,porigin_base,pvalue_base)
$origin_child((porigin_not_numerator),[PCFIELD 0]) = (porigin_plus_numerator)
$origin_child((porigin_not_numerator),[PCFIELD 1]) = (porigin_plus_denominator)
porigin_plus_numerator = PORIGIN n_unit pcpath_plus_numerator
porigin_plus_denominator = PORIGIN n_unit pcpath_plus_denominator
expression_signed_division = NExprUnaryPlus expression_not_division metadata_numerator
expression_not_positive = NExprBooleanNot expression_signed_division metadata_cond
expression_not_positive_base = NExprTernary expression_not_positive ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_not_positive_division = S_not_division[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_not_positive_base) :: (PCOCCURRENCE pcpath_left expression_not_positive) :: (PCOCCURRENCE pcpath_numerator expression_signed_division) :: (PCOCCURRENCE pcpath_not_numerator expression_not_division) :: (PCOCCURRENCE pcpath_plus_numerator expression_not_numerator) :: (PCOCCURRENCE pcpath_plus_denominator expression_not_denominator) :: pcunit.OCCURRENCES]]][.POOLS = [ppool_not[.CONSTANTS = (PCONSTANT pcpath_not_numerator (PINT 2)) :: (PCONSTANT pcpath_plus_numerator (PINT 6)) :: (PCONSTANT pcpath_plus_denominator (PINT 3)) :: ppool_not.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_not_numerator 18 true) :: (CODEEXPR pcpath_plus_numerator 18 true) :: (CODEEXPR pcpath_plus_denominator 18 true) :: pcode.EXPRESSIONS]]]
$string_read_raw_unary_integer(S_not_positive_division,porigin_numerator,2)
$string_read_raw_truth(S_not_positive_division,porigin_left,PBOOL false)
$string_read_raw_known_base(S_not_positive_division,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(early) + len(checks), derived + len(checks)
