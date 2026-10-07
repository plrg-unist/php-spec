#!/usr/bin/env python3
"""Independent reached arrow capture, sent-return and scoped delegation states."""
import os
import sys

import generator_force_close_protocol as driver
import arrow_generator_review as source

CASES = {
    'deferred-captures-and-sent-return': (b'<?php\n$snapshot=3;$shared=4;$f=fn($param,&$ref):Generator=>yield [$param,$ref,$snapshot];$g=$f(8,$shared);unset($f);$snapshot=9;$shared=7;$v=$g->current();echo $v[0],":",$v[1],":",$v[2],"|";$g->send(9);echo $g->getReturn();unset($g);echo "Z";\n', b'8:7:3|9Z', 0),
    'child-arrow-return-transfer': source.CASES['generator-delegation-used-return'],
    'active-fiber-private-receiver-release': (b'<?php\nclass Owner{private $v=3;private function leaf(){try{yield $this->v;}finally{echo "L",self::class,":",static::class,":",(int)(Fiber::getCurrent()!==null),"|";}}function make(){return fn()=>yield from $this->leaf();}}class Child extends Owner{}$f=new Fiber(function(){$c=new Child;$a=$c->make();$g=$a();unset($c,$a);echo $g->current(),"|";unset($g);echo "A|";return 5;});$f->start();echo "M",$f->getReturn();\n', b'3|LOwner:Child:1|A|M5', 0),
}
WATCHED = source.WATCHED + ['tests/semantics/arrow_generator_review_protocol.py']
PREFIX = r'''
dec $arrow_review_function(pstate,porigin) : bool
def $arrow_review_function(S,porigin) = true
  -- if $origin_node(S.SOURCES,porigin) = (NExprArrowFunction phpType14 phpType4_static phpType4_ref phpType16 phpType18 expression metadata)
def $arrow_review_function(S,porigin) = false -- otherwise
dec $arrow_review_return_head(ptask) : bool
def $arrow_review_return_head(RETURN_VALUE z) = true
def $arrow_review_return_head(ptask) = false -- otherwise
dec $arrow_review_return(ptask*) : int?
def $arrow_review_return(eps) = eps
def $arrow_review_return((RETURN_VALUE z) :: ptask*) = (z)
def $arrow_review_return(ptask :: ptask_tail*) = $arrow_review_return(ptask_tail*)
  -- if ~$arrow_review_return_head(ptask)
dec $arrow_review_reline(ptask*,int) : ptask*
def $arrow_review_reline(eps,z) = eps
def $arrow_review_reline((RETURN_VALUE z_old) :: ptask_tail*,z) = (RETURN_VALUE z) :: ptask_tail*
def $arrow_review_reline(ptask :: ptask_tail*,z) = ptask :: $arrow_review_reline(ptask_tail*,z)
  -- if ~$arrow_review_return_head(ptask)
dec $arrow_review_phase(pstate,nat) : bool
def $arrow_review_phase(S,0) = true
  -- if S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask*
  -- if pgeneratorop.NAME = "current"
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_FRESH
  -- if $arrow_review_function(S,pgenerator.FUNCTION)
def $arrow_review_phase(S,1) = true
  -- if $generator_active(S)
  -- if S.TODO = (CLOSURE_RECEIVE porigin 0) :: ptask*
  -- if $arrow_review_function(S,porigin)
def $arrow_review_phase(S,2) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if $arrow_review_function(S,pgenerator.FUNCTION)
def $arrow_review_phase(S,3) = true
  -- if $generator_active(S)
  -- if S.TODO = (RETURN_VALUE z) :: ptask*
  -- if $arrow_return(S,z) = (expression)
def $arrow_review_phase(S,4) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
  -- if $arrow_review_function(S,pgenerator.FUNCTION)
def $arrow_review_phase(S,5) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
  -- if $arrow_review_function(S,pgenerator.FUNCTION)
def $arrow_review_phase(S,6) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if S.ACTIVEFIBER =/= eps
  -- if $arrow_review_function(S,pgenclose.CONTEXT.FUNCTION)
def $arrow_review_phase(S,7) = true
  -- if S.ACTIVEFIBER =/= eps
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) = (pgenclose)
  -- if pgenclose.STAGE = CLOSE_BODY porigin
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("leaf")
def $arrow_review_phase(S,n) = false -- otherwise
dec $arrow_review_seek(pstate,nat,nat) : pstate
def $arrow_review_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $arrow_review_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $arrow_review_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $arrow_review_phase(S,n_phase)
def $arrow_review_seek(S,n_phase,0) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$arrow_review_phase(S,n_phase)
def $arrow_review_seek(S,n_phase,n) = $arrow_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$arrow_review_phase(S,n_phase)
  -- if $(n > 0)
dec $arrow_review_output(pevent) : bool
def $arrow_review_output(OUTPUT ptbytes) = true
def $arrow_review_output(pevent) = false -- otherwise
dec $arrow_review_outputs(pevent*) : ptbytes
def $arrow_review_outputs(eps) = eps
def $arrow_review_outputs((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $arrow_review_outputs(pevent*)
def $arrow_review_outputs(pevent :: pevent_tail*) = $arrow_review_outputs(pevent_tail*)
  -- if ~$arrow_review_output(pevent)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $arrow_review_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$arrow_review_phase({state},{phase})']


def valid(state):
    return driver.valid(state) + [f'$generator_state_valid({state})', f'$fiber_state_valid({state})']


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + driver.driver.byte_expr(os.fsencode(path)) + ',' + driver.driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    if name == 'deferred-captures-and-sent-return':
        checks += seek('S_fresh', 'S_initial', 0) + valid('S_fresh')
        checks += r'''
