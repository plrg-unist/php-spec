#!/usr/bin/env python3
"""Reached arrow Generator receives, frames, implicit returns and captured scopes."""
import os

import generator_force_close_protocol as protocol
import arrow_generator_prepare as source

CASES = {name: source.CASES[case] for name, case in [
    ('capture-receive', 'capture-and-argument-snapshots'),
    ('sent-payload', 'return-payload-skips-string-coercion'),
    ('captured-scope', 'private-captured-receiver-scope'),
    ('delegated-return', 'generator-delegation-return'),
]}
PREFIX = r'''
dec $arrow_gen_phase(pstate,nat) : bool
def $arrow_gen_phase(S,0) = true
  -- if S.TODO = (GENERATOR_CREATE porigin) :: ptask*
  -- if $origin_node(S.SOURCES,porigin) = (NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 expression metadata)
def $arrow_gen_phase(S,1) = true
  -- if S.TODO = (GENERATOR_ARGS pgeneratorop phpType7* poperand*) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_FRESH
  -- if $origin_node(S.SOURCES,pgenerator.FUNCTION) = (NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 expression metadata)
def $arrow_gen_phase(S,2) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE <- [GENERATOR_PAUSED,GENERATOR_DELEGATING]
  -- if $origin_node(S.SOURCES,pgenerator.FUNCTION) = (NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 expression metadata)
def $arrow_gen_phase(S,3) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask*
  -- if $arrow_context(S) /\ $generator_active(S)
def $arrow_gen_phase(S,4) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
  -- if $origin_node(S.SOURCES,pgenerator.FUNCTION) = (NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 expression metadata)
def $arrow_gen_phase(S,n) = false -- otherwise
dec $arrow_gen_seek(pstate,nat,nat) : pstate
def $arrow_gen_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $arrow_gen_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $arrow_gen_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $arrow_gen_phase(S,n_phase)
def $arrow_gen_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$arrow_gen_phase(S,n_phase)
  -- if n = 0 \/ (S.TODO = eps /\ S.FRAMES = eps)
def $arrow_gen_seek(S,n_phase,n) = $arrow_gen_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$arrow_gen_phase(S,n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.FRAMES =/= eps
dec $arrow_gen_outputs(pevent*) : ptbytes
dec $arrow_gen_output(pevent) : bool
def $arrow_gen_outputs(eps) = eps
def $arrow_gen_outputs((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $arrow_gen_outputs(pevent*)
def $arrow_gen_outputs(pevent :: pevent_tail*) = $arrow_gen_outputs(pevent_tail*)
  -- if ~($arrow_gen_output(pevent))
def $arrow_gen_output(OUTPUT ptbytes) = true
def $arrow_gen_output(pevent) = false -- otherwise
'''


def seek(state, previous, phase):
    return [f'{state}_found = $arrow_gen_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$arrow_gen_phase({state},{phase})']


