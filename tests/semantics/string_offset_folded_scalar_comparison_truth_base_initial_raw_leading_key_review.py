"""Typed folded comparisons retain the selected base and frozen raw offset."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpIdentical expression_less_compare expression_equal_compare metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_cond) = (PINT 1)', '$compiled_read(S_capture,porigin_cond) = (PBOOL true)')
    body = body.replace('$truth(S_capture,PINT 1)', '$truth(S_capture,PBOOL true)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpIdentical expression_less_compare expression_equal_compare metadata_cond)
expression_less_compare = NExprBinaryOpSmaller expression_modulo_compare expression_three_compare metadata_less_compare
expression_modulo_compare = NExprBinaryOpMod expression_add_compare expression_modulus_compare metadata_modulo_compare
expression_add_compare = NExprBinaryOpPlus expression_six_compare expression_false_compare metadata_add_compare
expression_equal_compare = NExprBinaryOpEqual expression_digit_compare expression_two_compare metadata_equal_compare
expression_six_compare = NScalarString (BYTES text_six_compare) metadata_six_compare
expression_false_compare = NExprConstFetch (NName (BYTES text_false_compare) metadata_false_name_compare) metadata_false_compare
expression_modulus_compare = NScalarString (BYTES text_modulus_compare) metadata_modulus_compare
expression_three_compare = NScalarInt (INTEGER 3) metadata_three_compare
expression_digit_compare = NScalarString (BYTES text_digit_compare) metadata_digit_compare
expression_two_compare = NScalarInt (INTEGER 2) metadata_two_compare
$base64(text_six_compare) = $ptascii("6")
$ptlc($base64(text_false_compare)) = $ptascii("false")
$base64(text_modulus_compare) = $ptascii("4")
$base64(text_digit_compare) = $ptascii("2")
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for parent, field, child, value in (
            ('cond', 0, 'less', 'PBOOL true'), ('cond', 1, 'equal', 'PBOOL true'),
            ('less_compare', 0, 'modulo', 'PINT 2'), ('less_compare', 1, 'three', 'PINT 3'),
            ('modulo_compare', 0, 'add', 'PINT 6'), ('modulo_compare', 1, 'modulus', 'PSTRING ($ptascii("4"))'),
            ('add_compare', 0, 'six', 'PSTRING ($ptascii("6"))'), ('add_compare', 1, 'false', 'PBOOL false'),
            ('equal_compare', 0, 'digit', 'PSTRING ($ptascii("2"))'), ('equal_compare', 1, 'two', 'PINT 2')):
        checks += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_{child}_compare)',
                   f'$origin_node(S_capture.SOURCES,porigin_{child}_compare) = (expression_{child}_compare)',
                   f'$compiled_read(S_capture,porigin_{child}_compare) = ({value})',
                   f'$string_read_raw_truth(S_capture,porigin_{child}_compare,{value})',
                   f'porigin_{child}_compare = PORIGIN n_unit pcpath_{child}_compare']
    checks += lines(r'''
$origin_child((porigin_false_compare),[PCFIELD 0]) = (porigin_false_name_compare)
$origin_node(S_capture.SOURCES,porigin_false_name_compare) = (NName (BYTES text_false_compare) metadata_false_name_compare)
porigin_false_name_compare = PORIGIN n_unit pcpath_false_name_compare
$binary_apply(S_capture,MODULO,PINT 6,PSTRING ($ptascii("4")),0) = S_capture[.RESULT = KNOWN (PINT 2)]
$binary_apply(S_capture,LESS,PINT 2,PINT 3,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$binary_apply(S_capture,EQUAL,PSTRING ($ptascii("2")),PINT 2,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$binary_apply(S_capture,IDENTICAL,PBOOL true,PBOOL true,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_raw_truth(S_capture,porigin_cond,PBOOL true)
S_budget_compare = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL false)]
$string_read_raw_truth(S_budget_compare,porigin_cond,PBOOL true)
$string_read_raw_known_base(S_budget_compare,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PBOOL false'), ('left', 'pcpath_less_compare', 'PBOOL false'),
            ('right', 'pcpath_equal_compare', 'PBOOL false'), ('bool_tag', 'pcpath_less_compare', 'PINT 1'),
            ('false_null', 'pcpath_false_compare', 'PNULL'), ('digit_tag', 'pcpath_digit_compare', 'PINT 2'),
            ('modulo', 'pcpath_modulo_compare', 'PINT 1')):
        own = value if label == 'own' else 'PBOOL true'
        checks += [f'S_bad_compare_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_compare_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_compare_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('less', 'pcpath_less_compare', 'NExprBinaryOpSmaller expression_modulo_compare expression_three_compare eps'),
            ('equal', 'pcpath_equal_compare', 'NExprBinaryOpEqual expression_digit_compare expression_two_compare eps'),
            ('name', 'pcpath_false_name_compare', 'NName (BYTES text_false_compare) eps')):
        checks += [f'S_bad_compare_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_compare_{label}_source,porigin_cond,PBOOL true)',
                   f'~$string_read_raw_known_base(S_bad_compare_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_bad_compare_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_equal_compare 12 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_compare_code,porigin_cond,PBOOL true)
~$string_read_raw_known_base(S_bad_compare_code,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
