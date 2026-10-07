#!/usr/bin/env python3
"""Independent reached Generator close during ordered frame-slot release."""
import os
from pathlib import Path

import generator_force_close_protocol as driver

ROOT = driver.ROOT

CASES = {
    'pending-frame-array-release': (
        b'<?php\nfunction seq($tag){try{yield 1;}finally{echo $tag,"|";if($tag==="A"){throw new Exception("new");}}}\nfunction makePair(){$a=seq("A");$b=seq("B");$a->current();$b->current();return [$a,$b];}\nfunction drop(){$owned=makePair();throw new Exception("old");}\n$f=new Fiber(function(){try{drop();}catch(Exception $e){echo $e->getMessage(),":",$e->getPrevious()?$e->getPrevious()->getMessage():"none","|";}return 9;});$f->start();echo "M",$f->getReturn();\n',
        b'A|B|new:old|M9', 0),
}
PREFIX = driver.PREFIX + r'''
dec $eager_close_review_tag(pstate,nat,text) : bool
def $eager_close_review_tag(S,n,text) = true
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.FRAME = (pframe)
  -- if pframe.LOCALS = (psymboltable)
  -- if $lookup(psymboltable.ENV,$ptascii("tag")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PSTRING $ptascii(text))
def $eager_close_review_tag(S,n,text) = false -- otherwise
def $close_phase(S,400) = true
  -- if S.ACTIVEFIBER =/= eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_a)) :: (DESTRUCTION_VALUE (HOBJECT n_b)) :: pdestructionjob*
  -- if $eager_close_review_tag(S,n_a,"A")
  -- if $eager_close_review_tag(S,n_b,"B")
  -- if $destructor_operation_for(S) = eps
  -- if $destructor_selected_frame(S) = (pdestructionframe)
  -- if pdestructionframe.PENDING = (n_old)
  -- if $throwable_field(S,n_old,"message") = PSTRING $ptascii("old")
def $close_phase(S,401) = true
  -- if S.ACTIVEFIBER =/= eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_b)) :: pdestructionjob*
  -- if $eager_close_review_tag(S,n_b,"B")
  -- if $destructor_selected_frame(S) = (pdestructionframe)
  -- if pdestructionframe.PENDING = (n_new)
  -- if $throwable_field(S,n_new,"message") = PSTRING $ptascii("new")
  -- if $throwable_field(S,n_new,"previous") = POBJECT n_old
  -- if $throwable_field(S,n_old,"message") = PSTRING $ptascii("old")
def $close_phase(S,402) = true
  -- if S.ACTIVEFIBER =/= eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_new) :: ptask*
  -- if $throwable_field(S,n_new,"message") = PSTRING $ptascii("new")
  -- if $throwable_field(S,n_new,"previous") = POBJECT n_old
  -- if $throwable_field(S,n_old,"message") = PSTRING $ptascii("old")
def $close_phase(S,403) = true
  -- if S.ACTIVEFIBER =/= eps
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if pgenclose.FRAME = (pframe)
  -- if pframe.LOCALS = (psymboltable)
  -- if $lookup(psymboltable.ENV,$ptascii("tag")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PSTRING $ptascii("A"))
def $close_phase(S,404) = true
  -- if S.ACTIVEFIBER =/= eps
  -- if S.TODO = [THROW_SEARCH n_new]
  -- if $throwable_field(S,n_new,"message") = PSTRING $ptascii("new")
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) = (pgenclose)
  -- if $lookup(S.ENV,$ptascii("tag")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PSTRING $ptascii("A"))
'''


def valid(state):
    return driver.valid(state) + [f'$generator_state_valid({state})',
                                 f'$fiber_state_valid({state})']


