"""A BooleanNot(quiet NINT numeric-string unary chain) shorthand keeps its fallback interned header and raw offset."""
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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary (NExprBooleanNot (NExprUnaryMinus (NExprUnaryPlus (NScalarString (BYTES text_input) metadata_leaf) metadata_plus) metadata_minus) metadata_cond) ABSENT (NScalarString (BYTES text_false) metadata_false) metadata)
n_input* = $base64(text_input)
n_input* = $ptascii(" 1 ")
i = 1
$long_range(i)
$startup_bytes(n_input*) /\ $c_string(n_input*) = n_input*
$numeric_string(n_input*) = FULLNUM (NINT i)
$coerce_number(PSTRING_CARRIER INTERNED_STRING n_input*) = COERCED (NINT i) false
i =/= 0
$base64(text_false) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBooleanNot (NExprUnaryMinus (NExprUnaryPlus (NScalarString (BYTES text_input) metadata_leaf) metadata_plus) metadata_minus) metadata_cond)
$compiled_read(S_capture,porigin_cond) = (PBOOL false)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_minus)
$origin_node(S_capture.SOURCES,porigin_minus) = (NExprUnaryMinus (NExprUnaryPlus (NScalarString (BYTES text_input) metadata_leaf) metadata_plus) metadata_minus)
$compiled_read(S_capture,porigin_minus) = (PINT i_minus)
i_minus = $(-1)
$long_range(i_minus)
i_minus =/= 0
$origin_child((porigin_minus),[PCFIELD 0]) = (porigin_plus)
$origin_node(S_capture.SOURCES,porigin_plus) = (NExprUnaryPlus (NScalarString (BYTES text_input) metadata_leaf) metadata_plus)
$compiled_read(S_capture,porigin_plus) = (PINT i_plus)
i_plus = 1
$long_range(i_plus)
$origin_child((porigin_plus),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (NScalarString (BYTES text_input) metadata_leaf)
$compiled_read(S_capture,porigin_leaf) = (PSTRING n_input*)
$compiled_string_value(S_capture,porigin_leaf,PSTRING n_input*) = PSTRING_CARRIER INTERNED_STRING n_input*
~$string_read_raw_unary_integer(S_capture,porigin_leaf,i)
$string_read_raw_unary_integer(S_capture,porigin_plus,i_plus)
$string_read_raw_unary_integer(S_capture,porigin_minus,i_minus)
$unary_apply(S_capture,POSITIVE,PSTRING_CARRIER INTERNED_STRING n_input*,12) = S_capture[.RESULT = KNOWN (PINT i_plus)]
$unary_apply(S_capture,NEGATIVE,PINT i_plus,12) = S_capture[.RESULT = KNOWN (PINT i_minus)]
~$string_read_raw_unary_integer(S_capture,porigin_minus,i_plus)
~$truth(S_capture,PBOOL false) /\ $truth(S_capture,PINT i_minus)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$compiled_read(S_capture,porigin_absent) = eps
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_node(S_capture.SOURCES,porigin_false) = (NScalarString (BYTES text_false) metadata_false)
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
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
S_wrong_condition = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0]) PNULL) :: ppool.CONSTANTS]]]
S_wrong_selected = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 2]) (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
''')
    for state in ('S_wrong_condition', 'S_wrong_selected'):
        checks += [f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_raw_capture({state},pkeyread.INPUT,pkeyread.BASE) = eps',
                   f'$string_read_raw_saved({state},pstringread) = eps',
                   f'~$string_read_source({state},pstringread)']
    for label, depth in (('minus', 2), ('plus', 3), ('leaf', 4)):
        path = 'pcpath_base ++ [' + ','.join(['PCFIELD 0'] * depth) + ']'
        for index, value in enumerate(('PINT 2', 'PFLOAT 0', 'PINT 9223372036854775808')):
            state = f'S_wrong_{label}_{index}'
            checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT ({path}) ({value})) :: ppool.CONSTANTS]]]',
                       f'~$string_read_raw_unary_integer({state},porigin_minus,i_minus)',
                       f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                       f'$string_read_raw_saved({state},pstringread) = eps',
                       f'~$string_read_source({state},pstringread)']
    # Change every raw occurrence coherently, so classification and result guards
    # are exercised independently of the parent/child source equality fences.
    for label, payload, pool, plus, minus in (
            ('zero', 'MA==', 'PSTRING ($ptascii("0"))', '0', '0'),
            ('minimum', 'LTkyMjMzNzIwMzY4NTQ3NzU4MDg=', 'PSTRING ($ptascii("-9223372036854775808"))', '$(-9223372036854775808)', '$(-9223372036854775808)'),
            ('minimum_space', 'LTkyMjMzNzIwMzY4NTQ3NzU4MDgg', 'PSTRING ($ptascii("-9223372036854775808 "))', '$(-9223372036854775808)', '$(-9223372036854775808)'),
            ('decimal', 'MS4w', 'PSTRING ($ptascii("1.0"))', '1', '$(-1)'),
            ('exponent', 'MWUw', 'PSTRING ($ptascii("1e0"))', '1', '$(-1)'),
            ('overflow', 'OTIyMzM3MjAzNjg1NDc3NTgwOA==', 'PSTRING ($ptascii("9223372036854775808"))', '1', '$(-1)'),
            ('leading', 'MXg=', 'PSTRING ($ptascii("1x"))', '1', '$(-1)'),
            ('nul', 'MQA=', 'PSTRING ([49,0])', '1', '$(-1)'),
            ('nonnumeric', 'eA==', 'PSTRING ($ptascii("x"))', '1', '$(-1)')):
        checks += lines(f'''
i_{label}_plus = {plus}
i_{label}_minus = {minus}
expression_{label}_leaf = NScalarString (BYTES "{payload}") metadata_leaf
expression_{label}_plus = NExprUnaryPlus expression_{label}_leaf metadata_plus
expression_{label}_minus = NExprUnaryMinus expression_{label}_plus metadata_minus
expression_{label}_cond = NExprBooleanNot expression_{label}_minus metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE (pcpath_base ++ [PCFIELD 0]) expression_{label}_cond) :: (PCOCCURRENCE (pcpath_base ++ [PCFIELD 0,PCFIELD 0]) expression_{label}_minus) :: (PCOCCURRENCE (pcpath_base ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0]) expression_{label}_plus) :: (PCOCCURRENCE (pcpath_base ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) expression_{label}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0,PCFIELD 0]) (PINT i_{label}_minus)) :: (PCONSTANT (pcpath_base ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0]) (PINT i_{label}_plus)) :: (PCONSTANT (pcpath_base ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) ({pool})) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_{label},porigin_base,pkeyread.BASE)
$string_read_raw_saved(S_{label},pstringread) = eps
~$string_read_source(S_{label},pstringread)
''')
        if label not in ('zero', 'minimum'):
            checks += [f'~$string_read_raw_unary_integer(S_{label},porigin_plus,i_{label}_plus)',
                       f'~$string_read_raw_unary_integer(S_{label},porigin_minus,i_{label}_minus)']
    checks += lines(r'''