def valid(state):
    return protocol.valid(state) + [f'$generator_state_valid({state})',
                                    f'$call_tasks_valid({state},{state}.TODO)',
                                    f'$call_frames_valid({state},{state}.FRAMES)',
                                    f'$call_current_valid({state})']


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + protocol.driver.byte_expr(os.fsencode(path)) + ',' + protocol.driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += seek('S_create', 'S_initial', 0) + valid('S_create')
    checks += r'''
S_create.TODO = (GENERATOR_CREATE porigin_arrow) :: ptask_create*
S_create.CURRENT = (pcallcontext_create)
pcallcontext_create.FUNCTION = porigin_arrow
pcallcontext_create.INSTANCE = (n_closure)
$function_at(S_create.CLOSURETEMPLATES,porigin_arrow) = (pfunction_arrow)
$function_generator(S_create,pfunction_arrow)
~pfunction_arrow.SIGNATURE.BYREF
$named_receives_ready(S_create,pfunction_arrow)
$generator_create_valid(S_create,porigin_arrow)
$closure_callable(S_create,n_closure)
$arrow_line(pfunction_arrow.CODE.EXPRESSIONS,pfunction_arrow.BODY) = (z_arrow)
'''.strip().splitlines()
    checks += seek('S_fresh', 'S_create', 1) + valid('S_fresh')
    checks += r'''
S_fresh.TODO = (GENERATOR_ARGS pgeneratorop_fresh phpType7_fresh* poperand_fresh*) :: ptask_fresh*
n_gen = pgeneratorop_fresh.OBJECT
S_fresh.OBJECTS[n_gen] = GENERATOR pgenerator_fresh
pgenerator_fresh.FUNCTION = porigin_arrow
pgenerator_fresh.CLOSURE = (n_closure)
pgenerator_fresh.FRAME = (pframe_fresh)
pgenerator_fresh.RETURN = eps
pframe_fresh.CONTEXT = (pcallcontext_fresh)
pcallcontext_fresh.INSTANCE = (n_closure)
pframe_fresh.LOCALS = (psymboltable_fresh)
pframe_fresh.TODO = $function_body_tasks(S_fresh,pfunction_arrow)
(HOBJECT n_closure) <- S_fresh.ALLOCATIONS
'''.strip().splitlines()
    protocol.reject(checks, 'fresh_short_body', '$generator_set(S_fresh,n_gen,pgenerator_fresh[.FRAME = (pframe_fresh[.TODO = [RETURN_NULL]])])')
    protocol.reject(checks, 'fresh_missing_closure', '$generator_set(S_fresh,n_gen,pgenerator_fresh[.CLOSURE = eps])')
    if name == 'capture-receive':
        checks += r'''
$trace_slot(S_fresh,psymboltable_fresh.ENV,$ptascii("p")) = PINT 3
$lookup(psymboltable_fresh.ENV,$ptascii("x")) = eps
$object_body(S_fresh.OBJECTS[n_closure]) = REALCLOSURE porigin_arrow ([DIRECT (PINT 2)]) pstaticcell_fresh*
'''.strip().splitlines()
    if name == 'captured-scope':
        checks += r'''
pcallcontext_fresh.RECEIVER = (n_receiver)
pcallcontext_fresh.LEXICAL_CLASS = (porigin_owner)
pcallcontext_fresh.CALLED_CLASS = (porigin_child)
$class_at(S_fresh.CLASSES,porigin_owner) = (pclassdesc_owner)
pclassdesc_owner.NAME = $ptascii("Owner")
$class_at(S_fresh.CLASSES,porigin_child) = (pclassdesc_child)
pclassdesc_child.NAME = $ptascii("Child")
(HOBJECT n_receiver) <- S_fresh.ALLOCATIONS
$($heap_owners($heap_graph(S_fresh),HOBJECT n_receiver) > 0)
$lookup(S_fresh.ENV,$ptascii("f")) = eps
$lookup(S_fresh.ENV,$ptascii("o")) = eps
'''.strip().splitlines()
    checks += seek('S_paused', 'S_fresh', 2) + valid('S_paused')
    checks += r'''
S_paused.OBJECTS[n_gen] = GENERATOR pgenerator_paused
pgenerator_paused.FRAME = (pframe_paused)
pgenerator_paused.CLOSURE = (n_closure)
pgenerator_paused.RETURN = eps
$generator_frame_valid(S_paused,pgenerator_paused,pframe_paused)
'''.strip().splitlines()
    if name == 'capture-receive':
        checks += ['pgenerator_paused.VALUE = (PINT 5)', 'pgenerator_paused.KEY = (PINT 0)',
                   'pframe_paused.LOCALS = (psymboltable_paused)',
                   '$trace_slot(S_paused,psymboltable_paused.ENV,$ptascii("x")) = PINT 2']
    if name == 'sent-payload':
        checks += ['pgenerator_paused.VALUE = (PINT 1)',
                   'pfunction_arrow.SIGNATURE.RETURNS =/= eps']
    if name == 'captured-scope':
        checks += ['pframe_paused.CONTEXT = (pcallcontext_paused)',
                   'pcallcontext_paused.RECEIVER = (n_receiver)',
                   '(HOBJECT n_receiver) <- S_paused.ALLOCATIONS']
    if name == 'delegated-return':
        checks += r'''
pgenerator_paused.PHASE = GENERATOR_DELEGATING
pgenerator_paused.DELEGATE = (pgeneratorfrom_paused)
pgeneratorfrom_paused.INPUT = (POBJECT n_child)
S_paused.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_PAUSED
pgenerator_child.VALUE = (PINT 1)
'''.strip().splitlines()
    else:
        protocol.reject(checks, 'paused_missing_key', '$generator_set(S_paused,n_gen,pgenerator_paused[.KEY = eps])')
    checks += seek('S_return', 'S_paused', 3) + valid('S_return')
    checks += r'''
S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*
$arrow_return(S_return,z_return) = (expression_return)
$typed_return_task_valid(S_return,z_return)
$generator_active(S_return)
S_return.FRAMES = pframe_resumer :: pframe_resumer_tail*
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_return) :: ptask_resumer*
pgeneratorop_return.OBJECT = n_gen
'''.strip().splitlines()
    protocol.reject(checks, 'wrong_return_line', 'S_return[.TODO = (RETURN_VALUE $(z_return + 1)) :: ptask_return*]')
    protocol.reject(checks, 'wrong_reference_return', 'S_return[.TODO = (RETURN_REF_VALUE z_return) :: ptask_return*]')
    if name == 'sent-payload':
        checks += ['S_return.RESULT = KNOWN (POBJECT n_payload)',
                   '$typed_return_value(S_return,z_return) = S_return',
                   '(HOBJECT n_payload) <- S_return.ALLOCATIONS']
    checks += seek('S_closed', 'S_return', 4) + valid('S_closed')
    checks += r'''
S_closed.OBJECTS[n_gen] = GENERATOR pgenerator_closed
pgenerator_closed.FRAME = eps
pgenerator_closed.CLOSURE = (n_closure)
pgenerator_closed.RETURN =/= eps
$generator_closure_valid(S_closed,pgenerator_closed)
'''.strip().splitlines()
    if name == 'sent-payload':
        checks += ['pgenerator_closed.RETURN = (POBJECT n_payload)']
    elif name == 'delegated-return':
        checks += ['pgenerator_closed.RETURN = (PINT 9)',
                   '$generator_from_input_of(pgenerator_closed.DELEGATE) = eps']
    else:
        checks += ['pgenerator_closed.RETURN = (PNULL)']
    checks += ['S_stopped = $drive_steps(S_closed,0)',
               'S_stopped.COMPLETION = BUDGET',
               'S_stopped = S_closed[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               'S_direct = $drive(S_closed,4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps', 'S_resumed.ITERATORS = eps',
               '$arrow_gen_outputs(S_resumed.EVENTS) = ' + protocol.driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    return checks


def main():
    source.WATCHED = source.WATCHED + ['tests/semantics/arrow_generator_protocol.py']
    protocol.source = source
    protocol.CASES = CASES
    protocol.PREFIX = PREFIX
    protocol.assertions = assertions
    return protocol.main()


if __name__ == '__main__':
    raise SystemExit(main())