S_fresh.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_fresh*
S_fresh.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_fresh
pgenerator_fresh.FRAME = (pframe_fresh)
pframe_fresh.LOCALS = (psymboltable_fresh)
pframe_fresh.CONTEXT = (pcallcontext_fresh)
pgenerator_fresh.CLOSURE = (n_closure)
pcallcontext_fresh.INSTANCE = (n_closure)
pcallcontext_fresh.FUNCTION = pgenerator_fresh.FUNCTION
pframe_fresh.TODO = [CLOSURE_RECEIVE pgenerator_fresh.FUNCTION 0]
S_fresh.OBJECTS[n_closure] = REALCLOSURE pgenerator_fresh.FUNCTION ([DIRECT (PINT 3)]) eps
$function_at(S_fresh.CLOSURETEMPLATES,pgenerator_fresh.FUNCTION) = (pfunction)
pfunction.SIGNATURE.RETURNS =/= eps
$generator_return_supertype(pfunction.SIGNATURE.RETURNS)
~pfunction.SIGNATURE.BYREF
$trace_slot(S_fresh,psymboltable_fresh.ENV,$ptascii("param")) = PINT 8
$trace_slot(S_fresh,psymboltable_fresh.ENV,$ptascii("ref")) = PINT 7
$lookup(psymboltable_fresh.ENV,$ptascii("snapshot")) = eps
$lookup(psymboltable_fresh.ENV,$ptascii("ref")) = (n_shared)
$lookup(S_fresh.ENV,$ptascii("shared")) = (n_shared)
$trace_slot(S_fresh,S_fresh.ENV,$ptascii("snapshot")) = PINT 9
$heap_owners($heap_graph(S_fresh),HOBJECT n_closure) = 1
'''.strip().splitlines()
        driver.reject(checks, 'receive_cursor', '$generator_set(S_fresh,pgeneratorop.OBJECT,pgenerator_fresh[.FRAME = (pframe_fresh[.TODO = [CLOSURE_RECEIVE pgenerator_fresh.FUNCTION 1]])])')
        driver.reject(checks, 'capture_alias', 'S_fresh[.OBJECTS = $object_set(S_fresh.OBJECTS,n_closure,REALCLOSURE pgenerator_fresh.FUNCTION ([ALIAS n_shared]) eps)]')
        checks += seek('S_receive', 'S_fresh', 1) + valid('S_receive')
        checks += ['S_receive.CURRENT = (pcallcontext_fresh)',
                   '$lookup(S_receive.ENV,$ptascii("snapshot")) = eps',
                   'S_receive.TODO = [CLOSURE_RECEIVE pgenerator_fresh.FUNCTION 0]']
        checks += seek('S_paused', 'S_receive', 2) + valid('S_paused')
        checks += r'''
S_paused.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_paused
pgenerator_paused.FRAME = (pframe_paused)
pframe_paused.LOCALS = (psymboltable_paused)
$trace_slot(S_paused,psymboltable_paused.ENV,$ptascii("snapshot")) = PINT 3
$lookup(psymboltable_paused.ENV,$ptascii("ref")) = (n_shared)
$arrow_review_return(pframe_paused.TODO) = (z_return)
$generator_send_target(pframe_paused.TODO)
pgenerator_paused.VALUE = (PARRAY n_array)
S_paused.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)),ENTRY (KINT 1) (DIRECT (PINT 7)),ENTRY (KINT 2) (DIRECT (PINT 3))]
'''.strip().splitlines()
        driver.reject(checks, 'implicit_return_line', '$generator_set(S_paused,pgeneratorop.OBJECT,pgenerator_paused[.FRAME = (pframe_paused[.TODO = $arrow_review_reline(pframe_paused.TODO,$(z_return + 1))])])')
        checks += seek('S_return', 'S_paused', 3) + valid('S_return')
        checks += ['S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
                   'S_return.RESULT = KNOWN (PINT 9)',
                   '$typed_return_value(S_return,z_return).RESULT = KNOWN (PINT 9)',
                   '$typed_return_value(S_return,z_return).COMPLETION = NORMAL']
        driver.reject(checks, 'return_site', 'S_return[.TODO = (RETURN_VALUE $(z_return + 1)) :: ptask_return*]')
        previous = 'S_return'
    elif name == 'child-arrow-return-transfer':
        checks += seek('S_link', 'S_initial', 5) + valid('S_link')
        checks += r'''
