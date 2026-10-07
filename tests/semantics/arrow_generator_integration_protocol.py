#!/usr/bin/env python3
"""Independent reached Arrow/Fiber/source retirement on the composed parent."""
import os

import generator_force_close_protocol as driver
import arrow_generator_integration as source

CHILD = b"function ready311(){echo 'R|';}\n\necho\n $x;"
CASES = source.CASES
WATCHED = driver.source.WATCHED + [
    'spec/semantics/117-arrow-compiler.watsup',
    'spec/semantics/118-arrows.watsup',
    'spec/semantics/84-call-integrity.watsup',
    'spec/semantics/281-fibers.watsup',
    'spec/semantics/298-source-stringable-lifetime.watsup',
    'spec/semantics/310-generator-fiber-close.watsup',
    'spec/semantics/311-arrow-generators.watsup',
    'spec/semantics/314-source-expression-emission.watsup',
    'tests/semantics/arrow_generator_integration.py',
    'tests/semantics/arrow_generator_integration_protocol.py',
]
PREFIX = r'''
dec $arrow_integration_phase(pstate,nat) : bool
def $arrow_integration_phase(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = SOURCE_OPERAND_ENTER psourceoperand n
def $arrow_integration_phase(S,1) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
  -- if $origin_node(S.SOURCES,pgenerator.FUNCTION) = (NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 expression metadata)
def $arrow_integration_phase(S,2) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if $origin_node(S.SOURCES,pgenclose.CONTEXT.FUNCTION) = (NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 expression metadata)
def $arrow_integration_phase(S,n) = false -- otherwise
dec $arrow_integration_seek(pstate,nat,nat) : pstate
def $arrow_integration_seek(S,n_phase,n) = S -- if $arrow_integration_phase(S,n_phase)
def $arrow_integration_seek(S,n_phase,n) = S
  -- if ~$arrow_integration_phase(S,n_phase)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $arrow_integration_seek(S,n_phase,0) = S -- if ~$arrow_integration_phase(S,n_phase)
def $arrow_integration_seek(S,n_phase,n) = $arrow_integration_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~$arrow_integration_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $arrow_integration_outputs(pevent*) : ptbytes
def $arrow_integration_outputs(eps) = eps
def $arrow_integration_outputs((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $arrow_integration_outputs(pevent*)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $arrow_integration_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$arrow_integration_phase({state},{phase})']


def valid(state):
    return driver.valid(state) + [f'$call_entry_check({state}) = {state}',
                                 f'$generator_state_valid({state})', f'$fiber_state_valid({state})']


def assertions(checked, path, directory, name):
    frontend = driver.Worker([str(driver.driver.types.PHP), '-n', *driver.driver.types.FLAGS,
                              '-d', 'short_open_tag=1', '-d', 'extension=' + str(driver.ROOT / '.tools/php-file.so'),
                              str(driver.ROOT / 'frontend/worker.php')], directory / 'child-frontend')
    try:
        parsed = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                   'profile': 'cli-raw-85', 'source': driver.driver.b64(CHILD)})
        assert parsed['accepted']
    finally:
        frontend.close()
    adapter = driver.Worker([str(driver.ROOT / '_build/default/adapter/main.exe'), str(driver.ROOT)], directory / 'child-adapter')
    try:
        child = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert child['ok']
    finally:
        adapter.close()
    (directory / 'child.php-fragment').write_bytes(CHILD)
    (directory / 'child-checked.json').write_text(driver.json.dumps(child) + '\n')
    driver.PREFIX += '\ndec $arrow_integration_child() : program\ndef $arrow_integration_child() = ' + child['fixture'] + '\n'
    initial = ('$php_file_startup_run(' + checked['fixture'] + ',10000,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT))
               + ',{REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")})')
    checks = ['S_wait = ' + initial, 'S_wait.COMPLETION = SOURCE_PENDING',
              'S_wait.EVALCONTEXTS = pevalcontext :: eps', 'n_unit = pevalcontext.UNIT',
              'pevalcontext.BYTES = ' + driver.driver.byte_expr(CHILD)]
    checks += r'''
