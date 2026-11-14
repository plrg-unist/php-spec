"""Raw finite float truth keeps a shorthand fallback and its initial raw offset."""
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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata)
expression_cond = NExprBooleanNot expression_leaf metadata_cond
expression_leaf = NScalarFloat (FLOAT text_float) metadata_float
n_bits = $hex_bits(text_float,0)
n_bits = 4608308318706860032
$base64(text_false) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_cond)
$compiled_read(S_capture,porigin_cond) = eps
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (expression_leaf)
$compiled_read(S_capture,porigin_leaf) = (PFLOAT n_bits)
$float_decode(n_bits) = FINITE 0 n_num n_den
$(n_num > 0)
$compiled_precision(S_capture,(porigin_cond)) = (14)
$compiled_precision(S_capture,(porigin_leaf)) = (14)
$string_read_raw_truth(S_capture,porigin_leaf,PFLOAT n_bits)
$string_read_runtime_value(S_capture,porigin_leaf) = (PFLOAT n_bits)
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL false)
$truth_value(S_capture,PFLOAT n_bits,12) = S_capture[.RESULT = KNOWN (PBOOL true)]
$number_bool(NFLOAT n_bits) = (true,false)
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$compiled_read(S_capture,porigin_absent) = eps
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$compiled_read(S_capture,porigin_false) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_false,PSTRING ($ptascii("abc"))) = pkeyread.BASE
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
porigin_base = PORIGIN n_unit pcpath_base
porigin_cond = PORIGIN n_unit pcpath_cond
porigin_leaf = PORIGIN n_unit pcpath_leaf
porigin_false = PORIGIN n_unit pcpath_false
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
pcunit.ID = n_unit /\ ppool.UNIT = n_unit /\ pcode.UNIT = n_unit
~$string_read_raw_truth(S_capture,porigin_leaf,PINT 1)
~$string_read_raw_truth(S_capture,porigin_leaf,PBOOL true)
~$string_read_raw_truth(S_capture,porigin_leaf,PFLOAT 1)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
$code_expression(pcode.EXPRESSIONS,pcpath_cond) = ((12,false))
$code_expression(pcode.EXPRESSIONS,pcpath_leaf) = ((12,true))
''')
    for label, value in (('type','PINT 1'), ('bits','PFLOAT 1'), ('truth','PBOOL true')):
        state = 'S_pool_' + label
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth({state},porigin_leaf,PFLOAT n_bits)',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_plan({state}) = eps']
    for label, path, value in (('condition','pcpath_cond','PBOOL false'),
                                ('parent','pcpath_base','PSTRING ($ptascii("abc"))'),
                                ('fallback','pcpath_false','PSTRING ($ptascii("XYZ"))')):
        state = 'S_forged_' + label
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 12 true) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_plan({state}) = eps']
    for label, path in (('condition','pcpath_cond'), ('leaf','pcpath_leaf')):
        state = 'S_precision_' + label
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION {path} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_raw_truth({state},porigin_leaf,PFLOAT n_bits)',
                   f'$string_read_runtime_value({state},porigin_cond) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_plan({state}) = eps']
    # Coherent local source/pool projections isolate finiteness and false truth.
    # They have no original-source or native credit.
    for label, bits, allowed, truth in (
            ('subnormal',1,True,True),
            ('maximum',9218868437227405311,True,True),
            ('zero',0,True,False),
            ('negative_zero',9223372036854775808,True,False),
            ('infinity',9218868437227405312,False,True),
            ('nan',9221120237041090560,False,True)):
        state = 'S_local_' + label
        checks += lines(f'''
expression_{label} = NScalarFloat (FLOAT "{bits:016x}") metadata_float
expression_{label}_cond = NExprBooleanNot expression_{label} metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_leaf expression_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PFLOAT {bits})) :: ppool.CONSTANTS]]]
$compiled_read({state},porigin_leaf) = (PFLOAT {bits})
$string_read_raw_truth({state},porigin_leaf,PFLOAT {bits}) = {str(allowed).lower()}
$truth({state},PFLOAT {bits}) = {str(truth).lower()}
$string_read_raw_known_base({state},porigin_base,pkeyread.BASE) = {str(allowed and truth).lower()}
''')
        if label == 'infinity':
            checks += [f'$truth_value({state},PFLOAT {bits},12) = {state}[.RESULT = KNOWN (PBOOL true)]']
        if label == 'nan':
            checks += [f'$truth_value({state},PFLOAT {bits},12) =/= {state}[.RESULT = KNOWN (PBOOL true)]']
    for label, payload in (('short','3ff4'), ('alphabet','3ff400000000000g')):
        state = 'S_malformed_' + label
        checks += lines(f'''
expression_{label} = NScalarFloat (FLOAT "{payload}") metadata_float
expression_{label}_cond = NExprBooleanNot expression_{label} metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_leaf expression_{label}) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth({state},porigin_leaf,PFLOAT n_bits)
~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)
''')
    for label, path, node in (
            ('leaf','pcpath_leaf','NScalarInt (INTEGER 1) metadata_float'),
            ('condition','pcpath_cond','expression_leaf'),
            ('fallback','pcpath_false','NScalarInt (INTEGER 1) metadata_false')):
        state = 'S_detached_' + label
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_plan({state}) = eps']
    checks += lines(r'''
S_no_code = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_no_code,porigin_cond) = eps
~$string_read_raw_known_base(S_no_code,porigin_base,pkeyread.BASE)
$string_read_plan(S_no_code) = eps
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
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in checks),
        len(checks), len(checks) - derived_start)