def assertions(checked, path, directory, name):
    byte_expr = driver.driver.byte_expr
    checks = ['S_initial = $php_file_run(' + checked['fixture'] + ',0,' +
              byte_expr(os.fsencode(path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
              '~S_initial.COMPILESTOP']
    checks += driver.seek('S_before', 'S_initial', 400) + valid('S_before')
    checks += r'''
S_before.ACTIVEFIBER = (n_fiber)
S_before.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_RUNNING
pfiber.VM = eps
S_before.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_carrier) :: ptask_tail*
S_before.DESTRUCTION.RELEASES = pdestructionrelease :: pdestructionrelease_tail*
S_before.DESTRUCTION.FRAMES = pdestructionframe_carrier :: pdestructionframe_carrier_tail*
pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_a)) :: (DESTRUCTION_VALUE (HOBJECT n_b)) :: pdestructionjob_tail*
pdestructionrelease.USER
$destructor_release_valid(S_before,pdestructionrelease)
$destructor_frame_valid(S_before,pdestructionframe_carrier)
$destructor_selected_frame(S_before) = (pdestructionframe_carrier)
pdestructionframe_carrier.PENDING = (n_old)
$throwable_live(S_before,n_old)
$throwable_field(S_before,n_old,"message") = PSTRING $ptascii("old")
S_before.OBJECTS[n_a] = GENERATOR pgenerator_a
S_before.OBJECTS[n_b] = GENERATOR pgenerator_b
pgenerator_a.PHASE = GENERATOR_PAUSED
pgenerator_b.PHASE = GENERATOR_PAUSED
$heap_owners($heap_graph(S_before),HOBJECT n_a) = 1
$heap_owners($heap_graph(S_before),HOBJECT n_b) = 1
pdestructionrelease_remaining = pdestructionrelease[.JOBS = (DESTRUCTION_VALUE (HOBJECT n_b)) :: pdestructionjob_tail*]
S_unheld = $destructor_release_replace(S_before,pdestructionrelease_remaining)
$heap_owners($heap_graph(S_unheld),HOBJECT n_a) = 0
$heap_owners($heap_graph(S_unheld),HOBJECT n_b) = 1
$generator_destructor_pending(S_unheld,HOBJECT n_a)
~$destructor_uncalled_node(S_unheld,HOBJECT n_a)
S_bad_missing_carrier = S_before[.DESTRUCTION.FRAMES = pdestructionframe_carrier_tail*]
$heap_graph(S_bad_missing_carrier) = $heap_graph(S_before)
$heap_valid($heap_graph(S_bad_missing_carrier))
~$call_descriptors_valid(S_bad_missing_carrier)
pdestructionframe_carrier_bad = pdestructionframe_carrier[.PENDING = (n_b)]
S_bad_pending_carrier = S_before[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_carrier_bad) :: ptask_tail*][.DESTRUCTION.FRAMES = pdestructionframe_carrier_bad :: pdestructionframe_carrier_tail*]
$heap_valid($heap_graph(S_bad_pending_carrier))
~$call_descriptors_valid(S_bad_pending_carrier)
pdestructionrelease_bad = pdestructionrelease[.USER = false]
S_bad_release_source = S_before[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_bad) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_carrier) :: ptask_tail*][.DESTRUCTION.RELEASES = pdestructionrelease_bad :: pdestructionrelease_tail*]
$heap_graph(S_bad_release_source) = $heap_graph(S_before)
$heap_valid($heap_graph(S_bad_release_source))
~$call_descriptors_valid(S_bad_release_source)
S_bridge_budget = $drive_steps(S_before,1)
S_bridge_budget.COMPLETION = BUDGET
S_bridge = S_bridge_budget[.COMPLETION = NORMAL]
S_bridge.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (DESTRUCTOR_RELEASE pdestructionrelease_remaining) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_carrier) :: ptask_tail*
S_bridge.DESTRUCTION.RELEASES = pdestructionrelease_remaining :: pdestructionrelease_tail*
S_bridge.DESTRUCTION.FRAMES = S_before.DESTRUCTION.FRAMES
S_bridge.ACTIVEFIBER = S_before.ACTIVEFIBER
S_bridge.CURRENT = S_before.CURRENT
S_bridge.ORIGIN = S_before.ORIGIN
pgenrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_a)]
pgenrelease.PENDING = (n_old)
pgenrelease.VALUE = S_before.RESULT
pgenrelease.BASE = S_before.BASE
$heap_owners($heap_graph(S_bridge),HOBJECT n_a) = 1
$heap_owners($heap_graph(S_bridge),HOBJECT n_b) = 1
S_bad_generator_pending = S_bridge[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease[.PENDING = (n_b)]) :: (DESTRUCTOR_RELEASE pdestructionrelease_remaining) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_carrier) :: ptask_tail*]
$heap_valid($heap_graph(S_bad_generator_pending))
~$call_descriptors_valid(S_bad_generator_pending)
'''.strip().splitlines()
    checks += valid('S_bridge')
    checks += driver.seek('S_enter', 'S_bridge', 403) + valid('S_enter')
    checks += r'''
S_enter.TODO = (GENERATOR_CLOSE_ENTER pgenclose_a) :: ptask_enter*
pgenclose_a.OBJECT = n_a
pgenclose_a.PENDING = (n_old)
pgenclose_a.STAGE = CLOSE_QUEUED
S_enter.ACTIVEFIBER = (n_fiber)
S_enter.DESTRUCTION.FRAMES = S_before.DESTRUCTION.FRAMES
$heap_owners($heap_graph(S_enter),HOBJECT n_b) = 1
'''.strip().splitlines()
    checks += driver.seek('S_throw', 'S_enter', 404) + valid('S_throw')
    checks += r'''
S_throw.TODO = [THROW_SEARCH n_new]
S_throw.CURRENT = (pcallcontext_a)
S_throw.FRAMES = pframe_close_a :: pframe_close_tail*
pframe_close_a.TODO = (GENERATOR_CLOSE_DONE pgenclose_done_a) :: ptask_done_a*
pgenclose_done_a.OBJECT = n_a
pgenclose_done_a.CONTEXT = pcallcontext_a
pgenclose_done_a.PENDING = (n_old)
$lookup(S_throw.ENV,$ptascii("tag")) = (n_tag_cell)
S_throw.STORE[n_tag_cell] = DEFINED (PSTRING $ptascii("A"))
$generator_close_active(S_throw)
$heap_owners($heap_graph(S_throw),HOBJECT n_b) = 1
S_restore_budget = $drive_steps(S_throw,1)
S_restore_budget.COMPLETION = BUDGET
S_restore = S_restore_budget[.COMPLETION = NORMAL]
S_restore.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease_frame_a) :: (GENERATOR_CLOSE_DONE pgenclose_finished_a) :: ptask_done_a*
pgenclose_finished_a = pgenclose_done_a[.STAGE = CLOSE_FINISHED]
pgenrelease_frame_a.PENDING = (n_new)
DESTRUCTION_VALUE (HCELL n_tag_cell) <- pgenrelease_frame_a.JOBS
S_restore.DESTRUCTION.FRAMES = S_before.DESTRUCTION.FRAMES
S_restore.ACTIVEFIBER = (n_fiber)
S_restore.CURRENT = S_before.CURRENT
S_restore.OBJECTS[n_a] = GENERATOR pgenerator_closed_a
pgenerator_closed_a.PHASE = GENERATOR_CLOSED
pgenerator_closed_a.FRAME = eps
$heap_owners($heap_graph(S_restore),HOBJECT n_b) = 1
'''.strip().splitlines()
    checks += valid('S_restore')
    checks += driver.seek('S_after_a', 'S_restore', 401) + valid('S_after_a')
    checks += r'''
S_after_a.ACTIVEFIBER = (n_fiber)
S_after_a.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_after_a) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_carrier_new) :: ptask_tail*
S_after_a.DESTRUCTION.RELEASES = pdestructionrelease_after_a :: pdestructionrelease_tail*
S_after_a.DESTRUCTION.FRAMES = pdestructionframe_carrier_new :: pdestructionframe_carrier_tail*
pdestructionframe_carrier_new = pdestructionframe_carrier[.PENDING = (n_new)]
pdestructionrelease_after_a.JOBS = (DESTRUCTION_VALUE (HOBJECT n_b)) :: pdestructionjob_after_a*
$throwable_live(S_after_a,n_new)
$throwable_field(S_after_a,n_new,"previous") = POBJECT n_old
~((HOBJECT n_a) <- S_after_a.ALLOCATIONS)
S_after_a.OBJECTS[n_b] = GENERATOR pgenerator_b
$heap_owners($heap_graph(S_after_a),HOBJECT n_b) = 1
$close_outputs(S_after_a.EVENTS) = $ptascii("A|")
$destructor_selected_pending(S_after_a,(pdestructionframe_carrier_new)) = (n_new)
S_second_budget = $drive_steps(S_after_a,1)
S_second_budget.COMPLETION = BUDGET
S_second = S_second_budget[.COMPLETION = NORMAL]
S_second.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease_b) :: ptask_second*
pgenrelease_b.JOBS = [DESTRUCTION_VALUE (HOBJECT n_b)]
pgenrelease_b.PENDING = (n_new)
S_second.DESTRUCTION.FRAMES = S_after_a.DESTRUCTION.FRAMES
S_second.ACTIVEFIBER = (n_fiber)
'''.strip().splitlines()
    checks += valid('S_second')
    checks += driver.seek('S_catch', 'S_second', 402) + valid('S_catch')
    checks += r'''
S_catch.ACTIVEFIBER = (n_fiber)
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_new) :: ptask_catch*
$throwable_field(S_catch,n_new,"previous") = POBJECT n_old
~((HOBJECT n_a) <- S_catch.ALLOCATIONS)
~((HOBJECT n_b) <- S_catch.ALLOCATIONS)
~(pdestructionframe_carrier_new <- S_catch.DESTRUCTION.FRAMES)
$close_outputs(S_catch.EVENTS) = $ptascii("A|B|")
S_stopped = $drive_steps(S_restore,0)
S_stopped.COMPLETION = BUDGET
S_stopped = S_restore[.COMPLETION = BUDGET]
S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)
S_direct = $drive(S_restore,4096)
S_resumed = S_direct
S_resumed.COMPLETION = NORMAL
S_resumed.TODO = eps
S_resumed.FRAMES = eps
S_resumed.ACTIVEFIBER = eps
S_resumed.FIBERCALLERS = eps
$close_outputs_only(S_resumed.EVENTS)
'''.strip().splitlines()
    checks += ['$close_outputs(S_resumed.EVENTS) = ' + byte_expr(CASES[name][1])]
    return checks + valid('S_resumed')


def main():
    driver.source.WATCHED += [
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/291-fiber-lifecycle.watsup',
        'spec/semantics/302-fiber-callback-retirement.watsup',
        'spec/semantics/310-generator-fiber-close.watsup',
        str(Path(__file__).relative_to(ROOT)),
    ]
    driver.__file__ = __file__
    driver.CASES = CASES
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
