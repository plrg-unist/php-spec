"""A certified scalar-conditioned full ternary keeps its selected header and frozen raw offset."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_key),KEYREF false,PHASE STRING_LEADING 1}
pkeyread.VALUE = PSTRING ($ptascii("1x"))
pkeyread.INPUT = VARIABLE ($ptascii("key")) 12
pkeyread.LINE = 12 /\ pkeyread.PHASE = KEY_NULL
pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)
S_capture.RESULT = KNOWN pkeyread.BASE
n_key = 0 /\ S_capture.REFCELLS = eps
S_capture.CELL = 0 /\ S_capture.LOCATION = ROOT 0
S_capture.STRINGDATA = [$ptascii("512")]
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
S_capture.STORE[n_key] = DEFINED pkeyread.VALUE
$string_read_cell(S_capture,n_key)
$string_read_capture(S_capture,pkeyread.INPUT) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_key_capture(S_capture,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_raw_capture(S_capture,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (1)
$string_read_raw_saved(S_capture,pstringread) = (1)
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond expression_true expression_false metadata)
expression_cond = NExprBinaryOpMinus expression_add expression_one metadata_cond
expression_add = NExprBinaryOpPlus expression_left expression_right metadata_add
expression_left = NScalarInt (INTEGER 1) metadata_left
expression_right = NScalarInt (INTEGER 2) metadata_right
expression_one = NScalarInt (INTEGER 1) metadata_one
expression_true = NScalarString (BYTES text_true) metadata_true
expression_false = NScalarString (BYTES text_false) metadata_false
$base64(text_true) = $ptascii("abc") /\ $base64(text_false) = $ptascii("XYZ")
$compiled_read(S_capture,porigin_base) = eps
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_cond)
$compiled_read(S_capture,porigin_cond) = (PINT 2)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_add)
$origin_node(S_capture.SOURCES,porigin_add) = (expression_add)
$compiled_read(S_capture,porigin_add) = (PINT 3)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_one)
$origin_node(S_capture.SOURCES,porigin_one) = (expression_one)
$compiled_read(S_capture,porigin_one) = (PINT 1)
$origin_child((porigin_add),[PCFIELD 0]) = (porigin_left)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$compiled_read(S_capture,porigin_left) = (PINT 1)
$origin_child((porigin_add),[PCFIELD 1]) = (porigin_right)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$compiled_read(S_capture,porigin_right) = (PINT 2)
$string_read_raw_unary_integer(S_capture,porigin_cond,2)
$string_read_raw_truth(S_capture,porigin_cond,PINT 2)
$truth_value(S_capture,PINT 2,0) = S_capture[.RESULT = KNOWN (PBOOL true)]
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_true)
$origin_node(S_capture.SOURCES,porigin_true) = (expression_true)
$compiled_read(S_capture,porigin_true) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_true,PSTRING ($ptascii("abc"))) = pkeyread.BASE
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_node(S_capture.SOURCES,porigin_false) = (expression_false)
$compiled_read(S_capture,porigin_false) = (PSTRING ($ptascii("XYZ")))
$compiled_string_value(S_capture,porigin_false,PSTRING ($ptascii("XYZ"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
$string_read_source(S_capture,pstringread)
$string_read_message(pstringread) = $ptascii("Illegal string offset \"1x\"")
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LINE = 12 /\ perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("Illegal string offset \"1x\"")
$error_call_valid(S_before,perrorcall)
$heap_graph(S_before) = $heap_graph(S_capture)
S_before.STORE = S_capture.STORE
''') + guards('S_capture') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("key")) = (n_key)
$lookup(S.ENV,$ptascii("got")) = (1)
pvalue_current = PSTRING ($ptascii("Illegal string offset \"1x\""))
S.STORE[n_key] = DEFINED pvalue_current
S.STORE[1] = DEFINED (PINT 99)
S.REFCELLS = eps
$numeric_string($ptascii("Illegal string offset \"1x\"")) = NOTNUMERIC
$string_read_key_current(S,pstringread) = eps
$string_read_current_offset(S,pstringread,pvalue_current) = eps
$string_read_raw_saved(S,pstringread) = (1)
$string_read_source(S,pstringread)
$string_read_ready(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_callback_cast_retained(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1]),EDGES eps,ROOTS ([HCELL 1,HCELL 0]),DEBTS eps}
$heap_valid(H)
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_after
S_after = S_expected
$heap_graph(S_after) = H /\ S_after.EVENTS = S.EVENTS
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
$drive_steps(S_expected,1) = $drive_steps(S,2)
S_done = $drive_steps(S_after,1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset \"1x\";R:b;K:Illegal string offset \"1x\";Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE','RESULT')
    checks.append('S_capture = $initial_state(NORMAL)' + ''.join('[.' + f + ' = S_capture.' + f + ']' for f in fields))
    derived_start = len(checks)
    checks += lines(r'''
$string_read_raw_known_base(S_capture,porigin_true,pkeyread.BASE)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
pvalue_wrong = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))
pkeyread_wrong = pkeyread[.BASE = pvalue_wrong][.OWNERS = BASE_VALUE (KNOWN pvalue_wrong)]
pstringread_wrong = pstringread[.READ = pkeyread_wrong]
$key_read_owners_source(S,pkeyread_wrong)
$string_read_raw_saved(S,pstringread_wrong) = eps
~$string_read_source(S,pstringread_wrong)
$string_read_raw_capture(S_capture[.RESULT = KNOWN pvalue_wrong],pkeyread.INPUT,pvalue_wrong) = eps
porigin_base = PORIGIN n_unit pcpath_base
S_capture.POOLS = [ppool]
S_wrong_condition = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0]) (PBOOL false)) :: ppool.CONSTANTS]]]
S_wrong_selected = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 1]) (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
S_wrong_skipped = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 2]) (PSTRING ($ptascii("abc")))) :: ppool.CONSTANTS]]]
''')
    for state in ('S_wrong_condition', 'S_wrong_selected', 'S_wrong_skipped'):
        checks += [f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_raw_capture({state},pkeyread.INPUT,pkeyread.BASE) = eps',
                   f'$string_read_raw_saved({state},pstringread) = eps',
                   f'~$string_read_source({state},pstringread)']
    checks += lines(r'''
pvalue_condition = PINT 2
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_condition)
$string_read_raw_capture(S_capture[.RESULT = KNOWN pvalue_condition],pkeyread.INPUT,pvalue_condition) = eps
$string_read_raw_saved(S,pstringread[.READ.BASE = pvalue_condition][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_condition)]) = eps
~$string_read_source(S,pstringread[.READ.BASE = pvalue_condition][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_condition)])
S_wrong_condition_value = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0]) (PINT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_wrong_condition_value,porigin_base,pkeyread.BASE)
$string_read_plan(S_wrong_condition_value) = eps
S_capture.CODE = [pcode]
n_unit = pcode.UNIT
S_parent_constant = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PSTRING ($ptascii("abc")))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 12 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_parent_constant,porigin_base) = (PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_parent_constant,porigin_base,pkeyread.BASE)
$string_read_plan(S_parent_constant) = eps
~$string_read_source(S[.ORIGIN = eps],pstringread)
~$string_read_source(S,pstringread[.READ.LINE = 13])
~$string_read_source(S,pstringread[.BASECELL = (n_key)])
~$string_read_source(S,pstringread[.KEYCELL = eps])
~$string_read_source(S,pstringread[.PHASE = STRING_CAST])
''')
    for field in ('SOURCES','CODE','POOLS'):
        checks += [f'~$string_read_raw_known_base(S_capture[.{field} = eps],porigin_base,pkeyread.BASE)',
                   f'$string_read_plan(S_capture[.{field} = eps]) = eps',
                   f'~$string_read_source(S[.{field} = eps],pstringread)']
    for value in ('PSTRING ($ptascii("abc"))', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))'):
        checks += [f'$string_read_raw_leading({value},pkeyread.VALUE) = eps',
                   f'$string_read_raw_capture(S_capture[.RESULT = KNOWN ({value})],pkeyread.INPUT,{value}) = eps']
    checks += lines(r'''
porigin_cond = PORIGIN n_unit pcpath_cond
porigin_add = PORIGIN n_unit pcpath_add
porigin_one = PORIGIN n_unit pcpath_one
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
porigin_true = PORIGIN n_unit pcpath_true
porigin_false = PORIGIN n_unit pcpath_false
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
''')
    for label, path, value in ((label,path,value) for label,path in
            (('root','pcpath_cond'),('add','pcpath_add'),('one','pcpath_one'),
             ('left','pcpath_left'),('right','pcpath_right'))
            for value in ('PINT 7','PFLOAT 0','PINT 9223372036854775808')):
        state = f'S_pool_{label}_{len(checks)}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth({state},porigin_cond,PINT 2)',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_plan({state}) = eps',
                   f'$string_read_raw_saved({state},pstringread) = eps']
    for label, path, node in (
            ('condition','pcpath_cond','NExprBinaryOpMinus expression_add expression_one eps'),
            ('add','pcpath_add','NExprBinaryOpPlus expression_left expression_right eps'),
            ('left','pcpath_left','NScalarInt (INTEGER 1) eps'),
            ('true','pcpath_true','NScalarString (BYTES text_true) eps'),
            ('false','pcpath_false','NScalarString (BYTES text_false) eps')):
        state = 'S_metadata_' + label
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_plan({state}) = eps',
                   f'$string_read_raw_saved({state},pstringread) = eps']
    # Coherent local projections test raw scalar authority and both truth branches.
    # NUL belongs only to an INTERNED condition and adds no owned release route.
    for label, node, value, truth, child in (
            ('true','NExprConstFetch (NName (BYTES "VHJ1RQ==") eps) eps','PBOOL true',True,'NName (BYTES "VHJ1RQ==") eps'),
            ('false','NExprConstFetch (NName (BYTES "RmFMc0U=") eps) eps','PBOOL false',False,'NName (BYTES "RmFMc0U=") eps'),
            ('null','NExprConstFetch (NName (BYTES "TnVsbA==") eps) eps','PNULL',False,'NName (BYTES "TnVsbA==") eps'),
            ('zero','NScalarInt (INTEGER 0) eps','PINT 0',False,None),
            ('minimum','NScalarInt (INTEGER $(-9223372036854775808)) eps','PINT $(-9223372036854775808)',True,None),
            ('maximum','NScalarInt (INTEGER 9223372036854775807) eps','PINT 9223372036854775807',True,None),
            ('empty','NScalarString (BYTES "") eps','PSTRING eps',False,None),
            ('ascii_zero','NScalarString (BYTES "MA==") eps','PSTRING ([48])',False,None),
            ('nul','NScalarString (BYTES "eAA=") eps','PSTRING ([120,0])',True,None),
            ('float_zero','NScalarFloat (FLOAT "0000000000000000") eps','PFLOAT 0',False,None),
            ('float_negative_zero','NScalarFloat (FLOAT "8000000000000000") eps','PFLOAT 9223372036854775808',False,None),
            ('float_subnormal','NScalarFloat (FLOAT "0000000000000001") eps','PFLOAT 1',True,None)):
        child_fact = '' if child is None else f'(PCOCCURRENCE (pcpath_cond ++ [PCFIELD 0]) ({child})) :: '
        selected = 'pkeyread.BASE' if truth else 'PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))'
        checks += lines(f'''
expression_scalar_{label} = {node}
expression_{label}_base = NExprTernary expression_scalar_{label} expression_true expression_false metadata
S_scalar_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_scalar_{label}) :: {child_fact}pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond ({value})) :: ppool.CONSTANTS]]]
$compiled_read(S_scalar_{label},porigin_cond) = ({value})
$string_read_raw_truth(S_scalar_{label},porigin_cond,{value})
$truth_value(S_scalar_{label},{value},0) = S_scalar_{label}[.RESULT = KNOWN (PBOOL {str(truth).lower()})]
$string_read_raw_known_base(S_scalar_{label},porigin_base,{selected})
''')
        if child is not None:
            checks += [f'S_bad_name_{label} = S_scalar_{label}[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_scalar_{label}) :: (PCOCCURRENCE (pcpath_cond ++ [PCFIELD 0]) (NName (BYTES "d3Jvbmc=") eps)) :: pcunit.OCCURRENCES]]]',
                       f'~$string_read_raw_truth(S_bad_name_{label},porigin_cond,{value})',
                       f'~$string_read_raw_known_base(S_bad_name_{label},porigin_base,{selected})']
    for label, node, value in (
            ('outside','NScalarInt (INTEGER 9223372036854775808) eps','PINT 9223372036854775808'),
            ('qualified','NExprConstFetch (NNameFullyQualified (BYTES "dHJ1ZQ==") eps) eps','PBOOL true'),
            ('infinity','NScalarFloat (FLOAT "7ff0000000000000") eps','PFLOAT 9218868437227405312'),
            ('nan','NScalarFloat (FLOAT "7ff8000000000000") eps','PFLOAT 9221120237041090560'),
            ('short','NScalarFloat (FLOAT "1") eps','PFLOAT 1'),
            ('upper','NScalarFloat (FLOAT "3FF0000000000000") eps','PFLOAT 4607182418800017408'),
            ('alphabet','NScalarFloat (FLOAT "000000000000000g") eps','PFLOAT 0')):
        checks += lines(f'''
expression_bad_{label} = {node}
expression_bad_{label}_base = NExprTernary expression_bad_{label} expression_true expression_false metadata
S_bad_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bad_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_bad_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond ({value})) :: ppool.CONSTANTS]]]
~$string_read_raw_truth(S_bad_{label},porigin_cond,{value})
~$string_read_raw_known_base(S_bad_{label},porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_bad_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
''')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in checks),
        len(checks), len(checks) - derived_start)
