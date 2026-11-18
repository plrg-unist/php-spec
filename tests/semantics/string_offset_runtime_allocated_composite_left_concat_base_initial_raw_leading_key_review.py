"""Measured composite LEFT BASE and literal suffix allocation certificates."""

import json

from string_offset_retained_carrier_protocol import PREFIX, lines, seek
from string_offset_runtime_allocated_composite_left_concat_base_initial_raw_leading_key_cases import CASES


def front(program, filename_b64, reference=False):
    identity = 4 if reference else 2
    text = '-10.5bcdefg' if reference else '0YZ'
    left = '-10.5bcde' if reference else '0'
    suffix = 'fg' if reference else 'YZ'
    index = 9 if reference else 1
    registry = '[$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),$ptascii("-10.5bcde"),$ptascii("-10.5bcdefg")]' if reference else '[$ptascii("512"),$ptascii("0"),$ptascii("0YZ")]'
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
               f'pvalue_left = PSTRING_CARRIER (REQUEST_STRING {identity-1}) ($ptascii("{left}"))',
               f'pvalue_raw = PSTRING ($ptascii("{index}x"))',
               f'pvalue_byte = PSTRING_CARRIER INTERNED_STRING ([{102 if reference else 89}])',
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
expression_right = NScalarString (BYTES text_right) metadata_right
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
$string_carrier_valid(S_capture,pvalue_base)
$string_carrier_valid(S_capture,pvalue_left)
$string_read_allocated_base(S_capture,porigin_left,pvalue_left)
~$string_read_allocated_value(S_capture,porigin_left,pvalue_left)
$string_read_runtime_value(S_capture,porigin_left) = eps
$concat_constant(S_capture,(porigin_left)) = false
$concat_constant(S_capture,(porigin_right)) = true
''') + [f'$base64(text_right) = $ptascii("{suffix}")',
       f'$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("{suffix}")))',
       f'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("{suffix}"))',
       '$string_read_runtime_value(S_capture,porigin_right) = (pvalue_right)',
       f'S_before = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:{identity}]]',
       f'$string_concat(S_before,pvalue_left,pvalue_right,false,true) = S_before[.STRINGDATA = S_before.STRINGDATA ++ [$ptascii("{text}")]][.RESULT = KNOWN pvalue_base]']
    if reference:
        checks += lines(r'''
expression_left = NExprBinaryOpCoalesce expression_selected expression_outer_skipped metadata_left
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_selected)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_outer_skipped)
$origin_node(S_capture.SOURCES,porigin_selected) = (expression_selected)
$origin_node(S_capture.SOURCES,porigin_outer_skipped) = (expression_outer_skipped)
$string_read_literal_bytes(expression_outer_skipped) = eps
$compiled_read(S_capture,porigin_outer_skipped) = eps
expression_selected = NExprTernary expression_chain ABSENT expression_skipped metadata_selected
$origin_child((porigin_selected),[PCFIELD 0]) = (porigin_chain)
$origin_child((porigin_selected),[PCFIELD 2]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_chain) = (expression_chain)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
expression_chain = NExprBinaryOpConcat expression_inner expression_suffix metadata_chain
expression_inner = NExprBinaryOpConcat expression_cast expression_inner_suffix metadata_inner
$origin_child((porigin_chain),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_chain),[PCFIELD 1]) = (porigin_suffix)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_inner),[PCFIELD 1]) = (porigin_inner_suffix)
$origin_node(S_capture.SOURCES,porigin_inner) = (expression_inner)
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
$origin_node(S_capture.SOURCES,porigin_inner_suffix) = (expression_inner_suffix)
$origin_node(S_capture.SOURCES,porigin_suffix) = (expression_suffix)
$string_read_allocated_base(S_capture,porigin_selected,pvalue_left)
~$string_read_allocated_value(S_capture,porigin_selected,pvalue_left)
$string_read_allocated_value(S_capture,porigin_chain,pvalue_left)
$truth(S_capture,pvalue_left)
''')
    else:
        checks += lines(r'''
expression_left = NExprTernary expression_condition expression_cast expression_skipped metadata_left
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_cast)
$origin_child((porigin_left),[PCFIELD 2]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_condition) = (expression_condition)
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
expression_condition = NExprCastInt (NScalarInt (INTEGER 1) metadata_condition_atom) metadata_condition
porigin_selected = porigin_cast
expression_selected = expression_cast
$string_read_runtime_value(S_capture,porigin_condition) = (PINT 1)
$string_read_allocated_value(S_capture,porigin_cast,pvalue_left)
~$truth(S_capture,pvalue_left)
''')
    checks += lines(r'''
expression_cast = NExprCastString expression_number metadata_cast
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_number)
$origin_node(S_capture.SOURCES,porigin_number) = (expression_number)
''')
    if reference:
        checks += lines(r'''
