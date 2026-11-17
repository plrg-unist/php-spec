"""Reached REQUEST temporaries retain identity through a leading-key Warning."""

import json

from string_offset_retained_carrier_protocol import PREFIX, lines, seek
from string_offset_runtime_allocated_string_base_initial_raw_leading_key_cases import CASES


def render(program, filename_b64, reference=False):
    index = 2 if reference else 0
    identity = 2 if reference else 1
    text = '10bc' if reference else '10'
    byte = 98 if reference else 49
    raw = str(index) + 'x'
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand z_key KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) z_key
S_capture.RESULT = KNOWN pvalue_base
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_key),KEYREF b_reference,PHASE STRING_LEADING i}
pkeyread.BASE = pvalue_base /\ pkeyread.INPUT = poperand
pkeyread.VALUE = pvalue_raw /\ pkeyread.LINE = z_key
pkeyread.OWNERS = BASE_VALUE (KNOWN pvalue_base)
pkeyread.PHASE = KEY_NULL
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
S_capture.STORE[n_key] = DEFINED pvalue_raw
S_capture.STORE[n_got] = DEFINED (PINT 99)
$string_carrier_valid(S_capture,pvalue_base)
$string_read_capture(S_capture,KNOWN pvalue_base) = ((pvalue_base,eps))
$string_read_base_capture(S_capture,KNOWN pvalue_base) = ((pvalue_base,eps))
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
$string_read_raw_leading(pvalue_base,pvalue_raw) = eps
$string_read_allocated_leading(S_capture,pvalue_base,pvalue_raw) = (i)
$string_read_raw_saved(S_capture,pstringread) = (i)
$string_read_provider_ready(S_capture,pstringread)
$string_read_source(S_capture,pstringread)
$key_read_owners_source(S_capture,pkeyread)
$key_read_input_source(S_capture,pkeyread)
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
porigin_base = PORIGIN n_unit pcpath_base
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$code_expression(pcode.EXPRESSIONS,pcpath_base) = ((z_base,false))
$code_expression(pcode.EXPRESSIONS,pcpath_left) = ((z_left,false))
$(z_base > 0 /\ z_left > 0)
$compiled_precision(S_capture,(porigin_base)) = (14)
$compiled_precision(S_capture,(porigin_left)) = (14)
$compiled_read(S_capture,porigin_base) = eps
$compiled_read(S_capture,porigin_left) = eps
$compiled_read(S_capture,porigin_right) = eps
$compiled_identity_value(S_capture,porigin_base) = eps
$compiled_identity_value(S_capture,porigin_left) = eps
$constant_at(ppool.CONSTANTS,pcpath_base) = eps
$constant_at(ppool.CONSTANTS,pcpath_left) = eps
$string_read_runtime_value(S_capture,porigin_left) = eps
$string_read_runtime_value(S_capture,porigin_base) = eps
$string_read_allocated_value(S_capture,porigin_left,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$task_nodes(STRING_READ_RESULT pstringread) = eps
$base_nodes(pkeyread.OWNERS) = eps
$heap_valid($heap_graph(S_capture))
PhpStep: S_capture ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = z_key
$error_call_valid(S_dispatch,perrorcall)
S_dispatch.STRINGDATA = S_capture.STRINGDATA
S_dispatch.STORE = S_capture.STORE
$heap_graph(S_dispatch) = $heap_graph(S_capture)
''') + seek('S_dispatch', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
S.STORE[n_got] = DEFINED (PINT 99)
S.STORE[n_key] = DEFINED (PSTRING perrorcall.MESSAGE)
$string_read_raw_saved(S,pstringread) = (i)
$string_read_source(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_ready(S,pstringread)
$string_read_key_current(S,pstringread) = eps
$heap_valid($heap_graph(S))
S.STRINGDATA = S_capture.STRINGDATA
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_after
S_after = S_expected
S_after.STRINGDATA = S.STRINGDATA
$heap_graph(S_after) = $heap_graph(S)
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
$drive_steps(S,2) = $drive_steps(S_expected,1)
S_done = $drive_steps(S_after,1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
$retained_outputs_only(S_done.EVENTS)
''')
    # Bind concrete measured source facts before the checks that consume them.
    facts = [f'i = {index}', f'b_reference = {str(reference).lower()}',
             f'pvalue_base = PSTRING_CARRIER (REQUEST_STRING {identity}) ($ptascii("{text}"))',
             f'pvalue_raw = PSTRING ($ptascii("{raw}"))',
             f'pvalue_byte = PSTRING_CARRIER INTERNED_STRING ([{byte}])']
    checks[2:2] = facts
    data = '[$ptascii("512"),$ptascii("10")' + (',$ptascii("10bc")' if reference else '') + ']'
    checks += [f'S_capture.STRINGDATA = {data}',
               '$retained_outputs(S_done.EVENTS) = $ptascii(' + json.dumps(CASES[int(reference)]['expected_stdout']) + ')']
    if reference:
        checks += lines(r'''
$lookup(S_capture.ENV,$ptascii("alias")) = (n_key)
S_capture.REFCELLS = [n_key]
$lookup(S.ENV,$ptascii("alias")) = (n_key)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current =/= n_key
S.STORE[n_current] = DEFINED (PINT 3)
$heap_owners($heap_graph(S),HCELL n_key) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
expression_left = NExprBinaryOpConcat expression_cast expression_literal metadata_left
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_literal)
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
$origin_node(S_capture.SOURCES,porigin_literal) = (expression_literal)
$string_read_allocated_value(S_capture,porigin_cast,PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("10")))
~$string_read_allocated_value(S_capture,porigin_cast,pvalue_base)
$concat_constant(S_capture,(porigin_cast)) = false
$concat_constant(S_capture,(porigin_literal)) = true
''')
    else:
        checks += lines(r'''
$lookup(S.ENV,$ptascii("key")) = (n_key)
S_capture.REFCELLS = eps /\ S.REFCELLS = eps
$heap_owners($heap_graph(S),HCELL n_key) = 1
porigin_cast = porigin_left
expression_cast = expression_left
''')
    checks += lines(r'''
expression_cast = NExprCastString expression_integer metadata_cast
expression_integer = NScalarInt (INTEGER 10) metadata_integer
porigin_cast = PORIGIN n_unit pcpath_cast
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_integer)
porigin_integer = PORIGIN n_unit pcpath_integer
$compiled_read(S_capture,porigin_integer) = (PINT 10)
$compiled_identity_value(S_capture,porigin_integer) = (PINT 10)
''')
    derived_start = len(checks)
    checks += lines(r'''
S_later = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("10"),$ptascii("10bc")]]
$string_read_raw_saved(S_later,pstringread) = (i)
$string_read_source(S_later,pstringread)
$string_read_ready(S_later,pstringread)
$string_read_resume(S_later,pstringread) = S_later[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
S_stale = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("unrelated")]]
$string_read_allocated_base(S_stale,porigin_base,pvalue_base)
$string_read_raw_capture(S_stale,poperand,pvalue_base) = eps
$string_read_plan(S_stale) = eps
$string_bytes(pvalue_base) = (n_base_bytes*)
S_equal = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [n_base_bytes*]]
pvalue_equal = PSTRING_CARRIER (REQUEST_STRING (|S_capture.STRINGDATA|)) n_base_bytes*
$string_carrier_valid(S_equal,pvalue_base) /\ $string_carrier_valid(S_equal,pvalue_equal)
$string_same(pvalue_base,pvalue_equal) = (false)
$string_read_raw_capture(S_equal,poperand,pvalue_equal) = eps
$string_read_raw_saved(S_equal,pstringread[.READ.BASE = pvalue_equal]) = eps
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([49,0,98])
S_nul = S[.STRINGDATA = S.STRINGDATA ++ [[49,0,98]]]
$string_carrier_valid(S_nul,pvalue_nul)
$string_read_allocated_leading(S_nul,pvalue_nul,pvalue_raw) = eps
~$string_read_allocated_base(S_nul,porigin_base,pvalue_nul)
S_empty_emitted = $string_concat(S,pvalue_base,PSTRING_CARRIER INTERNED_STRING eps,false,false)
S_empty_emitted = S[.RESULT = KNOWN pvalue_base]
S_empty_constant = $string_concat(S,pvalue_base,PSTRING_CARRIER INTERNED_STRING eps,false,true)
S_empty_constant = S[.STRINGDATA = S.STRINGDATA ++ [n_base_bytes*]][.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) n_base_bytes*)]
~$string_read_allocated_base(S_capture,porigin_base,PSTRING ($ptascii("10")))
~$string_read_allocated_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("10")))
S_wrong_registry = S_capture[.STRINGDATA = [$ptascii("wrong")]]
~$string_carrier_valid(S_wrong_registry,pvalue_base)
~$string_read_allocated_base(S_wrong_registry,porigin_base,pvalue_base)
$string_read_plan(S_wrong_registry) = eps
~$string_read_allocated_base(S_capture[.SOURCES = eps],porigin_base,pvalue_base)
~$string_read_allocated_base(S_capture[.CODE = eps],porigin_base,pvalue_base)
~$string_read_allocated_base(S_capture[.POOLS = eps],porigin_base,pvalue_base)
$string_read_plan(S_capture[.ORIGIN = eps]) = eps
$string_read_plan(S_capture[.CVS = eps]) = eps
$string_read_plan(S_capture[.ENV = eps]) = eps
~$string_read_source(S[.ORIGIN = eps],pstringread)
~$string_read_source(S,pstringread[.READ.LINE = $(z_key + 1)])
~$string_read_source(S,pstringread[.PHASE = STRING_LEADING $(i + 1)])
''')
    for update in ('.BASECELL = (n_key)', '.KEYCELL = eps', '.READ.PHASE = KEY_CV',
                   '.READ.INPUT = KNOWN pvalue_raw',
                   '.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("key")) z_key)'):
        checks += [f'$string_read_raw_saved(S,pstringread[{update}]) = eps',
                   f'~$string_read_source(S,pstringread[{update}])']
    for value in ('PSTRING eps', 'PSTRING ($ptascii("word"))', 'PSTRING ($ptascii("1.5x"))',
                  'PSTRING ($ptascii("9223372036854775808x"))', 'PSTRING ([49,0,120])'):
        checks.append(f'$string_read_allocated_leading(S,pvalue_base,{value}) = eps')
    for node in ('base', 'left', 'cast', 'integer'):
        for label, update in (
                ('code', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} 0 false) :: pcode.EXPRESSIONS]]'),
                ('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]')):
            name = f'S_bad_{node}_{label}'
            checks += [f'{name} = S_capture[{update}]',
                       f'~$string_read_allocated_base({name},porigin_base,pvalue_base)',
                       f'$string_read_plan({name}) = eps']
    for node in ('base', 'left', 'cast'):
        name = 'S_folded_' + node
        checks += [f'{name} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} z_left true) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_allocated_base({name},porigin_base,pvalue_base)']
    for integer in (0, 9, 11, 9223372036854775808):
        name = 'S_changed_integer_' + str(integer)
        checks += [f'{name} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_integer (NScalarInt (INTEGER {integer}) metadata_integer)) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({name},porigin_base,pvalue_base)']
    body = PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks)
    return body, len(checks), len(checks) - derived_start


def render_reference(program, filename_b64):
    return render(program, filename_b64, True)