S_wait.ACTIVEFIBER = (n_fiber)
S_wait.CURRENT = (pcallcontext_leaf)
$generator_context_operation(S_wait,pcallcontext_leaf) = (pgeneratorop_leaf)
S_wait.FRAMES = pframe_leaf :: pframe_tail*
S_arrow = $constant_frame_scope(S_wait,pframe_leaf,pframe_tail*)
S_arrow.CURRENT = (pcallcontext_arrow)
$generator_context_operation(S_arrow,pcallcontext_arrow) = (pgeneratorop_arrow)
S_arrow.OBJECTS[pgeneratorop_arrow.OBJECT] = GENERATOR pgenerator_arrow
pgenerator_arrow.CLOSURE = (n_closure)
$function_at(S_arrow.CLOSURETEMPLATES,pgenerator_arrow.FUNCTION) = (pfunction_arrow)
pfunction_arrow.SIGNATURE.RETURNS = [PTBRANCH ([PTBUILTIN "iterable"])]
$call_supported_signature(S_arrow,pfunction_arrow)
$trace_slot(S_arrow,S_arrow.ENV,$ptascii("default")) = POBJECT n_default
$trace_slot(S_wait,S_wait.ENV,$ptascii("default")) = POBJECT n_default
psourceresponse = SOURCE_ACCEPT n_unit pevalcontext.BYTES $arrow_integration_child()
$call_descriptors_valid(S_wait)
$heap_valid($heap_graph(S_wait))
$eval_response_valid(S_wait,psourceresponse)
S_live_owner_bad = S_wait[.EVALCONTEXTS = [pevalcontext[.OWNER = $(pevalcontext.OWNER + 1)]]]
$heap_graph(S_live_owner_bad) = $heap_graph(S_wait)
$heap_valid($heap_graph(S_live_owner_bad))
~$call_descriptors_valid(S_live_owner_bad)
~$eval_response_valid(S_live_owner_bad,psourceresponse)
$eval_resume(S_live_owner_bad,psourceresponse).COMPLETION = UNSUPPORTED "invalid eval parser response"
S_wait.FIBERCALLERS = pfibercaller :: eps
pfibercaller.VM.GLOBAL
pfibercaller.VM.FRAMES = eps
pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_wait_tail*
S_view = $fiber_vm_restore(S_wait,pfibercaller.VM)[.ACTIVEFIBER = pfibercaller.PREVIOUS][.FIBERCALLERS = eps][.COMPLETION = NORMAL][.EVALCONTEXTS = eps]
$fiber_vm_valid(S_wait,pfibercaller.VM,pfibercaller.PREVIOUS,eps)
$call_descriptors_scoped_valid(S_wait,S_view)
~$call_descriptors_scoped_valid(S_live_owner_bad,S_view)
pfibervm_direct = pfibercaller.VM[.TODO = (FIBER_WAIT pfibercaller.API) :: (EVAL_AWAIT n_unit) :: ptask_wait_tail*]
pfibervm_choose = pfibercaller.VM[.TODO = (FIBER_WAIT pfibercaller.API) :: (CHOOSE ([EVAL_AWAIT n_unit]) eps ($eval_site_line(S_wait,pevalcontext.SITE))) :: ptask_wait_tail*]
pframe_marker = pframe_leaf[.TODO = [EVAL_AWAIT n_unit]]
pfibervm_frame = pfibercaller.VM[.FRAMES = [pframe_marker]]
~$eval_frames_markers_valid(S_view,[pframe_marker])
'''.strip().splitlines()
    # Main has no parked frame: the frame control also fails GLOBAL+FRAMES.
    # The marker helper above separately exercises the bridge's frame guard.
    for label in ('direct', 'choose', 'frame'):
        state = 'S_parked_' + label
        vm = 'pfibervm_' + label
        checks += [f'{state} = S_wait[.FIBERCALLERS = [pfibercaller[.VM = {vm}]]]',
                   f'$heap_valid($heap_graph({state}))',
                   f'~$fiber_vm_valid({state},{vm},pfibercaller.PREVIOUS,eps)',
                   f'~$call_descriptors_valid({state})',
                   f'~$eval_response_valid({state},psourceresponse)']
    checks += r'''
