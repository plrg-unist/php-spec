"""Finite FLOAT comparisons and XOR retain typed values and the frozen raw key."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpLogicalXor expression_greater_boolean expression_identical_boolean metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_cond) = (PINT 1)', '$compiled_read(S_capture,porigin_cond) = (PBOOL true)')
    body = body.replace('$truth(S_capture,PINT 1)', '$truth(S_capture,PBOOL true)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpLogicalXor expression_greater_boolean expression_identical_boolean metadata_cond)
expression_greater_boolean = NExprBinaryOpGreater expression_add_boolean expression_one_boolean metadata_greater_boolean
expression_add_boolean = NExprBinaryOpPlus expression_decimal_boolean expression_false_boolean metadata_add_boolean
expression_identical_boolean = NExprBinaryOpIdentical expression_negative_boolean expression_zero_boolean metadata_identical_boolean
expression_negative_boolean = NExprUnaryMinus expression_zero_string_boolean metadata_negative_boolean
expression_decimal_boolean = NScalarString (BYTES text_decimal_boolean) metadata_decimal_boolean
expression_false_boolean = NExprConstFetch (NName (BYTES text_false_boolean) metadata_false_name_boolean) metadata_false_boolean
expression_one_boolean = NScalarInt (INTEGER 1) metadata_one_boolean
expression_zero_boolean = NScalarInt (INTEGER 0) metadata_zero_boolean
expression_zero_string_boolean = NScalarString (BYTES text_zero_string_boolean) metadata_zero_string_boolean
$base64(text_decimal_boolean) = $ptascii("1.5")
$ptlc($base64(text_false_boolean)) = $ptascii("false")
$base64(text_zero_string_boolean) = $ptascii("0.0")
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for parent, field, child, value in (
            ('cond', 0, 'greater', 'PBOOL true'), ('cond', 1, 'identical', 'PBOOL false'),
            ('greater_boolean', 0, 'add', 'PFLOAT 4609434218613702656'), ('greater_boolean', 1, 'one', 'PINT 1'),
            ('add_boolean', 0, 'decimal', 'PSTRING ($ptascii("1.5"))'), ('add_boolean', 1, 'false', 'PBOOL false'),
            ('identical_boolean', 0, 'negative', 'PFLOAT 9223372036854775808'), ('identical_boolean', 1, 'zero', 'PINT 0'),
            ('negative_boolean', 0, 'zero_string', 'PSTRING ($ptascii("0.0"))')):
        checks += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_{child}_boolean)',
                   f'$origin_node(S_capture.SOURCES,porigin_{child}_boolean) = (expression_{child}_boolean)',
                   f'$compiled_read(S_capture,porigin_{child}_boolean) = ({value})',
                   f'$string_read_raw_truth(S_capture,porigin_{child}_boolean,{value})',
                   f'porigin_{child}_boolean = PORIGIN n_unit pcpath_{child}_boolean']
    checks += lines(r'''
$origin_child((porigin_false_boolean),[PCFIELD 0]) = (porigin_false_name_boolean)
$origin_node(S_capture.SOURCES,porigin_false_name_boolean) = (NName (BYTES text_false_boolean) metadata_false_name_boolean)
porigin_false_name_boolean = PORIGIN n_unit pcpath_false_name_boolean
$binary_apply(S_capture,GREATER,PFLOAT 4609434218613702656,PINT 1,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$binary_apply(S_capture,IDENTICAL,PFLOAT 9223372036854775808,PINT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$binary_apply(S_capture,LOGICALXOR,PBOOL true,PBOOL false,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_raw_truth(S_capture,porigin_cond,PBOOL true)
S_budget_boolean = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL false)]
$string_read_raw_truth(S_budget_boolean,porigin_cond,PBOOL true)
$string_read_raw_known_base(S_budget_boolean,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PBOOL false'), ('greater', 'pcpath_greater_boolean', 'PBOOL false'),
            ('identical', 'pcpath_identical_boolean', 'PBOOL true'), ('float_tag', 'pcpath_add_boolean', 'PINT 1'),
            ('negative_zero_bits', 'pcpath_negative_boolean', 'PFLOAT 0'),
            ('false_null', 'pcpath_false_boolean', 'PNULL'), ('one_float', 'pcpath_one_boolean', 'PFLOAT 4607182418800017408'),
            ('zero_bool', 'pcpath_zero_boolean', 'PBOOL false')):
        own = value if label == 'own' else 'PBOOL true'
        checks += [f'S_bad_boolean_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_boolean_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_boolean_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('greater', 'pcpath_greater_boolean', 'NExprBinaryOpGreater expression_add_boolean expression_one_boolean eps'),
            ('negative', 'pcpath_negative_boolean', 'NExprUnaryMinus expression_zero_string_boolean eps'),
            ('name', 'pcpath_false_name_boolean', 'NName (BYTES text_false_boolean) eps')):
        checks += [f'S_bad_boolean_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_boolean_{label}_source,porigin_cond,PBOOL true)',
                   f'~$string_read_raw_known_base(S_bad_boolean_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_bad_boolean_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_negative_boolean 12 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_boolean_code,porigin_cond,PBOOL true)
~$string_read_raw_known_base(S_bad_boolean_code,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