expression_number = NExprUnaryMinus expression_atom metadata_number
expression_atom = NScalarFloat (FLOAT "4025000000000000") metadata_atom
$origin_child((porigin_number),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$compiled_read(S_capture,porigin_number) = (PFLOAT 13845472629420457984)
$string_read_runtime_value(S_capture,porigin_number) = (PFLOAT 13845472629420457984)
''')
    else:
        checks += lines(r'''
expression_number = NScalarFloat (FLOAT "0000000000000000") metadata_number
$compiled_read(S_capture,porigin_number) = (PFLOAT 0)
$string_read_runtime_value(S_capture,porigin_number) = (PFLOAT 0)
''')
    nodes = ['base', 'left', 'right', 'selected', 'cast', 'number', 'skipped']
    if reference:
        nodes += ['chain', 'inner', 'suffix', 'inner_suffix', 'outer_skipped', 'atom']
    else:
        nodes += ['condition']
    for node in nodes:
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    emitted = ['base', 'left', 'selected', 'cast'] + (['chain', 'inner'] if reference else ['condition'])
    for node in emitted:
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},false))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = eps']
    checks += lines(r'''
$code_expression(pcode.EXPRESSIONS,pcpath_right) = ((z_right,true))
$(z_right > 0)
$precision_value(S_capture) = 14
''')
    return prefix, checks


def render(program, filename_b64, reference=False):
    prefix, checks = front(program, filename_b64, reference=reference)
    checks += lines(r'''
$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$string_read_runtime_value(S_capture,porigin_base) = eps
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
S.STORE[n_current] = DEFINED (PINT 10)
$heap_owners($heap_graph(S),HCELL n_key) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
$string_byte_read(S,$ptascii("-10.5bcdefg"),10,z_key) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([103]))]
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
$string_read_source(S_later,pstringread)
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
$string_read_raw_saved(S_clone,pstringread[.READ.BASE = pvalue_clone]) = eps
S_nul = S[.STRINGDATA = S.STRINGDATA ++ [[48,0,89]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([48,0,89])
$string_carrier_valid(S_nul,pvalue_nul)
$string_read_allocated_leading(S_nul,pvalue_nul,pvalue_raw) = eps
~$string_read_allocated_value(S_nul,porigin_base,pvalue_nul)
S_right_flag = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right z_right false) :: pcode.EXPRESSIONS]]]
$string_read_allocated_base(S_right_flag,porigin_left,pvalue_left)
~$string_read_allocated_value(S_right_flag,porigin_base,pvalue_base)
$string_read_plan(S_right_flag) = eps
S_right_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]]
~$string_read_allocated_value(S_right_pool,porigin_base,pvalue_base)
S_right_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NScalarString (BYTES text_right) eps)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_value(S_right_source,porigin_base,pvalue_base)
S_live_precision = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
~$string_read_allocated_value(S_live_precision,porigin_base,pvalue_base)
$string_read_plan(S_live_precision) = eps
S_post_precision = S[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$string_read_raw_saved(S_post_precision,pstringread) = eps
S_budget = S_capture[.COMPLETION = BUDGET]
~$string_read_allocated_value(S_budget,porigin_base,pvalue_base)
$string_read_allocated_base(S_budget,porigin_base,pvalue_base)
$string_read_plan(S_budget) = (pstringread)
''')
    for node in ('base', 'left', 'selected', 'cast') + (('chain', 'inner') if reference else ('condition',)):
        for label, line, folded in [('line', '0', 'false'), ('folded', f'z_{node}', 'true')]:
            state = f'S_bad_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {folded}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_value({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    for node in ('base', 'left', 'right', 'selected', 'cast', 'number'):
        state = f'S_bad_precision_{node}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_value({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    for update in ('.BASECELL = (n_key)', '.KEYCELL = eps', '.READ.PHASE = KEY_CV',
                   '.READ.OWNERS = BASE_VALUE (KNOWN pvalue_left)'):
        checks += [f'$string_read_raw_saved(S,pstringread[{update}]) = eps',
                   f'~$string_read_source(S,pstringread[{update}])']
    if reference:
        checks += lines(r'''
expression_outer_skipped = NExprTernary expression_unused_condition expression_unused_true expression_unused_false metadata_unused
$origin_child((porigin_outer_skipped),[PCFIELD 0]) = (porigin_unused_condition)
$origin_child((porigin_unused_condition),[PCFIELD 0]) = (porigin_unused_atom)
porigin_unused_atom = PORIGIN n_unit pcpath_unused_atom
$origin_node(S_capture.SOURCES,porigin_unused_atom) = (NScalarInt (INTEGER 1) metadata_unused_atom)
S_unused_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_unused_descendant,porigin_left,pvalue_left)
$string_read_allocated_value(S_unused_descendant,porigin_base,pvalue_base)
$string_read_plan(S_unused_descendant) = (pstringread)
S_unused_root = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_outer_skipped (NExprTernary expression_unused_condition expression_unused_true expression_unused_false eps)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_base(S_unused_root,porigin_left,pvalue_left)
~$string_read_allocated_value(S_unused_root,porigin_base,pvalue_base)
$string_read_plan(S_unused_root) = eps
''')
    body = prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks)
    return body, len(checks), len(checks) - derived_start
