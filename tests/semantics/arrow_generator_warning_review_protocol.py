#!/usr/bin/env python3
"""Independent source-reached delayed YIELD warning continuation checks."""
import os
import sys

import generator_force_close_protocol as driver
import arrow_generator_review as source

CASES = {
    'multiline-value-warning-delayed-key': (
        b'<?php\nfunction warn($n,$m,$f,$l){$GLOBALS["key"]="new";echo "H",$l,"|";return true;}set_error_handler("warn");\n$key="old";\n$f=fn(&$key):Generator=>\n    yield $key =>\n        $missing;\n$g=$f($key);unset($f);echo "C|";echo (int)($g->current()===null),":",$g->key(),"|";$g->send(9);echo $g->getReturn();unset($g);echo "Z";\n',
        b'C|H6|1:new|9Z', 0),
    'handler-throw-retains-computed-key': (
        b'<?php\nfunction keygen(){try{yield 1;}finally{echo "K|";}}\nfunction keyval(){$k=keygen();$k->current();return $k;}\nfunction warn($n,$m,$f,$l){echo "H",$l,"|";throw $GLOBALS["sent"];}set_error_handler("warn");\n$sent=new Exception("handler");$f=fn()=>yield keyval()=>$missing;\n$g=$f();unset($f);echo "C|";try{$g->current();}catch(Exception $e){echo "E",(int)($e===$sent),":",(int)($e->getPrevious()===null),"|";}echo "V",(int)$g->valid(),"|";unset($g);echo "Z";\n',
        b'C|H5|E1:1|V0|K|Z', 0),
}
OWN = 'tests/semantics/arrow_generator_warning_review_protocol.py'
WATCHED = source.WATCHED + [
    'spec/semantics/207-error-handler-runtime.watsup', OWN,
]
PREFIX = r'''
dec $arrow_warning_review_phase(pstate,nat) : bool
def $arrow_warning_review_phase(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin poperand?
  -- if $generator_active(S)
def $arrow_warning_review_phase(S,1) = true
  -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask*
  -- if perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin poperand?
  -- if $generator_active(S)
def $arrow_warning_review_phase(S,2) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $arrow_warning_review_phase(S,3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin poperand?
  -- if $generator_active(S)
def $arrow_warning_review_phase(S,n) = false -- otherwise
dec $arrow_warning_review_seek(pstate,nat,nat) : pstate
def $arrow_warning_review_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $arrow_warning_review_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $arrow_warning_review_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $arrow_warning_review_phase(S,n_phase)
def $arrow_warning_review_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$arrow_warning_review_phase(S,n_phase)
  -- if n = 0 \/ (S.TODO = eps /\ S.FRAMES = eps)
def $arrow_warning_review_seek(S,n_phase,n) = $arrow_warning_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$arrow_warning_review_phase(S,n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.FRAMES =/= eps
dec $arrow_warning_review_output(pevent) : bool
def $arrow_warning_review_output(OUTPUT ptbytes) = true
def $arrow_warning_review_output(pevent) = false -- otherwise
dec $arrow_warning_review_outputs(pevent*) : ptbytes
def $arrow_warning_review_outputs(eps) = eps
def $arrow_warning_review_outputs((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $arrow_warning_review_outputs(pevent*)
def $arrow_warning_review_outputs(pevent :: pevent_tail*) = $arrow_warning_review_outputs(pevent_tail*)
  -- if ~$arrow_warning_review_output(pevent)
dec $arrow_warning_review_step(pstate) : pstate
def $arrow_warning_review_step(S) = S_next
  -- PhpStep: S ~> S_next
'''


def seek(state, previous, phase):
    return [f'{state}_found = $arrow_warning_review_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$arrow_warning_review_phase({state},{phase})', *valid(state)]


