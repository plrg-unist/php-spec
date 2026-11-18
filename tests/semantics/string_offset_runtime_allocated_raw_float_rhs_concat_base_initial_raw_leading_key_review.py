"""Reached one-row FLOAT RHS allocation and frozen raw-key continuations."""

import json

from string_offset_retained_carrier_protocol import PREFIX, lines, seek
from string_offset_runtime_allocated_raw_float_rhs_concat_base_initial_raw_leading_key_cases import CASES


def front(program, filename_b64, reference=False):
    identity = 5 if reference else 3
    text = '-10.5bcde12.5' if reference else '420'
    left = '-10.5bcde' if reference else '42'
    right = '12.5' if reference else '0'
    bits = 4623226492472524800 if reference else 0
    index = 11 if reference else 2
    rows = ['512', '-10.5', '-10.5bc', left, right, text] if reference else ['512', left, right, text]
    registry = '[' + ','.join('$ptascii(' + json.dumps(row) + ')' for row in rows) + ']'
    old = 'def $retained_frontier(S, 0) = ($string_read_plan(S) =/= eps)'
    assert PREFIX.count(old) == 1
    prefix = PREFIX.replace(old, f'''def $retained_frontier(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING {identity}) ($ptascii("{text}")))
  -- if poperand = VARIABLE ($ptascii("key")) z''')
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture')
    checks += [f'i = {index}', f'z_key = {18 if reference else 12}',
               f'b_reference = {str(reference).lower()}',
               f'pvalue_base = PSTRING_CARRIER (REQUEST_STRING {identity}) ($ptascii("{text}"))',
               f'pvalue_left = PSTRING_CARRIER (REQUEST_STRING {identity-2}) ($ptascii("{left}"))',
               f'pvalue_right = PSTRING_CARRIER (REQUEST_STRING {identity-1}) ($ptascii("{right}"))',
               f'pvalue_raw = PSTRING ($ptascii("{index}x"))',
               f'pvalue_byte = PSTRING_CARRIER INTERNED_STRING ([{46 if reference else 48}])',
               f'S_capture.STRINGDATA = {registry}'] + lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand z_key KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) z_key
S_capture.RESULT = KNOWN pvalue_base
S_capture.COMPLETION = NORMAL /\ S_capture.CONSTCONTEXT = eps
S_capture.ORIGIN = (porigin_site)
$origin_child((porigin_site),[PCFIELD 0]) = (porigin_base)
$origin_node(S_capture.SOURCES,porigin_base) = (expression_base)
expression_base = NExprBinaryOpConcat expression_left expression_right metadata_base
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
expression_right = NExprCastString expression_right_number metadata_right
expression_right_number = NScalarFloat (FLOAT text_right_bits) metadata_right_number
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_number)
$origin_node(S_capture.SOURCES,porigin_right_number) = (expression_right_number)
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
$string_carrier_valid(S_capture,pvalue_base)
$string_carrier_valid(S_capture,pvalue_left)
$string_carrier_valid(S_capture,pvalue_right)
$string_read_allocated_base(S_capture,porigin_left,pvalue_left)
$string_read_allocated_value(S_capture,porigin_right,pvalue_right)
$string_read_runtime_value(S_capture,porigin_base) = eps
$string_read_runtime_value(S_capture,porigin_right) = eps
$concat_constant(S_capture,(porigin_left)) = false
$concat_constant(S_capture,(porigin_right)) = false
''')
    checks += [f'text_right_bits = "{bits:016x}"',
               f'$compiled_read(S_capture,porigin_right_number) = (PFLOAT {bits})',
               f'$string_read_runtime_value(S_capture,porigin_right_number) = (PFLOAT {bits})',
               f'$number_text(NFLOAT {bits},14) = ($ptascii("{right}"),false)']
    if reference:
        checks += lines(r'''
~$string_read_allocated_value(S_capture,porigin_left,pvalue_left)
expression_left = NExprBinaryOpCoalesce expression_selected expression_skipped metadata_left
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_selected)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_selected) = (expression_selected)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
expression_selected = NExprTernary expression_chain ABSENT expression_inner_skipped metadata_selected
$origin_child((porigin_selected),[PCFIELD 0]) = (porigin_chain)
$origin_node(S_capture.SOURCES,porigin_chain) = (expression_chain)
$string_read_allocated_base(S_capture,porigin_selected,pvalue_left)
~$string_read_allocated_value(S_capture,porigin_selected,pvalue_left)
$string_read_allocated_value(S_capture,porigin_chain,pvalue_left)
$truth(S_capture,pvalue_left)
''')
    else:
        checks += lines(r'''
expression_left = NExprCastString (NScalarInt (INTEGER 42) metadata_left_number) metadata_left
$string_read_allocated_value(S_capture,porigin_left,pvalue_left)
''')
    for node in ('base', 'left', 'right', 'right_number'):
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    for node in ('base', 'left', 'right'):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},false))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = eps']
    checks += ['$precision_value(S_capture) = 14']
    checks += [f'S_before_right = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:{identity-1}]]',
               f'S_right = S_before_right[.STRINGDATA = S_before_right.STRINGDATA ++ [$ptascii("{right}")]][.RESULT = KNOWN pvalue_right]',
               f'$cast_apply(S_before_right,CASTSTRING,PFLOAT {bits},z_right) = S_right',
               f'$string_concat(S_right,pvalue_left,pvalue_right,false,false) = S_right[.STRINGDATA = S_right.STRINGDATA ++ [$ptascii("{text}")]][.RESULT = KNOWN pvalue_base]']
    return prefix, checks


def render(program, filename_b64, reference=False):
    prefix, checks = front(program, filename_b64, reference=reference)
    checks += lines(r'''
