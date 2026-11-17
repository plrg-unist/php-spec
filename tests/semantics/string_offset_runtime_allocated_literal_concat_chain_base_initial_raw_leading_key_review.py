"""Reached literal CONCAT chains keep their exact temporary and saved offset."""

import json

from string_offset_retained_carrier_protocol import PREFIX, lines, seek
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_cases import CASES


def render(program, filename_b64, extra_program=None, extra_filename_b64=None, reference=False):
    index = 3 if reference else 0
    byte = 99 if reference else 49
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture')
    checks += [f'i = {index}', f'b_reference = {str(reference).lower()}',
               f'z_key = {18 if reference else 12}',
               f'pvalue_byte = PSTRING_CARRIER INTERNED_STRING ([{byte}])',
               f'pvalue_raw = PSTRING ($ptascii("{index}x"))'] + lines(r'''
pvalue_base = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("10bcde"))
S_capture.RESULT = KNOWN pvalue_base
S_capture.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10bc"),$ptascii("10bcde")]
S_capture.TODO = (KEY_READ_DIM poperand z_key KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) z_key
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
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
$string_read_raw_saved(S_capture,pstringread) = (i)
$string_read_source(S_capture,pstringread)
$string_read_provider_ready(S_capture,pstringread)
$key_read_owners_source(S_capture,pkeyread)
$key_read_input_source(S_capture,pkeyread)
$task_nodes(STRING_READ_RESULT pstringread) = eps
$base_nodes(pkeyread.OWNERS) = eps
$heap_valid($heap_graph(S_capture))
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
''')
    if reference:
        checks += lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_chain expression_skipped metadata_base)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_chain)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
$compiled_read(S_capture,porigin_skipped) = eps
$lookup(S_capture.ENV,$ptascii("alias")) = (n_key)
S_capture.REFCELLS = [n_key]
''')
    else:
        checks += ['porigin_chain = porigin_base', 'S_capture.REFCELLS = eps']
    checks += lines(r'''