def valid(state):
    return driver.valid(state) + [f'$generator_state_valid({state})']


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + driver.driver.byte_expr(os.fsencode(path)) + ',' + driver.driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    if name == 'handler-throw-retains-computed-key':
        return throw_assertions(checks, name)
    checks += seek('S_pending', 'S_initial', 0)
    checks += r'''
S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_pending*
perrorcall.RESUME = ERROR_READ_RESULT perrorread
perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin (VARIABLE n_keyname* z_key)
perrorread.TASK = perrorread.ORIGINAL
perrorread.INPUT = VARIABLE $ptascii("missing") 6
perrorread.NAME = $ptascii("missing")
perrorread.LINE = 6
perrorread.RESULT = KNOWN PNULL
n_keyname* = $ptascii("key")
z_key = 5
S_pending.ORIGIN = (porigin)
$generator_yield_site(S_pending,porigin)
$generator_yield_line(S_pending,porigin) = 6
~$generator_close_active(S_pending)
$error_read_valid(S_pending,perrorread)
$error_call_valid(S_pending,perrorcall)
S_pending.FRAMES = pframe_resumer :: pframe_resumer_tail*
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resumer*
S_pending.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FRAME = eps
pgenerator_running.VALUE = eps
pgenerator_running.KEY = eps
$lookup(S_pending.ENV,$ptascii("missing")) = (n_missing)
S_pending.STORE[n_missing] = UNDEFINED
$lookup(S_pending.ENV,n_keyname*) = (n_key)
n_key <- S_pending.REFCELLS
S_pending.STORE[n_key] = DEFINED (PSTRING $ptascii("old"))
'''.strip().splitlines()
    checks += seek('S_returned', 'S_pending', 1)
    checks += r'''
S_returned.TODO = (ERROR_READ_RESULT perrorread) :: ptask_returned*
S_returned.ORIGIN = (porigin)
$error_read_valid(S_returned,perrorread)
$call_task_valid(S_returned,ERROR_READ_RESULT perrorread)
S_returned.STORE[n_missing] = UNDEFINED
S_returned.STORE[n_key] = DEFINED (PSTRING $ptascii("new"))
$lookup(S_returned.ENV,n_keyname*) = (n_key)
psymboltable_globals = $fiber_globals(S_returned)
$lookup(psymboltable_globals.ENV,n_keyname*) = (n_key)
$arrow_warning_review_outputs(S_returned.EVENTS) = $ptascii("C|H6|")
'''.strip().splitlines()
    for label, record in [
        ('name', 'perrorread[.NAME = $ptascii("key")]'),
        ('line', 'perrorread[.LINE = 5]'),
        ('input', 'perrorread[.INPUT = VARIABLE $ptascii("key") 6]'),
        ('source_name', 'perrorread[.INPUT = VARIABLE $ptascii("key") 6][.NAME = $ptascii("key")]'),
        ('source_line', 'perrorread[.INPUT = VARIABLE $ptascii("missing") 5][.LINE = 5]'),
        ('result', 'perrorread[.RESULT = KNOWN (PINT 9)]'),
        ('task', 'perrorread[.TASK = GENERATOR_YIELD_STORE porigin eps]'),
        ('original', 'perrorread[.ORIGINAL = GENERATOR_YIELD_STORE porigin eps]'),
        ('key_source', 'perrorread[.ORIGINAL = GENERATOR_YIELD_STORE porigin (VARIABLE $ptascii("missing") 6)][.TASK = GENERATOR_YIELD_STORE porigin (VARIABLE $ptascii("missing") 6)]'),
        ('key_line', 'perrorread[.ORIGINAL = GENERATOR_YIELD_STORE porigin (VARIABLE n_keyname* 6)][.TASK = GENERATOR_YIELD_STORE porigin (VARIABLE n_keyname* 6)]'),
        ('missing_key', 'perrorread[.ORIGINAL = GENERATOR_YIELD_STORE porigin eps][.TASK = GENERATOR_YIELD_STORE porigin eps]'),
    ]:
        driver.reject(checks, label, 'S_returned[.TODO = (ERROR_READ_RESULT ' + record + ') :: ptask_returned*]')
    driver.reject(checks, 'site', 'S_returned[.ORIGIN = $origin_child((porigin),[PCFIELD 1])]')
    checks += ['S_store = $arrow_warning_review_step(S_returned)', 'S_store.COMPLETION = NORMAL',
               'S_store.TODO = perrorread.TASK :: ptask_returned*',
               'S_store.RESULT = KNOWN PNULL', 'S_store.BASE = perrorread.BASE',
               *valid('S_store')]
    checks += seek('S_paused', 'S_store', 2)
    checks += ['S_paused.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_paused',
               'pgenerator_paused.VALUE = (PNULL)',
               'pgenerator_paused.KEY = (PSTRING $ptascii("new"))',
               'pgenerator_paused.FRAME = (pframe_paused)',
               'S_paused.STORE[n_missing] = UNDEFINED']
    return checks + finish('S_returned', name)