$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_key),KEYREF b_reference,PHASE STRING_LEADING i}
pkeyread.BASE = pvalue_base /\ pkeyread.INPUT = poperand
pkeyread.VALUE = pvalue_raw /\ pkeyread.LINE = z_key
pkeyread.SITE = porigin_site
pkeyread.OWNERS = BASE_VALUE (KNOWN pvalue_base)
pkeyread.PHASE = KEY_NULL
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
S_capture.STORE[n_key] = DEFINED pvalue_raw
S_capture.STORE[n_got] = DEFINED (PINT 99)
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
$string_read_raw_saved(S_capture,pstringread) = (i)
$string_read_source(S_capture,pstringread)
$string_read_provider_ready(S_capture,pstringread)
$key_read_owners_source(S_capture,pkeyread)
$key_read_input_source(S_capture,pkeyread)
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
S.STRINGDATA = S_capture.STRINGDATA
S.STORE[n_got] = DEFINED (PINT 99)
S.STORE[n_key] = DEFINED (PSTRING perrorcall.MESSAGE)
$string_read_raw_saved(S,pstringread) = (i)
$string_read_source(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_ready(S,pstringread)
$string_read_key_current(S,pstringread) = eps
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_after
S_after = S_expected
$heap_graph(S_after) = $heap_graph(S)
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
$drive_steps(S,2) = $drive_steps(S_expected,1)
S_done = $drive_steps(S_after,1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
$retained_outputs_only(S_done.EVENTS)
''')
    checks += ['$retained_outputs(S_done.EVENTS) = $ptascii(' + json.dumps(CASES[int(reference)]['expected_stdout']) + ')']
    if reference:
        checks += lines(r'''
$lookup(S_capture.ENV,$ptascii("alias")) = (n_key)
S_capture.REFCELLS = [n_key]
$lookup(S.ENV,$ptascii("alias")) = (n_key)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current =/= n_key
S.STORE[n_current] = DEFINED (PINT 12)
$heap_owners($heap_graph(S),HCELL n_key) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
$string_byte_read(S,$ptascii("-10.5bcde12.5"),12,z_key) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([53]))]
''')
    else:
        checks += lines(r'''
$lookup(S.ENV,$ptascii("key")) = (n_key)
S_capture.REFCELLS = eps /\ S.REFCELLS = eps
$heap_owners($heap_graph(S),HCELL n_key) = 1
''')
    derived_start = len(checks)
    checks += lines(r'''
S_later = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback")]]
$string_read_raw_saved(S_later,pstringread) = (i)
$string_read_ready(S_later,pstringread)
$string_read_resume(S_later,pstringread) = S_later[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
S_stale = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("unrelated")]]
$string_read_allocated_value(S_stale,porigin_base,pvalue_base)
$string_read_raw_capture(S_stale,poperand,pvalue_base) = eps
$string_read_plan(S_stale) = eps
$string_bytes(pvalue_base) = (n_base*)
S_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [n_base*]]
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING (|S_capture.STRINGDATA|)) n_base*
$string_carrier_valid(S_clone,pvalue_clone)
$string_same(pvalue_base,pvalue_clone) = (false)
~$string_read_allocated_value(S_clone,porigin_base,pvalue_clone)
$string_read_raw_capture(S_clone[.RESULT = KNOWN pvalue_clone],poperand,pvalue_clone) = eps
S_right_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprCastString expression_right_number eps)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_value(S_right_source,porigin_base,pvalue_base)
S_number_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_number (NScalarFloat (FLOAT text_right_bits) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_value(S_number_source,porigin_base,pvalue_base)
S_number_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right_number PNULL) :: ppool.CONSTANTS]]]
~$string_read_allocated_value(S_number_pool,porigin_base,pvalue_base)
S_live_precision = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
~$string_read_allocated_value(S_live_precision,porigin_base,pvalue_base)
$string_read_plan(S_live_precision) = eps
S_post_precision = S[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$string_read_raw_saved(S_post_precision,pstringread) = eps
S_budget = S_capture[.COMPLETION = BUDGET]
~$string_read_allocated_value(S_budget,porigin_base,pvalue_base)
$string_read_allocated_base(S_budget,porigin_base,pvalue_base)
$string_read_plan(S_budget) = (pstringread)
S_const = S_capture[.CONSTCONTEXT = ({ORIGIN porigin_base,LINE z_key,FACTS eps})]
~$string_read_allocated_value(S_const,porigin_base,pvalue_base)
''')
    for node in ('base', 'left', 'right'):
        for label, line, folded in [('line', '0', 'false'), ('folded', f'z_{node}', 'true')]:
            state = f'S_bad_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {folded}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_value({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    for node in ('base', 'left', 'right', 'right_number'):
        state = f'S_bad_precision_{node}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_value({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    for update in ('.BASECELL = (n_key)', '.KEYCELL = eps', '.READ.PHASE = KEY_CV',
                   '.READ.OWNERS = BASE_VALUE (KNOWN pvalue_left)'):
        checks += [f'$string_read_raw_saved(S,pstringread[{update}]) = eps',
                   f'~$string_read_source(S,pstringread[{update}])']
    body = prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks)
    return body, len(checks), len(checks) - derived_start