$origin_node(S_capture.SOURCES,porigin_chain) = (expression_chain)
expression_chain = NExprBinaryOpConcat expression_inner expression_suffix metadata_chain
expression_inner = NExprBinaryOpConcat expression_cast expression_inner_suffix metadata_inner
expression_cast = NExprCastString expression_integer metadata_cast
expression_integer = NScalarInt (INTEGER 10) metadata_integer
expression_inner_suffix = NScalarString (BYTES text_inner_suffix) metadata_inner_suffix
expression_suffix = NScalarString (BYTES text_suffix) metadata_suffix
$base64(text_inner_suffix) = $ptascii("bc")
$base64(text_suffix) = $ptascii("de")
$origin_child((porigin_chain),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_chain),[PCFIELD 1]) = (porigin_suffix)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_inner),[PCFIELD 1]) = (porigin_inner_suffix)
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_integer)
pvalue_cast = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("10"))
pvalue_inner = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("10bc"))
$string_read_allocated_value(S_capture,porigin_cast,pvalue_cast)
$string_read_allocated_value(S_capture,porigin_inner,pvalue_inner)
$string_read_allocated_value(S_capture,porigin_chain,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$string_read_runtime_value(S_capture,porigin_chain) = eps
$concat_constant(S_capture,(porigin_cast)) = false
$concat_constant(S_capture,(porigin_inner_suffix)) = true
$concat_constant(S_capture,(porigin_inner)) = false
$concat_constant(S_capture,(porigin_suffix)) = true
''')
    nodes = dict(base=None, chain='expression_chain', inner='expression_inner',
                 cast='expression_cast', integer='expression_integer',
                 inner_suffix='expression_inner_suffix', suffix='expression_suffix')
    for node, expression in nodes.items():
        checks.append(f'porigin_{node} = PORIGIN n_unit pcpath_{node}')
        if expression:
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{node}) = ({expression})')
        checks.append(f'$compiled_precision(S_capture,(porigin_{node})) = (14)')
    emitted = ['base', 'chain', 'inner', 'cast'] if reference else ['chain', 'inner', 'cast']
    for node in emitted:
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},false))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = eps',
                   f'$compiled_identity_value(S_capture,porigin_{node}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{node}) = eps']
    for node, value in [('integer', 'PINT 10'),
                        ('inner_suffix', 'PSTRING ($ptascii("bc"))'),
                        ('suffix', 'PSTRING ($ptascii("de"))')]:
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},true))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = ({value})',
                   f'$compiled_identity_value(S_capture,porigin_{node}) = ({value})']
    checks += lines(r'''
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
    checks += ['$retained_outputs(S_done.EVENTS) = $ptascii(' +
               json.dumps(CASES[int(reference)]['expected_stdout']) + ')']
    if reference:
        checks += lines(r'''
$lookup(S.ENV,$ptascii("alias")) = (n_key)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current =/= n_key
S.STORE[n_current] = DEFINED (PINT 4)
$heap_owners($heap_graph(S),HCELL n_key) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
$string_byte_read(S,$ptascii("10bcde"),4,z_key) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([100]))]
''')
    else:
        checks += ['$lookup(S.ENV,$ptascii("key")) = (n_key)', 'S.REFCELLS = eps']
    derived_start = len(checks)
    checks += lines(r'''
S_later = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("10bcde")]]
$string_read_raw_saved(S_later,pstringread) = (i)
$string_read_source(S_later,pstringread)
$string_read_ready(S_later,pstringread)
$string_read_resume(S_later,pstringread) = S_later[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
S_stale = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("unrelated")]]
$string_read_allocated_base(S_stale,porigin_base,pvalue_base)
$string_read_raw_capture(S_stale,poperand,pvalue_base) = eps
$string_read_plan(S_stale) = eps
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("10bcde"))
S_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("10bcde")]]
$string_carrier_valid(S_clone,pvalue_clone)
$string_same(pvalue_clone,pvalue_base) = (false)
~$string_read_allocated_base(S_clone,porigin_base,pvalue_clone)
$string_read_raw_capture(S_clone[.RESULT = KNOWN pvalue_clone],poperand,pvalue_clone) = eps
$string_read_raw_saved(S_clone,pstringread[.READ.BASE = pvalue_clone]) = eps
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 4) ([49,48,0,98])
S_nul = S[.STRINGDATA = S.STRINGDATA ++ [[49,48,0,98]]]
$string_carrier_valid(S_nul,pvalue_nul)
$string_read_allocated_leading(S_nul,pvalue_nul,pvalue_raw) = eps
~$string_read_allocated_base(S_nul,porigin_base,pvalue_nul)
''')
    for node in emitted:
        for label, flag, line in [('line', 'false', '0'), ('folded', 'true', f'z_{node}')]:
            name = f'S_bad_{node}_{label}'
            checks += [f'{name} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_base({name},porigin_base,pvalue_base)',
                       f'$string_read_plan({name}) = eps']
    for node in nodes:
        name = f'S_bad_{node}_precision'
        checks += [f'{name} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_base({name},porigin_base,pvalue_base)']
    for node, value in [('integer', 'PSTRING ($ptascii("10"))'),
                        ('inner_suffix', 'PSTRING ($ptascii("wrong"))'),
                        ('suffix', 'PSTRING ($ptascii("wrong"))')]:
        name = f'S_bad_{node}_pool'
        checks += [f'{name} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{node} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_base({name},porigin_base,pvalue_base)']
    for node in ('inner_suffix', 'suffix'):
        checks += [f'S_flag_{node} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} z_{node} false) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_allocated_base(S_flag_{node},porigin_base,pvalue_base)']
    for identity, data in enumerate(['[$ptascii("512"),$ptascii("wrong"),$ptascii("10bc"),$ptascii("10bcde")]',
                                     '[$ptascii("512"),$ptascii("10"),$ptascii("wrong"),$ptascii("10bcde")]',
                                     '[$ptascii("512"),$ptascii("10"),$ptascii("10bc"),$ptascii("wrong")]']):
        checks += [f'S_registry_{identity} = S_capture[.STRINGDATA = {data}]',
                   f'~$string_read_allocated_base(S_registry_{identity},porigin_base,pvalue_base)']
    for update in ('.BASECELL = (n_key)', '.KEYCELL = eps', '.READ.PHASE = KEY_CV',
                   '.READ.OWNERS = BASE_VALUE (KNOWN pvalue_inner)'):
        checks += [f'$string_read_raw_saved(S,pstringread[{update}]) = eps',
                   f'~$string_read_source(S,pstringread[{update}])']
    for label, update in (
            ('sources', '.SOURCES = eps'), ('code', '.CODE = eps'), ('pools', '.POOLS = eps'),
            ('constant_context', '.CONSTCONTEXT = ({ORIGIN porigin_base,LINE z_key,FACTS eps})')):
        name = 'S_missing_' + label
        checks += [f'{name} = S_capture[{update}]',
                   f'~$string_read_allocated_base({name},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({name},poperand,pvalue_base) = eps']
    for node, expression in (
            ('inner', 'NExprBinaryOpConcat expression_cast expression_inner_suffix eps'),
            ('cast', 'NExprCastString expression_integer eps'),
            ('integer', 'NScalarInt (INTEGER 10) eps'),
            ('inner_suffix', 'NScalarString (BYTES text_inner_suffix) eps'),
            ('suffix', 'NScalarString (BYTES text_suffix) eps')):
        name = 'S_shadow_' + node
        checks += [f'{name} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({name},porigin_base,pvalue_base)']
    if reference:
        checks += lines(r'''
porigin_skipped = PORIGIN n_unit pcpath_skipped
S_skipped = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_skipped 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_skipped,porigin_base,pvalue_base)
$string_read_raw_capture(S_skipped,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
''')
    if extra_program is not None:
        checks += ['S_extra_initial = $php_run(' + extra_program + ',0,' + json.dumps(extra_filename_b64) + ')',
                   'S_extra_initial.COMPLETION = BUDGET'] + seek('S_extra_initial', 0, 'S_extra') + lines(r'''
S_extra.RESULT = KNOWN pvalue_extra
pvalue_extra = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("10bcde"))
S_extra.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10bc"),$ptascii("10bcde"),$ptascii("10bcde")]
S_extra.ORIGIN = (porigin_extra_site)
$origin_child((porigin_extra_site),[PCFIELD 0]) = (porigin_extra)
$origin_node(S_extra.SOURCES,porigin_extra) = (NExprBinaryOpConcat expression_extra_left (NScalarString (BYTES "") metadata_extra_empty) metadata_extra)
$origin_child((porigin_extra),[PCFIELD 0]) = (porigin_extra_left)
$origin_child((porigin_extra),[PCFIELD 1]) = (porigin_extra_empty)
$concat_constant(S_extra,(porigin_extra_left)) = false
$concat_constant(S_extra,(porigin_extra_empty)) = true
$string_read_allocated_value(S_extra,porigin_extra_left,pvalue_base)
$string_read_allocated_base(S_extra,porigin_extra,pvalue_extra)
~$string_read_allocated_base(S_extra,porigin_extra,pvalue_base)
S_extra_prefix = S_extra[.STRINGDATA = S_extra.STRINGDATA[0:4]]
$string_concat(S_extra_prefix,pvalue_base,PSTRING_CARRIER INTERNED_STRING eps,false,true) = S_extra_prefix[.STRINGDATA = S_extra.STRINGDATA][.RESULT = KNOWN pvalue_extra]
$string_concat(S_extra_prefix,pvalue_base,PSTRING_CARRIER INTERNED_STRING eps,false,false) = S_extra_prefix[.RESULT = KNOWN pvalue_base]
S_extra_done = $drive_steps(S_extra,1000)
S_extra_done.COMPLETION = NORMAL /\ S_extra_done.EXITSTATUS = 0
$retained_outputs_only(S_extra_done.EVENTS)
''')
        checks += ['$retained_outputs(S_extra_done.EVENTS) = $ptascii(' +
                   json.dumps(CASES[0]['expected_stdout']) + ')']
    body = PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks)
    return body, len(checks), len(checks) - derived_start


def render_reference(program, filename_b64):
    return render(program, filename_b64, reference=True)