S_entry = $eval_resume(S_wait,psourceresponse)
S_entry.COMPLETION = NORMAL
S_entry.TODO = (SOURCE_OPERAND_ENTER psourceoperand n_unit) :: ptask_body*
psourceoperand.INPUT = KNOWN (POBJECT n_operand)
psourceoperand.OWNER = |S_entry.FRAMES|
$(psourceoperand.OWNER > 0)
psourceoperand.KIND = 0
$source_operand_enter_valid(S_entry,psourceoperand,n_unit)
$source_operand_entry_origin(S_entry,psourceoperand,n_unit) = (porigin_work)
$origin_node(S_entry.SOURCES,porigin_work) = (NExprVariable (BYTES text_x) metadata_x)
$base64(text_x) = $ptascii("x")
$variable_line((BYTES text_x),metadata_x) = 4
$compiled_read(S_entry,porigin_work) = eps
S_owner_bad = S_entry[.TODO = (SOURCE_OPERAND_ENTER psourceoperand[.OWNER = $(psourceoperand.OWNER + 1)] n_unit) :: ptask_body*]
S_tail_bad = S_entry[.TODO = [SOURCE_OPERAND_ENTER psourceoperand n_unit]]
$heap_valid($heap_graph(S_owner_bad))
~$source_operand_enter_valid(S_owner_bad,psourceoperand[.OWNER = $(psourceoperand.OWNER + 1)],n_unit)
$call_entry_check(S_owner_bad).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
$heap_valid($heap_graph(S_tail_bad))
~$source_operand_enter_valid(S_tail_bad,psourceoperand,n_unit)
$call_entry_check(S_tail_bad).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
'''.strip().splitlines()
    checks += valid('S_entry') + seek('S_retired', 'S_entry', 0) + valid('S_retired')
    checks += r'''
S_retired.ACTIVEFIBER = (n_fiber)
S_retired.CURRENT = (pcallcontext_destructor)
$destructor_context_call(pcallcontext_destructor,S_retired.CURRENT,S_retired.FRAMES) = (pdestructorcall)
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.SOURCE = SOURCE_OPERAND_ENTER psourceoperand n_unit
pdestructionoperation.ORIGIN = (porigin_work)
pdestructionoperation.CALLER = S_entry.CURRENT
S_owner = $source_string_owner_scope(S_retired,psourceoperand.OWNER)
S_owner.CURRENT = (pcallcontext_leaf)
$generator_context_operation(S_owner,pcallcontext_leaf) = (pgeneratorop_leaf)
$destructor_call_live(S_retired,pdestructorcall)
$($heap_owners($heap_graph(S_retired),HOBJECT n_default) > 0)
$($heap_owners($heap_graph(S_retired),HOBJECT n_closure) > 0)
'''.strip().splitlines()
    checks += seek('S_paused', 'S_retired', 1) + valid('S_paused')
    checks += ['S_paused.ACTIVEFIBER = (n_fiber)',
               'S_paused.OBJECTS[pgeneratorop_arrow.OBJECT] = GENERATOR pgenerator_paused',
               '$generator_cached_value(S_paused,pgeneratorop_arrow.OBJECT,false) = PINT 5',
               'pgenerator_paused.CLOSURE = (n_closure)',
               '$heap_owners($heap_graph(S_paused),HOBJECT n_closure) = 1']
    checks += seek('S_close', 'S_paused', 2) + valid('S_close')
    checks += ['S_close.ACTIVEFIBER = (n_fiber)',
               'S_close.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_close*',
               'pgenclose.CONTEXT.INSTANCE = (n_closure)',
               '$generator_close_enter_valid(S_close,pgenclose)',
               'S_zero = $drive_steps(S_close,0)', 'S_zero.COMPLETION = BUDGET',
               'S_zero.TODO = S_close.TODO', 'S_zero.FRAMES = S_close.FRAMES',
               'S_resumed = $drive(S_zero[.COMPLETION = NORMAL],4096)',
               'S_direct = $drive(S_close,4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.ACTIVEFIBER = eps',
               '$arrow_integration_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    return checks


def main():
    driver.CASES = CASES
    driver.source.WATCHED = WATCHED
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