def finish(previous, name):
    return [f'S_stopped = $drive_steps({previous},0)', 'S_stopped.COMPLETION = BUDGET',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps', 'S_resumed.ITERATORS = eps',
               '$arrow_warning_review_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1]),
               *valid('S_resumed')]


def throw_assertions(checks, name):
    checks += seek('S_pending', 'S_initial', 0)
    checks += r'''
S_pending.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_pending*
perrorcall.RESUME = ERROR_READ_RESULT perrorread
perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin (KNOWN (POBJECT n_keygen))
perrorread.TASK = perrorread.ORIGINAL
perrorread.INPUT = VARIABLE $ptascii("missing") 5
perrorread.NAME = $ptascii("missing")
perrorread.LINE = 5
perrorread.RESULT = KNOWN PNULL
$error_read_valid(S_pending,perrorread)
$error_call_valid(S_pending,perrorcall)
S_pending.OBJECTS[n_keygen] = GENERATOR pgenerator_key
pgenerator_key.PHASE = GENERATOR_PAUSED
$heap_owners($heap_graph(S_pending),HOBJECT n_keygen) = 1
S_pending.FRAMES = pframe_resumer :: pframe_resumer_tail*
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resumer*
S_pending.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FRAME = eps
pgenerator_running.KEY = eps
pgenerator_running.VALUE = eps
'''.strip().splitlines()
    checks += seek('S_throw', 'S_pending', 3)
    checks += r'''
S_throw.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_throw*
perrorcall_entered[.TARGET = eps] = perrorcall
S_throw.FRAMES = pframe_resumer :: pframe_resumer_tail*
$error_read_valid(S_throw,perrorread)
$error_entered_call_valid(S_throw,perrorcall_entered)
$trace_slot(S_throw,$fiber_globals(S_throw).ENV,$ptascii("sent")) = POBJECT n_throwable
$throwable_field(S_throw,n_throwable,"message") = PSTRING $ptascii("handler")
$throwable_field(S_throw,n_throwable,"previous") = PNULL
$heap_owners($heap_graph(S_throw),HOBJECT n_keygen) = 1
$arrow_warning_review_outputs(S_throw.EVENTS) = $ptascii("C|H5|")
S_closed = $arrow_warning_review_step(S_throw)
S_closed.COMPLETION = NORMAL
S_closed.TODO = (THROW_SEARCH n_throwable) :: (GENERATOR_RESUME pgeneratorop) :: ptask_resumer*
S_closed.CURRENT = pframe_resumer.CONTEXT
S_closed.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (PNULL)
pgenerator_closed.KEY = (POBJECT n_keygen)
pgenerator_closed.RETURN = eps
S_closed.OBJECTS[n_keygen] = GENERATOR pgenerator_key
$heap_owners($heap_graph(S_closed),HOBJECT n_keygen) = 1
$throwable_field(S_closed,n_throwable,"previous") = PNULL
$trace_slot(S_closed,$fiber_globals(S_closed).ENV,$ptascii("sent")) = POBJECT n_throwable
'''.strip().splitlines()
    checks += valid('S_closed') + finish('S_closed', name)
    checks += ['~((HOBJECT n_keygen) <- S_resumed.ALLOCATIONS)',
               '~((HOBJECT pgeneratorop.OBJECT) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    mode = sys.argv[sys.argv.index('--mode') + 1] if '--mode' in sys.argv else 'check'
    if mode == 'native':
        source.driver.CASES = CASES
        source.driver.DECLARATIONS = {}
        source.driver.UNSUPPORTED = {}
        source.driver.WATCHED = [OWN, 'tests/semantics/profile.json']
        return source.driver.main()
    source.WATCHED = [OWN, 'tests/semantics/profile.json'] if mode == 'fixtures' else WATCHED
    driver.source = source
    driver.CASES = CASES
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
