"""Quiet integer complements preserve actual scalar arithmetic and frozen raw keys."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBitwiseNot expression_child_bitnot metadata_cond)')
    body = body.replace('PINT 1', 'PINT $(-4)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBitwiseNot expression_child_bitnot metadata_cond)
expression_child_bitnot = NExprBinaryOpMul expression_sum_bitnot expression_factor_bitnot metadata_child_bitnot
expression_sum_bitnot = NExprBinaryOpPlus expression_string_bitnot expression_true_bitnot metadata_sum_bitnot
expression_string_bitnot = NScalarString (BYTES text_string_bitnot) metadata_string_bitnot
expression_true_bitnot = NExprConstFetch (NName (BYTES text_true_bitnot) metadata_true_name_bitnot) metadata_true_bitnot
expression_factor_bitnot = NScalarString (BYTES text_factor_bitnot) metadata_factor_bitnot
$base64(text_string_bitnot) = $ptascii("2")
$ptlc($base64(text_true_bitnot)) = $ptascii("true")
$base64(text_factor_bitnot) = $ptascii("1")
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_child_bitnot)
$origin_child((porigin_child_bitnot),[PCFIELD 0]) = (porigin_sum_bitnot)
$origin_child((porigin_child_bitnot),[PCFIELD 1]) = (porigin_factor_bitnot)
$origin_child((porigin_sum_bitnot),[PCFIELD 0]) = (porigin_string_bitnot)
$origin_child((porigin_sum_bitnot),[PCFIELD 1]) = (porigin_true_bitnot)
$origin_child((porigin_true_bitnot),[PCFIELD 0]) = (porigin_true_name_bitnot)
$origin_node(S_capture.SOURCES,porigin_true_name_bitnot) = (NName (BYTES text_true_bitnot) metadata_true_name_bitnot)
''')
    for name, value in (('child', 'PINT 3'), ('sum', 'PINT 3'),
                        ('string', 'PSTRING ($ptascii("2"))'),
                        ('true', 'PBOOL true'), ('factor', 'PSTRING ($ptascii("1"))')):
        checks += [f'$origin_node(S_capture.SOURCES,porigin_{name}_bitnot) = (expression_{name}_bitnot)',
                   f'$compiled_read(S_capture,porigin_{name}_bitnot) = ({value})',
                   f'$string_read_raw_truth(S_capture,porigin_{name}_bitnot,{value})',
                   f'porigin_{name}_bitnot = PORIGIN n_unit pcpath_{name}_bitnot']
    checks += lines(r'''
~$string_read_raw_unary_integer(S_capture,porigin_child_bitnot,3)
~$string_read_raw_unary_integer(S_capture,porigin_cond,$(-4))
$bitnot_value(S_capture,PINT 3,0) = S_capture[.RESULT = KNOWN (PINT $(-4))]
$string_read_raw_truth(S_capture,porigin_cond,PINT $(-4))
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_true_name_bitnot = PORIGIN n_unit pcpath_true_name_bitnot
S_budget_bitnot = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
$string_read_raw_truth(S_budget_bitnot,porigin_cond,PINT $(-4))
$string_read_raw_known_base(S_budget_bitnot,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PINT $(-3)'),
            ('child', 'pcpath_child_bitnot', 'PINT 4'),
            ('child_float', 'pcpath_child_bitnot', 'PFLOAT 4613937818241073152'),
            ('child_bool', 'pcpath_child_bitnot', 'PBOOL true'),
            ('child_null', 'pcpath_child_bitnot', 'PNULL'),
            ('sum', 'pcpath_sum_bitnot', 'PINT 4'),
            ('leaf_tag', 'pcpath_true_bitnot', 'PINT 1')):
        own = value if label == 'own' else 'PINT $(-4)'
        checks += [f'S_bad_bitnot_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_bitnot_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_bitnot_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('child', 'pcpath_child_bitnot', 'NExprBinaryOpMul expression_sum_bitnot expression_factor_bitnot eps'),
            ('sum', 'pcpath_sum_bitnot', 'NExprBinaryOpPlus expression_string_bitnot expression_true_bitnot eps'),
            ('name', 'pcpath_true_name_bitnot', 'NName (BYTES text_true_bitnot) eps')):
        checks += [f'S_bad_bitnot_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_bitnot_{label}_source,porigin_cond,PINT $(-4))',
                   f'~$string_read_raw_known_base(S_bad_bitnot_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_bad_bitnot_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_child_bitnot 12 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_bitnot_code,porigin_cond,PINT $(-4))
S_bad_bitnot_own_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_cond (NExprBitwiseNot expression_child_bitnot eps)) :: pcunit.OCCURRENCES]]]
$string_read_raw_truth(S_bad_bitnot_own_source,porigin_cond,PINT $(-4))
~$string_read_raw_known_base(S_bad_bitnot_own_source,porigin_base,pkeyread.BASE)
S_bad_bitnot_own_float = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 13839561654909534208)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_bad_bitnot_own_float,porigin_cond,PFLOAT 13839561654909534208)
S_bad_bitnot_own_bool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL true)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_bad_bitnot_own_bool,porigin_cond,PBOOL true)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