$string_read_raw_unary_integer(S_zero,porigin_plus,0)
$string_read_raw_unary_integer(S_zero,porigin_minus,0)
$string_read_raw_unary_integer(S_minimum,porigin_plus,i_minimum_plus)
~$string_read_raw_unary_integer(S_minimum,porigin_minus,i_minimum_minus)
$unary_apply(S_minimum,NEGATIVE,PINT i_minimum_plus,12) = S_minimum[.RESULT = KNOWN (PFLOAT 4890909195324358656)]
$numeric_string($ptascii("-9223372036854775808")) = FULLNUM (NINT $(-9223372036854775808))
$numeric_string($ptascii("-9223372036854775808 ")) = FULLNUM (NFLOAT 14114281232179134464)
$coerce_number(PSTRING ($ptascii("1x"))) = COERCED (NINT 1) true
$coerce_number(PSTRING ([49,0])) = COERCED (NINT 1) true
''')
    for label, expression in (
            ('float', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_leaf'),
            ('integer', 'NScalarInt (INTEGER 1) metadata_leaf'),
            ('name', 'NExprConstFetch (NName (BYTES "UEhQX0lOVF9NQVg=") metadata_leaf) metadata_leaf')):
        state = f'S_leaf_{label}'
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_base ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_unary_integer({state},porigin_plus,i_plus)',
                   f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
pvalue_condition = PBOOL false
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_condition)
$string_read_raw_capture(S_capture[.RESULT = KNOWN pvalue_condition],pkeyread.INPUT,pvalue_condition) = eps
$string_read_raw_saved(S,pstringread[.READ.BASE = pvalue_condition][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_condition)]) = eps
~$string_read_source(S,pstringread[.READ.BASE = pvalue_condition][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_condition)])
S_integer_condition = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0]) (PINT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_integer_condition,porigin_base,pkeyread.BASE)
$string_read_plan(S_integer_condition) = eps
S_true_condition = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0]) (PBOOL true)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_true_condition,porigin_base,pkeyread.BASE)
$string_read_plan(S_true_condition) = eps
S_wrong_leaf = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) (PBOOL false)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_wrong_leaf,porigin_base,pkeyread.BASE)
$string_read_raw_capture(S_wrong_leaf,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_raw_saved(S_wrong_leaf,pstringread) = eps
~$string_read_source(S_wrong_leaf,pstringread)
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
