"""A certified zero tree retains its literal base and original reference key."""
import base64

from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_integer
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_integer(program, filename_b64)
    old = 'NExprTernary (NScalarInt (INTEGER 0) metadata_cond)'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprTernary expression_cond')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_left) = (expression_cond)
expression_cond = NExprBinaryOpPlus expression_mul expression_six metadata_cond
expression_mul = NExprBinaryOpMul expression_outer expression_minus metadata_mul
expression_outer = NExprUnaryPlus expression_inner metadata_outer
expression_inner = NExprUnaryPlus expression_text metadata_inner
expression_text = NScalarString (BYTES text_two) metadata_text
expression_minus = NExprUnaryMinus expression_three metadata_minus
expression_three = NScalarInt (INTEGER 3) metadata_three
expression_six = NScalarInt (INTEGER 6) metadata_six
$base64(text_two) = $ptascii("2")
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_mul)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_six)
$origin_child((porigin_mul),[PCFIELD 0]) = (porigin_outer)
$origin_child((porigin_mul),[PCFIELD 1]) = (porigin_minus)
$origin_child((porigin_outer),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_text)
$origin_child((porigin_minus),[PCFIELD 0]) = (porigin_three)
$origin_node(S_capture.SOURCES,porigin_mul) = (expression_mul)
$origin_node(S_capture.SOURCES,porigin_outer) = (expression_outer)
$origin_node(S_capture.SOURCES,porigin_inner) = (expression_inner)
$origin_node(S_capture.SOURCES,porigin_text) = (expression_text)
$origin_node(S_capture.SOURCES,porigin_minus) = (expression_minus)
$origin_node(S_capture.SOURCES,porigin_three) = (expression_three)
$origin_node(S_capture.SOURCES,porigin_six) = (expression_six)
$compiled_read(S_capture,porigin_mul) = (PINT $(-6))
$compiled_read(S_capture,porigin_outer) = (PINT 2)
$compiled_read(S_capture,porigin_inner) = (PINT 2)
$compiled_read(S_capture,porigin_text) = (PSTRING ($ptascii("2")))
$compiled_read(S_capture,porigin_minus) = (PINT $(-3))
$compiled_read(S_capture,porigin_three) = (PINT 3)
$compiled_read(S_capture,porigin_six) = (PINT 6)
$string_read_raw_unary_integer(S_capture,porigin_left,0)
$string_read_raw_truth(S_capture,porigin_left,PINT 0)
$truth_value(S_capture,PINT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
S_capture.SOURCES = [pcunit]
$origin_node(S_capture.SOURCES,porigin_true) = (expression_true)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_false)
porigin_mul = PORIGIN n_unit pcpath_mul
porigin_outer = PORIGIN n_unit pcpath_outer
porigin_text = PORIGIN n_unit pcpath_text
S_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]]
$string_read_raw_known_base(S_precision,porigin_base,pvalue_base)
S_zero_line = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 0 true) :: pcode.EXPRESSIONS]]]
$string_read_raw_known_base(S_zero_line,porigin_base,pvalue_base)
S_budget = S_capture[.COMPLETION = BUDGET]
$truth_value(S_budget,PINT 0,0) = S_budget[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_known_base(S_budget,porigin_base,pvalue_base)
''')
    for label, path, value in (
            ('multiply', 'pcpath_mul', 'PINT $(-5)'),
            ('sign', 'pcpath_outer', 'PINT 3'),
            ('string', 'pcpath_text', 'PSTRING ($ptascii("3"))'),
            ('type', 'pcpath_left', 'PFLOAT 0')):
        checks += lines(f'''
S_tree_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_tree_{label},porigin_left,PINT 0)
~$string_read_raw_known_base(S_tree_{label},porigin_base,pvalue_base)
$string_read_plan(S_tree_{label}) = eps
''')
    for label, path, node in (
            ('condition', 'pcpath_left', 'NExprBinaryOpPlus expression_mul expression_six eps'),
            ('true', 'pcpath_true', 'NScalarString (BYTES text_true) eps'),
            ('false', 'pcpath_right', 'NScalarString (BYTES text_right) eps')):
        checks += lines(f'''
S_detached_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_detached_{label},porigin_base,pvalue_base)
$string_read_plan(S_detached_{label}) = eps
''')
    checks += lines(r'''
