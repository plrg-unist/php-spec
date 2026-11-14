"""A quiet Boolean sign retains typed truth and a falsey selected raw-key base."""

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprUnaryPlus expression_special_child metadata_cond)')
    arms = '(NScalarString (BYTES text_true) metadata_true) (NScalarString (BYTES text_false) metadata_false)'
    assert body.count(arms) == 1
    body = body.replace(arms, '(NScalarString (BYTES text_false) metadata_false) (NScalarString (BYTES text_true) metadata_true)')
    body = body.replace('PCFIELD 1', 'PCFIELD SELECTED').replace('PCFIELD 2', 'PCFIELD 1').replace('PCFIELD SELECTED', 'PCFIELD 2')
    body = body.replace('PINT 1', 'PINT 0')
    truth = '  -- if $truth(S_capture,PINT 0)\n'
    assert body.count(truth) == 1
    body = body.replace(truth, truth.replace('if $truth', 'if ~$truth'))
    wrong = '(PCONSTANT (pcpath_base ++ [PCFIELD 0]) (PINT 0))'
    assert body.count(wrong) == 1
    body = body.replace(wrong, wrong.replace('PINT 0', 'PINT 1'))
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprUnaryPlus expression_special_child metadata_cond)
expression_special_child = NExprConstFetch (NName (BYTES text_special_child) metadata_special_name) metadata_special_child
$ptlc($base64(text_special_child)) = $ptascii("false")
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_special_child)
$origin_node(S_capture.SOURCES,porigin_special_child) = (expression_special_child)
$compiled_read(S_capture,porigin_special_child) = (PBOOL false)
$origin_child((porigin_special_child),[PCFIELD 0]) = (porigin_special_name)
$origin_node(S_capture.SOURCES,porigin_special_name) = (NName (BYTES text_special_child) metadata_special_name)
$string_read_raw_truth(S_capture,porigin_special_child,PBOOL false)
$coerce_number(PBOOL false) = COERCED (NINT 0) false
$unary_apply(S_capture,POSITIVE,PBOOL false,0) = S_capture[.RESULT = KNOWN (PINT 0)]
~$string_read_raw_unary_integer(S_capture,porigin_cond,0)
$string_read_raw_truth(S_capture,porigin_cond,PINT 0)
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
porigin_special_child = PORIGIN n_unit pcpath_special_child
porigin_special_name = PORIGIN n_unit pcpath_special_name
S_budget_special = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]
$string_read_raw_truth(S_budget_special,porigin_cond,PINT 0)
$string_read_raw_known_base(S_budget_special,porigin_base,pkeyread.BASE)
''')
    for label, path, value in (
            ('own', 'pcpath_cond', 'PINT 1'),
            ('child_null', 'pcpath_special_child', 'PNULL'),
            ('child_true', 'pcpath_special_child', 'PBOOL true'),
            ('child_int', 'pcpath_special_child', 'PINT 0'),
            ('child_float', 'pcpath_special_child', 'PFLOAT 0')):
        own = value if label == 'own' else 'PINT 0'
        checks += [f'S_bad_special_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_bad_special_{label},porigin_cond,{own})',
                   f'~$string_read_raw_known_base(S_bad_special_{label},porigin_base,pkeyread.BASE)']
    for label, path, node in (
            ('child', 'pcpath_special_child', 'NExprConstFetch (NName (BYTES text_special_child) metadata_special_name) eps'),
            ('name', 'pcpath_special_name', 'NName (BYTES text_special_child) eps'),
            ('fully_qualified', 'pcpath_special_name', 'NNameFullyQualified (BYTES text_special_child) metadata_special_name')):
        checks += [f'S_bad_special_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_truth(S_bad_special_{label}_source,porigin_cond,PINT 0)',
                   f'~$string_read_raw_known_base(S_bad_special_{label}_source,porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_bad_special_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_special_child 12 false) :: pcode.EXPRESSIONS]]]
~$string_read_raw_truth(S_bad_special_code,porigin_cond,PINT 0)
S_bad_special_own_bool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL false)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_bad_special_own_bool,porigin_cond,PBOOL false)
S_bad_special_own_float = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PFLOAT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_bad_special_own_float,porigin_cond,PFLOAT 0)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