S_link.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_link*
S_link.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_outer
pgenerator_outer.FRAME = (pframe_outer)
pgenerator_outer.DELEGATE = (pgeneratorfrom)
pgeneratorfrom.INPUT = (POBJECT n_child)
S_link.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_PAUSED
pgenerator_child.FRAME = (pframe_child)
$arrow_review_function(S_link,pgenerator_child.FUNCTION)
$arrow_review_return(pframe_outer.TODO) = (z_outer)
$arrow_review_return(pframe_child.TODO) = (z_child)
$generator_send_target(pframe_outer.TODO)
$generator_send_target(pframe_child.TODO)
pgenerator_child.CLOSURE = (n_child_closure)
pgenerator_outer.CLOSURE = (n_outer_closure)
n_child_closure =/= n_outer_closure
$heap_owners($heap_graph(S_link),HOBJECT n_child_closure) = 1
$heap_owners($heap_graph(S_link),HOBJECT n_outer_closure) = 1
'''.strip().splitlines()
        driver.reject(checks, 'child_return_line', '$generator_set(S_link,n_child,pgenerator_child[.FRAME = (pframe_child[.TODO = $arrow_review_reline(pframe_child.TODO,$(z_child + 1))])])')
        driver.reject(checks, 'outer_return_line', '$generator_set(S_link,pgeneratorop.OBJECT,pgenerator_outer[.FRAME = (pframe_outer[.TODO = $arrow_review_reline(pframe_outer.TODO,$(z_outer + 1))])])')
        checks += seek('S_closed', 'S_link', 4) + valid('S_closed')
        checks += r'''
S_closed.OBJECTS[n_child] = GENERATOR pgenerator_child_closed
pgenerator_child_closed.RETURN = (POBJECT n_sent)
$trace_slot(S_closed,$fiber_globals(S_closed).ENV,$ptascii("sent")) = POBJECT n_sent
$arrow_review_function(S_closed,pgenerator_child_closed.FUNCTION)
'''.strip().splitlines()
        previous = 'S_closed'
    else:
        checks += seek('S_body', 'S_initial', 7) + valid('S_body')
        checks += r'''
$generator_close_saved(S_body,S_body.CURRENT,S_body.FRAMES) = (pgenclose_leaf)
pgenclose_leaf.CONTEXT.RECEIVER = (n_receiver)
pgenclose_leaf.CONTEXT.LEXICAL_CLASS = (porigin_owner)
pgenclose_leaf.CONTEXT.CALLED_CLASS = (porigin_child)
S_body.ACTIVEFIBER = (n_fiber)
~$fiber_transfer_domain(S_body)
$($heap_owners($heap_graph(S_body),HOBJECT n_receiver) > 0)
'''.strip().splitlines()
        driver.reject(checks, 'close_fiber_identity', 'S_body[.ACTIVEFIBER = eps]')
        checks += seek('S_queued', 'S_body', 6) + valid('S_queued')
        checks += r'''
S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_queued*
pgenclose.FRAME = (pframe_queued)
pgenclose.CONTEXT.INSTANCE = (n_closure)
pgenclose.CONTEXT.RECEIVER = (n_receiver)
S_queued.ACTIVEFIBER = (n_fiber)
S_queued.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_RUNNING
$closure_scope_at(S_queued.CLOSURESCOPES,n_closure) = (pclosurescope)
pclosurescope.RECEIVER = (n_receiver)
pclosurescope.LEXICAL = porigin_owner
pclosurescope.CALLED = porigin_child
porigin_owner =/= porigin_child
pgenclose.CONTEXT.LEXICAL_CLASS = (porigin_owner)
pgenclose.CONTEXT.CALLED_CLASS = (porigin_child)
$lookup(S_queued.ENV,$ptascii("c")) = eps
$heap_owners($heap_graph(S_queued),HOBJECT pgenclose.OBJECT) = 1
$generator_close_enter_valid(S_queued,pgenclose)
'''.strip().splitlines()
        driver.reject(checks, 'close_receiver', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose[.CONTEXT = pgenclose.CONTEXT[.RECEIVER = eps]]) :: ptask_queued*]')
        previous = 'S_queued'
    checks += [f'S_stopped = $drive_steps({previous},0)', 'S_stopped.COMPLETION = BUDGET',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps', 'S_resumed.FRAMES = eps',
               'S_resumed.ITERATORS = eps',
               '$arrow_review_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    if name == 'active-fiber-private-receiver-release':
        checks += ['~((HOBJECT n_receiver) <- S_resumed.ALLOCATIONS)',
                   '~((HOBJECT n_closure) <- S_resumed.ALLOCATIONS)', 'S_resumed.ACTIVEFIBER = eps']
    return checks


def main():
    if '--mode' in sys.argv and sys.argv[sys.argv.index('--mode') + 1] == 'native':
        source.driver.CASES = CASES
        source.driver.DECLARATIONS = {}
        source.driver.UNSUPPORTED = {}
        source.driver.WATCHED = ['tests/semantics/arrow_generator_review_protocol.py', 'tests/semantics/profile.json']
        return source.driver.main()
    source.WATCHED = WATCHED
    driver.source = source
    driver.CASES = CASES
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