$string_read_raw_truth(S_detached_condition,porigin_left,PINT 0)
$compiled_read(S_detached_true,porigin_true) = (PSTRING ($ptascii("XYZ")))
$compiled_string_value(S_detached_true,porigin_true,PSTRING ($ptascii("XYZ"))) = pvalue_wrong
$compiled_read(S_detached_false,porigin_right) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_detached_false,porigin_right,PSTRING ($ptascii("abc"))) = pvalue_base
''')
    # These are local source/pool projections, not additional source executions.
    for label, node, value, valid, truth in (
            ('true', 'NExprConstFetch (NName (BYTES "VHJ1RQ==") metadata_cond) metadata_cond', 'PBOOL true', True, True),
            ('false', 'NExprConstFetch (NName (BYTES "RmFMc0U=") metadata_cond) metadata_cond', 'PBOOL false', True, False),
            ('null', 'NExprConstFetch (NName (BYTES "TnVMbA==") metadata_cond) metadata_cond', 'PNULL', True, False),
            ('qualified_false', 'NExprConstFetch (NNameFullyQualified (BYTES "ZmFsc2U=") metadata_cond) metadata_cond', 'PBOOL false', False, False),
            ('qualified_null', 'NExprConstFetch (NNameFullyQualified (BYTES "bnVsbA==") metadata_cond) metadata_cond', 'PNULL', False, False),
            ('wrong_false', 'NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_cond) metadata_cond', 'PBOOL true', False, True),
            ('minimum', 'NScalarInt (INTEGER $(-9223372036854775808)) metadata_cond', 'PINT $(-9223372036854775808)', True, True),
            ('outside', 'NScalarInt (INTEGER 9223372036854775808) metadata_cond', 'PINT 9223372036854775808', False, True),
            ('zero', 'NScalarString (BYTES "MA==") metadata_cond', 'PSTRING ([48])', True, False),
            ('empty', 'NScalarString (BYTES "") metadata_cond', 'PSTRING eps', True, False),
            ('nul_text', 'NScalarString (BYTES "eAA=") metadata_cond', 'PSTRING ([120,0])', True, True),
            ('subnormal', 'NScalarFloat (FLOAT "0000000000000001") metadata_cond', 'PFLOAT 1', True, True),
            ('negative_zero', 'NScalarFloat (FLOAT "8000000000000000") metadata_cond', 'PFLOAT 9223372036854775808', True, False),
            ('infinity', 'NScalarFloat (FLOAT "7ff0000000000000") metadata_cond', 'PFLOAT 9218868437227405312', False, True),
            ('nan', 'NScalarFloat (FLOAT "7ff8000000000000") metadata_cond', 'PFLOAT 9221120237041090560', False, True),
            ('uppercase', 'NScalarFloat (FLOAT "3FF4000000000000") metadata_cond', 'PFLOAT 4608308318706860032', False, True),
            ('short_hex', 'NScalarFloat (FLOAT "1") metadata_cond', 'PFLOAT 1', False, True),
            ('invalid_hex', 'NScalarFloat (FLOAT "000000000000000g") metadata_cond', 'PFLOAT 1', False, True)):
        name = {'true': 'TruE', 'false': 'FaLsE', 'null': 'NuLl'}.get(label)
        name_occurrence = ''
        if name is not None:
            encoded = base64.b64encode(name.encode()).decode()
            name_occurrence = f' :: (PCOCCURRENCE (pcpath_left ++ [PCFIELD 0]) (NName (BYTES "{encoded}") metadata_cond))'
        checks += lines(f'''
expression_scalar_{label} = {node}
expression_base_{label} = NExprTernary expression_scalar_{label} expression_true expression_false metadata
S_scalar_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}) :: (PCOCCURRENCE pcpath_left expression_scalar_{label}){name_occurrence} :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left ({value})) :: ppool.CONSTANTS]]]
$compiled_read(S_scalar_{label},porigin_left) = ({value})
$string_read_raw_truth(S_scalar_{label},porigin_left,{value}) = {str(valid).lower()}
$string_read_raw_known_base(S_scalar_{label},porigin_base,pvalue_wrong) = {str(valid and truth).lower()}
$string_read_raw_known_base(S_scalar_{label},porigin_base,pvalue_base) = {str(valid and not truth).lower()}
''')
        if name is not None:
            checks += lines(f'''
S_name_{label} = S_scalar_{label}[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_{label}) :: (PCOCCURRENCE pcpath_left expression_scalar_{label}) :: (PCOCCURRENCE (pcpath_left ++ [PCFIELD 0]) (NName (BYTES "{encoded}") eps)) :: pcunit.OCCURRENCES]]]
$compiled_read(S_name_{label},porigin_left) = ({value})
~$string_read_raw_truth(S_name_{label},porigin_left,{value})
~$string_read_raw_known_base(S_name_{label},porigin_base,pvalue_base)
~$string_read_raw_known_base(S_name_{label},porigin_base,pvalue_wrong)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
