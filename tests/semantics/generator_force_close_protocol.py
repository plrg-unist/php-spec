#!/usr/bin/env python3
"""Source-reached last-owner close authority, cache and pending-outcome checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

from recorded_worker import Worker
import generator_force_close_review as source
import typed_static_invoke_set_protocol as driver

ROOT = source.ROOT
CASES = {name: source.CASES[case] for name, case in [
    ('graph-input', 'graph-temporary-child'),
    ('graph-queued', 'graph-temporary-child'),
    ('graph-frames', 'graph-temporary-child'),
    ('parameter-held', 'graph-child-parameter'),
    ('cache-input', 'array-reference-cache-child'),
    ('cache-body', 'array-reference-cache-child'),
    ('pending-return', 'paused-finally-return-child'),
    ('scope-body', 'inherited-private-forced-finally'),
    ('scanning-plan', 'catch-bypassed-nested-finally'),
    ('foreach-cursor', 'foreach-generator-force-close'),
    ('caller-pending', 'caller-unwind-pending-exception'),
]}
PREFIX = r'''
dec $close_body_named(pstate,text) : bool
def $close_body_named(S,text) = true
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) = (pgenclose)
  -- if pgenclose.STAGE = CLOSE_BODY porigin
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii(text)
def $close_body_named(S,text) = false -- otherwise
dec $close_return_head(ptask) : bool
dec $close_return_operand(ptask*) : poperand?
def $close_return_operand(eps) = eps
def $close_return_operand((FINALLY_RETURN porigin porigin_source poperand) :: ptask*) = (poperand)
def $close_return_operand(ptask :: ptask_tail*) = $close_return_operand(ptask_tail*)
  -- if ~$close_return_head(ptask)
def $close_return_head(FINALLY_RETURN porigin porigin_source poperand) = true
def $close_return_head(ptask) = false -- otherwise
dec $close_next_head(ptask) : bool
def $close_next_head(GENERATOR_NEXT pgeneratorop) = true
def $close_next_head(ptask) = false -- otherwise
dec $close_next_operation(ptask*) : pgeneratorop?
def $close_next_operation(eps) = eps
def $close_next_operation((GENERATOR_NEXT pgeneratorop) :: ptask*) = (pgeneratorop)
def $close_next_operation(ptask :: ptask_tail*) = $close_next_operation(ptask_tail*)
  -- if ~$close_next_head(ptask)
dec $close_ordinary_marker(ptask*,porigin) : ptask*
def $close_ordinary_marker(eps,porigin) = eps
def $close_ordinary_marker((GENERATOR_CLOSE_FINALLY porigin) :: ptask_tail*,porigin) = (FINALLY_RESUME porigin eps) :: $close_ordinary_marker(ptask_tail*,porigin)
def $close_ordinary_marker((FINALLY_PHASE porigin 6) :: ptask_tail*,porigin) = (FINALLY_PHASE porigin 0) :: $close_ordinary_marker(ptask_tail*,porigin)
def $close_ordinary_marker(ptask :: ptask_tail*,porigin) = ptask :: $close_ordinary_marker(ptask_tail*,porigin)
  -- if ptask =/= GENERATOR_CLOSE_FINALLY porigin /\ ptask =/= FINALLY_PHASE porigin 6
dec $close_phase(pstate,nat) : bool
def $close_phase(S,0) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "current"
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
def $close_phase(S,10) = true
  -- if S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if pgenrelease.JOBS =/= eps
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("outer")
def $close_phase(S,11) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("inner")
def $close_phase(S,12) = $close_body_named(S,"inner")
def $close_phase(S,13) = $close_body_named(S,"outer")
def $close_phase(S,20) = true
  -- if $close_phase(S,0)
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.INPUT = (PARRAY n)
  -- if pgeneratorfrom.CURRENT = (REFERENCE n_cell)
def $close_phase(S,21) = $close_body_named(S,"seq")
def $close_phase(S,30) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("seq")
  -- if pgenclose.FRAME = (pframe)
  -- if $close_return_operand(pframe.TODO) = (KNOWN (POBJECT n))
def $close_phase(S,40) = true
  -- if $close_body_named(S,"seq")
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER =/= eps
def $close_phase(S,50) = true
  -- if S.TODO = (GENERATOR_CLOSE_SCAN n porigin) :: ptask*
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) = (pgenclose)
  -- if pgenclose.STAGE = CLOSE_SCANNING
  -- if pgenclose.NEXT = 1
  -- if |$generator_close_regions(S,pgenclose.SITE)| = 2
def $close_phase(S,60) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("seq")
  -- if pgenclose.FRAME = (pframe)
  -- if $useriter_tasks_ids(pframe.TODO) = [n_cursor]
def $close_phase(S,70) = true
  -- if $close_body_named(S,"seq")
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) = (pgenclose)
  -- if pgenclose.PENDING = (n)
  -- if $throwable_field(S,n,"message") = PSTRING $ptascii("old")
def $close_phase(S,71) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) =/= eps
  -- if $throwable_field(S,n,"message") = PSTRING $ptascii("new")
def $close_phase(S,72) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask*
  -- if $throwable_field(S,n,"message") = PSTRING $ptascii("new")
  -- if $throwable_field(S,n,"previous") = POBJECT n_old
  -- if $throwable_field(S,n_old,"message") = PSTRING $ptascii("old")
def $close_phase(S,n_phase) = false -- otherwise
dec $close_seek(pstate,nat,nat) : pstate
def $close_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $close_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $close_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $close_phase(S,n_phase)
def $close_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$close_phase(S,n_phase)
  -- if n = 0 \/ (S.TODO = eps /\ S.FRAMES = eps)
def $close_seek(S,n_phase,n) = $close_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$close_phase(S,n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.FRAMES =/= eps
dec $close_output(pevent) : bool
dec $close_outputs(pevent*) : nat*
def $close_outputs(eps) = eps
def $close_outputs((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $close_outputs(pevent*)
def $close_outputs(pevent :: pevent_tail*) = $close_outputs(pevent_tail*)
  -- if ~$close_output(pevent)
def $close_output(OUTPUT ptbytes) = true
def $close_output(pevent) = false -- otherwise
dec $close_outputs_only(pevent*) : bool
def $close_outputs_only(eps) = true
def $close_outputs_only(pevent :: pevent_tail*) = ($close_output(pevent) /\ $close_outputs_only(pevent_tail*))
'''


def seek(name, previous, phase):
    return [f'{name}_found = $close_seek({previous},{phase},4096)',
            f'{name}_found.COMPLETION = NORMAL \\/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$close_phase({name},{phase})']


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def reject(checks, name, expression):
    state = 'S_bad_' + name
    checks += [f'{state} = {expression}', f'$heap_valid($heap_graph({state}))',
               f'~$call_descriptors_valid({state})']


def body_binding(state, name='seq'):
    return [f'{state}.CURRENT = (pcallcontext_body)',
            f'{state}.FRAMES = pframe_caller :: pframe_caller_tail*',
            'pframe_caller.TODO = (GENERATOR_CLOSE_DONE pgenclose_body) :: ptask_caller*',
            'pgenclose_body.CONTEXT = pcallcontext_body',
            'pgenclose_body.STAGE = CLOSE_BODY porigin_finally',
            f'$trace_context_function({state},pcallcontext_body) = $ptascii("{name}")',
            f'{state}.OBJECTS[pgenclose_body.OBJECT] = GENERATOR pgenerator_body',
            'pgenerator_body.PHASE = GENERATOR_RUNNING', 'pgenerator_body.FRAME = eps',
            '$generator_from_input_of(pgenerator_body.DELEGATE) = eps']


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + driver.byte_expr(os.fsencode(path)) + ',' + driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    previous = 'S_initial'
    if name in ['graph-input', 'graph-frames', 'parameter-held']:
        checks += seek('S_live', previous, 0) + valid('S_live')
        checks += r'''
S_live.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_live*
S_live.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_live
pgenerator_live.DELEGATE = (pgeneratorfrom_live)
pgeneratorfrom_live.INPUT = (POBJECT n_child)
n_parent = pgeneratorop.OBJECT
'''.strip().splitlines()
        previous = 'S_live'
    if name == 'graph-input':
        checks += seek('S_input', previous, 10) + valid('S_input')
        checks += r'''
S_input.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_input*
pgenclose.OBJECT = n_parent
pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_child)) :: pdestructionjob_tail*
S_input.OBJECTS[n_parent] = GENERATOR pgenerator_parent
pgenerator_parent.PHASE = GENERATOR_CLOSING
pgenerator_parent.FRAME = eps
$generator_from_input_of(pgenerator_parent.DELEGATE) = eps
S_input.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_PAUSED
$heap_owners($heap_graph(S_input),HOBJECT n_child) = 1
$heap_owners($heap_graph(S_input)[.ROOTS = $destruction_node_delete($machine_roots(S_input),HOBJECT n_parent)],HOBJECT n_parent) = 0
'''.strip().splitlines()
        reject(checks, 'duplicate_input', 'S_input[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: (GENERATOR_CLOSE_ENTER pgenclose) :: (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_input*]')
        previous = 'S_input'
    elif name == 'graph-queued':
        checks += seek('S_queued', previous, 11) + valid('S_queued')
        checks += r'''
S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_queued*
pgenclose.FRAME = (pframe_queued)
pgenclose.STAGE = CLOSE_QUEUED
pgenclose.NEXT = 0
pframe_queued.CONTEXT = (pgenclose.CONTEXT)
S_queued.CURRENT = pgenclose.CALLER
S_queued.ORIGIN = pgenclose.CALLSITE
$generator_close_regions(S_queued,pgenclose.SITE) = [porigin_finally]
$generator_close_unentered(pframe_queued.TODO,[porigin_finally]) = [porigin_finally]
$heap_owners($heap_graph(S_queued)[.ROOTS = $destruction_node_delete($machine_roots(S_queued),HOBJECT pgenclose.OBJECT)],HOBJECT pgenclose.OBJECT) = 0
'''.strip().splitlines()
        reject(checks, 'lost_plan', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose[.FRAME = (pframe_queued[.ORIGIN = (pgenclose.CONTEXT.FUNCTION)][.TODO = eps])]) :: ptask_queued*]')
        reject(checks, 'external_owner', 'S_queued[.HELD = S_queued.HELD ++ [HOBJECT pgenclose.OBJECT]]')
        reject(checks, 'caller_site', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose[.CALLSITE = (pgenclose.CONTEXT.FUNCTION)]) :: ptask_queued*]')
        previous = 'S_queued'
    elif name == 'graph-frames':
        checks += seek('S_inner', previous, 12) + valid('S_inner')
        checks += r'''
S_inner.CURRENT = (pcallcontext_inner)
S_inner.FRAMES = pframe_inner :: pframe_inner_tail*
pframe_inner.TODO = (GENERATOR_CLOSE_DONE pgenclose_inner) :: ptask_inner*
pgenclose_inner.OBJECT = n_child
$trace_context_function(S_inner,pcallcontext_inner) = $ptascii("inner")
$generator_close_claims(pframe_inner.TODO) = [n_child,n_parent]
'''.strip().splitlines()
        checks += seek('S_body', 'S_inner', 13) + valid('S_body') + body_binding('S_body', 'outer')
        checks += ['pgenclose_body.OBJECT = n_parent', '~((HOBJECT n_child) <- S_body.ALLOCATIONS)']
        reject(checks, 'body_context', 'S_body[.FRAMES = pframe_caller[.TODO = (GENERATOR_CLOSE_DONE pgenclose_body[.CONTEXT = pcallcontext_body[.FUNCTION = pgenclose_inner.CONTEXT.FUNCTION]]) :: ptask_caller*] :: pframe_caller_tail*]')
        checks += ['S_bad_ordinary_marker = S_body[.TODO = $close_ordinary_marker(S_body.TODO,porigin_finally)]',
                   '$heap_valid($heap_graph(S_bad_ordinary_marker))',
                   '$finally_current_complete(S_bad_ordinary_marker)',
                   '~$call_descriptors_valid(S_bad_ordinary_marker)']
        previous = 'S_body'
    elif name == 'parameter-held':
        checks += seek('S_body', previous, 13) + valid('S_body') + body_binding('S_body', 'outer')
        checks += r'''
pgenclose_body.OBJECT = n_parent
S_body.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_PAUSED
$trace_slot(S_body,S_body.ENV,$ptascii("i")) = POBJECT n_child
$heap_owners($heap_graph(S_body),HOBJECT n_child) = 1
'''.strip().splitlines()
        previous = 'S_body'
    elif name in ['cache-input', 'cache-body']:
        checks += seek('S_live', previous, 20) + valid('S_live')
        checks += r'''
S_live.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_live*
S_live.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_live
pgenerator_live.DELEGATE = (pgeneratorfrom_live)
pgeneratorfrom_live.INPUT = (PARRAY n_input)
pgeneratorfrom_live.CURRENT = (REFERENCE n_cell)
S_live.STORE[n_cell] = DEFINED (POBJECT n_child)
n_parent = pgeneratorop.OBJECT
'''.strip().splitlines()
        checks += seek('S_body', 'S_live', 21) + valid('S_body') + body_binding('S_body')
        checks += r'''
pgenclose_body.OBJECT = n_parent
pgenerator_body.DELEGATE = (pgeneratorfrom_body)
pgeneratorfrom_body.CURRENT = (REFERENCE n_cell)
~((HARRAY n_input) <- S_body.ALLOCATIONS)
S_body.STORE[n_cell] = DEFINED (POBJECT n_child)
$heap_owners($heap_graph(S_body),HCELL n_cell) = 1
S_body.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_PAUSED
$heap_owners($heap_graph(S_body),HOBJECT n_child) = 1
'''.strip().splitlines()
        if name == 'cache-input':
            reject(checks, 'stranded_input', '$generator_set(S_body,n_parent,pgenerator_body[.DELEGATE = (pgeneratorfrom_body[.INPUT = (POBJECT n_child)])])')
        else:
            reject(checks, 'wrapped_claim', 'S_body[.FRAMES = pframe_caller[.TODO = (AT pgenclose_body.SITE (GENERATOR_CLOSE_DONE pgenclose_body)) :: ptask_caller*] :: pframe_caller_tail*]')
        previous = 'S_body'
    elif name == 'pending-return':
        checks += seek('S_queued', previous, 30) + valid('S_queued')
        checks += r'''
S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_queued*
pgenclose.FRAME = (pframe_queued)
$close_return_operand(pframe_queued.TODO) = (KNOWN (POBJECT n_child))
S_queued.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.PHASE = GENERATOR_PAUSED
$heap_owners($heap_graph(S_queued),HOBJECT n_child) = 1
'''.strip().splitlines()
        checks += seek('S_inner', 'S_queued', 12) + valid('S_inner')
        checks += r'''
S_inner.FRAMES = pframe_inner :: pframe_inner_tail*
pframe_inner.TODO = (GENERATOR_CLOSE_DONE pgenclose_inner) :: ptask_inner*
pgenclose_inner.OBJECT = n_child
pframe_inner.CONTEXT = eps
$generator_close_context_tasks(pgenclose.CONTEXT,pframe_inner.TODO)
'''.strip().splitlines()
        checks += seek('S_body', 'S_inner', 21) + valid('S_body') + body_binding('S_body')
        checks += ['~((HOBJECT n_child) <- S_body.ALLOCATIONS)', 'pgenclose_body.OBJECT = pgenclose.OBJECT']
        previous = 'S_body'
    elif name == 'scope-body':
        checks += seek('S_body', previous, 40) + valid('S_body') + body_binding('S_body')
        checks += r'''
pcallcontext_body.RECEIVER = (n_receiver)
pcallcontext_body.LEXICAL_CLASS = (porigin_owner)
pcallcontext_body.CALLED_CLASS = (porigin_child)
$class_at(S_body.CLASSES,porigin_owner) = (pclassdesc_owner)
pclassdesc_owner.NAME = $ptascii("Owner")
$class_at(S_body.CLASSES,porigin_child) = (pclassdesc_child)
pclassdesc_child.NAME = $ptascii("Child")
$this_receiver(S_body) = (n_receiver)
$property_resolve(S_body,n_receiver,$ptascii("v")) = PROPERTY_ACCESS ptbytes_private
$property_quiet(S_body,POBJECT n_receiver,$ptascii("v"),0).RESULT = KNOWN (PINT 7)
'''.strip().splitlines()
        reject(checks, 'called_scope', 'S_body[.FRAMES = pframe_caller[.TODO = (GENERATOR_CLOSE_DONE pgenclose_body[.CONTEXT = pcallcontext_body[.CALLED_CLASS = (porigin_owner)]]) :: ptask_caller*] :: pframe_caller_tail*]')
        previous = 'S_body'
    elif name == 'scanning-plan':
        checks += seek('S_scan', previous, 50) + valid('S_scan')
        checks += r'''
S_scan.TODO = (GENERATOR_CLOSE_SCAN n_parent porigin_site) :: ptask_scan*
S_scan.CURRENT = (pcallcontext_body)
S_scan.FRAMES = pframe_caller :: pframe_caller_tail*
pframe_caller.TODO = (GENERATOR_CLOSE_DONE pgenclose_body) :: ptask_caller*
pgenclose_body.STAGE = CLOSE_SCANNING
pgenclose_body.NEXT = 1
$generator_close_regions(S_scan,porigin_site) = [porigin_inner,porigin_outer]
$generator_close_unentered(ptask_scan*,[porigin_inner,porigin_outer]) = [porigin_outer]
'''.strip().splitlines()
        reject(checks, 'lost_outer', 'S_scan[.TODO = [GENERATOR_CLOSE_SCAN n_parent porigin_site]][.ORIGIN = (pcallcontext_body.FUNCTION)]')
        reject(checks, 'wrong_progress', 'S_scan[.FRAMES = pframe_caller[.TODO = (GENERATOR_CLOSE_DONE pgenclose_body[.NEXT = 2]) :: ptask_caller*] :: pframe_caller_tail*]')
        previous = 'S_scan'
    elif name == 'foreach-cursor':
        checks += seek('S_queued', previous, 60) + valid('S_queued')
        checks += r'''
S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_queued*
pgenclose.FRAME = (pframe_queued)
$useriter_tasks_ids(pframe_queued.TODO) = [n_cursor]
$useriter_task_ids(GENERATOR_CLOSE_ENTER pgenclose) = [n_cursor]
$generator_cursor_owners_valid(S_queued)
$iterator_lookup(S_queued.ITERATORS,n_cursor) = (GENERATORITER n_cursor n_child)
$close_next_operation(pframe_queued.TODO) = (pgeneratorop_cursor)
'''.strip().splitlines()
        reject(checks, 'duplicate_cursor', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose[.FRAME = (pframe_queued[.TODO = pframe_queued.TODO ++ [GENERATOR_NEXT pgeneratorop_cursor]])]) :: ptask_queued*]')
        checks += ['~$generator_cursor_owners_valid(S_bad_duplicate_cursor)']
        checks += seek('S_body', 'S_queued', 21) + valid('S_body') + body_binding('S_body')
        checks += ['$iterator_lookup(S_body.ITERATORS,n_cursor) = eps', '~((HOBJECT n_child) <- S_body.ALLOCATIONS)']
        previous = 'S_body'
    elif name == 'caller-pending':
        checks += seek('S_body', previous, 70) + valid('S_body') + body_binding('S_body')
        checks += r'''
pgenclose_body.PENDING = (n_old)
$throwable_live(S_body,n_old)
$throwable_field(S_body,n_old,"message") = PSTRING $ptascii("old")
$throwable_field(S_body,n_old,"previous") = PNULL
$($heap_owners($heap_graph(S_body),HOBJECT n_old) > 0)
'''.strip().splitlines()
        checks += seek('S_new', 'S_body', 71) + valid('S_new')
        checks += r'''
S_new.TODO = (THROW_SEARCH n_new) :: ptask_throw*
n_new =/= n_old
$throwable_live(S_new,n_new)
$throwable_live(S_new,n_old)
$throwable_field(S_new,n_new,"previous") = PNULL
$generator_close_saved(S_new,S_new.CURRENT,S_new.FRAMES) = (pgenclose_throw)
pgenclose_throw.PENDING = (n_old)
'''.strip().splitlines()
        checks += seek('S_catch', 'S_new', 72) + valid('S_catch')
        checks += r'''
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_new) :: ptask_catch*
$throwable_live(S_catch,n_new)
$throwable_live(S_catch,n_old)
$throwable_field(S_catch,n_new,"previous") = POBJECT n_old
$heap_owners($heap_graph(S_catch),HOBJECT n_old) = 1
~((HOBJECT pgenclose_body.OBJECT) <- S_catch.ALLOCATIONS)
'''.strip().splitlines()
        previous = 'S_catch'
    checks += [f'S_stopped = $drive_steps({previous},0)', 'S_stopped.COMPLETION = BUDGET',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps', 'S_resumed.FRAMES = eps',
               'S_resumed.ITERATORS = eps', '$close_outputs_only(S_resumed.EVENTS)',
               '$close_outputs(S_resumed.EVENTS) = ' + driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    if name in ['cache-input', 'cache-body']:
        checks += ['~((HCELL n_cell) <- S_resumed.ALLOCATIONS)', '~((HOBJECT n_child) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['fixtures', 'prepare', 'check'], default='check')
    parser.add_argument('--select', help='Comma-separated exact group IDs')
    parser.add_argument('--sl', action='store_true', help='Use maintained strict production SL mode')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES)
    assert names and len(names) == len(set(names)) and all(n in CASES for n in names)
    out = Path(tempfile.mkdtemp(prefix='generator-force-close-protocol-', dir=ROOT / '.tools'))
    watched = source.WATCHED + [str(Path(__file__).relative_to(ROOT)), 'tests/semantics/_build/default/numeric_runner.exe']
    def fingerprints():
        return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in watched}
    report = {'result': 'fail', 'mode': args.mode, 'backend': 'sl' if args.sl else 'al',
              'records': [], 'assertions': 0, 'selection': names, 'root': str(ROOT),
              'before': fingerprints(), 'profile': driver.types.PROFILE,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    print(out, flush=True)
    try:
        (out / 'case-fixture.py').write_bytes(Path(__file__).read_bytes())
        for item in ['base.json', 'parent-composition.json', 'parent-union.diff']:
            provenance = ROOT / '.tools' / item
            if provenance.is_file():
                (out / item).write_bytes(provenance.read_bytes())
        identity = source.run([str(driver.types.PHP), '-n', *driver.types.FLAGS, '-r',
                               'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,get_loaded_extensions(),ini_get_all(null,false)]);'], out / 'runtime', 10)
        assert identity.returncode == 0 and not identity.stderr
        report['runtime'] = json.loads(identity.stdout)
        assert report['runtime'][:4] == ['8.5.10', 'cli', 8, False]
        assert all(report['runtime'][5][key] == value for key, value in driver.types.PROFILE.items())
        for name in names:
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES[name][0])
            row = {'id': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                   'evaluated': args.mode == 'check'}
            report['records'].append(row)
            native = source.run([str(driver.types.PHP), '-n', *driver.types.FLAGS, str(path)], directory / 'native', 10)
            row.update(native_exit=native.returncode, native_stdout=driver.b64(native.stdout), native_stderr=driver.b64(native.stderr))
            assert native.returncode == 0 and native.stdout == CASES[name][1] and not native.stderr
            frontend = Worker([str(driver.types.PHP), '-n', *driver.types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': driver.b64(path.read_bytes())})
                assert parsed['accepted']
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                finally:
                    adapter.close()
            finally:
                frontend.close()
            checks = assertions(checked, path, directory, name)
            (directory / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX + '\ndec $body() : bool\ndef $body() = true\n' +
                               ''.join('  -- if ' + check + '\n' for check in checks) +
                               '\ndec $main() : bool\ndef $main() = ' + ('true' if args.mode == 'prepare' else '$body()') + '\n')
            row['assertions'] = len(checks)
            if args.mode != 'fixtures':
                runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
                modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
                argv = [str(runner)] + (['--sl'] if args.sl else []) + [str(ROOT / module) for module in modules] + [str(fixture)]
                result = driver.process(argv, directory / 'numeric', 300, ROOT)
                assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['assertions'] += len(checks) if args.mode == 'check' else 0
            row['passed'] = True
            print(name, args.mode, 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprints()
        if report['before'] != report['after']:
            report['result'] = 'fail'
            report['failure'] = {'type': 'InputChanged', 'message': 'semantic/source/fixture inputs changed'}
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)
    return 0 if report['result'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
