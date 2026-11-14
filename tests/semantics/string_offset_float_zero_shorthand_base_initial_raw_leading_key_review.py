"""A literal positive-zero float shorthand keeps its fallback interned header and raw offset."""
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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary (NScalarFloat (FLOAT text_cond) metadata_cond) ABSENT (NScalarString (BYTES text_false) metadata_false) metadata)
$hex_bits(text_cond,0) = 0
$base64(text_false) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$compiled_read(S_capture,porigin_cond) = (PFLOAT 0)
~$truth(S_capture,PFLOAT 0)
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
$string_read_raw_known_base(S_capture,porigin_false,pkeyread.BASE)
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
S_wrong_condition = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0]) PNULL) :: ppool.CONSTANTS]]]
S_wrong_selected = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 2]) (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
''')
    for state in ('S_wrong_condition', 'S_wrong_selected'):
        checks += [f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_raw_capture({state},pkeyread.INPUT,pkeyread.BASE) = eps',
                   f'$string_read_raw_saved({state},pstringread) = eps',
                   f'~$string_read_source({state},pstringread)']
    checks += lines(r'''
pvalue_condition = PFLOAT 0
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_condition)
$string_read_raw_capture(S_capture[.RESULT = KNOWN pvalue_condition],pkeyread.INPUT,pvalue_condition) = eps
$string_read_raw_saved(S,pstringread[.READ.BASE = pvalue_condition][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_condition)]) = eps
~$string_read_source(S,pstringread[.READ.BASE = pvalue_condition][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_condition)])
S_integer_condition = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0]) (PINT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_integer_condition,porigin_base,pkeyread.BASE)
$string_read_plan(S_integer_condition) = eps
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
expression_condition_other = NScalarFloat (FLOAT "3ff0000000000000") metadata_cond
expression_base_other = NExprTernary expression_condition_other ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_other = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_base_other) :: (PCOCCURRENCE (pcpath_base ++ [PCFIELD 0]) expression_condition_other) :: pcunit.OCCURRENCES]]]
$origin_node(S_other.SOURCES,porigin_base) = (expression_base_other)
$origin_node(S_other.SOURCES,porigin_cond) = (expression_condition_other)
$compiled_read(S_other,porigin_cond) = (PFLOAT 0)
~$string_read_raw_known_base(S_other,porigin_base,pkeyread.BASE)
$string_read_raw_capture(S_other,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_raw_saved(S_other,pstringread) = eps
~$string_read_source(S_other,pstringread)
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
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in checks),
        len(checks), len(checks) - derived_start)
