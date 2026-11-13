#!/usr/bin/env python3
"""Source-reached NEVER Get exit preserves status and retires its receiver guard."""
import hashlib
import json
from pathlib import Path
import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_void_never_return_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][3]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
SOURCE = ROW['source']
HELPERS = ''

CHECKS = [
    'S.CURRENT = (pcallcontext) /\\ pcallcontext.FUNCTION = porigin_method',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'ppropertyget.OBJECT = n_receiver /\\ ppropertyget.METHOD = porigin_method /\\ ppropertyget.NAME = $ptascii("go")',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "never"]))] /\\ ~pfunction.SIGNATURE.BYREF',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.TYPE = eps',
    '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
    '$property_get_context(S,pcallcontext) /\\ $property_get_frame(S,pcallcontext,pframe)',
    'pexitcall.KIND = INTRINSIC_EXIT /\\ pexitcall.SENT = [KNOWN (PINT 13)]',
    'pexitcall.INDEX = 1 /\\ ~pexitcall.NAMED /\\ pexitcall.OWNER = eps',
    '$exit_selected_valid(S,pexitcall) /\\ $exit_invoke_valid(S,pexitcall)',
    '~$exit_invoke_valid(S,pexitcall[.LINE = $(pexitcall.LINE + 1)])',
    '$task_nodes(EXIT_INVOKE pexitcall) = eps /\\ $call_receiver_roots(pcallcontext) = eps',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_formal)',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
    'S.STORE[n_selector] = DEFINED pvalue_selector',
    '$string_bytes(pvalue_selector) = ($ptascii("go"))',
    'S.EVENTS = [OUTPUT $ptascii("go"),OUTPUT $ptascii(":EXIT;")]',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'S_raw = $exit_receive(S[.TODO = ptask_tail*],pexitcall)',
    'PhpStep: S ~> S_raw',
    'S_raw.COMPLETION = EXITED 13 /\\ S_raw.EXITSTATUS = 13',
    'S_raw.TODO = eps /\\ S_raw.ORIGIN = eps /\\ S_raw.TRACE = eps /\\ S_raw.ERRORORIGIN = eps',
    'S_raw.CURRENT = S.CURRENT /\\ S_raw.FRAMES = S.FRAMES /\\ S_raw.EVENTS = S.EVENTS',
    '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 2',
    'S_unwind = $exit_start_unwind(S_raw,13)',
    'S_unwind.TODO = [EXIT_UNWIND 13] /\\ S_unwind.COMPLETION = NORMAL',
    '$exit_unwind_valid(S_unwind,13)',
    '$heap_owners($heap_graph(S_unwind),HOBJECT n_receiver) = 2',
    'S_zero = $drive(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive(S,1)',
    'S_one = S_unwind[.COMPLETION = BUDGET]',
    '$drive(S_zero[.COMPLETION = NORMAL],1) = S_one',
    '$call_descriptors_valid(S_one) /\\ $heap_valid($heap_graph(S_one))',
    'PhpStep: S_unwind ~> S_parent',
    'S_parent.TODO = [EXIT_UNWIND 13] /\\ S_parent.CURRENT = eps /\\ S_parent.FRAMES = eps',
    '$heap_owners($heap_graph(S_parent),HOBJECT n_receiver) = 1',
    '~$property_get_guard_tasks(S_parent.TODO,n_receiver,ppropertyget.NAME)',
    '$heap_owners($heap_graph(S_parent),HCELL n_formal) = 0',
    'S_done = $drive(S_one[.COMPLETION = NORMAL],16)',
    'S_done.COMPLETION = EXITED 13 /\\ S_done.EXITSTATUS = 13',
    'S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.ORIGIN = eps /\\ S_done.TRACE = eps /\\ S_done.ERRORORIGIN = eps',
    'S_done.EVENTS = S.EVENTS /\\ S_done.STORE[n_selector] = DEFINED pvalue_selector',
    '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
    '$heap_owners($heap_graph(S_done),HCELL n_formal) = 0',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive(S,16) = S_done',
]
CASES = {'named-never-return-get-exit-guard-retirement': {
    'source': SOURCE,
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_method '
              '-- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*'),
    'checks': CHECKS,
}}

def render(case,fixture,filename):
    stage = case['stage']
    text = (HELPERS + '\ndec $stage(pstate) : bool\n'
            'def $stage(S) = true -- if ' + stage + '\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate,nat) : pstate\n'
            'def $seek(S,n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
            'def $seek(S,n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1))) '
            '-- if $(n > 0) /\\ ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + fixture + ',0,' + filename + ')\n'
            '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
            '  -- if S_found = $seek(S_initial,2000)\n'
            '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
            '  -- if S = S_found[.COMPLETION = NORMAL]\n'
            '  -- if ' + stage + '\n')
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in case['checks'])
    return text,len(case['checks']) + 6


if __name__ == '__main__':
    protocol.run(CASES,(Path(__file__),CATALOGUE),fixture_renderer=render,
                 runner_flags=('--sl',))
