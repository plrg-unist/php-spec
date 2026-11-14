"""Emitted finite float NOT preserves a shorthand base through initial-key reference rebinding."""
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $float_peer_front(pstate, nat) : bool
def $float_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 18) 18 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $float_peer_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $float_peer_front(S, n) = false -- otherwise
dec $float_peer_seek(pstate, nat, nat) : pstate
def $float_peer_seek(S, n_stage, n) = S
  -- if $float_peer_front(S, n_stage)
def $float_peer_seek(S, n_stage, n) = S
  -- if ~$float_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $float_peer_seek(S, n_stage, 0) = S
  -- if ~$float_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $float_peer_seek(S, n_stage, n) = $float_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$float_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $float_peer_seek({start},{stage},1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$float_peer_front(S_capture,0)
S_capture.CURRENT = eps /\ S_capture.FRAMES = eps
poperand = VARIABLE ($ptascii("key")) 18
S_capture.TODO = (KEY_READ_DIM poperand 18 KEY_R) :: ptask_tail*
pvalue_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pvalue_raw = PSTRING ($ptascii("1x"))
S_capture.RESULT = KNOWN pvalue_base
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_old)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_old = 0 /\ n_got = 1
n_key_cell? = (n_old)
S_capture.STORE[n_old] = DEFINED pvalue_raw
S_capture.STORE[n_got] = DEFINED (PINT 99)
S_capture.REFCELLS = [n_old]
~$string_read_cell(S_capture,n_old)
$call_reference_operand_valid(S_capture,REFERENCE n_old)
$heap_owners($heap_graph(S_capture),HCELL n_old) = 2
$heap_owners($heap_graph(S_capture),HCELL n_got) = 1
$heap_valid($heap_graph(S_capture))
$string_read_capture(S_capture,poperand) = eps
$string_read_key_capture(S_capture,poperand,pvalue_base) = eps
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,n_key_cell?))
$string_read_base_capture(S_capture,S_capture.RESULT) = ((pvalue_base,eps))
$string_read_raw_leading(pvalue_base,pvalue_raw) = (1)
S_capture.ORIGIN = (porigin)
$origin_child((porigin),[PCFIELD 0]) = (porigin_base)
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary (NExprBooleanNot (NScalarFloat (FLOAT text_float) metadata_float) metadata_cond) ABSENT (NScalarString (BYTES text_false) metadata_false) metadata)
text_float = "0000000000000001"
$hex_bits(text_float,0) = 1
$float_decode(1) = FINITE 0 n_num n_den
n_num = 1
$number_bool(NFLOAT 1) = (true,false)
$truth_value(S_capture,PFLOAT 1,18) = S_capture[.RESULT = KNOWN (PBOOL true)]
$base64(text_false) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBooleanNot (NScalarFloat (FLOAT text_float) metadata_float) metadata_cond)
$compiled_read(S_capture,porigin_cond) = eps
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (NScalarFloat (FLOAT text_float) metadata_float)
$compiled_read(S_capture,porigin_leaf) = (PFLOAT 1)
$compiled_precision(S_capture,(porigin_cond)) = (14)
$compiled_precision(S_capture,(porigin_leaf)) = (14)
$string_read_raw_truth(S_capture,porigin_leaf,PFLOAT 1)
$string_read_runtime_value(S_capture,porigin_leaf) = (PFLOAT 1)
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL false)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$compiled_read(S_capture,porigin_absent) = eps
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_node(S_capture.SOURCES,porigin_false) = (NScalarString (BYTES text_false) metadata_false)
$compiled_read(S_capture,porigin_false) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_false,PSTRING ($ptascii("abc"))) = pvalue_base
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
pkeyread = {SITE porigin,GLOBAL false,MODE KEY_R,INPUT poperand,VALUE pvalue_raw,BASE pvalue_base,OWNERS BASE_VALUE S_capture.RESULT,LINE 18,PHASE KEY_NULL,KEY KSTRING eps,NAME eps}
$key_read_input_source(S_capture,pkeyread)
$key_read_owners_source(S_capture,pkeyread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_old),KEYREF true,PHASE STRING_LEADING 1}
$string_read_key_reference(S_capture,pstringread.KEYCELL)
$string_read_raw_saved(S_capture,pstringread) = (1)
$string_read_source(S_capture,pstringread)
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
$string_read_plan(S_capture) = (pstringread)
$error_handler_eligible(S_capture,2)
S_capture.STRINGDATA = [$ptascii("512")]
H_capture = {NODES ([HCELL n_old,HCELL n_got]),EDGES eps,ROOTS ([HCELL n_got,HCELL n_old,HCELL n_old]),DEBTS eps}
$heap_graph(S_capture) = H_capture
$heap_owners(H_capture,HCELL n_old) = 2
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 18
perrorcall.MESSAGE = $ptascii("Illegal string offset \"1x\"")
$error_call_valid(S_before,perrorcall)
$heap_graph(S_before) = H_capture /\ S_before.STORE = S_capture.STORE
$drive_steps(S_capture,0) = S_capture[.COMPLETION = BUDGET]
$drive_steps(S_capture,1) = S_before[.COMPLETION = BUDGET]
$drive_steps(S_before,1) = $drive_steps(S_capture,2)
''') + guards('S_capture') + guards('S_before') + seek('S_before', 1, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current =/= n_old /\ n_current =/= n_got
S.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S.STORE[n_current] = DEFINED (PINT 2)
S.STORE[n_got] = DEFINED (PINT 99)
n_old <- S.REFCELLS /\ n_current <- S.REFCELLS
$heap_owners($heap_graph(S),HCELL n_old) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
$string_read_raw_saved(S,pstringread) = (1)
$string_read_source(S,pstringread)
$string_read_ready(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_callback_raw_key(S,pstringread) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
H = {NODES ([HCELL n_old,HCELL n_got,HCELL n_current]),EDGES eps,ROOTS ([HCELL n_current,HCELL n_got,HCELL n_old]),DEBTS eps}
$heap_graph(S) = H
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
S_done.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S_done.STORE[n_current] = DEFINED (PINT 2)
S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([98]))
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset \"1x\";R:b;K:2;A:Illegal string offset \"1x\";Z;")
''') + guards('S') + guards('S_after') + guards('S_done')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','RESULT','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks.append('S_capture = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S_capture.' + field + ']' for field in fields))
    derived_start = len(checks)
    checks += lines(r"""
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
porigin_base = PORIGIN n_unit pcpath_base
porigin_cond = PORIGIN n_unit pcpath_cond
porigin_leaf = PORIGIN n_unit pcpath_leaf
porigin_false = PORIGIN n_unit pcpath_false
pcunit.ID = n_unit /\ ppool.UNIT = n_unit /\ pcode.UNIT = n_unit
$code_expression(pcode.EXPRESSIONS,pcpath_cond) = ((18,false))
$code_expression(pcode.EXPRESSIONS,pcpath_leaf) = ((18,true))
~$string_read_raw_truth(S_capture,porigin_leaf,PINT 1)
~$string_read_raw_truth(S_capture,porigin_leaf,PBOOL true)
~$string_read_raw_truth(S_capture,porigin_leaf,PFLOAT 2)
""")
    for label, bits, valid, truth in (
            ('fraction',4608308318706860032,True,True),
            ('negative',13831680355561635840,True,True),
            ('maximum',9218868437227405311,True,True),
            ('zero',0,True,False), ('negative_zero',9223372036854775808,True,False),
            ('infinity',9218868437227405312,False,True),
            ('negative_infinity',18442240474082181120,False,True),
            ('nan',9221120237041090560,False,True)):
        checks += lines(f"""
expression_{label} = NScalarFloat (FLOAT "{bits:016x}") metadata_float
expression_{label}_cond = NExprBooleanNot expression_{label} metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_leaf expression_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PFLOAT {bits})) :: ppool.CONSTANTS]]]
$compiled_read(S_{label},porigin_leaf) = (PFLOAT {bits})
$string_read_raw_truth(S_{label},porigin_leaf,PFLOAT {bits}) = {str(valid).lower()}
$string_read_raw_known_base(S_{label},porigin_base,pvalue_base) = {str(valid and truth).lower()}
""")
        if label in ('infinity','negative_infinity'):
            checks.append(f'$truth_value(S_{label},PFLOAT {bits},18) = S_{label}[.RESULT = KNOWN (PBOOL true)]')
    for label, payload in (('short','1'), ('long','00000000000000001'),
                           ('upper','3FF4000000000000'), ('alphabet','000000000000000g')):
        checks += lines(f"""
expression_{label} = NScalarFloat (FLOAT "{payload}") metadata_float
expression_{label}_cond = NExprBooleanNot expression_{label} metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_leaf expression_{label}) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_{label},porigin_leaf,PFLOAT 1)
~$string_read_raw_known_base(S_{label},porigin_base,pvalue_base)
""")
    # Old scalar folds keep their own compiled false result. NUL here belongs to
    # an interned condition; it introduces no owned NUL string or release route.
    for label, expression, value, valid, selected in (
            ('true', 'NExprConstFetch (NName (BYTES "VHJ1RQ==") metadata_float) metadata_float', 'PBOOL true', True, True),
            ('false', 'NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_float) metadata_float', 'PBOOL false', False, False),
            ('null', 'NExprConstFetch (NName (BYTES "bnVsbA==") metadata_float) metadata_float', 'PNULL', False, False),
            ('qualified', 'NExprConstFetch (NNameFullyQualified (BYTES "dHJ1ZQ==") metadata_float) metadata_float', 'PBOOL true', False, False),
            ('text', 'NScalarString (BYTES "dHJ1dGh5") metadata_float', 'PSTRING ($ptascii("truthy"))', True, True),
            ('nul', 'NScalarString (BYTES "eAA=") metadata_float', 'PSTRING ([120,0])', True, True),
            ('empty', 'NScalarString (BYTES "") metadata_float', 'PSTRING eps', True, False),
            ('ascii_zero', 'NScalarString (BYTES "MA==") metadata_float', 'PSTRING ([48])', True, False),
            ('integer', 'NScalarInt (INTEGER 3) metadata_float', 'PINT 3', True, True),
            ('minimum', 'NScalarInt (INTEGER $(-9223372036854775808)) metadata_float', 'PINT $(-9223372036854775808)', True, True),
            ('integer_zero', 'NScalarInt (INTEGER 0) metadata_float', 'PINT 0', True, False),
            ('outside', 'NScalarInt (INTEGER 9223372036854775808) metadata_float', 'PINT 9223372036854775808', False, False)):
        checks += lines(f"""
expression_scalar_{label} = {expression}
expression_scalar_{label}_cond = NExprBooleanNot expression_scalar_{label} metadata_cond
expression_scalar_{label}_base = NExprTernary expression_scalar_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_scalar_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_scalar_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_scalar_{label}_cond) :: (PCOCCURRENCE pcpath_leaf expression_scalar_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL false)) :: (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_scalar_{label},porigin_cond) = (PBOOL false)
$string_read_raw_truth(S_scalar_{label},porigin_leaf,{value}) = {str(valid).lower()}
$string_read_raw_known_base(S_scalar_{label},porigin_base,pvalue_base) = {str(selected).lower()}
""")
    checks += lines(r"""
S_true_fallback_metadata = S_scalar_true[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_scalar_true_base) :: (PCOCCURRENCE pcpath_cond expression_scalar_true_cond) :: (PCOCCURRENCE pcpath_leaf expression_scalar_true) :: (PCOCCURRENCE pcpath_false (NScalarString (BYTES text_false) eps)) :: pcunit.OCCURRENCES]]]
$compiled_read(S_true_fallback_metadata,porigin_false) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_true_fallback_metadata,porigin_false,PSTRING ($ptascii("abc"))) = pvalue_base
$string_read_raw_truth(S_true_fallback_metadata,porigin_leaf,PBOOL true)
~$string_read_raw_known_base(S_true_fallback_metadata,porigin_base,pvalue_base)
S_scalar_carrier = S_scalar_text[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond (PBOOL false)) :: (PCONSTANT pcpath_leaf (PSTRING_CARRIER INTERNED_STRING ($ptascii("truthy")))) :: ppool.CONSTANTS]]]
$compiled_string_value(S_scalar_carrier,porigin_leaf,PSTRING ($ptascii("truthy"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("truthy"))
~$string_read_raw_truth(S_scalar_carrier,porigin_leaf,PSTRING ($ptascii("truthy")))
~$string_read_raw_known_base(S_scalar_carrier,porigin_base,pvalue_base)
S_scalar_emitted = S_scalar_true[.CODE = [pcode]]
$compiled_read(S_scalar_emitted,porigin_cond) = eps
$string_read_raw_truth(S_scalar_emitted,porigin_leaf,PBOOL true)
~$string_read_raw_known_base(S_scalar_emitted,porigin_base,pvalue_base)
""")
    for label, value in (('integer','PINT 1'), ('boolean','PBOOL true'),
                          ('text','PSTRING ($ptascii("1"))'), ('bits','PFLOAT 0')):
        checks += [f'S_pool_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_truth(S_pool_{label},porigin_leaf,PFLOAT 1)',
                   f'~$string_read_raw_known_base(S_pool_{label},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_pool_{label}) = eps']
    for label, path, value in (('condition','pcpath_cond','PBOOL false'),
                                ('wrong_condition','pcpath_cond','PBOOL true'),
                                ('parent','pcpath_base','PSTRING ($ptascii("abc"))'),
                                ('fallback','pcpath_false','PSTRING ($ptascii("XYZ"))')):
        checks += [f'S_forged_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 18 true) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_known_base(S_forged_{label},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_forged_{label}) = eps']
    for node in ('cond','leaf'):
        checks += [f'S_precision_{node} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_raw_truth(S_precision_{node},porigin_leaf,PFLOAT 1)',
                   f'$string_read_runtime_value(S_precision_{node},porigin_cond) = eps',
                   f'~$string_read_raw_known_base(S_precision_{node},porigin_base,pvalue_base)']
    for label, path, expression in (
            ('leaf','pcpath_leaf','NScalarFloat (FLOAT "0000000000000001") eps'),
            ('condition','pcpath_cond','NScalarFloat (FLOAT text_float) metadata_float'),
            ('fallback','pcpath_false','NScalarInt (INTEGER 1) metadata_false')):
        checks += [f'S_detached_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_detached_{label},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_detached_{label}) = eps']
    checks.append('$string_read_raw_truth(S_detached_leaf,porigin_leaf,PFLOAT 1)')
    for label, expression in (
            ('unary','NExprUnaryPlus (NScalarFloat (FLOAT text_float) metadata_float) metadata_float'),
            ('fetch','NExprConstFetch (NName (BYTES "SU5G") metadata_float) metadata_float')):
        checks += lines(f"""
expression_unsupported_{label} = {expression}
S_unsupported_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_leaf expression_unsupported_{label}) :: pcunit.OCCURRENCES]]]
~$string_read_raw_truth(S_unsupported_{label},porigin_leaf,PFLOAT 1)
~$string_read_raw_known_base(S_unsupported_{label},porigin_base,pvalue_base)
""")
    checks += lines(r"""
S_no_line = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_no_line,porigin_cond) = eps
~$string_read_raw_known_base(S_no_line,porigin_base,pvalue_base)
S_bad_heap = S_capture[.ENV = (BIND ($ptascii("ghost")) 99) :: S_capture.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_raw_capture(S_bad_heap,poperand,pvalue_base) = eps
~$string_read_source(S,pstringread[.BASECELL = (n_old)])
~$string_read_source(S,pstringread[.KEYCELL = eps])
~$string_read_source(S,pstringread[.READ.LINE = 19])
~$string_read_source(S,pstringread[.READ.INPUT = KNOWN pvalue_raw])
~$string_read_source(S,pstringread[.READ.PHASE = KEY_CV])
~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])
""")
    for field in ('SOURCES','CODE','POOLS'):
        checks += [f'~$string_read_raw_known_base(S_capture[.{field} = eps],porigin_base,pvalue_base)',
                   f'$string_read_plan(S_capture[.{field} = eps]) = eps',
                   f'~$string_read_source(S[.{field} = eps],pstringread)']
    for value in ('PBOOL false', 'PSTRING ($ptascii("abc"))',
                  'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
                  'PSTRING_CARRIER INTERNED_STRING ([97,0,99])'):
        checks.append(f'$string_read_raw_capture(S_capture[.RESULT = KNOWN ({value})],poperand,{value}) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
