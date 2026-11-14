"""Folded non-FLOAT NOT certifies a selected full-ternary base before a Warning."""
import base64

from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 1) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary (NExprBooleanNot (NScalarInt (INTEGER 0) metadata_leaf) metadata_cond)')
    body = body.replace('$compiled_read(S_capture,porigin_cond) = (PINT 1)',
                        '$compiled_read(S_capture,porigin_cond) = (PBOOL true)')
    body = body.replace('$truth(S_capture,PINT 1)', '$truth(S_capture,PBOOL true)')
    body = body.replace('pvalue_condition = PINT 1', 'pvalue_condition = PBOOL true')
    checks = lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBooleanNot (NScalarInt (INTEGER 0) metadata_leaf) metadata_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_leaf)
porigin_leaf = PORIGIN n_unit pcpath_leaf
$origin_node(S_capture.SOURCES,porigin_leaf) = (NScalarInt (INTEGER 0) metadata_leaf)
$compiled_read(S_capture,porigin_leaf) = (PINT 0)
$string_read_raw_truth(S_capture,porigin_leaf,PINT 0)
$truth_value(S_capture,PINT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_truth(S_capture,porigin_cond,PBOOL true)
~$string_read_raw_truth(S_capture,porigin_cond,PBOOL false)
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
expression_true = NScalarString (BYTES text_true) metadata_true
expression_false = NScalarString (BYTES text_false) metadata_false
S_budget = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget,porigin_cond,PBOOL true)
$string_read_raw_known_base(S_budget,porigin_base,pkeyread.BASE)
''')
    for label, node, value, truth, name in (
            ('one','NScalarInt (INTEGER 1) metadata_leaf','PINT 1',True,None),
            ('false','NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_leaf) metadata_leaf','PBOOL false',False,'false'),
            ('true','NExprConstFetch (NName (BYTES "VHJ1RQ==") metadata_leaf) metadata_leaf','PBOOL true',True,'TruE'),
            ('null','NExprConstFetch (NName (BYTES "bnVsbA==") metadata_leaf) metadata_leaf','PNULL',False,'null'),
            ('empty','NScalarString (BYTES "") metadata_leaf','PSTRING eps',False,None),
            ('zero_text','NScalarString (BYTES "MA==") metadata_leaf','PSTRING ([48])',False,None),
            ('truthy_text','NScalarString (BYTES "eA==") metadata_leaf','PSTRING ([120])',True,None),
            ('nul_text','NScalarString (BYTES "eAA=") metadata_leaf','PSTRING ([120,0])',True,None)):
        name_occurrence = ''
        if name is not None:
            encoded = base64.b64encode(name.encode()).decode()
            name_occurrence = f'(PCOCCURRENCE (pcpath_leaf ++ [PCFIELD 0]) (NName (BYTES "{encoded}") metadata_leaf)) :: '
        result = str(not truth).lower()
        selected = 'pkeyread.BASE' if not truth else 'PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))'
        checks += lines(f'''
expression_leaf_{label} = {node}
expression_not_{label} = NExprBooleanNot expression_leaf_{label} metadata_cond
expression_base_{label} = NExprTernary expression_not_{label} expression_true expression_false metadata
S_leaf_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}) :: (PCOCCURRENCE pcpath_cond expression_not_{label}) :: (PCOCCURRENCE pcpath_leaf expression_leaf_{label}) :: {name_occurrence}pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL {result})) :: (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]
$string_read_raw_truth(S_leaf_{label},porigin_leaf,{value})
$truth_value(S_leaf_{label},{value},0) = S_leaf_{label}[.RESULT = KNOWN (PBOOL {str(truth).lower()})]
$string_read_raw_truth(S_leaf_{label},porigin_cond,PBOOL {result})
$string_read_raw_known_base(S_leaf_{label},porigin_base,{selected})
''')
    # FLOAT remains emitted even when its truth conversion would be quiet.
    checks += lines(r'''
expression_float = NScalarFloat (FLOAT "3ff0000000000000") metadata_leaf
expression_not_float = NExprBooleanNot expression_float metadata_cond
expression_base_float = NExprTernary expression_not_float expression_true expression_false metadata
S_float_forged = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_float) :: (PCOCCURRENCE pcpath_cond expression_not_float) :: (PCOCCURRENCE pcpath_leaf expression_float) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL false)) :: (PCONSTANT pcpath_leaf (PFLOAT 4607182418800017408)) :: ppool.CONSTANTS]]]
$compiled_read(S_float_forged,porigin_cond) = (PBOOL false)
$string_read_raw_truth(S_float_forged,porigin_leaf,PFLOAT 4607182418800017408)
$truth_value(S_float_forged,PFLOAT 4607182418800017408,0) = S_float_forged[.RESULT = KNOWN (PBOOL true)]
~$string_read_raw_truth(S_float_forged,porigin_cond,PBOOL false)
~$string_read_raw_known_base(S_float_forged,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_float_forged,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_float_emitted = S_float_forged[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 12 false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_float_emitted,porigin_cond) = eps
~$string_read_raw_truth(S_float_emitted,porigin_cond,PBOOL false)
$string_read_runtime_value(S_float_emitted,porigin_cond) = (PBOOL false)
~$string_read_raw_known_base(S_float_emitted,porigin_base,pkeyread.BASE)
''')
    for label, update in (
            ('result','[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL false)) :: ppool.CONSTANTS]]]'),
            ('type','[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PINT 1)) :: ppool.CONSTANTS]]]'),
            ('leaf','[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT 1)) :: ppool.CONSTANTS]]]'),
            ('source','[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_leaf (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]')):
        checks += [f'S_bad_{label} = S_capture{update}',
                   f'~$string_read_raw_truth(S_bad_{label},porigin_cond,PBOOL true)',
                   f'~$string_read_raw_known_base(S_bad_{label},porigin_base,pkeyread.BASE)',
                   f'$string_read_plan(S_bad_{label}) = eps']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
