"""Folded double NOT keeps a literal base and the original reference key."""

from string_offset_conditional_base_initial_raw_leading_key_peer_review import render as render_conditional
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_conditional(program, filename_b64)
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_condition)
expression_condition = NExprBooleanNot expression_not metadata_cond
expression_not = NExprBooleanNot expression_zero metadata_not
expression_zero = NExprBinaryOpPlus expression_product expression_six metadata_zero
expression_product = NExprBinaryOpMul expression_outer expression_minus metadata_product
expression_outer = NExprUnaryPlus expression_inner metadata_outer
expression_inner = NExprUnaryPlus expression_text metadata_inner
expression_text = NScalarString (BYTES text_two) metadata_text
expression_minus = NExprUnaryMinus (NScalarInt (INTEGER 3) metadata_three) metadata_minus
expression_six = NScalarInt (INTEGER 6) metadata_six
$base64(text_two) = $ptascii("2")
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_not)
$origin_child((porigin_not),[PCFIELD 0]) = (porigin_zero)
$origin_node(S_capture.SOURCES,porigin_not) = (expression_not)
$origin_node(S_capture.SOURCES,porigin_zero) = (expression_zero)
$compiled_read(S_capture,porigin_not) = (PBOOL true)
$compiled_read(S_capture,porigin_zero) = (PINT 0)
$string_read_raw_unary_integer(S_capture,porigin_zero,0)
$string_read_raw_truth(S_capture,porigin_zero,PINT 0)
$truth_value(S_capture,PINT 0,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_raw_truth(S_capture,porigin_not,PBOOL true)
$truth_value(S_capture,PBOOL true,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_raw_truth(S_capture,porigin_cond,PBOOL false)
$truth_value(S_capture,PBOOL false,0) = S_capture[.RESULT = KNOWN (PBOOL false)]
$type_bytes(PINT 0) =/= $ptascii("float")
$type_bytes(PBOOL true) =/= $ptascii("float")
$origin_node(S_capture.SOURCES,porigin_true) = (expression_true)
$origin_node(S_capture.SOURCES,porigin_false) = (expression_false)
expression_true = NScalarString (BYTES text_true) metadata_true
expression_false = NScalarString (BYTES text_false) metadata_false
$base64(text_true) = $ptascii("XYZ")
$base64(text_false) = $ptascii("abc")
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
porigin_base = PORIGIN n_unit pcpath_base
porigin_not = PORIGIN n_unit pcpath_not
porigin_zero = PORIGIN n_unit pcpath_zero
pcode.UNIT = n_unit /\ pcunit.ID = n_unit
$code_expression(pcode.EXPRESSIONS,pcpath_cond) = ((18,true))
$code_expression(pcode.EXPRESSIONS,pcpath_not) = ((18,true))
$compiled_precision(S_capture,(porigin_cond)) = (14)
$compiled_precision(S_capture,(porigin_not)) = (14)
S_budget = S_capture[.COMPLETION = BUDGET]
$string_read_raw_truth(S_budget,porigin_cond,PBOOL false)
$string_read_raw_known_base(S_budget,porigin_base,pvalue_base)
''')
    for label, path, value, result in (
            ('outer', 'pcpath_cond', 'PBOOL true', 'PBOOL true'),
            ('inner', 'pcpath_not', 'PBOOL false', 'PBOOL false'),
            ('zero', 'pcpath_zero', 'PINT 1', 'PBOOL false'),
            ('type', 'pcpath_cond', 'PINT 0', 'PINT 0')):
        checks += lines(f'''
S_pool_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_pool_{label},porigin_cond,{result})
~$string_read_raw_known_base(S_pool_{label},porigin_base,pvalue_base)
$string_read_plan(S_pool_{label}) = eps
''')
    for label, path, node in (
            ('condition', 'pcpath_cond', 'NExprBooleanNot expression_not eps'),
            ('inner', 'pcpath_not', 'NExprBooleanNot expression_zero eps'),
            ('zero', 'pcpath_zero', 'NExprBinaryOpPlus expression_product expression_six eps')):
        checks += lines(f'''
S_node_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]
~$string_read_raw_known_base(S_node_{label},porigin_base,pvalue_base)
$string_read_plan(S_node_{label}) = eps
''')
    # Finite FLOAT truth is quiet, but Zend deliberately emits every FLOAT NOT.
    # Forged own PBOOL facts must not bypass that separate runtime certificate.
    for label, bits, result in (('zero', 0, True), ('subnormal', 1, False)):
        boolean = str(result).lower()
        child_truth = str(not result).lower()
        checks += lines(f'''
expression_float_{label} = NScalarFloat (FLOAT "{bits:016x}") metadata_not
expression_float_not_{label} = NExprBooleanNot expression_float_{label} metadata_cond
expression_float_base_{label} = NExprTernary expression_float_not_{label} expression_true expression_false metadata
S_float_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_float_base_{label}) :: (PCOCCURRENCE pcpath_cond expression_float_not_{label}) :: (PCOCCURRENCE pcpath_not expression_float_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL {boolean})) :: (PCONSTANT pcpath_not (PFLOAT {bits})) :: ppool.CONSTANTS]]]
$compiled_read(S_float_{label},porigin_cond) = (PBOOL {boolean})
$compiled_read(S_float_{label},porigin_not) = (PFLOAT {bits})
$string_read_raw_truth(S_float_{label},porigin_not,PFLOAT {bits})
$truth_value(S_float_{label},PFLOAT {bits},0) = S_float_{label}[.RESULT = KNOWN (PBOOL {child_truth})]
~$string_read_raw_truth(S_float_{label},porigin_cond,PBOOL {boolean})
~$string_read_raw_known_base(S_float_{label},porigin_base,pvalue_base)
~$string_read_raw_known_base(S_float_{label},porigin_base,pvalue_wrong)
S_emitted_{label} = S_float_{label}[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 18 false) :: pcode.EXPRESSIONS]]]
$compiled_read(S_emitted_{label},porigin_cond) = eps
$string_read_runtime_value(S_emitted_{label},porigin_cond) = (PBOOL {boolean})
~$string_read_raw_truth(S_emitted_{label},porigin_cond,PBOOL {boolean})
~$string_read_raw_known_base(S_emitted_{label},porigin_base,pvalue_base)
~$string_read_raw_known_base(S_emitted_{label},porigin_base,pvalue_wrong)
''')
    # Only a local certificate projection: no additional source/native credit.
    checks += lines(r'''
expression_shorthand = NExprTernary expression_condition ABSENT expression_false metadata
S_shorthand = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_shorthand) :: pcunit.OCCURRENCES]]]
$compiled_read(S_shorthand,porigin_base) = eps
$compiled_read(S_shorthand,porigin_cond) = (PBOOL false)
$string_read_raw_truth(S_shorthand,porigin_not,PBOOL true)
$truth_value(S_shorthand,PBOOL true,0) = S_shorthand[.RESULT = KNOWN (PBOOL true)]
$string_read_raw_known_base(S_shorthand,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_shorthand,porigin_base,pvalue_wrong)
S_shorthand_wrong_inner = S_shorthand[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_not (PBOOL false)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_shorthand_wrong_inner,porigin_base,pvalue_base)
S_shorthand_wrong_outer = S_shorthand[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL true)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_shorthand_wrong_outer,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
