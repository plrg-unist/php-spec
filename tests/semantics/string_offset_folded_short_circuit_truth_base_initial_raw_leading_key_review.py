"""Folded short-circuit truth keeps skipped names and the frozen raw offset."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBinaryOpBooleanOr expression_inner_short expression_skip_short metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_cond) = (PINT 1)', '$compiled_read(S_capture,porigin_cond) = (PBOOL true)')
    body = body.replace('$truth(S_capture,PINT 1)', '$truth(S_capture,PBOOL true)')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBinaryOpBooleanOr expression_inner_short expression_skip_short metadata_cond)
expression_inner_short = NExprBinaryOpBooleanOr expression_zero_short expression_and_short metadata_inner_short
expression_and_short = NExprBinaryOpLogicalAnd expression_word_short expression_true_short metadata_and_short
expression_zero_short = NScalarFloat (FLOAT text_zero_short) metadata_zero_short
expression_word_short = NScalarString (BYTES text_word_short) metadata_word_short
expression_true_short = NExprConstFetch (NName (BYTES text_true_short) metadata_true_name_short) metadata_true_short
expression_skip_short = NExprConstFetch (NName (BYTES text_skip_short) metadata_skip_name_short) metadata_skip_short
text_zero_short = "0000000000000000"
$base64(text_word_short) = $ptascii("word")
$ptlc($base64(text_true_short)) = $ptascii("true")
$base64(text_skip_short) = $ptascii("NEVER_EVALUATED_A")
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for parent, field, child, value in (
            ('cond', 0, 'inner', 'PBOOL true'), ('inner_short', 0, 'zero', 'PFLOAT 0'),
            ('inner_short', 1, 'and', 'PBOOL true'), ('and_short', 0, 'word', 'PSTRING ($ptascii("word"))'),
            ('and_short', 1, 'true', 'PBOOL true')):
        checks += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_{child}_short)',
                   f'$origin_node(S_capture.SOURCES,porigin_{child}_short) = (expression_{child}_short)',
                   f'$compiled_read(S_capture,porigin_{child}_short) = ({value})',
                   f'$string_read_raw_truth(S_capture,porigin_{child}_short,{value})',
                   f'porigin_{child}_short = PORIGIN n_unit pcpath_{child}_short']
    checks += lines(r'''
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_skip_short)
$origin_node(S_capture.SOURCES,porigin_skip_short) = (expression_skip_short)
porigin_skip_short = PORIGIN n_unit pcpath_skip_short
$compiled_read(S_capture,porigin_skip_short) = eps
$origin_child((porigin_true_short),[PCFIELD 0]) = (porigin_true_name_short)
$origin_node(S_capture.SOURCES,porigin_true_name_short) = (NName (BYTES text_true_short) metadata_true_name_short)
porigin_true_name_short = PORIGIN n_unit pcpath_true_name_short
$truth_value(S_capture,PFLOAT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$truth_value(S_capture,PSTRING ($ptascii("word")),0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$truth_value(S_capture[.RESULT = KNOWN (PBOOL true)],PBOOL true,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$truth_value(S_capture[.RESULT = KNOWN (PBOOL false)],PBOOL true,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_raw_truth(S_capture,porigin_cond,PBOOL true)
S_budget_short = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL false)]
$string_read_raw_truth(S_budget_short,porigin_cond,PBOOL true)
$string_read_raw_known_base(S_budget_short,porigin_base,pkeyread.BASE)
S_skip_pool_short = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_skip_short (PINT 99)) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_skip_pool_short,porigin_cond,PBOOL true)
$string_read_raw_known_base(S_skip_pool_short,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PBOOL false'), ('inner', 'pcpath_inner_short', 'PBOOL false'),
            ('and', 'pcpath_and_short', 'PBOOL false'), ('word', 'pcpath_word_short', 'PSTRING ($ptascii("0"))'),
            ('true_tag', 'pcpath_true_short', 'PINT 1'), ('zero_bits', 'pcpath_zero_short', 'PFLOAT 9223372036854775808')):
        own = value if label == 'own' else 'PBOOL true'
        checks += [f'S_bad_short_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_short_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_short_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('inner', 'pcpath_inner_short', 'NExprBinaryOpBooleanOr expression_zero_short expression_and_short eps'),
            ('skip', 'pcpath_skip_short', 'NExprConstFetch (NName (BYTES text_skip_short) metadata_skip_name_short) eps'),
            ('name', 'pcpath_true_name_short', 'NName (BYTES text_true_short) eps')):
        checks += [f'S_bad_short_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_short_{label}_source,porigin_cond,PBOOL true)',
                   f'~$string_read_raw_known_base(S_bad_short_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_bad_short_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_and_short 12 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_short_code,porigin_cond,PBOOL true)
~$string_read_raw_known_base(S_bad_short_code,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
