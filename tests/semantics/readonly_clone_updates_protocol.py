#!/usr/bin/env python3
"""Source-reached clone update windows, progress and own Stringable consumers."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
from readonly_clone_updates_sources import CASES, EXPECTED, snapshot

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $clone_updates_review_output(pevent*) : ptbytes
dec $clone_updates_review_is_output(pevent) : bool
def $clone_updates_review_output(eps) = eps
def $clone_updates_review_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $clone_updates_review_output(pevent*)
def $clone_updates_review_output(pevent :: pevent_tail*) = $clone_updates_review_output(pevent_tail*) -- if ~$clone_updates_review_is_output(pevent)
def $clone_updates_review_is_output(OUTPUT ptbytes) = true
def $clone_updates_review_is_output(pevent) = false -- otherwise
dec $clone_updates_review_cursor(pstate,nat) : bool
def $clone_updates_review_cursor(S,n) = true
  -- if S.TODO = (CLONE_READONLY_UPDATE pcloneupdate) :: ptask_tail*
  -- if pcloneupdate.CURSOR = n
def $clone_updates_review_cursor(S,n) = false -- otherwise
dec $clone_updates_review_string(pstate) : pcloneupdatestring?
def $clone_updates_review_string(S) = (pcloneupdatestring)
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) :: (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_tail*
  -- if $context_target(pcallcontext) = METHOD_TARGET n porigin_method
  -- if n = pcloneupdatestring.OBJECT
  -- if $clone_update_string_context(S,pcallcontext)
def $clone_updates_review_string(S) = eps -- otherwise
dec $clone_updates_review_phase(pstate,nat) : bool
def $clone_updates_review_phase(S,0) = true
  -- if S.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*
def $clone_updates_review_phase(S,1) = true
  -- if $clone_updates_review_output(S.EVENTS) = $ptascii("C|6|")
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_tail*
  -- if $clone_context_valid(S,pcallcontext)
def $clone_updates_review_phase(S,2) = $clone_updates_review_cursor(S,0)
def $clone_updates_review_phase(S,3) = $clone_updates_review_cursor(S,1)
def $clone_updates_review_phase(S,4) = $clone_updates_review_cursor(S,2)
def $clone_updates_review_phase(S,5) = (S.CLONES = eps /\ $clone_updates_review_output(S.EVENTS) = $ptascii("Cannot assign string to property Owner::$y of type int|"))
def $clone_updates_review_phase(S,6) = ($clone_updates_review_string(S) =/= eps /\ $clone_updates_review_output(S.EVENTS) = $ptascii("T|"))
def $clone_updates_review_phase(S,7) = true
  -- if $clone_updates_review_string(S) = (pcloneupdatestring)
  -- if $location_slot(S,PROPERTY pcloneupdatestring.UPDATE.OPERATION.TARGET pcloneupdatestring.KEY) = DEFINED (PSTRING $ptascii("inner"))
def $clone_updates_review_phase(S,8) = true
  -- if S.TODO = (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING $ptascii("outer"))
def $clone_updates_review_phase(S,9) = true
  -- if $clone_updates_review_string(S) = (pcloneupdatestring)
  -- if $location_slot(S,PROPERTY pcloneupdatestring.UPDATE.OPERATION.TARGET $ptascii("mutable")) = UNDEFINED
def $clone_updates_review_phase(S,10) = (S.ACTIVEFIBER = eps /\ S.CLONES =/= eps /\ $clone_updates_review_output(S.EVENTS) = $ptascii("T|pause|"))
def $clone_updates_review_phase(S,11) = (S.ACTIVEFIBER = eps /\ S.CLONES =/= eps /\ $clone_updates_review_output(S.EVENTS) = $ptascii("T|pause|inner|"))
def $clone_updates_review_phase(S,n) = false -- otherwise
dec $clone_updates_review_terminal(pstate) : bool
def $clone_updates_review_terminal(S) = (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $clone_updates_review_seek(pstate,nat,nat) : pstate
def $clone_updates_review_seek(S,n_phase,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $clone_updates_review_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $clone_updates_review_phase(S[.COMPLETION = NORMAL],n_phase)
def $clone_updates_review_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$clone_updates_review_phase(S[.COMPLETION = NORMAL],n_phase)
  -- if n = 0 \/ $clone_updates_review_terminal(S)
def $clone_updates_review_seek(S,n_phase,n) = $clone_updates_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$clone_updates_review_phase(S[.COMPLETION = NORMAL],n_phase)
  -- if ~$clone_updates_review_terminal(S) /\ $(n > 0)
'''

THROW_PREFIX = r'''
def $clone_updates_review_phase(S,12) = (S.CLONES = eps /\ $clone_updates_review_output(S.EVENTS) = $ptascii("T|stop|BaseBox/__toString/clone|"))
'''

ALIAS_PREFIX = r'''
def $clone_updates_review_phase(S,13) = (S.CLONES = eps /\ $clone_updates_review_output(S.EVENTS) = $ptascii("T|Cannot assign string to reference held by property Owner::$y of type int|clone|"))
'''

def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))',
            f'$clone_windows_valid({state})']

def seek(parent, state, phase):
    return [f'{state}_found = $clone_updates_review_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$clone_updates_review_phase({state},{phase})', *valid(state)]

def complete(state, expected):
    encoded = '[' + ', '.join(str(c) for c in expected.encode()) + ']'
    return [f'S_done = $drive_steps({state},2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$clone_updates_review_output(S_done.EVENTS) = ' + encoded,
            'S_done.CLONES = eps', *valid('S_done')]

def reject(name, changed, predicate=None):
    state = 'S_bad_' + name
    clauses = [f'{state} = {changed}', f'$heap_valid($heap_graph({state}))',
               f'~$call_descriptors_valid({state})']
    if predicate:
        clauses.append(f'~{predicate}({state})')
    return clauses

def window(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_enter',0),
              'S_enter.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_enter_tail*',
              'S_enter.CLONES = [pclonewindow_enter]',
              'pclonewindow_enter.OPERATION = pcloneoperation',
              'pclonewindow_enter.PHASE = CLONE_CALLBACK',
              'pclonewindow_enter.AVAILABLE = [$ptascii("x"),$ptascii("y"),$ptascii("z")]',
              'pcloneoperation.CALL = (pclonecall)',
              r'pcloneoperation.INPUT = eps /\ pcloneoperation.SCOPE = eps',
              *seek('S_enter','S_callback',1),
              'S_callback.CLONES = [pclonewindow_enter[.AVAILABLE = [$ptascii("x"),$ptascii("y")]][.REVISIONS = [{KEY $ptascii("x"), COUNT 0},{KEY $ptascii("y"), COUNT 0},{KEY $ptascii("z"), COUNT 1}]]]',
              '$location_slot(S_callback,PROPERTY pcloneoperation.TARGET $ptascii("z")) = DEFINED (PINT 6)',
              *seek('S_callback','S_zero',2),
              'S_zero.TODO = (CLONE_READONLY_UPDATE pcloneupdate_zero) :: ptask_zero_tail*',
              'pcloneupdate_zero.OPERATION = pcloneoperation',
              r'pcloneupdate_zero.CURSOR = 0 /\ pcloneupdate_zero.VISITED = eps',
              'S_zero.CLONES = [pclonewindow_zero]',
              'pclonewindow_zero = pclonewindow_enter[.PHASE = CLONE_UPDATES]',
              '$clone_updates_valid(S_zero,pcloneupdate_zero)',
              '$clone_reinitable(S_zero,pcloneoperation.TARGET,$ptascii("z"))',
              'pclonecall.SENT = [NAMED_SENT (KNOWN (POBJECT pcloneoperation.SOURCE)),NAMED_SENT (KNOWN (PARRAY pcloneupdate_zero.ARRAY))]',
              'S_zero.ARRAYS[pcloneupdate_zero.ARRAY].ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PSTRING $ptascii("2"))),ENTRY (KSTRING $ptascii("y")) (DIRECT (PSTRING $ptascii("4")))]',
              '$lookup(S_zero.ENV,$ptascii("other")) = (n_other_cell)',
              'S_zero.STORE[n_other_cell] = DEFINED (POBJECT n_other)',
              r'$(pcloneoperation.SOURCE < n_other) /\ $(n_other < pcloneoperation.TARGET)',
              '$location_slot(S_zero,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 1)',
              *seek('S_zero','S_one',3),
              'S_one.TODO = (CLONE_READONLY_UPDATE pcloneupdate_one) :: ptask_one_tail*',
              'pcloneupdate_one.OPERATION = pcloneoperation',
              'pcloneupdate_one.ARRAY = pcloneupdate_zero.ARRAY',
              'pcloneupdate_one.VISITED = [pclonevisit_x]',
              'pclonevisit_x.KEY = KSTRING $ptascii("x")',
              'pclonevisit_x.TARGET = $ptascii("x")',
              'pclonevisit_x.DECL = $clone_visit_decl(S_one,pcloneoperation.TARGET,$ptascii("x"))',
              r'pclonevisit_x.VALUE = (PINT 2) /\ pclonevisit_x.PRECISION = 14',
              'S_one.CLONES = [pclonewindow_one]',
              'pclonewindow_one = pclonewindow_zero[.AVAILABLE = [$ptascii("y"),$ptascii("z")]][.REVISIONS = [{KEY $ptascii("x"), COUNT 1},{KEY $ptascii("y"), COUNT 0},{KEY $ptascii("z"), COUNT 0}]]',
              '$clone_updates_valid(S_one,pcloneupdate_one)',
              '$location_slot(S_one,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 2)',
              '$task_nodes(CLONE_READONLY_UPDATE pcloneupdate_one) = [HOBJECT pcloneoperation.TARGET] ++ $clone_call_nodes(pclonecall)']
    checks += reject('missing_window','S_one[.CLONES = eps]')
    checks += reject('duplicate_window','S_one[.CLONES = S_one.CLONES ++ S_one.CLONES]','$clone_windows_valid')
    checks += reject('callback_phase','S_one[.CLONES = [pclonewindow_one[.PHASE = CLONE_CALLBACK]]]','$clone_windows_valid')
    checks += reject('restored_allowance','S_one[.CLONES = [pclonewindow_one[.AVAILABLE = $ptascii("x") :: pclonewindow_one.AVAILABLE]]]')
    checks += reject('duplicate_consumer','S_one[.TODO = (CLONE_READONLY_UPDATE pcloneupdate_one) :: (CLONE_READONLY_UPDATE pcloneupdate_one) :: ptask_one_tail*]')
    changes = [
        ('cursor_without_receipt','pcloneupdate_one[.VISITED = eps]'),
        ('receipt_without_cursor','pcloneupdate_one[.CURSOR = 0]'),
        ('cursor_past_end','pcloneupdate_one[.CURSOR = 3]'),
        ('duplicate_receipt','pcloneupdate_one[.CURSOR = 2][.VISITED = [pclonevisit_x,pclonevisit_x]]'),
        ('receipt_key','pcloneupdate_one[.VISITED = [pclonevisit_x[.KEY = KSTRING $ptascii("y")]]]'),
        ('receipt_target','pcloneupdate_one[.VISITED = [pclonevisit_x[.TARGET = $ptascii("y")]]]'),
        ('receipt_decl','pcloneupdate_one[.VISITED = [pclonevisit_x[.DECL = eps]]]'),
        ('receipt_value','pcloneupdate_one[.VISITED = [pclonevisit_x[.VALUE = (PINT 1)]]]'),
    ]
    for name, changed in changes:
        update = 'pcloneupdate_bad_' + name
        checks += [f'{update} = {changed}']
        checks += reject(name,'S_one[.TODO = (CLONE_READONLY_UPDATE '+update+') :: ptask_one_tail*]')
        checks += [f'~$clone_updates_valid(S_bad_{name},{update})']
    checks += ['pcloneupdate_skipped = pcloneupdate_zero[.CURSOR = 1][.VISITED = [pclonevisit_x[.VALUE = (PINT 1)]]]',
               'S_skipped = S_zero[.TODO = (CLONE_READONLY_UPDATE pcloneupdate_skipped) :: ptask_zero_tail*][.CLONES = [pclonewindow_one]]',
               r'S_skipped.STORE = S_zero.STORE /\ S_skipped.OBJECTPROPS = S_zero.OBJECTPROPS',
               '$clone_updates_base_valid(S_skipped,pcloneupdate_skipped)',
               '$location_slot(S_skipped,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 1)',
               '~$clone_reinitable(S_skipped,pcloneoperation.TARGET,$ptascii("x"))',
               '~$clone_updates_valid(S_skipped,pcloneupdate_skipped)',
               '$heap_valid($heap_graph(S_skipped))', '~$call_descriptors_valid(S_skipped)']
    for name, operation in [
        ('coupled_line','pcloneoperation[.LINE = $(pcloneoperation.LINE + 1)][.CALL = (pclonecall[.LINE = $(pclonecall.LINE + 1)])]'),
        ('sameclass_target','pcloneoperation[.TARGET = n_other]'),
    ]:
        op, update, state = 'pcloneoperation_'+name, 'pcloneupdate_'+name, 'S_'+name
        checks += [f'{op} = {operation}', f'{update} = pcloneupdate_one[.OPERATION = {op}]',
                   f'{state} = S_one[.TODO = (CLONE_READONLY_UPDATE {update}) :: ptask_one_tail*][.CLONES = [pclonewindow_one[.OPERATION = {op}]]]',
                   f'$clone_updates_body_valid({state},{op})',
                   f'$clone_windows_valid({state})', f'$heap_valid($heap_graph({state}))',
                   f'~$clone_updates_valid({state},{update})', f'~$call_descriptors_valid({state})']
    checks += [*seek('S_one','S_two',4),
               'S_two.TODO = (CLONE_READONLY_UPDATE pcloneupdate_two) :: ptask_two_tail*',
               'pcloneupdate_two.VISITED = [pclonevisit_x,pclonevisit_y]',
               'pclonevisit_y.KEY = KSTRING $ptascii("y")',
               'pclonevisit_y.VALUE = (PINT 4)',
               'S_two.CLONES = [pclonewindow_one[.AVAILABLE = [$ptascii("z")]][.REVISIONS = [{KEY $ptascii("x"), COUNT 1},{KEY $ptascii("y"), COUNT 1},{KEY $ptascii("z"), COUNT 0}]]]',
               '$location_slot(S_two,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 2)',
               '$location_slot(S_two,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PINT 4)',
               '$location_slot(S_two,PROPERTY pcloneoperation.TARGET $ptascii("z")) = DEFINED (PINT 6)',
               '$clone_updates_valid(S_two,pcloneupdate_two)']
    return checks + complete('S_two',expected)

def abrupt(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_zero',2),
              'S_zero.TODO = (CLONE_READONLY_UPDATE pcloneupdate_zero) :: ptask_zero_tail*',
              'pcloneoperation = pcloneupdate_zero.OPERATION',
              'S_zero.CLONES = [pclonewindow_zero]',
              'pclonewindow_zero.PHASE = CLONE_UPDATES',
              'pclonewindow_zero.AVAILABLE = [$ptascii("x"),$ptascii("y")]',
              *seek('S_zero','S_one',3),
              'S_one.TODO = (CLONE_READONLY_UPDATE pcloneupdate_one) :: ptask_one_tail*',
              'pcloneupdate_one.OPERATION = pcloneoperation',
              'pcloneupdate_one.VISITED = [pclonevisit_x]',
              'pclonevisit_x.VALUE = (PINT 2)',
              'S_one.CLONES = [pclonewindow_zero[.AVAILABLE = [$ptascii("y")]][.REVISIONS = [{KEY $ptascii("x"), COUNT 1},{KEY $ptascii("y"), COUNT 0}]]]',
              '$location_slot(S_one,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 2)',
              '$location_slot(S_one,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PINT 3)',
              *seek('S_one','S_caught',5),
              'S_caught.CLONES = eps',
              '$location_slot(S_caught,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 2)',
              '$location_slot(S_caught,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PINT 3)',
              '~$clone_reinitable(S_caught,pcloneoperation.TARGET,$ptascii("y"))']
    return checks + complete('S_caught',expected)

def stringable(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_body',6),
              '$clone_updates_review_string(S_body) = (pcloneupdatestring)',
              'S_body.CURRENT = (pcallcontext)', 'S_body.FRAMES = pframe :: pframe_tail*',
              'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_string_tail*',
              'n_object = pcloneupdatestring.OBJECT',
              'pcloneupdate = pcloneupdatestring.UPDATE', 'pcloneoperation = pcloneupdate.OPERATION',
              r'porigin_site = pcloneoperation.SITE /\ z_line = pcloneoperation.LINE',
              r'pcloneupdate.CURSOR = 0 /\ pcloneupdate.VISITED = eps',
              'S_body.CLONES = [pclonewindow]',
              r'pclonewindow.PHASE = CLONE_UPDATES /\ pclonewindow.OPERATION = pcloneoperation',
              'pclonewindow.AVAILABLE = [$ptascii("x")]',
              'S_caller = $parameter_string_frame_scope(S_body,pframe,pframe_tail*)',
              '$clone_update_string_valid(S_caller,pcloneupdatestring)',
              '$clone_update_string_context(S_body,pcallcontext)',
              '$method_current_scope(S_caller) = pcloneoperation.SCOPE',
              '$method_current_scope(S_body) =/= pcloneoperation.SCOPE',
              '$property_set_denied(S_body,pcloneoperation.TARGET,$ptascii("x"))',
              '$location_slot(S_body,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("seed"))',
              '$task_nodes(CLONE_READONLY_STRING pcloneupdatestring) = $clone_operation_nodes(pcloneoperation) ++ [HOBJECT n_object]']
    for name, record in [
        ('object','pcloneupdatestring[.OBJECT = pcloneoperation.TARGET]'),
        ('key','pcloneupdatestring[.KEY = $ptascii("missing")]'),
        ('decl','pcloneupdatestring[.DECL = pcloneoperation.SITE]'),
        ('cursor','pcloneupdatestring[.UPDATE = pcloneupdate[.CURSOR = 1]]'),
    ]:
        capture = 'pcloneupdatestring_bad_' + name
        checks += [f'{capture} = {record}']
        changed = 'S_body[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING '+capture+') :: ptask_string_tail*] :: pframe_tail*]'
        checks += reject('string_'+name,changed)
    checks += reject('string_missing_window','S_body[.CLONES = eps]')
    checks += reject('string_wrong_phase','S_body[.CLONES = [pclonewindow[.PHASE = CLONE_CALLBACK]]]','$clone_windows_valid')
    checks += reject('string_producer_receiver','S_body[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT pcloneoperation.TARGET porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_string_tail*] :: pframe_tail*]')
    checks += reject('string_producer_line','S_body[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_site $(z_line + 1)) :: (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_string_tail*] :: pframe_tail*]')
    checks += [*seek('S_body','S_inner',7),
               'S_inner.CLONES = [pclonewindow[.AVAILABLE = eps][.REVISIONS = [{KEY $ptascii("x"), COUNT 1}]]]',
               'S_inner.FRAMES = pframe_inner :: pframe_inner_tail*',
               'S_inner_caller = $parameter_string_frame_scope(S_inner,pframe_inner,pframe_inner_tail*)',
               '$clone_update_string_valid(S_inner_caller,pcloneupdatestring)',
               '~$clone_reinitable(S_inner,pcloneoperation.TARGET,$ptascii("x"))',
               *seek('S_inner','S_result',8),
               'S_result.TODO = (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_result_tail*',
               '$clone_update_string_valid(S_result,pcloneupdatestring)',
               'S_result.CLONES = [pclonewindow[.AVAILABLE = eps][.REVISIONS = [{KEY $ptascii("x"), COUNT 1}]]]',
               '$location_slot(S_result,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("inner"))',
               *seek('S_result','S_one',3),
               'S_one.TODO = (CLONE_READONLY_UPDATE pcloneupdate_one) :: ptask_one_tail*',
               'pcloneupdate_one.VISITED = [pclonevisit]',
               'pclonevisit.VALUE = (PSTRING $ptascii("outer"))',
               'pclonevisit.PRECISION = pcloneupdatestring.PRECISION',
               '$clone_updates_valid(S_one,pcloneupdate_one)',
               '$location_slot(S_one,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("outer"))']
    return checks + complete('S_one',expected)

def mutable(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_body',9),
              '$clone_updates_review_string(S_body) = (pcloneupdatestring)',
              'S_body.FRAMES = pframe :: pframe_tail*',
              'S_caller = $parameter_string_frame_scope(S_body,pframe,pframe_tail*)',
              'pcloneupdate = pcloneupdatestring.UPDATE', 'pcloneoperation = pcloneupdate.OPERATION',
              'pcloneupdate.CURSOR = 1',
              'pcloneupdate.VISITED = [pclonevisit_mutable]',
              'pclonevisit_mutable.KEY = KSTRING $ptascii("mutable")',
              'pclonevisit_mutable.TARGET = $ptascii("mutable")',
              'pclonevisit_mutable.DECL = $clone_visit_decl(S_caller,pcloneoperation.TARGET,$ptascii("mutable"))',
              'pclonevisit_mutable.VALUE = eps',
              '$location_slot(S_body,PROPERTY pcloneoperation.TARGET $ptascii("mutable")) = UNDEFINED',
              '$clone_updates_valid(S_caller,pcloneupdate)',
              '$clone_update_string_valid(S_caller,pcloneupdatestring)',
              *seek('S_body','S_result',8),
              '$clone_update_string_valid(S_result,pcloneupdatestring)',
              '$location_slot(S_result,PROPERTY pcloneoperation.TARGET $ptascii("mutable")) = UNDEFINED',
              *seek('S_result','S_two',4),
              'S_two.TODO = (CLONE_READONLY_UPDATE pcloneupdate_two) :: ptask_two_tail*',
              'pcloneupdate_two.VISITED = [pclonevisit_mutable,pclonevisit_string]',
              'pclonevisit_string.VALUE = (PSTRING $ptascii("outer"))',
              '$clone_updates_valid(S_two,pcloneupdate_two)',
              '$location_slot(S_two,PROPERTY pcloneoperation.TARGET $ptascii("mutable")) = UNDEFINED']
    return checks + complete('S_two',expected)

def stringable_guards(initial, expected):
    return stringable(initial, expected)[:58]

def stringable_continuation(initial, expected):
    clauses = stringable(initial, expected)
    return clauses[:29] + clauses[58:]

def fiber(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_parked',10),
              'S_parked.CLONES = [pclonewindow]',
              'pcloneoperation = pclonewindow.OPERATION',
              'pclonewindow.PHASE = CLONE_UPDATES',
              'pclonewindow.AVAILABLE = [$ptascii("x")]',
              '$clone_window_fibers(S_parked,S_parked.ALLOCATIONS,pcloneoperation,CLONE_UPDATES)',
              '~$clone_window_fibers(S_parked,S_parked.ALLOCATIONS,pcloneoperation,CLONE_CALLBACK)',
              '~$clone_window_tasks(S_parked.TODO,pcloneoperation,CLONE_UPDATES)',
              '~$clone_window_frames(S_parked.FRAMES,pcloneoperation,CLONE_UPDATES)',
              '$clone_reinitable(S_parked,pcloneoperation.TARGET,$ptascii("x"))',
              *seek('S_parked','S_main_written',11),
              'S_main_written.CLONES = [pclonewindow[.AVAILABLE = eps][.REVISIONS = [{KEY $ptascii("x"), COUNT 1}]]]',
              '$clone_window_fibers(S_main_written,S_main_written.ALLOCATIONS,pcloneoperation,CLONE_UPDATES)',
              '~$clone_reinitable(S_main_written,pcloneoperation.TARGET,$ptascii("x"))',
              '$location_slot(S_main_written,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("inner"))']
    checks += reject('parked_missing_window','S_main_written[.CLONES = eps]')
    checks += reject('parked_wrong_phase','S_main_written[.CLONES = [pclonewindow[.PHASE = CLONE_CALLBACK][.AVAILABLE = eps]]]','$clone_windows_valid')
    checks += reject('parked_duplicate_window','S_main_written[.CLONES = S_main_written.CLONES ++ S_main_written.CLONES]','$clone_windows_valid')
    return checks + complete('S_main_written',expected)

def inherited_throw(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_body',6),
              '$clone_updates_review_string(S_body) = (pcloneupdatestring)',
              'S_body.CURRENT = (pcallcontext)',
              'S_body.FRAMES = pframe :: pframe_tail*',
              'S_caller = $parameter_string_frame_scope(S_body,pframe,pframe_tail*)',
              'pcloneupdate = pcloneupdatestring.UPDATE',
              'pcloneoperation = pcloneupdate.OPERATION',
              'pcloneupdate.CURSOR = 1',
              'pcloneupdate.VISITED = [pclonevisit_y]',
              'pclonevisit_y.VALUE = (PINT 2)',
              '$clone_updates_valid(S_caller,pcloneupdate)',
              '$clone_update_string_valid(S_caller,pcloneupdatestring)',
              '$object_name(S_body,pcloneupdatestring.OBJECT) = $ptascii("Box")',
              '$trace_context_class(S_body,pcallcontext) = ($ptascii("BaseBox"))',
              '$trace_context(S_body,eps,(pcallcontext)) = ptraceframe_string :: ptraceframe_clone :: ptraceframe_tail*',
              'ptraceframe_string.CLASS = ($ptascii("BaseBox"))',
              'ptraceframe_string.FUNCTION = $ptascii("__toString")',
              r'ptraceframe_string.FILE = eps /\ ptraceframe_string.LINE = $(-1)',
              'ptraceframe_clone.FUNCTION = $ptascii("clone")',
              'ptraceframe_clone.CLASS = eps',
              'ptraceframe_clone.LINE = pcloneoperation.LINE',
              'S_body.CLONES = [pclonewindow]',
              r'pclonewindow.PHASE = CLONE_UPDATES /\ pclonewindow.AVAILABLE = [$ptascii("x")]',
              '$clone_reinitable(S_body,pcloneoperation.TARGET,$ptascii("x"))',
              '~$clone_reinitable(S_body,pcloneoperation.TARGET,$ptascii("y"))',
              '$location_slot(S_body,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("seed"))',
              '$location_slot(S_body,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PINT 2)',
              *seek('S_body','S_caught',12),
              'S_caught.CLONES = eps',
              '~$clone_reinitable(S_caught,pcloneoperation.TARGET,$ptascii("x"))',
              '~$clone_reinitable(S_caught,pcloneoperation.TARGET,$ptascii("y"))',
              '$location_slot(S_caught,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PSTRING $ptascii("seed"))',
              '$location_slot(S_caught,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PINT 2)']
    return checks + complete('S_caught',expected)

def inherited_throw_trace(initial, expected):
    return inherited_throw(initial, expected)[:35]


def inherited_throw_frontier(initial, expected):
    checks = inherited_throw(initial, expected)
    return checks[:15] + checks[35:47]


def alias_failure(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_body',6),
              '$clone_updates_review_string(S_body) = (pcloneupdatestring)',
              'S_body.FRAMES = pframe :: pframe_tail*',
              'S_caller = $parameter_string_frame_scope(S_body,pframe,pframe_tail*)',
              'pcloneupdate = pcloneupdatestring.UPDATE',
              'pcloneoperation = pcloneupdate.OPERATION',
              r'pcloneupdate.CURSOR = 0 /\ pcloneupdate.VISITED = eps',
              '$clone_update_string_valid(S_caller,pcloneupdatestring)',
              '$property_readonly_desc(S_caller,pcloneoperation.TARGET,$ptascii("x")) = eps',
              '$objectprops_record_at(S_body.OBJECTPROPS,pcloneoperation.TARGET) = (pobjectprops)',
              '$property_slot_at(pobjectprops.SLOTS,$ptascii("x")) = (ppropertyslot)',
              'ppropertyslot.STATE = PROP_VALUE (ALIAS n_cell)',
              'S_body.STORE[n_cell] = DEFINED (PINT 1)',
              'S_body.CLONES = [pclonewindow]',
              r'pclonewindow.PHASE = CLONE_UPDATES /\ pclonewindow.AVAILABLE = [$ptascii("z")]',
              '$clone_reinitable(S_body,pcloneoperation.TARGET,$ptascii("z"))',
              *seek('S_body','S_result',8),
              'S_result.TODO = (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_result_tail*',
              '$clone_update_string_valid(S_result,pcloneupdatestring)',
              'S_result.STORE[n_cell] = DEFINED (PINT 1)',
              'S_result.CLONES = [pclonewindow]',
              '$location_slot(S_result,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 1)',
              '$location_slot(S_result,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PINT 1)',
              *seek('S_result','S_caught',13),
              'S_caught.CLONES = eps',
              'S_caught.STORE[n_cell] = DEFINED (PINT 1)',
              '~$clone_reinitable(S_caught,pcloneoperation.TARGET,$ptascii("z"))',
              '$location_slot(S_caught,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 1)',
              '$location_slot(S_caught,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PINT 1)',
              '$location_slot(S_caught,PROPERTY pcloneoperation.SOURCE $ptascii("x")) = DEFINED (PINT 1)']
    return checks + complete('S_caught',expected)

def alias_this(initial, expected):
    checks = alias_failure(initial, expected)
    at = checks.index('S_result_found = $clone_updates_review_seek(S_body,8,2048)')
    extra = [
        'S_body.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("other")) = (n_other_cell)',
        'S_body.STORE[n_other_cell] = DEFINED (POBJECT n_other)',
        r'$(n_other < pcloneoperation.SOURCE) /\ $(pcloneoperation.SOURCE < pcloneoperation.TARGET)',
        '$this_receiver(S_caller) = (pcloneoperation.SOURCE)',
        '$this_receiver(S_caller) =/= (n_other)',
        'pcloneoperation.CALL = (pclonecall)',
        'pclonecall.SENT = (NAMED_SENT (KNOWN (POBJECT pcloneoperation.SOURCE))) :: pnamedslot_tail*',
        'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring) :: ptask_string_tail*',
        '$clone_operation_source_valid(S_caller,pcloneoperation)',
        'pclonecall_bad_source = pclonecall[.SENT = (NAMED_SENT (KNOWN (POBJECT n_other))) :: pnamedslot_tail*]',
        'pcloneoperation_bad_source = pcloneoperation[.SOURCE = n_other][.CALL = (pclonecall_bad_source)]',
        'pcloneupdatestring_bad_source = pcloneupdatestring[.UPDATE = pcloneupdate[.OPERATION = pcloneoperation_bad_source]]',
        'pframe_bad_source = pframe[.TODO = (STRINGIFY_RESULT n_object porigin_site z_line) :: (CLONE_READONLY_STRING pcloneupdatestring_bad_source) :: ptask_string_tail*]',
        'S_bad_source = S_body[.FRAMES = pframe_bad_source :: pframe_tail*][.CLONES = [pclonewindow[.OPERATION = pcloneoperation_bad_source]]]',
        'S_bad_caller = $parameter_string_frame_scope(S_bad_source,pframe_bad_source,pframe_tail*)',
        '$this_receiver(S_bad_caller) = (pcloneoperation.SOURCE)',
        '$clone_updates_body_valid(S_bad_caller,pcloneoperation_bad_source)',
        '$clone_windows_valid(S_bad_source)',
        '$heap_valid($heap_graph(S_bad_source))',
        '~$clone_operation_source_valid(S_bad_caller,pcloneoperation_bad_source)',
        '~$clone_update_string_valid(S_bad_caller,pcloneupdatestring_bad_source)',
        '~$call_descriptors_valid(S_bad_source)',
    ]
    return checks[:at] + extra + checks[at:]

def named_this(initial, expected):
    checks = alias_this(initial, expected)
    at = checks.index('S_result_found = $clone_updates_review_seek(S_body,8,2048)')
    return checks[:at] + ['pclonecall.NAMED', 'pclonecall.INDEX = 2']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True,
                        choices=['window', 'abrupt', 'stringable_guards', 'stringable_continuation', 'mutable', 'fiber', 'inherited_throw_trace', 'inherited_throw_frontier', 'alias_this', 'named_this'])
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--prepare', action='store_true', help='frontend/adapter only; no model credit')
    args = parser.parse_args()
    names = {'window': 'readonly-state-clone-with-update-window',
             'abrupt': 'readonly-clone-with-abrupt-retains-prefix',
             'stringable_guards': 'readonly-clone-with-stringable-inner-consumes-window',
             'stringable_continuation': 'readonly-clone-with-stringable-inner-consumes-window',
             'mutable': 'readonly-clone-with-mutable-visit-unset',
             'fiber': 'readonly-clone-with-stringable-fiber-window',
             'inherited_throw_trace': 'readonly-clone-with-inherited-stringable-throw-relocks',
             'inherited_throw_frontier': 'readonly-clone-with-inherited-stringable-throw-relocks',
             'alias_this': 'readonly-clone-with-mutable-stringable-alias-this',
             'named_this': 'readonly-clone-with-named-mutable-stringable-alias-this'}
    name = names[args.group]
    source_bytes, expected = CASES[name], EXPECTED[name]
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='readonly-clone-updates-'+args.group+'-', dir=ROOT/'.tools')).resolve()
    path = out/'source.php'; path.write_bytes(source_bytes)
    report = {'passed': False, 'before': before, 'group': args.group, 'source': str(path),
              'source_sha256': sha(path), 'state_assertions_evaluated': 0,
              'mode': 'prepared; model UNRUN' if args.prepare else 'source-reached',
              'profile': cross.invoke.types.PROFILE, 'runner_mode': 'AL', 'jobs': 1}
    frontend = adapter = None
    print(out, flush=True)
    try:
        frontend = Worker([str(ROOT/'.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source_bytes).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(path)).decode())+')'
        clauses = globals()[args.group](initial, expected)
        clauses = ['program_source = '+checked['fixture'], *clauses]
        fixture = out/'protocol.watsup'
        prefix = PREFIX + {'inherited_throw_trace': THROW_PREFIX, 'inherited_throw_frontier': THROW_PREFIX, 'alias_this': ALIAS_PREFIX}.get(args.group, '')
        fixture.write_text(prefix+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+
            '\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report['prepared_assertions'] = len(clauses)
        if not args.prepare:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),
                *[str(ROOT/p) for p in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report.update(passed=True, state_assertions_evaluated=len(clauses))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['after'] = snapshot(args.freeze)
        report['source_unchanged'] = report['source_sha256'] == sha(path)
        report['passed'] = report['passed'] and report['before'] == report['after'] and report['source_unchanged']
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['mode'] if args.prepare else report['passed'], flush=True)
    assert args.prepare or report['passed']


if __name__ == '__main__':
    main()
